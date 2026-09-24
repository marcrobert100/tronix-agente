# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
from pathlib import Path

PROFILE = Path(r'C:\xampp\htdocs\agente\blaze_profile_stealth')
PROFILE.mkdir(parents=True, exist_ok=True)
USER = '92917380500'
PASS = 'jumentoMrs@300'

rev = """() => {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
}"""

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), headless=False, channel='chrome',
        viewport={'width': 1500, 'height': 950},
        args=['--disable-blink-features=AutomationControlled'])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(pg)

    pg.goto('https://blaze.bet.br/pt/games/double', wait_until='domcontentloaded', timeout=45000)

    for _ in range(10):
        pg.wait_for_timeout(2500)
        try:
            pg.evaluate("""() => { [...document.querySelectorAll('button')].forEach(b=>{
                const t=(b.textContent||'').trim();
                if(/ACEITAR TODOS/i.test(t)||/mais de 18/i.test(t)) b.click();
            }); }""")
        except: pass
    pg.wait_for_timeout(3000)

    # abrir login modal
    try:
        pg.evaluate("""() => {
            [...document.querySelectorAll('button,a,span')].find(e=>{
                const t=(e.textContent||'').trim();
                return /^Ent(e|r)ar$|^Entre$/i.test(t);
            })?.click();
        }""")
    except: pass
    pg.wait_for_timeout(4000)

    try:
        pg.fill('#text-input-1', USER, timeout=10000)
        pg.fill('#text-input-2', PASS, timeout=10000)
        print('credenciais OK')
    except Exception as e:
        print('fill err', str(e)[:100])

    pg.wait_for_timeout(3000)

    # Turnstile: se campo ativo/parece checkbox, clicar; esperar resolver
    for i in range(20):
        pg.wait_for_timeout(2000)
        st = pg.evaluate("""() => {
            const modal = document.querySelector('[class*=modal]');
            const btn = modal ? [...modal.querySelectorAll('button')].find(b=>/^Entrar$/.test((b.textContent||'').trim())) : null;
            const ts = document.querySelector('.turnstile-container iframe, .cf-turnstile iframe, [class*=cf-chl]');
            return {
                disabled: btn ? btn.disabled : 'n/a',
                tsFrame: ts ? {src:(ts.src||'').slice(0,80), w:ts.width, h:ts.height} : null,
                val: (document.querySelector('input[name=cf-turnstile-response]')||{}).value || null
            };
        }""")
        if st.get('disabled') is False:
            print(f'turnstile OK after {i*2}s, botao ativo!')
            break
        if i % 3 == 0:
            print(f'  [{(i+1)*2}s] disabled={st["disabled"]} ts={st["tsFrame"]} val={st["val"] is not None}')
    ctx.close()