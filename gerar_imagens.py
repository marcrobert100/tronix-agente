"""
Gerador de imagens engraçadas usando Cloudflare Workers AI SDXL
Execute: python gerar_imagens.py
"""
import os
import sys

def tentar_cloudflare():
    """Tenta usar Cloudflare Workers AI SDXL"""
    try:
        import requests

        account_id = os.getenv("CF_ACCOUNT_ID")
        api_token = os.getenv("CF_API_TOKEN")

        if not account_id or not api_token:
            return False

        prompts = {
            "extraterrestre.png": "cartoon funny green alien with big oval head, huge round eyes, silly antennas, thin body, confused funny expression, bright colorful style",
            "gorila_humanoide.png": "cartoon funny humanoid gorilla, muscular but friendly, wearing sunglasses, silly grin, arms crossed, comedic pose, bright colorful cartoon style"
        }

        for filename, prompt in prompts.items():
            print(f"Gerando {filename} com Cloudflare SDXL...")
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf-stabilityai/stable-diffusion-xl-base-1.0",
                headers={"Authorization": f"Bearer {api_token}"},
                json={"prompt": prompt},
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("result"):
                    image_data = result["result"]["image"] if isinstance(result["result"], dict) else result["result"]
                    with open(f"C:/xampp/htdocs/agente/{filename}", "wb") as f:
                        f.write(image_data)
                    print(f"  Salvo: {filename}")
                else:
                    print(f"  Erro: {result}")
            else:
                print(f"  Erro HTTP: {response.status_code}")

        return True
    except Exception as e:
        print(f"Cloudflare error: {e}")
        return False

def gerar_com_pillow():
    """Gera imagens placeholder com Pillow"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Extraterrestre
        print("Gerando extraterrestre.png...")
        img = Image.new('RGB', (512, 512), color='#1a3a1a')
        draw = ImageDraw.Draw(img)

        # Cabeca oval verde
        draw.ellipse([106, 56, 406, 356], fill='#44cc44', outline='#228822', width=4)

        # Olhos grandes
        draw.ellipse([136, 136, 246, 246], fill='white', outline='#228822', width=3)
        draw.ellipse([266, 136, 376, 246], fill='white', outline='#228822', width=3)
        draw.ellipse([171, 166, 211, 206], fill='#222222')  # Pupila esquerda
        draw.ellipse([301, 166, 341, 206], fill='#222222')  # Pupila direita

        # Antenas
        draw.line([196, 56, 166, 16], fill='#44cc44', width=6)
        draw.line([316, 56, 346, 16], fill='#44cc44', width=6)
        draw.ellipse([146, 0, 186, 40], fill='#ffcc00')  # Balao esquerda
        draw.ellipse([326, 0, 366, 40], fill='#ffcc00')  # Balao direita

        # Boca confusa
        draw.arc([196, 276, 316, 336], start=0, end=180, fill='#228822', width=4)

        # Corpo magro
        draw.rectangle([216, 356, 296, 476], fill='#44cc44', outline='#228822', width=3)

        # Bracos magros
        draw.line([216, 386, 146, 436], fill='#44cc44', width=12)
        draw.line([296, 386, 366, 436], fill='#44cc44', width=12)

        img.save("C:/xampp/htdocs/agente/extraterrestre.png")
        print("  Salvo: extraterrestre.png")

        # Gorila humanoide
        print("Gerando gorila_humanoide.png...")
        img2 = Image.new('RGB', (512, 512), color='#2a2a3a')
        draw2 = ImageDraw.Draw(img2)

        # Corpo musculos
        draw2.ellipse([106, 156, 406, 456], fill='#4a3a2a', outline='#2a1a0a', width=4)

        # Cabeca
        draw2.ellipse([156, 36, 356, 236], fill='#5a4a3a', outline='#2a1a0a', width=4)

        # Face
        draw2.ellipse([186, 106, 326, 196], fill='#7a6a5a', outline='#4a3a2a', width=2)

        # Oculos escuros
        draw2.ellipse([176, 116, 256, 156], fill='#111111', outline='#333333', width=3)
        draw2.ellipse([256, 116, 336, 156], fill='#111111', outline='#333333', width=3)
        draw2.line([256, 136, 256, 136], fill='#333333', width=6)  # Ponte

        # Boca sorridente
        draw2.arc([206, 156, 306, 206], start=0, end=180, fill='#111111', width=4)

        # Bracos musculos cruzados
        draw2.line([106, 226, 56, 326], fill='#4a3a2a', width=20)
        draw2.line([406, 226, 456, 326], fill='#4a3a2a', width=20)

        # Maas do peitoral
        draw2.ellipse([146, 226, 236, 316], fill='#5a4a3a', outline='#3a2a1a', width=2)
        draw2.ellipse([276, 226, 366, 316], fill='#5a4a3a', outline='#3a2a1a', width=2)

        # Texto engraçado
        draw2.text((256, 476), "Que foi?!", fill='#ffcc00', anchor='mm')

        img2.save("C:/xampp/htdocs/agente/gorila_humanoide.png")
        print("  Salvo: gorila_humanoide.png")

        return True
    except ImportError:
        print("Pillow nao instalado. Instale com: pip install pillow")
        return False
    except Exception as e:
        print(f"Erro Pillow: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Gerador de Imagens Engraçadas")
    print("=" * 50)

    # Tenta Cloudflare primeiro
    if not tentar_cloudflare():
        print("\nCloudflare nao disponivel. Gerando com Pillow...")
        if not gerar_com_pillow():
            print("\nAlternativa: Use este link para gerar:")
            print("  https://www.bing.com/images/create")

    print("\nConcluido!")
