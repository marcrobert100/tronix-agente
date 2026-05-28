import os
import pymysql
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv('.env')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'tronix_system'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

CHAVE = os.environ.get('TRONIX_CHAVE')
if not CHAVE:
    raise ValueError("TRONIX_CHAVE não definida")

def criptografar(texto):
    f = Fernet(CHAVE.encode() if isinstance(CHAVE, str) else CHAVE)
    return f.encrypt(texto.encode()).decode()

def salvar_log_criptografado(agente, acao):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    acao_criptografada = criptografar(acao)
    
    sql = 'INSERT INTO logs_evolucao (agente, acao) VALUES (%s, %s)'
    cursor.execute(sql, (agente, acao_criptografada))
    conn.commit()
    
    log_id = cursor.lastrowid
    conn.close()
    return log_id

if __name__ == "__main__":
    log_id = salvar_log_criptografado('Tronix-SYSTEM', 'Teste de log criptografado')
    print(f"Log criptografado salvo com ID: {log_id}")