# -*- coding: utf-8 -*-
"""
TRONIX BLAZE - login via CHROME NORMAL (perfil real do usuario).
USO:
  python tronix_blaze_live.py --login   # 1x: abre Chrome, voce loga no Blaze, fecha
  python tronix_blaze_live.py           # live: reusa sessao, coleta resultados -> blaze_live.json
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

BASE = Path(r'C:\xampp\htdocs\agente')
HOME = Path.home()
PROFILE_USER = HOME / r'AppData\Local\Google\Chrome\User Data\Profile 10'
OUT_JSON = BASE / 'blaze_live.json'
GAME_URL = 'https://blaze.bet.br/pt/games/double'


def extrair_numeros(pg):
    return pg.evaluate("""() => {
        const out=[];
        const visit=(root)=>{
          root.querySelectorAll('*').forEach(el=>{
            const id=String(el.id||'');
            const cls=typeof el.className==='string'?el.className:'';
            const sig=(id+cls).toLowerCase();
            if(!/result|history|chip|bet|roll|numb|double|roulett|spectate|odds|entry-income/i.test(sig)) return;
            const txt=(el.childNodes.length===1&&el.childNodes[0].nodeType===3)?(el.textContent||'').trim():'';
            if(txt && /^(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14)$/.test(txt)) out.push(parseInt(txt));
          });
        };
        visit(document);
        return out;
    }""")


def aceitar_modais(pg, n=10):
    for _ in range(n):
        pg.wait_for_timeout(2000)
        try:
            pg.evaluate("""() => { [...document.querySelectorAll('button')].forEach(b=>{
                const t=(b.textContent||'').trim();
                if(/ACEITAR TODOS/i.test(t)||/mais de 18/i.test(t)||/entendi/i.test(t)) b.click();
            }); }""")
        except Exception:
            break


def chrome_aberto():
    try:
        r = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'],
                           capture_output=True, text=True, timeout=15)
        return 'chrome.exe' in r.stdout.lower()
    except Exception:
        return False


def novo_ctx(p, headed):
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE_USER), channel='chrome', headless=not headed,
        viewport={'width': 1500, 'height': 950},
        args=['--disable-blink-features=AutomationControlled'])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(pg)
    return ctx, pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--login', action='store_true')
    ap.add_argument('--segundos', type=int, default=3600)
    args = ap.parse_args()

    if chrome_aberto():
        print('!!! CHROME ABERTO - feche todas as janelas do Chrome e rode de novo')
        sys.exit(1)
    if not PROFILE_USER.exists():
        print('Perfil nao encontrado:', PROFILE_USER)
        sys.exit(1)

    with sync_playwright() as p:
        if args.login:
            ctx, pg = novo_ctx(p, headed=True)
            pg.goto(GAME_URL, wait_until='domcontentloaded', timeout=60000)
            aceitar_modais(pg)
            pg.wait_for_timeout(4000)
            print('=' * 60)
            print(' LOGIN MANUAL - logue no Blaze na janela que abriu')
            print(' entre com sua conta e deixe o DOUBLE aberto')
            print(' SO FECHE A JANELA QUANDO ESTIVER LOGADO NO JOGO')
            print('=' * 60)
            try:
                while True:
                    vivos = [pp for pp in ctx.pages if not pp.is_closed()]
                    if not vivos:
                        break
                    pg.wait_for_timeout(500)
            except KeyboardInterrupt:
                pass
            ctx.close()
            print('Sessao salva. Agora rode: python tronix_blaze_live.py')
            return

        # LIVE
        ctx, pg = novo_ctx(p, headed=False)
        pg.goto(GAME_URL, wait_until='domcontentloaded', timeout=60000)
        aceitar_modais(pg)
        pg.wait_for_timeout(4000)
        print('URL:', pg.url[:140])

        if 'modal=auth' in pg.url:
            print('!! Sessao nao logada. Rode: python tronix_blaze_live.py --login')

        print('Coletando resultados...')
        numeros = []
        t0 = time.time()
        while time.time() - t0 < args.segundos:
            try:
                nov = extrair_numeros(pg)
                if nov:
                    for n in nov:
                        if n != 0 and (not numeros or n != numeros[-1]):
                            numeros.append(n)
                    numeros = numeros[-300:]
                    OUT_JSON.write_text(
                        json.dumps({'numeros': numeros, 'atualizado': time.time()},
                                   ensure_ascii=False),
                        encoding='utf-8')
                    print(f'  [{len(numeros):>3}] ultimo: {numeros[-1]}')
            except Exception as e:
                print('  err:', str(e)[:80])
            pg.wait_for_timeout(3000)
        ctx.close()
    print('FIM. Resultados em', OUT_JSON)


if __name__ == '__main__':
    main()