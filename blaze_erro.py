# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PROFILE = Path(r'C:\xampp\htdocs\agente\blaze_profile_v2')
USER = '92917380500'
PASS = 'jumentoMrs@300'

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), headless=False,
        viewport={'width': 1500, 'height': 950})
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()

    pg.goto('https://blaze.bet.br/pt/games/double', wait_until='domcontentloaded', timeout=45000)
    for _ in range(8):
        pg.wait_for_timeout(2000)
        try:
            pg.evaluate("""() => { [...document.querySelectorAll('button')].forEach(b=>{
                const t=(b.textContent||'').trim();
                if(/ACEITAR TODOS/i.test(t)||/mais de 18/i.test(t)) b.click();
            }); }""")
        except: pass
    pg.wait_for_timeout(3000)
    pg.evaluate("""() => {
        [...document.querySelectorAll('button,a,span')].find(e=>{
            const t=(e.textContent||'').trim();
            return /^Ent(e|r)ar$|^Entre$/i.test(t);
        })?.click();
    }""")
    pg.wait_for_timeout(3000)
    try:
        pg.fill('#text-input-1', USER, timeout=10000)
        pg.fill('#text-input-2', PASS, timeout=10000)
    except Exception as e:
        print('fill err', str(e)[:100])
    pg.wait_for_timeout(1500)
    # ver foto do modal + turnstile
    info = pg.evaluate("""() => {
        const modal = document.querySelector('[class*=modal]');
        let campo='', icone='', aviso='';
        if(modal){
            campo = modal.innerText.slice(0,1500);
            icone = modal.querySelector('[class*=icon],[class*=turnstile]')? 'sim':'nao';
        }
        const wf = [...document.querySelectorAll('iframe')].map(f=>f.src.slice(0,80));
        return {url:location.href, modalTxt:campo, captcha:icone, iframes:wf.slice(0,6)};
    }""")
    print('=== INFO MODAL ===')
    print('url:', info['url'])
    print('captcha:', info['captcha'])
    print('iframes:', info['iframes'])
    print('---TEXTO MODAL---')
    print(info['modalTxt'])
    ctx.close()