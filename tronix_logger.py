import os
import sys
import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join(os.path.dirname(__file__), "tronix.db")
_ASSET_CACHE: dict[str, str] = {}
_LOG_LEVELS = ("info", "warn", "error")


class DB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self.conn

    def __exit__(self, *args: Any) -> None:
        self.conn.close()


def log(level: str, evento: str, **kwargs: Any) -> None:
    if level not in _LOG_LEVELS:
        level = "info"
    registro = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "level": level,
        "evento": evento,
    }
    registro.update(kwargs)
    print(json.dumps(registro, ensure_ascii=False), flush=True)


def _txt(valor: Any, nome: str = "", maximo: int = 500) -> str:
    if valor is None:
        return ""
    texto = str(valor).strip()
    return texto[:maximo]


def _int(valor: Any, minimo: int = 0) -> int:
    try:
        return max(minimo, int(valor))
    except (TypeError, ValueError):
        return minimo


def asset_hash(caminho: str) -> Optional[str]:
    try:
        h = hashlib.blake2b(digest_size=8)
        with open(caminho, "rb") as f:
            for bloco in iter(lambda: f.read(65536), b""):
                h.update(bloco)
        return h.hexdigest()
    except OSError:
        return None


def asset_cache_get(caminho: str) -> Optional[str]:
    chave = asset_hash(caminho)
    if chave and _ASSET_CACHE.get(chave) == caminho:
        return caminho
    return None


def asset_cache_set(caminho: str) -> None:
    chave = asset_hash(caminho)
    if chave:
        _ASSET_CACHE[chave] = caminho


def inicializar() -> bool:
    try:
        with DB() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conteudo (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo         TEXT CHECK(tipo IN ('imagem','video','mininovela','audio')) NOT NULL,
                    titulo       TEXT NOT NULL,
                    descricao    TEXT,
                    arquivo      TEXT NOT NULL,
                    pasta        TEXT DEFAULT 'uploads',
                    tamanho_kb   INTEGER DEFAULT 0,
                    duracao_seg  INTEGER DEFAULT NULL,
                    legenda      TEXT,
                    hashtags     TEXT,
                    voz_usada    TEXT,
                    status_post  TEXT CHECK(status_post IN ('pendente','postado','erro')) DEFAULT 'pendente',
                    rede_social  TEXT,
                    data_criacao  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_postagem DATETIME,
                    metadata     TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_conteudo_tipo ON conteudo(tipo);
                CREATE INDEX IF NOT EXISTS idx_conteudo_status ON conteudo(status_post);
                CREATE INDEX IF NOT EXISTS idx_conteudo_data ON conteudo(data_criacao);

                CREATE TABLE IF NOT EXISTS pipeline_log (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    acao         TEXT NOT NULL,
                    script       TEXT,
                    conteudo_id  INTEGER,
                    status       TEXT CHECK(status IN ('sucesso','erro')) NOT NULL,
                    mensagem     TEXT,
                    data         DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conteudo_id) REFERENCES conteudo(id) ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_pipeline_data ON pipeline_log(data);
                CREATE INDEX IF NOT EXISTS idx_pipeline_status ON pipeline_log(status);

                CREATE TABLE IF NOT EXISTS agendamento (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome         TEXT NOT NULL,
                    tipo         TEXT DEFAULT 'diario',
                    horario      TEXT NOT NULL,
                    script       TEXT NOT NULL,
                    parametros   TEXT,
                    ativo        INTEGER DEFAULT 1,
                    ultima_exec  DATETIME,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS tarefas (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    agente       TEXT NOT NULL,
                    acao         TEXT NOT NULL,
                    status       TEXT CHECK(status IN ('pendente','executando','concluido','erro')) DEFAULT 'pendente',
                    resultado    TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_fim     DATETIME
                );

                CREATE VIEW IF NOT EXISTS hoje AS
                    SELECT COUNT(*) AS total, tipo, SUM(tamanho_kb) AS kb
                    FROM conteudo
                    WHERE DATE(data_criacao) = DATE('now')
                    GROUP BY tipo;

                CREATE VIEW IF NOT EXISTS resumo_mensal AS
                    SELECT strftime('%Y-%m', data_criacao) AS mes,
                           tipo,
                           COUNT(*) AS total,
                           SUM(tamanho_kb) AS kb
                    FROM conteudo
                    GROUP BY mes, tipo
                    ORDER BY mes DESC;
            """)
        log("info", "banco_inicializado", db=DB_PATH)
        return True
    except Exception as e:
        log("error", "falha_inicializar", erro=str(e))
        return False


def registrar(tipo: str = "video", titulo: str = "", arquivo: str = "",
              pasta: str = "videos_saida", legenda: str = "", hashtags: str = "",
              voz_usada: str = "", tamanho_kb: int = 0, duracao_seg: int = 0) -> Optional[int]:
    tipo = tipo if tipo in ("imagem", "video", "mininovela", "audio") else "video"
    try:
        with DB() as conn:
            cur = conn.execute("""INSERT INTO conteudo
                (tipo, titulo, arquivo, pasta, tamanho_kb, duracao_seg, legenda, hashtags, voz_usada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (_txt(tipo, maximo=20), _txt(titulo, maximo=200), _txt(arquivo, maximo=300),
                 _txt(pasta, maximo=100), _int(tamanho_kb), _int(duracao_seg),
                 _txt(legenda), _txt(hashtags), _txt(voz_usada, maximo=50)))
            id_ = cur.lastrowid
        log("info", "conteudo_registrado", id=id_, titulo=titulo[:60], tipo=tipo)
        asset_cache_set(arquivo)
        return id_
    except Exception as e:
        log("error", "falha_registro", erro=str(e), arquivo=arquivo)
        return None


def registrar_lote(itens: list[dict]) -> list[int]:
    ids: list[int] = []
    try:
        with DB() as conn:
            for item in itens:
                tipo = item.get("tipo", "video")
                tipo = tipo if tipo in ("imagem", "video", "mininovela", "audio") else "video"
                cur = conn.execute("""INSERT INTO conteudo
                    (tipo, titulo, arquivo, pasta, tamanho_kb, duracao_seg, legenda, hashtags, voz_usada)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (tipo, _txt(item.get("titulo", ""), maximo=200),
                     _txt(item.get("arquivo", ""), maximo=300),
                     _txt(item.get("pasta", "videos_saida"), maximo=100),
                     _int(item.get("tamanho_kb", 0)), _int(item.get("duracao_seg", 0)),
                     _txt(item.get("legenda", "")), _txt(item.get("hashtags", "")),
                     _txt(item.get("voz_usada", ""), maximo=50)))
                ids.append(cur.lastrowid)
        log("info", "lote_registrado", quantidade=len(ids))
        return ids
    except Exception as e:
        log("error", "falha_lote", erro=str(e))
        return ids


def log_pipeline(acao: str, script: str, status: str, mensagem: str = "",
                 conteudo_id: Optional[int] = None) -> None:
    status = status if status in ("sucesso", "erro") else "sucesso"
    try:
        with DB() as conn:
            conn.execute("INSERT INTO pipeline_log (acao, script, conteudo_id, status, mensagem) VALUES (?, ?, ?, ?, ?)",
                        (_txt(acao, maximo=200), _txt(script, maximo=100),
                         conteudo_id, status, _txt(mensagem)))
    except Exception as e:
        log("error", "falha_log_pipeline", erro=str(e))


def marcar_postado(conteudo_id: int, rede: str = "instagram") -> None:
    rede = _txt(rede, maximo=50)
    try:
        with DB() as conn:
            conn.execute("UPDATE conteudo SET status_post='postado', rede_social=?, data_postagem=CURRENT_TIMESTAMP WHERE id=?",
                        (rede, conteudo_id))
        log("info", "conteudo_postado", id=conteudo_id, rede=rede)
    except Exception as e:
        log("error", "falha_marcar_postado", id=conteudo_id, erro=str(e))


def listar_pendentes() -> list[dict]:
    try:
        with DB() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM conteudo WHERE status_post='pendente' ORDER BY data_criacao DESC")
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        log("error", "falha_listar_pendentes", erro=str(e))
        return []


def estatisticas() -> dict:
    try:
        with DB() as conn:
            cur = conn.execute("SELECT tipo, COUNT(*) as total, SUM(tamanho_kb) as kb FROM conteudo GROUP BY tipo")
            linhas = cur.fetchall()
            return {
                "conteudos": {r["tipo"]: {"total": r["total"], "kb": r["kb"] or 0} for r in linhas},
                "total_geral": sum(r["total"] for r in linhas),
                "total_kb": sum(r["kb"] or 0 for r in linhas),
            }
    except Exception as e:
        log("error", "falha_estatisticas", erro=str(e))
        return {}


def registrar_tarefa(agente: str, acao: str) -> Optional[int]:
    try:
        with DB() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(tarefas)").fetchall()]
            if "data_criacao" in cols:
                cur = conn.execute("INSERT INTO tarefas (agente, acao) VALUES (?, ?)",
                            (_txt(agente, maximo=50), _txt(acao, maximo=200)))
            else:
                cur = conn.execute("INSERT INTO tarefas (agente, acao, payload, status) VALUES (?, ?, '', 'pendente')",
                            (_txt(agente, maximo=50), _txt(acao, maximo=200)))
            return cur.lastrowid
    except Exception as e:
        log("error", "falha_registrar_tarefa", erro=str(e))
        return None


def exportar_json(arquivo_saida: Optional[str] = None) -> str:
    try:
        saida = {"exportado_em": datetime.now(timezone.utc).isoformat()}
        with DB() as conn:
            conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
            conn.row_factory = sqlite3.Row
            saida["conteudos"] = [dict(r) for r in conn.execute("SELECT * FROM conteudo ORDER BY id DESC")]
            saida["pipeline_logs"] = [dict(r) for r in conn.execute("SELECT * FROM pipeline_log ORDER BY id DESC")]
            saida["agendamentos"] = [dict(r) for r in conn.execute("SELECT * FROM agendamento ORDER BY id DESC")]
            saida["tarefas"] = [dict(r) for r in conn.execute("SELECT * FROM tarefas ORDER BY id DESC")]
        json_str = json.dumps(saida, ensure_ascii=False, indent=2, default=str)
        if arquivo_saida:
            with open(arquivo_saida, "w", encoding="utf-8") as f:
                f.write(json_str)
            log("info", "exportado", arquivo=arquivo_saida)
            return arquivo_saida
        return json_str
    except Exception as e:
        log("error", "falha_exportar", erro=str(e))
        return ""


def limpar(dias: int = 30) -> dict:
    from datetime import timedelta
    limite = (datetime.now() - timedelta(days=dias)).isoformat()
    try:
        removidos = 0
        with DB() as conn:
            removidos = conn.execute("DELETE FROM pipeline_log WHERE data < ?", (limite,)).rowcount
        with DB() as conn:
            conn.execute("VACUUM")
        log("info", "limpeza_concluida", dias=dias, removidos=removidos)
        return {"removidos": removidos, "dias": dias}
    except Exception as e:
        log("error", "falha_limpar", erro=str(e))
        return {"erro": str(e)}


def _cmd_status(_args: list[str] = []) -> None:
    stats = estatisticas()
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def _cmd_listar(_args: list[str] = []) -> None:
    pendentes = listar_pendentes()
    if not pendentes:
        print("Nenhum conteudo pendente.")
        return
    for p in pendentes:
        print(f"  #{p['id']} [{p['tipo']}] {p['titulo']} - {p['arquivo']}")


def _cmd_exportar(args: list[str]) -> None:
    path = args[0] if args else "tronix_export.json"
    exportar_json(path)
    print(f"Exportado para {path}")


def _cmd_limpar(args: list[str]) -> None:
    dias = int(args[0]) if args else 30
    result = limpar(dias)
    print(f"Limpeza: {result.get('removidos', 0)} registros removidos (>{dias} dias)")


CLI_COMMANDS = {
    "status": ("Mostra estatisticas", _cmd_status),
    "listar": ("Lista conteudos pendentes", _cmd_listar),
    "exportar": ("Exporta banco como JSON", _cmd_exportar),
    "limpar": ("Remove logs antigos (padrao 30 dias)", _cmd_limpar),
}


def _main() -> None:
    inicializar()
    if len(sys.argv) < 2:
        print("Uso: python tronix_logger.py <comando> [args]")
        print("Comandos:")
        for nome, (desc, _) in CLI_COMMANDS.items():
            print(f"  {nome:12s} {desc}")
        return
    cmd = sys.argv[1]
    if cmd in CLI_COMMANDS:
        CLI_COMMANDS[cmd][1](sys.argv[2:])
    else:
        print(f"Comando desconhecido: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _main()
