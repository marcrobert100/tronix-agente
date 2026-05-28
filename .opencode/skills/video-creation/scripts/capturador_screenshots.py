"""
Capturador de Screenshots para Demo de Pizzaria
================================================
Captura automaticamente screenshots de páginas web para criar vídeos de demo.
"""

import asyncio
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Pagina:
    nome: str
    url: str
    wait_selector: Optional[str] = None


class CapturadorScreenshots:
    def __init__(self, pasta_output: str = "./screenshots"):
        self.pasta_output = Path(pasta_output)
        self.pasta_output.mkdir(exist_ok=True)
        self.paginas: list[Pagina] = []

    def adicionar_pagina(self, nome: str, url: str, wait_selector: str = None):
        """Adiciona uma página para capturar."""
        self.paginas.append(Pagina(nome, url, wait_selector))

    def gerar_fluxo_pizzaria(self, url_base: str):
        """Gera sequência padrão de páginas para demo de pizzaria."""
        self.paginas = [
            Pagina("01_login", f"{url_base}/login", "#btn-login"),
            Pagina("02_cardapio", f"{url_base}/cardapio", ".pizza-card"),
            Pagina("03_pizza_detalhes", f"{url_base}/pizza/1", ".pizza-info"),
            Pagina("04_carrinho", f"{url_base}/carrinho", ".cart-items"),
            Pagina("05_checkout", f"{url_base}/checkout", "#form-checkout"),
            Pagina("06_sucesso", f"{url_base}/pedido/sucesso", ".order-confirmed"),
        ]

    async def capturar_com_playwright(self):
        """Captura screenshots usando Playwright."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("❌ Playwright não instalado. Execute: pip install playwright")
            print("   Depois: playwright install chromium")
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})

            for pagina in self.paginas:
                print(f"📸 Capturando: {pagina.nome}")

                await page.goto(pagina.url)

                if pagina.wait_selector:
                    await page.wait_for_selector(pagina.wait_selector)

                await page.screenshot(
                    filename=f"{self.pasta_output / pagina.nome}.png",
                    full_page=True
                )

            await browser.close()
            print(f"✅ Screenshots salvos em: {self.pasta_output}")

    async def capturar_com_selenium(self):
        """Captura screenshots usando Selenium (alternativa)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError:
            print("❌ Selenium não instalado. Execute: pip install selenium")
            return

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)

        for pagina in self.paginas:
            print(f"📸 Capturando: {pagina.nome}")

            driver.get(pagina.url)

            if pagina.wait_selector:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(("css selector", pagina.wait_selector))
                )

            driver.save_screenshot(f"{self.pasta_output / pagina.nome}.png")

        driver.quit()
        print(f"✅ Screenshots salvos em: {self.pasta_output}")

    async def executar(self, usar_selenium: bool = False):
        """Executa a captura de screenshots."""
        if not self.paginas:
            print("⚠️ Nenhuma página adicionada!")
            return

        if usar_selenium:
            await self.capturar_com_selenium()
        else:
            await self.capturar_com_playwright()


async def capturar_demo_pizzaria(url: str, pasta: str = "./screenshots"):
    """Função principal para capturar demo de pizzaria."""
    capturador = CapturadorScreenshots(pasta)
    capturador.gerar_fluxo_pizzaria(url)
    await capturador.executar()


if __name__ == "__main__":
    print("📸 Capturador de Screenshots para Pizzaria")
    print("=" * 40)

    url_base = input("URL base do sistema: ").strip()

    asyncio.run(capturar_demo_pizzaria(url_base))