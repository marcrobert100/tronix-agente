import requests
import json

# Configuração da API Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2:0.5b"

def generate_text(prompt, model=MODEL):
    """Gera texto usando o modelo Ollama via API."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        return f"Erro: {e}"

# Exemplos de uso
if __name__ == "__main__":
    # Exemplo 1: Conversa simples
    print("=== Exemplo 1: Conversa simples ===")
    resposta = generate_text("Olá, como você está?")
    print(f"Resposta: {resposta}\n")

    # Exemplo 2: Tradução
    print("=== Exemplo 2: Tradução ===")
    resposta = generate_text("Traduza para inglês: 'Bom dia, mundo!'")
    print(f"Resposta: {resposta}\n")

    # Exemplo 3: Resumo
    print("=== Exemplo 3: Resumo ===")
    texto = "A inteligência artificial está transformando indústrias ao automatizar tarefas e analisar grandes volumes de dados."
    resposta = generate_text(f"Resuma este texto em uma frase: {texto}")
    print(f"Resposta: {resposta}\n")

    # Exemplo 4: Código
    print("=== Exemplo 4: Geração de código ===")
    resposta = generate_text("Escreva uma função Python que calcula o fatorial de um número.")
    print(f"Resposta: {resposta}\n")