"""Gera kaggle_ollama.ipynb a partir de celula_unica.py (fonte unica)."""
import json, io, os

AQUI = os.path.dirname(os.path.abspath(__file__))
fonte = os.path.join(AQUI, "celula_unica.py")
codigo = io.open(fonte, encoding="utf-8").read()

_n = [0]

def md(t):
    _n[0] += 1
    return {"cell_type": "markdown", "id": "md%02d" % _n[0], "metadata": {},
            "source": [l + "\n" for l in t.splitlines()]}

def code(t):
    _n[0] += 1
    return {"cell_type": "code", "id": "cd%02d" % _n[0],
            "execution_count": None, "metadata": {},
            "outputs": [], "source": [l + "\n" for l in t.splitlines()]}

cells = [
    md("""# GPU GRATIS (32 GB) PARA RODAR MODELO DE IA + TUNEL PARA O VS CODE

Pipeline: Kaggle GPU T4 x2 -> Ollama -> modelo -> Cloudflare tunnel -> VS Code / Windows.

**Antes de rodar, abra o painel Settings (lado direito do notebook):**
- Internet: **ON**
- Accelerator: **GPU T4 x2** (32 GB VRAM) -> clique *Turn on GPU T4 x2*
- Se aparecer `WARNING: ... TPU` ou nao aparecer `Tesla T4` no passo 1, volte e confira o Accelerator.

Depois: clique em *Add Code* (ou `+`), cole o codigo da celula abaixo e rode (**Shift+Enter**).
So a ultima parte (tunel) precisa ficar **rodando**."""),
    code('''# sonda: prova que a GPU foi alocada e que as celulas rodam
import subprocess
print("TRONIX START", flush=True)
print(subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True).stdout)
'''),
    code(codigo),
    md("""## Depois de rodar

1. Copie a `TUNEL ATIVO: https://xxxx.trycloudflare.com` da saida.
2. Windows -> VS Code -> extensao **Cline** -> engrenagem:
   - API Provider: **OpenAI Compatible**
   - Base URL: `https://xxxx.trycloudflare.com/v1`  (tem que terminar em `/v1`)
   - API Key: `ollama`
   - Model: `qwen3-coder:30b` (o que aparecer em `ollama list`)
3. Teste com: *"Responda em uma frase curta: voce esta conectado?"*

## Desligando (importante)

Ordem certa, senao voce **gasta cota de 30 h/semana** de GPU:
1. Parar a celula do tunel (square) -> a URL publica morre.
2. Botao **Stop Session** / power no Kaggle.
3. So depois fechar o navegador. Fechar aba sozinho **nao** desliga a sessao.

## Aviso de seguranca

A URL `trycloudflare.com` e **publica e sem senha** (a API Key `ollama` e ficticia).
Qualquer um com o link usa sua GPU. Encerre a sessao assim que terminar de testar."""),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "nbformat": 4, "nbformat_minor": 5,
}

destino = os.path.join(AQUI, "kaggle_ollama.ipynb")
io.open(destino, "w", encoding="utf-8").write(
    json.dumps(nb, ensure_ascii=False, indent=1))
print("gerado:", destino)
