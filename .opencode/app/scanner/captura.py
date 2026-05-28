import requests
import json
import time

def buscar_historico():
    # URL de exemplo de um agregador/API que fornece o histórico da Blaze
    # Nota: APIs diretas da Blaze costumam mudar, por isso usamos endpoints de histórico
    url = "https://blaze.com/api/roulette_games/recent" 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"🔄 [{time.strftime('%H:%M:%S')}] Tronix: Consultando rodadas...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            # Pega as últimas 5 cores (0: Branco, 1: Vermelho, 2: Preto)
            resultados = [{"cor": r['color'], "valor": r['roll']} for r in dados[:10]]
            
            print("✅ Dados capturados com sucesso!")
            for i, res in enumerate(resultados):
                cor_nome = "Branco ⚪" if res['cor'] == 0 else ("Vermelho 🔴" if res['cor'] == 1 else "Preto ⚫")
                print(f"   {i+1}º: {cor_nome} (Número: {res['valor']})")
                
            return resultados
        else:
            print(f"⚠️ Erro de conexão: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro crítico no Scanner: {e}")
        return None

if __name__ == "__main__":
    while True:
        buscar_historico()
        print("\n⏳ Aguardando próxima rodada (30s)...")
        time.sleep(30)
