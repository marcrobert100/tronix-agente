#!/usr/bin/env python3
"""
Roteirista - Agente que gera prompts de imagem e textos para videos.
Uso: python roteirista.py "tema do video"
"""

import requests
import os
import sys
import json
from pathlib import Path

# Credenciais Cloudflare
TOKEN = os.getenv("CF_API_TOKEN") or "cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64"
ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID") or "038280d984d9c936772700b7dbbc479e"

# Modelo Llama para texto
MODEL_LLAMA = "@cf/meta/llama-3-8b-instruct"


class Roteirista:
    """Agente roteirista que cria prompts e legendas para videos."""

    def __init__(self, token=None, account_id=None):
        self.token = token or TOKEN
        self.account_id = account_id or ACCOUNT_ID
        self.url_base = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai"

    def gerar_roteiro(self, tema, estilo="marketing"):
        """Gera um roteiro completo para o tema informado."""

        instrucao_idioma = "Você é um roteirista brasileiro especializado em vendas. Escreva legendas impactantes em português do Brasil."

        prompt_sistema = instrucao_idioma + """

Gere um roteiro detalhado com:
1. Um prompt de IMAGEM em INGLÊS (descritivo, otimizado para IA de imagem)
2. Uma LEGENDA curta em PORTUGUÊS (até 100 caracteres, impactante)
3. Uma HASHTAG relevante

Responda APENAS em JSON com este formato:
{{
    "prompt_imagem": "descrição em inglês",
    "legenda": "texto em português",
    "hashtag": "#hashtag"
}}"""

        payload = {
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Crie um roteiro para video sobre: {tema}"}
            ],
            "max_tokens": 500,
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        print(f"Consultando IA para tema: {tema}...")
        response = requests.post(
            f"{self.url_base}/run/{MODEL_LLAMA}",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print(f"ERRO: Status {response.status_code}")
            print(response.text)
            return None

        # Extrai a resposta do modelo
        data = response.json()
        conteudo = data.get("result", {}).get("response", "")

        # Tenta fazer parse do JSON na resposta
        try:
            # Limpa markdown se houver
            texto = conteudo.strip()
            if texto.startswith("```"):
                linhas = texto.split("\n")
                texto = "\n".join(linhas[1:-1] if linhas[-1] == "```" else linhas[1:])
            if texto.startswith("Here is"):
                # Remove texto explicativo antes do JSON
                inicio_json = texto.find("{")
                if inicio_json != -1:
                    texto = texto[inicio_json:]
                fim_json = texto.rfind("}") + 1
                if fim_json > 0:
                    texto = texto[:fim_json]

            roteiro = json.loads(texto)
            return roteiro
        except json.JSONDecodeError:
            print("AVISO: Resposta nao e JSON valido, tentando extrair campos...")
            # Fallback: extrai campos individuais
            resultado = {"prompt_imagem": tema, "legenda": "", "hashtag": "#gerado"}

            # Extrai prompt_imagem
            for marcador in ['"prompt_imagem":', "'prompt_imagem':"]:
                inicio = conteudo.find(marcador)
                if inicio != -1:
                    fim = conteudo.find('",', inicio)
                    if fim == -1:
                        fim = conteudo.find("',", inicio)
                    if fim == -1:
                        fim = conteudo.find('"', inicio + len(marcador))
                        if fim != -1:
                            fim2 = conteudo.find('"', fim + 1)
                            if fim2 != -1:
                                resultado["prompt_imagem"] = conteudo[fim+1:fim2]
                                break
                    else:
                        resultado["prompt_imagem"] = conteudo[inicio+len(marcador):fim].strip('" \n')
                        break

            # Extrai legenda
            for marcador in ['"legenda":', "'legenda':"]:
                inicio = conteudo.find(marcador)
                if inicio != -1:
                    fim = conteudo.find('",', inicio)
                    if fim == -1:
                        fim = conteudo.find("',", inicio)
                    if fim == -1:
                        fim = conteudo.find('"', inicio + len(marcador))
                        if fim != -1:
                            fim2 = conteudo.find('"', fim + 1)
                            if fim2 != -1:
                                resultado["legenda"] = conteudo[fim+1:fim2]
                                break
                    else:
                        resultado["legenda"] = conteudo[inicio+len(marcador):fim].strip('" \n')
                        break

            return resultado

    def gerar_varios(self, temas):
        """Gera roteiros para varios temas ao mesmo tempo."""
        roteiros = []
        for tema in temas:
            print(f"\n{'='*50}")
            roteiros.append(self.gerar_roteiro(tema))
        return roteiros


def main():
    if len(sys.argv) < 2:
        print("Uso: python roteirista.py \"tema do video\"")
        print("Ou passe multiplos temas:")
        print("python roteirista.py \"tema1\" \"tema2\" \"tema3\"")
        sys.exit(1)

    temas = sys.argv[1:]

    roteirista = Roteirista()

    if len(temas) == 1:
        # Single tema
        resultado = roteirista.gerar_roteiro(temas[0])
        if resultado:
            print("\n" + "="*50)
            print("ROTEIRO CRIADO:")
            print("="*50)
            print(f"Prompt da imagem:\n{resultado.get('prompt_imagem', 'N/D')}")
            print(f"\nLegenda:\n{resultado.get('legenda', 'N/D')}")
            print(f"\nHashtag:\n{resultado.get('hashtag', 'N/D')}")

            # Salva em arquivo
            arquivo = Path("uploads/roteiro.json")
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            print(f"\nRoteiro salvo em: {arquivo}")
    else:
        # Multiplos temas
        roteiros = []
        for tema in temas:
            resultado = roteirista.gerar_roteiro(tema)
            if resultado:
                roteiros.append({"tema": tema, **resultado})

        # Salva todos
        arquivo = Path("uploads/roteiros_batch.json")
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(roteiros, f, ensure_ascii=False, indent=2)

        print(f"\n{len(roteiros)} roteiros criados e salvos em: {arquivo}")


if __name__ == "__main__":
    main()
