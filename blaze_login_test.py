# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PROFILE = Path(r'C:\xampp\htdocs\agente\blaze_profile_v2')
PROFILE.mkdir(parents=True, exist_ok=True)
USER = '92917380500'
PASS = 'jumentoMrs@300'

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE), headless=False,
        viewport={'width': 1500, 'height': 950})
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()

    def aceitar():
        try:
            pg.evaluate("""() => {
                [...document.querySelectorAll('button')].forEach(b=>{
                    const t=(b.textContent||'').trim();
                    if(/ACEITAR TODOS/i.test(t) || /mais de 18/i.test(t)) b.click();
                });
            }""")
        except Exception as e:
            print('aceitar err', str(e)[:60])

    print('Abrindo site...')
    pg.goto('https://blaze.bet.br/pt/games/double', wait_until='domcontentloaded', timeout=45000)
    for _ in range(8):
        pg.wait_for_timeout(2000); aceitar()
    pg.wait_for_timeout(3000)
    print('URL1:', pg.url[:130])

    # clicar no Entrar (abrir modal login)
    try:
        pg.evaluate("""() => {
            const els=[...document.querySelectorAll('button,a,span')];
            const b=els.find(e=>{
                const t=(e.textContent||'').trim();
                return /^Ent(e|r)ar$/i.test(t) || (t==='Entrar'||t==='Entre');
            });
            if(b){ b.click(); return 'clicou'; }
            return 'nao achou';
        }""")
        print('modal login: acionado')
    except Exception as e:
        print('clicar err', str(e)[:60])
    pg.wait_for_timeout(3000)

    # listar inputs do modal
    inputs = pg.evaluate("""() => [...document.querySelectorAll('input')].map(i=>({
        type:i.type, name:i.name, ph:i.placeholder, id:i.id
    }))""")
    print('INPUTS:', inputs)

    # preencher se achar campo
    if inputs:
        try:
            pg.fill('input[type=text], input[type=tel], input[name=username], input#loginId', USER, timeout=8000)
            pg.fill('input[type=password]', PASS, timeout=8000)
            print('credenciais preenchidas')
            pg.screenshot(path=str(Path(r'C:\xampp\htdocs\agente\blaze_login_filled.png')))
            # botao entrar
            btns = pg.evaluate("""() => [...document.querySelectorAll('button')].map(b=>(b.textContent||'').trim()).filter(t=>t && t.length<30)""")
            print('BOTOES:', btns[:20])
        except Exception as e:
            print('preencher err', str(e)[:100])
            pg.screenshot(path=str(Path(r'C:\xampp\htdocs\agente\blaze_login_err.png')))

    print('Deixando 60s p/ inspecao...')
    pg.wait_for_timeout(60000)
    print('URL final:', pg.url[:130])
    ctx.close()
print('fim')