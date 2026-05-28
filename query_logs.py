import os
import pymysql
from dotenv import load_dotenv

load_dotenv('.env')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'tronix_system'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    sql = 'SELECT id, agente, acao, timestamp FROM logs_evolucao ORDER BY id DESC LIMIT 5'
    cursor.execute(sql)
    results = cursor.fetchall()
    
    print("=== ÚLTIMAS 5 AÇÕES - logs_evolucao ===")
    for row in results:
        print(f"ID: {row[0]} | Agente: {row[1]} | Ação: {row[2]} | Timestamp: {row[3]}")
    
    conn.close()
except Exception as e:
    print(f"Erro ao conectar: {e}")