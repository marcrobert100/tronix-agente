"""TRONIX MENTE - nucleo de auto-evolucao e interacao.

Da ao TRONIX um loop de reflexao (auto-pensante):
  1. Le a memoria (memoria_tronix.json last_actions) + banco.
  2. Consulta um LLM (provider gratuito via tronix_astra.gerar).
  3. Gera: padroes, licoes, proximas acoes, autonomia sugerida.
  4. Persiste em tronix.db [reflexoes] + reflexao_latest.md.
  5. Mantem perfil de interacao do usuario (perfil_marcos.json).

Uso:
  python tronix_mente.py --status
  python tronix_mente.py --refletir [--modelo openai/gpt-oss-120b] [--provider huggingface]
  python tronix_mente.py --perfil
  python tronix_mente.py --perfil --atualizar "chave=valor"
  python tronix_mente.py --sugerir
  python tronix_mente.py --auto          (refletir + atualizar perfil + log)
"""
import argparse
import datetime
import json
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
import tronix_astra as ta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

DB_PATH = BASE_DIR / "tronix.db"
MEMORIA_PATH = BASE_DIR / "memoria_tronix.json"
PERFIL_PATH = BASE_DIR / "perfil_marcos.json"
REFLEXAO_PATH = BASE_DIR / "reflexao_latest.md"

PERFIL_PADRAO = {
    "nome": "Marcos Roberto",
    "tratamento": "Marcos",
    "localizacao": "Vicosa-AL, Brasil",
    "empresa": "PCsolucoes",
    "idioma": "pt-BR",
    "tom_preferido": "direto, objetivo, sem enrolacao; frequentemente caveman",
    "formato_resposta": "resumos curtos; comandos prontos para copiar",
    "horario_trabalho": "periodo integral, sem restricao",
    "projetos_prioridade": ["InfoEngine", "Tronix AI Assistant", "Pipeline Midia", "Santinho Generator", "Homelab"],
    "evitar": ["explicacoes longas", "perguntar antes de agir quando instrucao e clara"],
    "autonomia": True,
    "ultima_atualizacao": None,
}


def conectar():
    c = sqlite3.connect(str(DB_PATH))
    c.execute(
        """CREATE TABLE IF NOT EXISTS reflexoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            conteudo TEXT,
            modelo TEXT,
            provider TEXT,
            data TEXT
        )"""
    )
    return c


def carregar_perfil():
    if PERFIL_PATH.exists():
        perfil = json.loads(PERFIL_PATH.read_text(encoding="utf-8"))
    else:
        perfil = dict(PERFIL_PADRAO)
    return perfil


def salvar_perfil(perfil):
    perfil["ultima_atualizacao"] = datetime.datetime.now().isoformat(timespec="seconds")
    PERFIL_PATH.write_text(
        json.dumps(perfil, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def ultimas_acoes(n=20):
    if not MEMORIA_PATH.exists():
        return []
    m = json.loads(MEMORIA_PATH.read_text(encoding="utf-8"))
    acoes = m.get("last_actions", [])
    linhas = []
    for a in acoes[-n:]:
        ts = str(a.get("timestamp", ""))[:16]
        ag = a.get("agente", "")
        ac = a.get("acao", "")
        linhas.append(f"- [{ts}] {ag}: {ac[:300]}")
    return linhas


def stats_db():
    c = conectar()
    out = {}
    for t in ["conteudo", "pipeline_log", "tarefas", "agendamento", "reflexoes"]:
        try:
            out[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except sqlite3.OperationalError:
            out[t] = 0
    return out


def montar_prompt_reflexao():
    perfil = carregar_perfil()
    stats = stats_db()
    acoes = ultimas_acoes(20)
    hoje = datetime.date.today().isoformat()
    blocos_acoes = "\n".join(acoes) if acoes else "(sem acoes registradas)"
    return f"""Voce e o TRONIX, agente pessoal de IA do Marcos Roberto (empresa PCsolucoes, Vicosa-AL).
Data: {hoje}

ESTADO DO SISTEMA:
- Banco tronix.db: {json.dumps(stats, ensure_ascii=False)}
- Ultimas acoes registradas:
{blocos_acoes}

PERFIL DO USUARIO:
{json.dumps(perfil, indent=2, ensure_ascii=False)}

TAREFA: faca uma reflexao de auto-evolucao. Responda EXATAMENTE neste formato Markdown:

## Padroes
(o que voce vem fazendo/com quais projetos, o que se repete)

## Licoes e melhorias de interacao
(o que melhorar na relacao TRONIX <-> Marcos; tom, formato, o que perguntar ou nao)

## Proximas 3 acoes sugeridas
1. ...
2. ...
3. ...

## Autonomia sugerida
(o que TRONIX pode fazer sozinho no futuro sem pedir permissao; seja especifico e seguro)

## Estado de saude
(1 frase resumindo se o sistema esta saudavel e o que precisa de atencao)

Seja direto, em portugues, sem introducao nem agradecimentos."""


def espelhar_mysql(texto, modelo):
    try:
        import pymysql
        conn = pymysql.connect(host="localhost", user="root", password="", database="tronix_system", charset="utf8mb4")
        with conn.cursor() as cur:
            resumo = " ".join(texto.splitlines()).strip()[:400]
            cur.execute(
                "INSERT INTO logs_evolucao (agente, acao) VALUES (%s, %s)",
                ("Tronix-MENTE", f"REFLEXAO ({modelo}): {resumo}"),
            )
        conn.commit()
        conn.close()
        print("[mente] reflexao espelhada no MySQL tronix_system.logs_evolucao")
    except Exception as e:
        print(f"[mente] MySQL indisponivel (opcional; ignorado): {e}")


def refletir(modelo, provider):
    print(f"[mente] consultando LLM ({provider}/{modelo})...")
    texto = ta.gerar(
        montar_prompt_reflexao(),
        modelo=modelo,
        esforco="medium",
        provider=provider,
    )
    REFLEXAO_PATH.write_text(texto, encoding="utf-8")
    c = conectar()
    agora = datetime.datetime.now().isoformat(timespec="seconds")
    c.execute(
        "INSERT INTO reflexoes (tipo, conteudo, modelo, provider, data) VALUES (?,?,?,?,?)",
        ("reflexao", texto, modelo, provider, agora),
    )
    c.commit()
    print(f"[mente] reflexao salva em reflexao_latest.md ({len(texto)} chars) e no banco.")
    espelhar_mysql(texto, modelo)
    return texto


def sugerir():
    c = conectar()
    try:
        row = c.execute(
            "SELECT conteudo, data FROM reflexoes ORDER BY id DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        row = None
    if not row:
        print("Sem reflexoes ainda. Rode: python tronix_mente.py --refletir")
        return
    conteudo, data = row
    print(f"Ultima reflexao ({data}):")
    print(conteudo)
    linha = [l for l in conteudo.splitlines() if l.strip().startswith("1. ")]
    if linha:
        print("\nProximo passo sugerido:")
        print(linha[0])


def perfil_atualizar(pares):
    perfil = carregar_perfil()
    for par in pares:
        if "=" not in par:
            print(f"[mente] ignora '{par}' (formato chave=valor)")
            continue
        k, _, v = par.partition("=")
        k = k.strip()
        v = v.strip()
        try:
            perfil[k] = json.loads(v)
        except json.JSONDecodeError:
            perfil[k] = v
        print(f"[mente] perfil atualizado: {k}")
    salvar_perfil(perfil)


def status():
    stats = stats_db()
    perfil = carregar_perfil()
    print("== TRONIX MENTE - STATUS ==")
    print(f"Banco: {json.dumps(stats, ensure_ascii=False)}")
    print(f"Perfil: {perfil.get('nome')} | tom: {perfil.get('tom_preferido')}")
    print(f"Autonomia: {'ON' if perfil.get('autonomia') else 'OFF'}")
    print(f"Reflexao mais recente: {REFLEXAO_PATH.name if REFLEXAO_PATH.exists() else 'nenhuma'}")
    print("\nProviders disponiveis:")
    for p, info in ta.PROVIDERS.items():
        chave = ta.carregar_api_key(p, p) or "(sem chave)"
        chave = (chave[:6] + "...") if chave != "(sem chave)" else chave
        print(f"  {p:12} -> {info['base_url'] or 'default'} | chave {chave}")


def main():
    ap = argparse.ArgumentParser(description="TRONIX MENTE - auto-evolucao")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--refletir", action="store_true")
    ap.add_argument("--sugerir", action="store_true")
    ap.add_argument("--perfil", action="store_true")
    ap.add_argument("--atualizar", nargs="*", default=None, help="chave=valor [chave=valor ...]")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--provider", default="huggingface")
    ap.add_argument("--modelo", default="openai/gpt-oss-120b")
    args = ap.parse_args()

    if args.status:
        status()
        return
    if args.atualizar is not None:
        perfil_atualizar(args.atualizar)
        return
    if args.perfil:
        print(json.dumps(carregar_perfil(), indent=2, ensure_ascii=False))
        return
    if args.sugerir:
        sugerir()
        return
    if args.auto or args.refletir:
        try:
            refletir(args.modelo, args.provider)
        except RuntimeError as e:
            print(f"[mente] ERRO na reflexao: {e}")
        return
    if not args.auto:
        ap.print_help()


if __name__ == "__main__":
    main()