from services.video_engine import VideoEngine
import os


def main():
    engine = VideoEngine(output_dir="output")
    
    script = """INTELIGÊNCIA ARTIFICIAL
O futuro está aqui.

IA transforma tudo:
Medicina, Educação, Arte, Ciência.

Máquinas que pensam.
Sistemas que aprendem.
Mundos que se reinventam.

Você está pronto para o amanhã?
A IA já está mudando tudo.

O limite é a sua imaginação."""

    print("[VIDEO] Criando video sobre Inteligencia Artificial...")
    print(f"Script: {script[:100]}...")
    
    img_path = "fotos/ia_placeholder.jpg"
    
    if not os.path.exists("fotos"):
        os.makedirs("fotos")
        print("Criando diretório fotos...")
    
    if not os.path.exists(img_path):
        print("[INFO] Criando imagem placeholder...")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1280, 720), color=(20, 20, 40))
            draw = ImageDraw.Draw(img)
            draw.text((540, 340), "IA", fill=(100, 200, 255))
            img.save(img_path)
            print("[OK] Imagem criada")
        except ImportError:
            print("[ERRO] PIL nao disponivel")
    
    duracao = 20.0
    
    try:
        video = engine.gerar_video(
            imagem_pizza=img_path,
            legenda=script.replace('\n', ' | '),
            duracao=duracao,
            output_name="video_ia_incrivel.mp4"
        )
        print(f"[OK] Video criado: {video}")
    except Exception as e:
        print("[ERRO] Erro: {e}")
        print("Tentando método alternativo...")
        
        try:
            import cv2
            import numpy as np
            
            width, height = 1280, 720
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter('output/video_ia.mp4', fourcc, 24.0, (width, height))
            
            for _ in range(24 * int(duracao)):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (20, 20, 40)
                
                cv2.putText(frame, "INTELIGENCIA ARTIFICIAL", (280, 340), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 200, 255), 3)
                
                out.write(frame)
            
            out.release()
            print("[OK] Video basico criado: output/video_ia.mp4")
        except Exception as e2:
            print("[ERRO] Erro no fallback: {e2}")


if __name__ == "__main__":
    main()