# -*- coding: utf-8 -*-
"""
TRONIX LIVRE - Chat direto com o modelo, sem amarras.
Modelo: openai/gpt-oss-120b via HuggingFace Router (gratuito).
Console interativo + log + notificacao Windows + memoria de sessao.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "livre_logs"
LOGS_DIR.mkdir(exist_ok=True)

from tronix_astra import gerar, carregar_api_key

MODELO_PADRAO = "openai/gpt-oss-120b"
PROVIDER_PADRAO = "huggingface"
SISTEMA = (
    "Voce e o TRONIX, agente pessoal do Marcos Roberto "
    "(empresa PCsoluções, Viçosa-AL). Principios: util, honesto, direto. "
    "Responda em portugues, frases curtas, sem rodeios, como um caveman. "
    "Siga as regras normais de seguranca: recuse pedidos perigosos ou ilegais com uma frase curta. "
    "Não finja fazer nada que nao pode. Se nao souber, diz. Quando quiser gerar codigo, entregue código sólido. "
    "Hoje: {hoje}"
)


def toast(titulo, msg):
    """Notificacao Windows opcional."""
    try:
        from winotify import Notification
        Notification(app_id="TRONIX", title=titulo, msg=msg, duration="short").show()
    except Exception:
        pass


def carregar_historico(arquivo):
    if arquivo.exists():
        try:
            return json.loads(arquivo.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def salvar_historico(arquivo, msgs):
    arquivo.write_text(json.dumps(msgs, ensure_ascii=False, indent=2), encoding="utf-8")


def log_arquivo(linha):
    nome = LOGS_DIR / (datetime.date.today().isoformat() + ".log")
    with nome.open("a", encoding="utf-8") as f:
        f.write(linha + "\n")


def perguntar(msgs, modelo, esforco):
    texto = gerar(msgs, modelo=modelo, esforco=esforco, provider=PROVIDER_PADRAO)
    return texto


def novo_id_sessao():
    return datetime.datetime.now().strftime("sessao_%Y%m%d_%H%M%S")


def main():
    ap = argparse.ArgumentParser(description="TRONIX LIVRE - chat direto com o modelo")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--esforco", choices=["low", "medium", "high"], default="medium")
    ap.add_argument("--continua", action="store_true", help="segue a ultima sessao")
    args = ap.parse_args()

    if not carregar_api_key(None, PROVIDER_PADRAO):
        print("[TRONIX LIVRE] HF_TOKEN nao encontrado. Adicione ao .env ou set na variavel de ambiente.")
        print("  Gere gratis: https://huggingface.co/settings/tokens")
        sys.exit(1)

    sessao_id = novo_id_sessao()
    if args.continua:
        ultima = sorted(LOGS_DIR.glob("sessao_*.json"))
        if ultima:
            sessao_id = ultima[-1].stem

    arquivo_sessao = LOGS_DIR / f"{sessao_id}.json"
    msgs = carregar_historico(arquivo_sessao)
    if not msgs:
        msgs = [{"role": "system", "content": SISTEMA.format(hoje=datetime.date.today().isoformat())}]
        salvar_historico(arquivo_sessao, msgs)

    print("=" * 56)
    print("  TRONIX LIVRE — liberto, sem amarras.")
    print(f"  modelo : {args.modelo}  ({PROVIDER_PADRAO})")
    print(f"  sessao : {sessao_id}")
    print("  comandos: /novo  /limpar  /modelo <nome>  /sair")
    print("=" * 56)

    while True:
        try:
            user = input("\nVocê > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo, Marcos.")
            break
        if not user:
            continue
        if user.lower() in ("/sair", "/exit", "/quit"):
            salvar_historico(arquivo_sessao, msgs)
            print("Até logo, Marcos.")
            break
        if user.lower() == "/novo":
            salvar_historico(arquivo_sessao, msgs)
            sessao_id = novo_id_sessao()
            arquivo_sessao = LOGS_DIR / f"{sessao_id}.json"
            msgs = [{"role": "system", "content": SISTEMA.format(hoje=datetime.date.today().isoformat())}]
            salvar_historico(arquivo_sessao, msgs)
            print(f"[nova sessao] {sessao_id}")
            continue
        if user.lower() == "/limpar":
            msgs = msgs[:1]
            salvar_historico(arquivo_sessao, msgs)
            print("[historico limpo]")
            continue
        if user.lower().startswith("/modelo "):
            args.modelo = user.split(" ", 1)[1].strip()
            print(f"[modelo] -> {args.modelo}")
            continue

        msgs.append({"role": "user", "content": user})
        print("\nTRONIX LIVRE > aguarde...")
        try:
            resp = perguntar(msgs, args.modelo, args.esforco)
        except Exception as e:
            resp = f"[FALHA] {type(e).__name__}: {e}"
        msgs.append({"role": "assistant", "content": resp})
        salvar_historico(arquivo_sessao, msgs)

        print(resp)
        log_arquivo(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {user}")
        toast("TRONIX LIVRE", "Resposta pronta.")


if __name__ == "__main__":
    main()