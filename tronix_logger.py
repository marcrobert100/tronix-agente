import os
import sys
import sqlite3
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join(os.path.dirname(__file__), "tronix.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS conteudo (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo        TEXT CHECK(tipo IN ('imagem','video','mininovela','audio')) NOT NULL,
                titulo      TEXT NOT NULL,
                descricao   TEXT,
                arquivo     TEXT NOT NULL,
                pasta       TEXT DEFAULT 'uploads',
                tamanho_kb  INTEGER DEFAULT 0,
                duracao_seg INTEGER DEFAULT NULL,
                legenda     TEXT,
                hashtags    TEXT,
                voz_usada   TEXT,
                status_post TEXT CHECK(status_post IN ('pendente','postado','erro')) DEFAULT 'pendente',
                rede_social TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_postagem DATETIME,
                metadata    TEXT
            );

            CREATE TABLE IF NOT EXISTS pipeline_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                acao        TEXT NOT NULL,
                script      TEXT,
                conteudo_id INTEGER,
                status      TEXT CHECK(status IN ('sucesso','erro')) NOT NULL,
                mensagem    TEXT,
                data        DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conteudo_id) REFERENCES conteudo(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS agendamento (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL,
                tipo        TEXT DEFAULT 'diario',
                horario     TEXT NOT NULL,
                script      TEXT NOT NULL,
                parametros  TEXT,
                ativo       INTEGER DEFAULT 1,
                ultima_exec DATETIME,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE VIEW IF NOT EXISTS hoje AS
                SELECT COUNT(*) AS total, tipo, SUM(tamanho_kb) AS kb
                FROM conteudo
                WHERE DATE(data_criacao) = DATE('now')
                GROUP BY tipo;
        """)
        conn.commit()
        print("  [DB] SQLite inicializado em tronix.db")
        return True
    except Exception as e:
        print(f"  [DB] Erro: {e}")
        return False
    finally:
        conn.close()

def registrar(tipo, titulo, arquivo, pasta="videos_saida", legenda="", hashtags="",
              voz_usada="", tamanho_kb=0, duracao_seg=0):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = """INSERT INTO conteudo
                 (tipo, titulo, arquivo, pasta, tamanho_kb, duracao_seg, legenda, hashtags, voz_usada)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (tipo, titulo, arquivo, pasta, tamanho_kb, duracao_seg, legenda, hashtags, voz_usada))
        conn.commit()
        id_ = cursor.lastrowid
        print(f"  [DB] Registrado: #{id_} - {titulo}")
        return id_
    except Exception as e:
        print(f"  [DB] Erro: {e}")
        return None
    finally:
        conn.close()

def log_pipeline(acao, script, status, mensagem="", conteudo_id=None):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pipeline_log (acao, script, conteudo_id, status, mensagem) VALUES (?, ?, ?, ?, ?)",
                       (acao, script, conteudo_id, status, mensagem))
        conn.commit()
    except Exception as e:
        print(f"  [DB] Erro log: {e}")
    finally:
        conn.close()

def marcar_postado(conteudo_id, rede="instagram"):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE conteudo SET status_post='postado', rede_social=?, data_postagem=CURRENT_TIMESTAMP WHERE id=?",
                       (rede, conteudo_id))
        conn.commit()
        print(f"  [DB] #{conteudo_id} marcado postado no {rede}")
    except Exception as e:
        print(f"  [DB] Erro: {e}")
    finally:
        conn.close()

def listar_pendentes():
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conteudo WHERE status_post='pendente' ORDER BY data_criacao DESC")
        return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        print(f"  [DB] Erro: {e}")
        return []
    finally:
        conn.close()

def estatisticas():
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, COUNT(*) as total, SUM(tamanho_kb) as kb FROM conteudo GROUP BY tipo")
        return [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        print(f"  [DB] Erro: {e}")
        return {}
    finally:
        conn.close()

if __name__ == "__main__":
    inicializar()
