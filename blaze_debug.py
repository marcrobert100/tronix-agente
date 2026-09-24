# -*- coding: utf-8 -*-
"""debug DOM Blaze logada - headed, salva html e procura numeros"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

BASE = Path(r'C:\xampp\htdocs\agente')
HOME = Path.home()
PROFILE_USER = HOME / r'AppData\Local\Google\Chrome\User Data\Profile 10'
GAME_URL = 'https://blaze.bet.br/pt/games/double'

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE_USER), channel='chrome', headless=False,
        viewport={'width': 1500, 'height': 950},
        args=['--disable-blink-features=AutomationControlled'])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    Stealth().apply_stealth_sync(pg)
    pg.goto(GAME_URL, wait_until='domcontentloaded', timeout=60000)
    for _ in range(15):
        pg.wait_for_timeout(2000)
        try:
            pg.evaluate("""() => { [...document.querySelectorAll('button')].forEach(b=>{
                const t=(b.textContent||'').trim();
                if(/ACEITAR TODOS/i.test(t)||/mais de 18/i.test(t)||/entendi/i.test(t)) b.click();
            }); }""")
        except Exception:
            break
    pg.wait_for_timeout(5000)
    print('URL:', pg.url[:150])
    (BASE/'debug_blaze.html').write_text(pg.content()[:300000], encoding='utf-8')
    # lista de textos de botoes + numeros
    info = pg.evaluate("""() => {
        const btns=[...document.querySelectorAll('button')].map(b=>(b.textContent||'').trim()).filter(t=>t.length<40).slice(0,40);
        const nums=[]; document.querySelectorAll('*').forEach(el=>{
            const id=String(el.id||''); const cls=typeof el.className==='string'?el.className:'';
            const sig=(id+cls).toLowerCase();
            if(!/result|history|chip|bet|roll|numb|double/i.test(sig)) return;
            const txt=(el.childNodes.length===1&&el.childNodes[0].nodeType===3)?(el.textContent||'').trim():'';
            if(txt && /^(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14)$/.test(txt)) nums.push(parseInt(txt));
        });
        return {btns, nums: nums.slice(0,80), len: document.body.innerText.length};
    }""")
    print('BOTOES:', info['btns'])
    print('NUMEROS:', info['nums'])
    print('BODYLEN:', info['len'])
    ctx.close()
print('fim debug')