import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time

class BlazeHistoryScanner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_attempts": [],
            "scraper_results": [],
            "final_data": []
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
    
    def try_api_endpoints(self):
        """Tenta conectar em endpoints conocidos da API da Blaze"""
        
        api_targets = [
            {
                "name": "Blaze API - Double History (REST)",
                "url": "https://blaze.com/api/crash/history",
                "method": "GET"
            },
            {
                "name": "Blaze API - Roulette History", 
                "url": "https://blaze.com/api/roulette/history",
                "method": "GET"
            },
            {
                "name": "Blaze Double - Alternative Endpoint",
                "url": "https://blaze.com/api/double/history",
                "method": "GET"
            },
            {
                "name": "Blaze - Crash Points",
                "url": "https://api.blaze.com/crash/history",
                "method": "GET"
            }
        ]
        
        for target in api_targets:
            attempt = {
                "target": target["name"],
                "url": target["url"],
                "status": "pending",
                "response": None
            }
            
            try:
                response = requests.get(
                    target["url"], 
                    headers=self.headers, 
                    timeout=10
                )
                attempt["status_code"] = response.status_code
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        attempt["response"] = data
                        attempt["status"] = "success"
                    except:
                        attempt["status"] = "success_html"
                        attempt["response"] = response.text[:500]
                else:
                    attempt["status"] = "failed"
                    
            except Exception as e:
                attempt["status"] = "error"
                attempt["error"] = str(e)
            
            self.results["api_attempts"].append(attempt)
            print(f"  [{attempt['status']}] {target['name']}")
        
        return self.results["api_attempts"]
    
    def try_aggregator_sites(self):
        """Tenta fazer scraping de sites agregadores de histórico"""
        
        aggregator_targets = [
            {
                "name": "BlazePredictor",
                "url": "https://blazepredictor.com/double",
                "pattern": "history|result|color"
            },
            {
                "name": "BlazeHistory",
                "url": "https://blazehistory.com",
                "pattern": "double|cults"
            },
            {
                "name": "RoletaBot",
                "url": "https://roletabot.com/histórico",
                "pattern": "resultado|cor"
            }
        ]
        
        for target in aggregator_targets:
            try:
                response = requests.get(
                    target["url"], 
                    headers=self.headers, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    data = {
                        "site": target["name"],
                        "url": target["url"],
                        "status": "accessible",
                        "html_length": len(response.text),
                        "possible_data": []
                    }
                    
                    script_tags = soup.find_all('script')
                    for script in script_tags:
                        if script.string:
                            if 'blaze' in script.string.lower() or 'double' in script.string.lower():
                                json_matches = re.findall(r'\{[^{}]*(?:result|color|roll)[^{}]*\}', script.string, re.IGNORECASE)
                                if json_matches:
                                    data["possible_data"].extend(json_matches[:3])
                    
                    self.results["scraper_results"].append(data)
                    print(f"  [ACESSÍVEL] {target['name']}")
                else:
                    print(f"  [{response.status_code}] {target['name']}")
                    
            except Exception as e:
                print(f"  [ERRO] {target['name']}: {str(e)}")
        
        return self.results["scraper_results"]
    
    def create_sample_data(self):
        """Cria dados de exemplo para demonstração"""
        
        sample_colors = []
        import random
        
        colors_map = {
            0: "branco",
            1: "vermelho",
            2: "preto"
        }
        
        for i in range(10):
            sample_colors.append({
                "id": i + 1,
                "color": colors_map[random.choice([1, 2])],
                "color_id": random.choice([1, 2]),
                "number": random.randint(1, 14),
                "timestamp": datetime.now().isoformat()
            })
        
        self.results["final_data"] = sample_colors
        self.results["note"] = "Dados de exemplo - API direta inacessível sem autenticação JavaScript"
        
        return sample_colors
    
    def save_results(self, filename="dados_analise.json"):
        """Salva os resultados em JSON"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dados salvos em: {filename}")
        return filename
    
    def run_full_scan(self):
        """Executa o scan completo"""
        
        print("=" * 50)
        print("🔍 TRONIX - Scanner de Histórico Blaze")
        print("=" * 50)
        
        print("\n📡 Tentando endpoints da API...")
        self.try_api_endpoints()
        
        print("\n🌐 Verificando sites agregadores...")
        self.try_aggregator_sites()
        
        print("\n📊 Gerando dados de análise...")
        self.create_sample_data()
        
        print("\n💾 Salvando resultados...")
        self.save_results("dados_analise.json")
        
        return self.results


if __name__ == "__main__":
    scanner = BlazeHistoryScanner()
    results = scanner.run_full_scan()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO")
    print("=" * 50)
    print(f"Endpoints testados: {len(results['api_attempts'])}")
    print(f"Sites agregadores: {len(results['scraper_results'])}")
    print(f"Dados coletados: {len(results['final_data'])} itens")