"""
Tronix Video Gen - Gerador de Videos via API
Suporta: Runway ML, Luma AI (Dream Machine), Replicate Video
Autor: Marcos Roberto / Tronix
"""

import requests
import os
import time
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class TronixVideoGen:
    """Classe para gerar videos via APIs externas."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Tronix-VideoGen/1.0",
            "Accept": "application/json"
        })

    # ==================== RUNWAY ML ====================

    def gerar_runway(self, prompt: str, duracao: int = 5,
                     modelo: str = "gen3a_turbo") -> dict:
        """
        Gera video via Runway ML API.

        Args:
            prompt: Descricao da cena
            duracao: Duracao em segundos (4 ou 10)
            modelo: Modelo (gen3a_turbo, etc)

        Returns:
            dict com URL do video
        """
        api_key = os.environ.get("RUNWAY_API_KEY")
        if not api_key:
            raise ValueError("RUNWAY_API_KEY nao definida no .env")

        # Criar tarefa de geracao
        url = "https://api.runwayml.com/v1/inference"

        payload = {
            "prompt": prompt,
            "model": modelo,
            "duration": duracao,
            "fps": 24
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"[RUNWAY] Enviando prompt...")
        resp = self.session.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        task_id = data.get("id")
        print(f"[RUNWAY] Task ID: {task_id}")

        return self._poll_runway(task_id)

    def _poll_runway(self, task_id: str, max_wait: int = 300) -> dict:
        """Faz polling ate o video ficar pronto."""
        url = f"https://api.runwayml.com/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {os.environ.get('RUNWAY_API_KEY')}"}

        inicio = time.time()
        while time.time() - inicio < max_wait:
            resp = self.session.get(url, headers=headers, timeout=30)
            data = resp.json()
            status = data.get("status")

            print(f"[RUNWAY] Status: {status}")

            if status == "completed":
                video_url = data.get("output", {}).get("video_url")
                return {"status": "success", "url": video_url, "provider": "runway"}

            if status == "failed":
                return {"status": "error", "message": "Video falhou"}

            time.sleep(10)

        return {"status": "error", "message": "Timeout esperando video"}

    # ==================== LUMA AI (Dream Machine) ====================

    def gerar_luma(self, prompt: str, duracao: int = 5) -> dict:
        """
        Gera video via Luma AI Dream Machine API.

        Args:
            prompt: Descricao da cena em ingles
            duracao: Duracao (3 ou 9 segundos)

        Returns:
            dict com URL do video
        """
        api_key = os.environ.get("LUMAAI_API_KEY")
        if not api_key:
            raise ValueError("LUMAAI_API_KEY nao definida no .env")

        url = "https://api.lumalabs.ai/dream-machine/v1/generations"

        payload = {
            "prompt": prompt,
            "duration": duracao
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"[LUMA AI] Enviando prompt...")
        resp = self.session.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        generation_id = data.get("id")
        print(f"[LUMA AI] Generation ID: {generation_id}")

        return self._poll_luma(generation_id)

    def _poll_luma(self, generation_id: str, max_wait: int = 300) -> dict:
        """Faz polling ate o video ficar pronto."""
        url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}"
        headers = {"Authorization": f"Bearer {os.environ.get('LUMAAI_API_KEY')}"}

        inicio = time.time()
        while time.time() - inicio < max_wait:
            resp = self.session.get(url, headers=headers, timeout=30)
            data = resp.json()
            status = data.get("state")

            print(f"[LUMA AI] Status: {status}")

            if status == "completed":
                videos = data.get("assets", {}).get("video", {})
                video_url = videos.get("url") if isinstance(videos, dict) else videos
                return {"status": "success", "url": video_url, "provider": "luma"}

            if status == "failed":
                return {"status": "error", "message": "Video falhou"}

            time.sleep(10)

        return {"status": "error", "message": "Timeout esperando video"}

    # ==================== REPLICATE (SVD / I2V) ====================

    def gerar_svd(self, imagem_url: str = None, prompt: str = "",
                  duracao: int = 25) -> dict:
        """
        Gera video via Replicate (Stable Video Diffusion).

        Args:
            imagem_url: URL de uma imagem (opcional)
            prompt: Texto descritivo
            duracao: Numero de frames (25 = 1 segundo)

        Returns:
            dict com URL do video
        """
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN nao definida no .env")

        import replicate

        if imagem_url:
            # Image-to-Video (I2V-Gen-XL)
            model = replicate.models.get("czr81/i2v-gen-xl")
            version = model.versions.get(
                "83d1tt5tcg2iqdc5kv7etg47t3nh32zqau3pclf4qjq1p2x7m4m"
            )
            output = version.predict(
                prompt=prompt,
                image=imagem_url,
                num_frames=min(duracao, 30)
            )
        else:
            # Text-to-Video (SVD)
            model = replicate.models.get("stability-ai/stable-video-diffusion")
            version = model.versions.get(
                "3f086bcd2fe8a4c2f6a6ea15f2ab8ed4da4b4f9e5e4a6c2f8b4d6e0c8a2b4d6"
            )
            output = version.predict(
                prompt=prompt,
                num_frames=duracao
            )

        return {
            "status": "success",
            "url": output[0] if isinstance(output, list) else output,
            "provider": "replicate"
        }

    # ==================== UTILIDADES ====================

    def baixar_video(self, url: str, pasta_saida: str = "tronix_output") -> str:
        """Baixa video da URL para pasta local."""
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)

        nome = f"tronix_video_{int(time.time())}.mp4"
        caminho = os.path.join(pasta_saida, nome)

        resp = self.session.get(url, timeout=300, stream=True)
        resp.raise_for_status()

        with open(caminho, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[DOWNLOAD] Salvo em: {caminho}")
        return caminho

    def salvar_json(self, dados: dict, nome: str = "tronix_video_resultado") -> str:
        """Salva resultado em JSON."""
        Path("tronix_output").mkdir(exist_ok=True)
        caminho = f"tronix_output/{nome}_{int(time.time())}.json"
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return caminho


# ==================== EXEMPLOS DE USO ====================

if __name__ == "__main__":
    video = TronixVideoGen()

    print("=" * 50)
    print("  TRONIX VIDEO GEN - Gerador de Videos")
    print("=" * 50)

    # --- Exemplo Luma AI (recomendado) ---
    resultado = video.gerar_luma(
        prompt="a drone flying over a futuristic city with neon lights at sunset",
        duracao=5
    )

    if resultado["status"] == "success":
        print(f"Video URL: {resultado['url']}")
        # video.baixar_video(resultado['url'])

    # --- Exemplo Runway ---
    # resultado = video.gerar_runway(
    #     prompt="a robot walking in the rain",
    #     duracao=5
    # )

    video.salvar_json(resultado)
    print("\nPronto!")
