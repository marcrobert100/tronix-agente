"""
Tronix Media Gen - Gerador de Imagens via API
Suporta: Leonardo.ai, OpenAI DALL-E
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


class TronixMediaGen:
    """Classe para gerar imagens via APIs externas."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Tronix-MediaGen/1.0",
            "Accept": "application/json"
        })

    # ==================== LEONARDO.AI ====================

    def gerar_leonardo(self, prompt: str, modelo: str = "leanring-v1-5",
                       quantidade: int = 1) -> dict:
        """
        Gera imagem via Leonardo.ai.

        Args:
            prompt: Descricao da imagem
            modelo: Modelo Leonardo (ex: leanring-v1-5, dreamshaper-v7)
            quantidade: Numero de imagens (1-4)

        Returns:
            dict com URLs das geradas
        """
        api_key = os.environ.get("LEONARDO_API_KEY")
        if not api_key:
            raise ValueError("LEONARDO_API_KEY nao definida no .env")

        url = "https://cloud.leonardo.ai/api/rest/v1/generations"

        payload = {
            "prompt": prompt,
            "modelId": modelo,
            "num_images": min(quantidade, 4),
            "width": 1024,
            "height": 1024,
            "promptMagic": True,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"[LEONARDO] Enviando prompt...")
        resp = self.session.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        generation_id = data["generations_by_pk"]["id"]
        print(f"[LEONARDO] Generation ID: {generation_id}")

        # Polling ate ficar pronto
        return self._poll_leonardo(generation_id)

    def _poll_leonardo(self, generation_id: str, max_wait: int = 120) -> dict:
        """Faz polling ate a geracao ficar pronta."""
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        headers = {"Authorization": f"Bearer {os.environ.get('LEONARDO_API_KEY')}"}

        inicio = time.time()
        while time.time() - inicio < max_wait:
            resp = self.session.get(url, headers=headers, timeout=30)
            data = resp.json()
            status = data["generations_by_pk"]["status"]

            print(f"[LEONARDO] Status: {status}")

            if status == "COMPLETE":
                imagens = data["generations_by_pk"]["generated_images"]
                urls = [img["url"] for img in imagens]
                return {"status": "success", "urls": urls, "provider": "leonardo"}

            if status in ("FAILED", "CANCELLED"):
                return {"status": "error", "message": f"Geracao falhou: {status}"}

            time.sleep(5)

        return {"status": "error", "message": "Timeout esperando geracao"}

    def baixar_leonardo(self, url: str, pasta_saida: str = "tronix_output") -> str:
        """Baixa imagem da URL para pasta local."""
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)

        nome = f"tronix_{int(time.time())}.png"
        caminho = os.path.join(pasta_saida, nome)

        resp = self.session.get(url, timeout=60)
        resp.raise_for_status()

        with open(caminho, "wb") as f:
            f.write(resp.content)

        print(f"[DOWNLOAD] Salvo em: {caminho}")
        return caminho

    # ==================== OPENAI DALL-E ====================

    def gerar_dalle(self, prompt: str, tamanho: str = "1024x1024",
                    qualidade: str = "standard") -> dict:
        """
        Gera imagem via OpenAI DALL-E 3.

        Args:
            prompt: Descricao da imagem
            tamanho: 1024x1024, 1792x1024, ou 1024x1792
            quality: standard ou hd

        Returns:
            dict com URL e status
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY nao definida no .env")

        url = "https://api.openai.com/v1/images/generations"

        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": tamanho,
            "quality": quality,
            "response_format": "url"
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"[DALL-E] Enviando prompt...")
        resp = self.session.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        url_img = data["data"][0]["url"]
        revised = data["data"][0].get("revised_prompt", prompt)

        print(f"[DALL-E] Imagem pronta!")
        return {
            "status": "success",
            "url": url_img,
            "revised_prompt": revised,
            "provider": "openai"
        }

    def baixar_dalle(self, url: str, pasta_saida: str = "tronix_output") -> str:
        """Baixa imagem DALL-E para pasta local."""
        Path(pasta_saida).mkdir(parents=True, exist_ok=True)

        nome = f"tronix_dalle_{int(time.time())}.png"
        caminho = os.path.join(pasta_saida, nome)

        resp = self.session.get(url, timeout=60)
        resp.raise_for_status()

        with open(caminho, "wb") as f:
            f.write(resp.content)

        print(f"[DOWNLOAD] Salvo em: {caminho}")
        return caminho

    # ==================== REPLICATE (STABLE DIFFUSION) ====================

    def gerar_stable_diffusion(self, prompt: str, negativo: str = "") -> dict:
        """
        Gera imagem via Replicate + Stable Diffusion XL.

        Args:
            prompt: Descricao positiva
            negativo: Elementos a evitar
        """
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN nao definida no .env")

        import replicate

        model = replicate.models.get("stability-ai/stable-diffusion")
        version = model.versions.get(
            "swarmsg/flux-schnell:88b374a2ba06ea23f40f8f38b5bc5d9e50a67f2ecb37e7683a49d14e08d1c97e"
        )

        print(f"[STABLE DIFFUSION] Gerando...")
        output = version.predict(
            prompt=prompt,
            negative_prompt=negativo,
            width=1024,
            height=1024,
            num_inference_steps=4,
            guidance_scale=0.0
        )

        return {
            "status": "success",
            "url": output[0] if isinstance(output, list) else output,
            "provider": "replicate"
        }

    # ==================== UTILIDADES ====================

    def salvar_json(self, dados: dict, nome: str = "tronix_resultado") -> str:
        """Salva resultado em JSON."""
        Path("tronix_output").mkdir(exist_ok=True)
        caminho = f"tronix_output/{nome}_{int(time.time())}.json"
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return caminho


# ==================== EXEMPLOS DE USO ====================

if __name__ == "__main__":
    gen = TronixMediaGen()

    print("=" * 50)
    print("  TRONIX MEDIA GEN - Gerador de Imagens")
    print("=" * 50)

    # --- Exemplo Leonardo.ai ---
    # resultado = gen.gerar_leonardo(
    #     prompt="futuristic city with neon lights, cyberpunk style, detailed",
    #     modelo="leanring-v1-5"
    # )
    # if resultado["status"] == "success":
    #     for url in resultado["urls"]:
    #         gen.baixar_leonardo(url)

    # --- Exemplo DALL-E 3 ---
    resultado = gen.gerar_dalle(
        prompt="a futuristic robot named Tronix standing in Viçosa, Brazil, sunset",
        tamanho="1024x1024",
        quality="standard"
    )

    if resultado["status"] == "success":
        print(f"URL: {resultado['url']}")
        # gen.baixar_dalle(resultado['url'])

    gen.salvar_json(resultado)
    print("\nPronto!")
