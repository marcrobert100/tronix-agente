"""
Tronix Memory - Integração agentmemory + fastCRW
Memória semântica persistente + Web scraping para agentes
"""

import json
import requests
from datetime import datetime
from pathlib import Path

AGENTMEMORY_URL = "http://localhost:3111"
FASTCRW_API_URL = "https://api.fastcrw.com"


class TronixMemory:
    """Camada de memória semântica para o Tronix"""
    
    def __init__(self, scope="tronix"):
        self.scope = scope
        self.base_url = AGENTMEMORY_URL
    
    def save(self, content, metadata=None):
        """Salvar uma memória"""
        try:
            response = requests.post(
                f"{self.base_url}/agentmemory/memory/save",
                json={
                    "content": content,
                    "scope": self.scope,
                    "metadata": metadata or {}
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, query, limit=5):
        """Buscar memórias por similaridade semântica"""
        try:
            response = requests.post(
                f"{self.base_url}/agentmemory/memory/search",
                json={
                    "query": query,
                    "scope": self.scope,
                    "limit": limit
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_context(self, query, token_budget=2000):
        """Obter contexto relevante para uma query"""
        try:
            response = requests.post(
                f"{self.base_url}/agentmemory/memory/context",
                json={
                    "query": query,
                    "scope": self.scope,
                    "token_budget": token_budget
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def sessions(self):
        """Listar sessões de memória"""
        try:
            response = requests.get(
                f"{self.base_url}/agentmemory/sessions",
                params={"scope": self.scope},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class TronixWebScraper:
    """Web scraping para o Tronix usando fastCRW"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.api_url = FASTCRW_API_URL
    
    def scrape(self, url, formats=None):
        """Scraping de uma URL"""
        try:
            from crw import CrwClient
            client = CrwClient()
            return client.scrape(url, formats=formats or ["markdown"])
        except Exception as e:
            return {"error": str(e)}
    
    def search(self, query, limit=10):
        """Busca web"""
        try:
            from crw import CrwClient
            client = CrwClient()
            return client.search(query, limit=limit)
        except Exception as e:
            return {"error": str(e)}
    
    def crawl(self, url, max_pages=10):
        """Crawl de um site"""
        try:
            from crw import CrwClient
            client = CrwClient()
            return client.crawl(url, max_pages=max_pages)
        except Exception as e:
            return {"error": str(e)}
    
    def map_site(self, url):
        """Mapear URLs de um site"""
        try:
            from crw import CrwClient
            client = CrwClient()
            return client.map(url)
        except Exception as e:
            return {"error": str(e)}


def criar_tronix_memory():
    """Criar instância de memória Tronix"""
    return TronixMemory()


def criar_tronix_scraper():
    """Criar instância de scraper Tronix"""
    return TronixWebScraper()


if __name__ == "__main__":
    print("=== Tronix Memory + Web Scraper ===")
    print(f"AgentMemory URL: {AGENTMEMORY_URL}")
    print(f"FastCRW API: {FASTCRW_API_URL}")
    
    # Testar memória
    memory = criar_tronix_memory()
    print("\n[1] Testando memória...")
    result = memory.save("Tronix é um agente AI para automação de mídia", {"tipo": "teste"})
    print(f"Save: {result}")
    
    # Testar busca
    result = memory.search("agente AI")
    print(f"Search: {result}")
    
    # Testar scraper
    scraper = criar_tronix_scraper()
    print("\n[2] Testando web scraper...")
    result = scraper.scrape("https://example.com")
    print(f"Scrape: {result.get('markdown', result)[:200]}...")
    
    print("\n[OK] Tronix Memory + Scraper instalados!")
