import os
import sys
import shutil
import time
from gradio_client import Client, handle_file

# Configurações de Produção
HF_TOKEN = "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"
SERVER = "multimodalart/stable-video-diffusion"

def processar_animacao(caminho_entrada):
    # 1. Validação de Entrada
    if not os.path.exists(caminho_entrada):
        print(f"ERROR: Arquivo {caminho_entrada} nao encontrado.")
        return

    # 2. Definir nome de saída baseado na entrada
    nome_base = os.path.basename(caminho_entrada).split('.')[0]
    diretorio_saida = "videos_animados"
    
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
    
    caminho_saida = os.path.join(diretorio_saida, f"animado_{nome_base}.mp4")

    print(f"🚀 TRONIX AI: Iniciando animacao de {nome_base}...")
    
    try:
        # 3. Conexão com o Cluster
        client = Client(SERVER, token=HF_TOKEN)
        
        # 4. Execução do Processamento (SVD Turbo)
        result = client.predict(
            image=handle_file(caminho_entrada),
            seed=0,
            randomize_seed=True,
            motion_bucket_id=127, # Movimento fluido
            fps_id=6,
            api_name="/video"
        )
        
        # 5. Tratamento de Resposta
        video_temp = result[0]['video'] if isinstance(result[0], dict) else result[0]
        
        if video_temp and os.path.exists(video_temp):
            shutil.copy(video_temp, caminho_saida)
            print(f"✅ SUCESSO: Video gerado em {caminho_saida}")
            print(f"📊 Tamanho: {os.path.getsize(caminho_saida)} bytes")
        else:
            print("❌ ERRO: Servidor nao retornou um arquivo valido.")

    except Exception as e:
        print(f"❌ FALHA NO MOTOR: {str(e)}")

if __name__ == "__main__":
    # Permite que o PHP passe o caminho da imagem por argumento
    # Exemplo: python animar_turbo.py uploads/foto.png
    if len(sys.argv) > 1:
        img_input = sys.argv[1]
    else:
        # Fallback para o seu teste atual do hambúrguer
        img_input = "uploads/imagem_1778515490_A close-up shot of a juicy hot.PNG"
    
    processar_animacao(img_input)
