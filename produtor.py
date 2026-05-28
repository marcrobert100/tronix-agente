import sys
import os
import json
import subprocess
import time
from pathlib import Path

# --- CONFIGURAÇÕES ---
TOKEN = "cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64"
ACCOUNT_ID = "038280d984d9c936772700b7dbbc479e"
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

from roteirista import Roteirista

class ProdutorPro:
    def __init__(self):
        self.roteirista = Roteirista(token=TOKEN, account_id=ACCOUNT_ID)

    def executar(self, tema):
        print(f"\n🎬 INICIANDO PRODUÇÃO TRONIX: {tema}")

        # 1. ROTEIRO
        roteiro = self.roteirista.gerar_roteiro(tema)
        prompt_ia = roteiro.get("prompt_imagem", tema)

        # 2. GERAR IMAGEM
        print("\n[1/4] Gerando imagem base...")
        cmd_img = f'set CF_API_TOKEN={TOKEN} && set CF_ACCOUNT_ID={ACCOUNT_ID} && python gera_imagem.py "{prompt_ia}"'
        subprocess.run(cmd_img, shell=True)

        # Localiza a imagem gerada
        imagens = sorted(UPLOADS_DIR.glob("imagem_*.png"))
        if not imagens: return print("Erro: Imagem não gerada.")
        imagem_path = imagens[-1]

        # 3. ANIMAR FUMAÇA (A PONTE)
        print(f"\n[2/4] 💨 Enviando {imagem_path.name} para o motor de fumaça...")
        cmd_anim = f'python animar_fogo.py "{imagem_path}"'
        subprocess.run(cmd_anim, shell=True)

        # Como você usa CPU, precisamos esperar o ComfyUI terminar antes de montar o vídeo
        print("\n[3/4] ⏳ Aguardando renderização na CPU... (Isso pode levar alguns minutos)")
        # Nota: No modo profissional, usaríamos um loop para checar se o arquivo apareceu na pasta output do ComfyUI
        time.sleep(10) 

        # 4. MONTAR VÍDEO FINAL
        print("\n[4/4] Montando clips e editando...")
        cmd_video = f'python gera_video.py --pasta uploads --texto "{roteiro.get("legenda", "")}"'
        subprocess.run(cmd_video, shell=True)

        print("\n✅ PRODUÇÃO CONCLUÍDA! Verifique a pasta uploads.")

if __name__ == "__main__":
    tema = sys.argv[1] if len(sys.argv) > 1 else "Hamburguer com fumaça"
    ProdutorPro().executar(tema)