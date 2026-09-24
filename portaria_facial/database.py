import sqlite3
import os
import json
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), 'portaria.db')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS pessoas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,
    unidade TEXT,
    embedding BLOB NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs_acesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id INTEGER,
    nome TEXT,
    cpf TEXT,
    reconhecido BOOLEAN,
    similaridade REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
);
'''

DEFAULT_SETTINGS = {
    'threshold': '0.6',
    'frase_liberacao': 'Acesso liberado, {nome}',
    'frase_negado': 'Acesso negado. Nao cadastrado.'
}

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.executescript(SCHEMA)
        for k, v in DEFAULT_SETTINGS.items():
            self.conn.execute(
                'INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)',
                (k, v)
            )
        self.conn.commit()

    def add_person(self, nome, cpf, tipo, unidade, embedding):
        emb_bytes = embedding.astype(np.float32).tobytes()
        cur = self.conn.execute(
            'INSERT INTO pessoas (nome, cpf, tipo, unidade, embedding) VALUES (?, ?, ?, ?, ?)',
            (nome, cpf, tipo, unidade, emb_bytes)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_people(self):
        cur = self.conn.execute(
            'SELECT id, nome, cpf, tipo, unidade FROM pessoas ORDER BY nome'
        )
        return [dict(row) for row in cur.fetchall()]

    def get_person_by_id(self, person_id):
        cur = self.conn.execute(
            'SELECT * FROM pessoas WHERE id = ?', (person_id,)
        )
        row = cur.fetchone()
        if row:
            d = dict(row)
            d['embedding'] = np.frombuffer(d['embedding'], dtype=np.float32)
            return d
        return None

    def get_all_embeddings(self):
        cur = self.conn.execute('SELECT id, nome, cpf, tipo, unidade, embedding FROM pessoas')
        results = []
        for row in cur.fetchall():
            d = dict(row)
            d['embedding'] = np.frombuffer(d['embedding'], dtype=np.float32)
            results.append(d)
        return results

    def delete_person(self, person_id):
        self.conn.execute('DELETE FROM pessoas WHERE id = ?', (person_id,))
        self.conn.commit()

    def log_access(self, pessoa_id, nome, cpf, reconhecido, similaridade):
        self.conn.execute(
            'INSERT INTO logs_acesso (pessoa_id, nome, cpf, reconhecido, similaridade) VALUES (?, ?, ?, ?, ?)',
            (pessoa_id, nome, cpf, reconhecido, similaridade)
        )
        self.conn.commit()

    def get_logs(self, limit=100):
        cur = self.conn.execute(
            'SELECT * FROM logs_acesso ORDER BY timestamp DESC LIMIT ?', (limit,)
        )
        return [dict(row) for row in cur.fetchall()]

    def get_settings(self):
        cur = self.conn.execute('SELECT chave, valor FROM configuracoes')
        settings = {}
        for row in cur.fetchall():
            key = row['chave']
            val = row['valor']
            if key == 'threshold':
                settings[key] = float(val)
            else:
                settings[key] = val
        for k, v in DEFAULT_SETTINGS.items():
            if k not in settings:
                settings[k] = float(v) if k == 'threshold' else v
        return settings

    def save_settings(self, threshold, frase_liberacao, frase_negado):
        self.conn.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?',
                          (str(threshold), 'threshold'))
        self.conn.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?',
                          (frase_liberacao, 'frase_liberacao'))
        self.conn.execute('UPDATE configuracoes SET valor = ? WHERE chave = ?',
                          (frase_negado, 'frase_negado'))
        self.conn.commit()

    def close(self):
        self.conn.close()