#!/usr/bin/env python3
"""
Tronix OpenHuman Bridge - Processa voice commands e integra com agentes CrewAI
Uso: python tronix_openhuman_agent.py "comando de voz"
"""

import os, sys, json, requests
from datetime import datetime

GATEWAY_URL = "http://localhost:8081"
OPENHUMAN_API = "http://localhost:3000/api"

def processar_comando(comando):
    """Processa voice command e retorna resposta"""
    comando_lower = comando.lower()
    
    # Comandos de status
    if any(word in comando_lower for word in ["status", "sistema", "saude"]):
        r = requests.get(f"{GATEWAY_URL}/health")
        return r.json()
    
    # Comandos de agentes
    elif any(word in comando_lower for word in ["agente", "agentes", "time"]):
        r = requests.get(f"{GATEWAY_URL}/agentes")
        return r.json()
    
    # Comandos de scripts
    elif any(word in comando_lower for word in ["script", "scripts", "ferramenta"]):
        r = requests.get(f"{GATEWAY_URL}/scripts")
        return r.json()
    
    # Comandos de execução
    elif any(word in comando_lower for word in ["executar", "rodar", "gerar"]):
        # Extrair nome do script
        for word in comando_lower.split():
            if word not in ["executar", "rodar", "gerar", "o", "a", "de", "do", "da"]:
                script = word
                break
        else:
            return {"erro": "Não identifiquei qual script executar"}
        
        r = requests.post(f"{GATEWAY_URL}/executar", json={"script": script})
        return r.json()
    
    # Comandos de memória
    elif any(word in comando_lower for word in ["memória", "historico", "ultimo"]):
        r = requests.get(f"{GATEWAY_URL}/memoria?limit=5")
        return r.json()
    
    # Comandos de conteúdo
    elif any(word in comando_lower for word in ["conteudo", "videos", "imagens"]):
        r = requests.get(f"{GATEWAY_URL}/dashboard/stats")
        return r.json()
    
    # Comando padrão
    else:
        return {
            "comando": comando,
            "resposta": "Comando não reconhecido. Tente: status, agentes, scripts, executar [script], memória, conteudo"
        }

def registrar_acao(comando, resposta):
    """Registra a ação no Gateway"""
    acao = f"OPENHUMAN_VOICE: {comando}"
    requests.post(f"{GATEWAY_URL}/memoria", json={
        "agente": "OPENHUMAN",
        "acao": acao
    })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tronix_openhuman_agent.py \"comando de voz\"")
        sys.exit(1)
    
    comando = " ".join(sys.argv[1:])
    print(f"Processando: {comando}")
    
    resposta = processar_comando(comando)
    print(json.dumps(resposta, indent=2, ensure_ascii=False))
    
    registrar_acao(comando, resposta)
