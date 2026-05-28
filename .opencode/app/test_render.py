import sys
import os
sys.path.append(os.getcwd())
from services.video_engine import VideoEngine

def main():
    print("🎬 TRONIX: Iniciando Renderização Real...")
    engine = VideoEngine()
    
    # Usando a imagem que você acabou de criar com o comando anterior
    input_img = "pizza.jpg"
    legenda = "🔥 Calabresa - Sabor Ardente!"
    
    if not os.path.exists(input_img):
        print("❌ Ops, a pizza.jpg sumiu!")
        return

    try:
        print("⏳ Processando frames (isso pode levar alguns segundos)...")
        video_path = engine.gerar_video(input_img, legenda)
        print(f"\n✅ SUCESSO TOTAL!")
        print(f"📂 Vídeo salvo em: {video_path}")
        print("🚀 O Tronix está oficialmente vivo!")
    except Exception as e:
        print(f"❌ Erro na renderização: {e}")

if __name__ == "__main__":
    main()
