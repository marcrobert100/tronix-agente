#!/usr/bin/env python3
"""
Sincronizador Automático do Tronix
==================================
Sincroniza automaticamente as skills e projetos do Tronix com o banco de dados.
"""

import pymysql
import json
import os
import sys
from datetime import datetime

def sync_tronix():
    """Main sync function"""
    print("=" * 60)
    print("  TRONIX DATABASE SYNC")
    print("=" * 60)
    print()
    
    # Connect to database
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='tronix_system',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("[OK] Conectado ao banco de dados Tronix System")
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")
        return False
    
    # Load skills from tronix_core.json
    try:
        with open('tronix_core.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            skills = data.get('skills_ativas', [])
            print(f"[INFO] Carregadas {len(skills)} skills de tronix_core.json")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar tronix_core.json: {e}")
        conn.close()
        return False
    
    # Sync skills to database
    try:
        with conn.cursor() as cursor:
            # Clear existing AI skills
            cursor.execute("DELETE FROM skills WHERE categoria = 'AI'")
            
            # Insert new skills
            for skill in skills:
                cursor.execute(
                    "INSERT INTO skills (nome, descricao, categoria) VALUES (%s, %s, %s)",
                    (skill, f"Skill {skill} do Tronix", "AI")
                )
            
            conn.commit()
            print(f"[OK] {len(skills)} skills sincronizadas no banco de dados")
    except Exception as e:
        print(f"[ERRO] Falha ao sincronizar skills: {e}")
        conn.close()
        return False
    
    # Log sync operation
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO logs_evolucao (agente, acao, timestamp) VALUES (%s, %s, %s)",
                ("Tronix Sync", f"Sincronizado {len(skills)} skills", datetime.now())
            )
            conn.commit()
            print("[OK] Log de sincronização registrado")
    except Exception as e:
        print(f"[ERRO] Falha ao registrar log: {e}")
    
    # Verify sync
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM skills WHERE categoria = 'AI'")
            result = cursor.fetchone()
            print(f"\n[INFO] Skills no banco de dados: {result['count']}")
            
            # Show first 10 skills
            cursor.execute("SELECT nome FROM skills WHERE categoria = 'AI' LIMIT 10")
            skills_db = cursor.fetchall()
            print("\n[INFO] Primeiras 10 skills:")
            for skill in skills_db:
                print(f"  - {skill['nome']}")
    except Exception as e:
        print(f"[ERRO] Falha ao verificar sincronização: {e}")
    
    conn.close()
    print("\n[OK] Sincronização concluída!")
    return True

if __name__ == "__main__":
    success = sync_tronix()
    sys.exit(0 if success else 1)
