import os
import sys
import shutil
import time as _time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from gradio_client import Client, handle_file

HF_TOKEN = "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"
SERVER = "multimodalart/stable-video-diffusion"

def gerar_video_tronix(caminho_img):
    saida_dir = "videos_saida"
    if not os.path.exists(saida_dir):
        os.makedirs(saida_dir)

    if not os.path.exists(caminho_img):
        print(f"ERRO: Imagem nao encontrada em: {caminho_img}")
        return

    try:
        print(f"Conectando ao servidor para animar: {caminho_img}")
        client = Client(SERVER, token=HF_TOKEN)
        
        result = client.predict(
            image=handle_file(caminho_img),
            seed=0,
            randomize_seed=True,
            motion_bucket_id=127,
            fps_id=6,
            api_name="/video"
        )
        
        video_temp = result[0]['video'] if isinstance(result[0], dict) else result[0]
        
        nome_final = f"tronix_{int(_time.time())}.mp4"
        caminho_final = os.path.join(saida_dir, nome_final)
        
        shutil.copy(video_temp, caminho_final)
        
        if os.path.exists(caminho_final):
            print(f"SUCESSO|{caminho_final}")
        else:
            print(f"ERRO: Falha ao copiar arquivo final.")

    except Exception as e:
        print(f"ERRO_MOTOR: {str(e)}")

if __name__ == "__main__":
    img = "uploads/imagem_1778515490_A close-up shot of a juicy hot.PNG"
    if len(sys.argv) > 1:
        img = sys.argv[1]
    gerar_video_tronix(img)
