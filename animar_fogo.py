import os
from gradio_client import Client, handle_file

# Configuração do servidor externo (Grátis)
# Esse modelo é ótimo para animar fotos de comida
client = Client("fffiloni/Stable-Video-Diffusion-img2vid")

def animar_hotdog(caminho_imagem):
    if not os.path.exists(caminho_imagem):
        print(f"❌ Arquivo não encontrado: {caminho_imagem}")
        return

    print(f"📡 Enviando {caminho_imagem} para os servidores da nuvem...")
    
    try:
        # Aqui a mágica acontece nos servidores deles, não na sua CPU!
        result = client.predict(
            image=handle_file(caminho_imagem),
            seed=42,
            randomize_seed=True,
            motion_bucket_id=127,
            fps=7,
            api_name="/video_generation"
        )
        
        # O resultado é uma lista, o vídeo está na primeira posição
        video_temp = result[0]
        video_final = f"VÍDEO_TRONIX_{os.path.basename(caminho_imagem)}.mp4"
        
        # Move o vídeo para a sua pasta atual
        import shutil
        shutil.move(video_temp, video_final)
        
        print(f"✅ SUCESSO! Vídeo pronto em segundos: {video_final}")
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

# Rodar agora com o seu hot-dog
img = "uploads/imagem_1778515490_A close-up shot of a juicy hot.PNG"
animar_hotdog(img)