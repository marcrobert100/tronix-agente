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
    except: pass

    # analisar btn entrar no modal: disabled? class? e estado do turnstile
    info = pg.evaluate("""() => {
        const modal = document.querySelector('[class*=modal]');
        const btn = modal ? [...modal.querySelectorAll('button')].find(b=>/^Entrar$/.test((b.textContent||'').trim())) : null;
        const ts = document.querySelector('input[name=cf-turnstile-response]');
        const turn = document.querySelector('[class*=turnstile], iframe[src*=turnstile], [id*=turnstile], [id*=cf-chl], [class*=cf-chl]');
        return {
            url: location.href,
            btnDisabled: btn ? btn.disabled : 'n/a',
            btnClass: btn ? String(btn.className).slice(0,80) : 'n/a',
            hasTurnstileInput: !!ts,
            turnstileInfo: turn ? String(turn.className||turn.id||'').slice(0,80) : null,
        };
    }""")
    print('=== ESTADO ===')
    print('url:', info['url'])
    print('btnDisabled:', info['btnDisabled'])
    print('btnClass:', info['btnClass'])
    print('hasTurnstileInput:', info['hasTurnstileInput'])
    print('turnstileInfo:', info['turnstileInfo'])

    # procurar todos os iframes turnstile/challenge
    frames_info = pg.evaluate("""() => [...document.querySelectorAll('iframe')].map(f=>({
        src: (f.src||'').slice(0,100), cls: String(f.className).slice(0,40), wid: f.width, hgt: f.height
    }))""")
    print('=== IFRAMES ===')
    for f in frames_info: print(f)

    pg.wait_for_timeout(20000)  # esperar turnstile resolver
    info2 = pg.evaluate("""() => {
        const modal = document.querySelector('[class*=modal]');
        const btn = modal ? [...modal.querySelectorAll('button')].find(b=>/^Entrar$/.test((b.textContent||'').trim())) : null;
        return { btnDisabled: btn?btn.disabled:'n/a', btnClass: btn?String(btn.className).slice(0,80):'n/a' };
    }""")
    print('=== APOS 20s FOCO ===')
    print('btnDisabled:', info2['btnDisabled'])
    print('btnClass:', info2['btnClass'])
    ctx.close()