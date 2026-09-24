"""
TRONIX QUALITY SHOWCASE
Gera 4 imagens de demonstracao em alta resolucao usando FLUX + Director
para provar a qualidade cinematografica do pipeline.
"""
import sys
import requests
import time
from pathlib import Path
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT = Path("C:/xampp/htdocs/agente/uploads/qualidade")
OUT.mkdir(parents=True, exist_ok=True)

# Diretor define estilo cinematografico de cada demo
DEMOS = [
    {
        "nome": "01_cinematic_farmer",
        "plano": "extreme_wide",
        "movimento": "static_cinematic",
        "prompt": "A elderly bearded farmer kneeling in golden wheat field at sunset, holding a small glowing star in weathered hands, dust particles floating in amber light, Studio Ghibli style, 8K cinematic, soft bokeh, warm sepia palette, photorealistic textures on worn hands, emotional and nostalgic mood, single light source from the star",
        "seed": 42,
    },
    {
        "nome": "02_renaissance_dancer",
        "plano": "close_up",
        "movimento": "slow_pan",
        "prompt": "Extreme close-up of a flamenco dancer's eyes reflecting candle flames, dramatic chiaroscuro lighting, baroque oil painting style, deep shadows on face, golden tears rolling down cheek, Rembrandt lighting, hyperrealistic iris detail, 8K macro photography, shallow depth of field f/1.4, warm amber and crimson palette",
        "seed": 137,
    },
    {
        "nome": "03_magical_forest",
        "plano": "wide",
        "movimento": "dolly_forward",
        "prompt": "Mystical bioluminescent forest at night, ancient oak trees with hanging vines glowing teal and magenta, fireflies dancing between trunks, a small wooden cabin in distance with warm window light, volumetric fog, god rays piercing through canopy, Studio Ghibli meets Blade Runner aesthetic, hyperdetailed 8K, cinematic anamorphic",
        "seed": 271,
    },
    {
        "nome": "04_underwater_ruins",
        "plano": "wide",
        "movimento": "pan",
        "prompt": "Sunken Greek marble temple underwater, sunlight rays piercing turquoise water, columns covered in coral and seaweed, schools of silver fish swirling around, a single golden statue reaching upward, god rays volumetric lighting, 8K photorealistic, James Cameron Avatar aesthetic, anamorphic lens, deep blues and golds",
        "seed": 314,
    },
]

def generate_flux(prompt: str, w: int, h: int, seed: int) -> bytes:
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
    params = {
        "width": w, "height": h, "seed": seed,
        "model": "flux", "nologo": "true",
        "enhance": "true", "private": "true",
    }
    print(f"  [gerando {w}x{h} seed={seed}] ", end="", flush=True)
    start = time.time()
    r = requests.get(url, params=params, timeout=180)
    elapsed = time.time() - start
    print(f"-> {len(r.content)/1024:.0f}KB em {elapsed:.1f}s")
    return r.content

def main():
    print("=" * 60)
    print("TRONIX - QUALITY SHOWCASE (FLUX 1536x1024)")
    print("=" * 60)
    for d in DEMOS:
        print(f"\n[Demo] {d['nome']}")
        print(f"  Plano: {d['plano']} | Movimento: {d['movimento']}")
        data = generate_flux(d['prompt'], 1536, 1024, d['seed'])
        out = OUT / f"{d['nome']}.jpg"
        out.write_bytes(data)
        print(f"  Salvo: {out} ({len(data)/1024:.0f}KB)")
    print("\n" + "=" * 60)
    print(f"OK! 4 imagens em {OUT}")
    print("=" * 60)

if __name__ == "__main__":
    main()
