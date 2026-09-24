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

    # abrir modal login
    pg.evaluate("""() => {
        [...document.querySelectorAll('button,a,span')].find(e=>{
            const t=(e.textContent||'').trim();
            return /^Ent(e|r)ar$|^Entre$/i.test(t);
        })?.click();
    }""")
    pg.wait_for_timeout(3000)

    # preencher
    try:
        pg.fill('#text-input-1', USER, timeout=10000)
        pg.fill('#text-input-2', PASS, timeout=10000)
        print('credenciais OK')
    except Exception as e:
        print('fill err', str(e)[:100])
    pg.wait_for_timeout(1000)

    # SUBMETER: clicar botao Entrar DENTRO do modal auth
    submitted = pg.evaluate("""() => {
        const modal = document.querySelector('[class*=modal]');
        if(!modal) return 'sem modal';
        const btn = [...modal.querySelectorAll('button')].find(b => {
            const t=(b.textContent||'').trim();
            return /^Entrar$|^Entrar$/i.test(t) && b.offsetParent!==null;
        });
        if(btn){ btn.click(); return 'submit OK'; }
        return 'botao nao achado';
    }""")
    print('submit:', submitted)
    pg.wait_for_timeout(8000)

    print('URL pos-login:', pg.url[:140])
    pg.screenshot(path=str(Path(r'C:\xampp\htdocs\agente\blaze_pos_login.png')))

    # ver se logou (procurar indicadores)
    info = pg.evaluate("""() => {
        const txt = document.body.innerText.slice(0,5000);
        const has = [];
        if(/saldo|balance|BRL/i.test(txt)) has.push('saldo');
        if(/DOUBLE|jogo|roulette/i.test(txt)) has.push('jogo');
        if(/modal=auth/i.test(location.href)) has.push('auth_modal_aberto');
        if(/policy_required/i.test(location.href)) has.push('policy_modal');
        return {url:location.href, has, bodyLen:txt.length};
    }""")
    print('INFO:', info)
    ctx.close()