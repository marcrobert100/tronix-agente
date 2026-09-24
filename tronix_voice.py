#!/usr/bin/env python3
"""
Tronix Voice - JARVIS local via Gemini Live API
Voz bidirecional em tempo real integrada ao ecossistema Tronix.
Uso:
  python tronix_voice.py              # iniciar conversa por voz
  python tronix_voice.py --status     # ver configuração
  python tronix_voice.py --mic        # listar dispositivos de áudio
Requisitos: GEMINI_API_KEY no .env (gratis em aistudio.google.com)
"""
import asyncio, os, sys, json, io, urllib.request, sqlite3
from pathlib import Path

import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
SAMPLE_RATE = 24000


def load_env() -> dict:
    env = {}
    envfile = ROOT / ".env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"')
    return env


ENV = load_env()
API_KEY = os.environ.get("GEMINI_API_KEY") or ENV.get("GEMINI_API_KEY")
MODEL = ENV.get("GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview")
FALLBACK_MODEL = "gemini-2.0-flash-live-001"
VOICE = ENV.get("GEMINI_LIVE_VOICE", "Kore")
GATEWAY = "http://localhost:8081"

SYSTEM_PROMPT = (
    "Você é TRONIX, assistente de voz pessoal do Marcos Roberto, dono da "
    "PCsoluções em Viçosa-AL, Brasil. Responda sempre em português brasileiro, "
    "de forma curta e direta, natural para conversa falada. "
    "Você controla um ecossistema de automação: status do sistema, agentes, "
    "scripts de geração de conteúdo (videos, imagens, mini novelas) e memória. "
    "Use as ferramentas disponíveis para consultar ou executar ações quando o "
    "Marcos pedir. Se algo falhar, seja honesto e sugira o próximo passo."
)


def http_json(method: str, path: str, body: dict = None, timeout: int = 8):
    url = f"{GATEWAY}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def run_tool(name: str, args: dict) -> dict:
    try:
        if name == "tronix_status":
            health = {"gateway": "offline", "banco": "unknown"}
            try:
                h = http_json("GET", "/health")
                health["gateway"] = "online"
                health.update(h)
            except Exception:
                pass
            try:
                con = sqlite3.connect(str(ROOT / "tronix.db"))
                con.execute("SELECT 1")
                con.close()
                health["banco"] = "online"
            except Exception as e:
                health["banco"] = f"erro: {e}"
            return health
        if name == "tronix_agentes":
            try:
                return http_json("GET", "/agentes")
            except Exception:
                core = json.loads((ROOT / "tronix_core.json").read_text(encoding="utf-8"))
                return {"agentes": core["multi_agente"]["agentes"]}
        if name == "tronix_scripts":
            return http_json("GET", "/scripts")
        if name == "tronix_executar":
            script = args.get("script", "")
            return http_json("POST", "/executar", {"script": script})
        if name == "tronix_memoria":
            return http_json("GET", "/memoria?limit=5")
        return {"erro": f"ferramenta desconhecida: {name}"}
    except Exception as e:
        return {"erro": str(e)}


def build_tools():
    string_schema = types.Schema(type="STRING")
    return [
        types.FunctionDeclaration(
            name="tronix_status",
            description="Verifica status do sistema Tronix: gateway, banco de dados, n8n.",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
        types.FunctionDeclaration(
            name="tronix_agentes",
            description="Lista os agentes disponíveis da equipe Tronix (CrewAI).",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
        types.FunctionDeclaration(
            name="tronix_scripts",
            description="Lista os scripts/ferramentas disponíveis no ecossistema Tronix.",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
        types.FunctionDeclaration(
            name="tronix_executar",
            description="Executa um script/ferramenta do Tronix pelo nome.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"script": string_schema},
                required=["script"],
            ),
        ),
        types.FunctionDeclaration(
            name="tronix_memoria",
            description="Consulta as últimas ações registradas na memória do Tronix.",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
    ]


class AudioHandler:
    @classmethod
    async def get_input_stream(cls):
        audio_queue = asyncio.Queue()

        def callback(indata, frames, time, status):
            audio_queue.put_nowait(bytes(indata))

        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            callback=callback,
            blocksize=int(SAMPLE_RATE * 0.1),
        )
        return stream, audio_queue

    @classmethod
    async def get_output_stream(cls):
        stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        return stream


async def handle_receive(session):
    try:
        async for msg in session.receive():
            if msg.function_call:
                fc = msg.function_call
                try:
                    args = json.loads(fc.args) if fc.args else {}
                except Exception:
                    args = {}
                print(f"\n[Tronix] chamando ferramenta: {fc.name}({args})", flush=True)
                result = await run_tool(fc.name, args)
                await session.send(function_response={fc.id: result})
            elif msg.server_content:
                turn = msg.server_content.model_turn
                if turn:
                    for part in turn.parts:
                        if part.text:
                            print(f"\n[Tronix] {part.text}", flush=True)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[erro receive] {e}", flush=True)


async def run_session(client, model):
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(parts=[types.Part(text=SYSTEM_PROMPT)]),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
            )
        ),
        tools=build_tools(),
    )
    async with client.aio.live.connect(model=model, config=config) as session:
        input_stream, audio_queue = await AudioHandler.get_input_stream()
        output_stream = await AudioHandler.get_output_stream()
        receive_task = asyncio.create_task(handle_receive(session))
        print("[Tronix] Voz ativa. Falando... (Ctrl+C para parar)", flush=True)
        try:
            with input_stream, output_stream:
                await session.send(input=audio_queue, output=output_stream)
                await asyncio.sleep(3600)
        finally:
            receive_task.cancel()


async def main():
    if not API_KEY:
        print("ERRO: GEMINI_API_KEY não encontrada no .env")
        print("Crie grátis em https://aistudio.google.com/apikey e adicione no C:\\xampp\\htdocs\\agente\\.env")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)
    try:
        await run_session(client, MODEL)
    except Exception as e:
        err = str(e)
        print(f"[erro] {MODEL}: {err[:200]}")
        if MODEL != FALLBACK_MODEL:
            print(f"[tentando] fallback {FALLBACK_MODEL}...")
            try:
                await run_session(client, FALLBACK_MODEL)
            except Exception as e2:
                print(f"[erro] fallback falhou: {str(e2)[:200]}")
                sys.exit(1)


def show_status():
    print("=== Tronix Voice ===")
    print(f"Modelo : {MODEL}")
    print(f"Fallback: {FALLBACK_MODEL}")
    print(f"Voz   : {VOICE}")
    print(f"API key: {'definida' if API_KEY else 'FALTANDO (crie em aistudio.google.com/apikey)'}")
    print(f"Gateway: {GATEWAY}")
    print(f"Skill voz: {len(build_tools())} ferramentas")


def list_mics():
    print("Dispositivos de áudio:")
    for dev in sd.query_devices():
        idx = dev["index"]
        name = dev["name"]
        ins = dev["max_input_channels"]
        outs = dev["max_output_channels"]
        if ins > 0 or outs > 0:
            print(f"  [{idx}] {name} (in={ins}, out={outs})")


if __name__ == "__main__":
    if "--status" in sys.argv:
        show_status()
    elif "--mic" in sys.argv:
        list_mics()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n[Tronix] Voz encerrada.")
