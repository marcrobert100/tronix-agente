# -*- coding: utf-8 -*-
"""
TRONIX BLAZE LIVE v2 - coleta resultados Double da Blaze via BestBlaze (publico, sem login).
Fonte: https://www.bestblaze.com.br/doubleRodadasDia  (atualiza ~30s)
Gera agente/blaze_live.json no formato {numeros:[...], cores:[...], atualizado: ts}
Uso: python tronix_bestblaze.py            (loop infinito, 30s polling)
     python tronix_bestblaze.py --once     (uma coleta e sai)
"""
import argparse
import json
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT_JSON = BASE / 'blaze_live.json'
URL = 'https://www.bestblaze.com.br/doubleRodadasDia'

PAT = re.compile(
    r'bb-blaze-tile__box (\w?)rodada\'?"\s*>\s*<span class="num">(\d+)</span>'
    r'.*?bb-blaze-tile__time">([^<]+)<', re.S)

COR_MAP = {'V': 'vermelho', 'P': 'preto', 'B': 'branco'}


def baixar():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='replace')


def extrair(html):
    tmp = PAT.findall(html)
    out = []
    for cor, num, hora in tmp:
        out.append({
            'numero': int(num),
            'cor': COR_MAP.get(cor, cor),
            'hora': hora,
        })
    # pagina vem mais nova primeiro -> inverter p/ cronologico
    out.reverse()
    return out


def coletar_e_salvar(primeira=False):
    html = baixar()
    rodadas = extrair(html)
    numeros = [r['numero'] for r in rodadas]
    cores = [r['cor'] for r in rodadas]
    dados = {
        'numeros': numeros,
        'cores': cores,
        'hora': [r['hora'] for r in rodadas],
        'atualizado': time.time(),
        'fonte': 'bestblaze',
    }
    OUT_JSON.write_text(json.dumps(dados, ensure_ascii=False), encoding='utf-8')
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(numeros)} rodadas | ultima: "
          f"{cores[-1]}/{numeros[-1]} as {rodadas[-1]['hora']}")
    return rodadas


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--segundos', type=int, default=0)
    args = ap.parse_args()
    if args.once:
        coletar_e_salvar()
    else:
        while True:
            try:
                coletar_e_salvar()
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] err: {str(e)[:100]}")
            time.sleep(30)