from pathlib import Path
from typing import Optional
import random


class VideoEngine:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def gerar_video(
        self,
        imagem_pizza: str,
        legenda: str,
        duracao: float = 5.0,
        output_name: Optional[str] = None
    ) -> str:
        try:
            from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
        except ImportError:
            return self._gerar_video_fallback(imagem_pizza, legenda, output_name)

        img_path = Path(imagem_pizza)
        if not img_path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {imagem_pizza}")

        clip_imagem = ImageClip(str(img_path)).set_duration(duracao)

        texto = TextClip(
            legenda,
            fontsize=50,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=clip_imagem.size
        )
        clip_texto = texto.set_duration(duracao).set_position(('center', 'bottom'))

        video = CompositeVideoClip([clip_imagem, clip_texto])

        if output_name is None:
            output_name = f"promo_pizza_{random.randint(1000, 9999)}.mp4"
        
        output_path = self.output_dir / output_name
        video.write_videofile(str(output_path), fps=24, codec='libx264')
        
        return str(output_path)

    def _gerar_video_fallback(self, imagem_pizza: str, legenda: str, output_name: Optional[str]) -> str:
        try:
            import cv2
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
        except ImportError:
            raise ImportError("Instale moviepy ou opencv-python + pillow")

        img = cv2.imread(imagem_pizza)
        if img is None:
            raise FileNotFoundError(f"Imagem não encontrada: {imagem_pizza}")

        height, width = img.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        if output_name is None:
            output_name = f"promo_pizza_{random.randint(1000, 9999)}.mp4"
        
        output_path = self.output_dir / output_name
        out = cv2.VideoWriter(str(output_path), fourcc, 24.0, (width, height))

        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), legenda, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = height - 80

        for _ in range(24 * 5):
            draw.rectangle([text_x - 10, text_y - 10, text_x + text_width + 10, text_y + 50], fill='black')
            draw.text((text_x, text_y), legenda, fill='white', font=font)
            
            frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        return str(output_path)

    def gerar_legenda_automatica(self, tipo_pizza: str) -> str:
        legendas = {
            "marguerita": "🍕 Marguerita - Clássica Italiana!",
            "calabresa": "🔥 Calabresa - Sabor Ardente!",
            "portuguesa": "🇵🇹 Portuguesa - Tradicional!",
            "frango": "🍗 Frango com Catupiry - Creamy!",
            "pepperoni": "🌶️ Pepperoni - Americanna!",
            "vegetariana": "🥗 Vegetariana - Fresh & Healthy!",
            "quatro_queijos": "🧀 Quatro Queijos - Para os lovers!",
            "banana": "🍌 Banana com Canela - Doce Tentação!",
            "chocolate": "🍫 Chocolate - O favorito de todos!",
        }
        
        tipo = tipo_pizza.lower().strip()
        return legendas.get(tipo, f"🍕 Pizza de {tipo_pizza} - Delícia!")


if __name__ == "__main__":
    engine = VideoEngine()
    
    legenda = engine.gerar_legenda_automatica("marguerita")
    print(f"Legenda gerada: {legenda}")
    
    print("Uso: engine.gerar_video('pizza.jpg', 'Sua legenda aqui')")