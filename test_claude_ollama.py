import requests
import json

# Configuração para Claude Code com Ollama
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen2:0.5b"

def test_claude_ollama():
    """Testa a integração do Claude Code com Ollama."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Olá, como você está?"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print("=== Teste Claude Code + Ollama ===")
        print(f"Modelo: {result.get('model', 'N/A')}")
        print(f"Resposta: {result['choices'][0]['message']['content']}")
        print(f"Tokens: {result['usage']['total_tokens']}")
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    test_claude_ollama()