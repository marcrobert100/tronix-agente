from services.video_engine import VideoEngine
import os


def main():
    # Inicializa o motor de vídeo
    engine = VideoEngine(output_dir="output")
    
    # Caminho da sua imagem de pizza
    imagem = "fotos/marguerita.jpg"  # <-- Mude para sua imagem
    
    # Gera legenda automática baseada no tipo
    tipo_pizza = "marguerita"  # <-- Mude para o tipo da pizza
    legenda = engine.gerar_legenda_automatica(tipo_pizza)
    
    print(f"Imagem: {imagem}")
    print(f"Legenda: {legenda}")
    print("Gerando vídeo...")
    
    # Gera o vídeo de 5 segundos
    video = engine.gerar_video(
        imagem_pizza=imagem,
        legenda=legenda,
        duracao=5.0
    )
    
    print(f"✅ Vídeo criado: {video}")


if __name__ == "__main__":
    main()