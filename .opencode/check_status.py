#!/usr/bin/env python3
"""
Verificador de Status do Tronix
================================
Verifica o status completo do sistema Tronix.
"""

import pymysql
import json
import os
import subprocess
import requests

def check_mysql():
    """Check MySQL connection"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='tronix_system',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM skills")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, f"MySQL conectado - {count} skills no banco"
    except Exception as e:
        return False, f"MySQL erro: {e}"

def check_ollama():
    """Check Ollama engine"""
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = len(data.get('models', []))
            return True, f"Ollama online - {models} modelos instalados"
        return False, "Ollama não responde"
    except:
        return False, "Ollama não está rodando"

def check_chat_server():
    """Check chat server"""
    try:
        response = requests.get("http://localhost:3333", timeout=2)
        if response.status_code == 200:
            return True, "Chat server online em http://localhost:3333"
        return False, f"Chat server erro: {response.status_code}"
    except:
        return False, "Chat server não está rodando"

def check_skills_sync():
    """Check if skills are synced"""
    try:
        with open('tronix_core.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            skills_count = len(data.get('skills_ativas', []))
        
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='tronix_system',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM skills WHERE categoria = 'AI'")
        db_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if skills_count == db_count:
            return True, f"Skills sincronizadas: {db_count}/{skills_count}"
        else:
            return False, f"Skills des sincronizadas: {db_count}/{skills_count}"
    except Exception as e:
        return False, f"Erro ao verificar skills: {e}"

def main():
    print("=" * 60)
    print("  TRONIX SYSTEM STATUS CHECK")
    print("=" * 60)
    print()
    
    checks = [
        ("MySQL Database", check_mysql),
        ("Ollama Engine", check_ollama),
        ("Chat Server", check_chat_server),
        ("Skills Sync", check_skills_sync),
    ]
    
    all_ok = True
    for name, check_func in checks:
        status, message = check_func()
        symbol = "[OK]" if status else "[ERRO]"
        print(f"{symbol} {name}: {message}")
        if not status:
            all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("  [OK] TODO O SISTEMA ESTÁ FUNCIONANDO!")
        print("  Acesse: http://localhost:3333")
    else:
        print("  [ATENCAO] ALGUNS COMPONENTES PRECISAM DE ATENCAO")
    print("=" * 60)

if __name__ == "__main__":
    main()
