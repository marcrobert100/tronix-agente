# -*- coding: utf-8 -*-
# VARRE os bundles JS do blaze.com e procura rotas de montantes (Double)
# 1) baixa home, lista <script src> 2) baixa cada bundle 3) extrai rotas /api/*
#    e strings com "amount|bet|bet_amount|total|stats|statistics|volume" proximas
import urllib.request, urllib.parse, re, json, sys
from pathlib import Path

OUT = Path(r'C:\xampp\htdocs\agente\_blaze_rotas_out.json')
HOME = Path(r'C:\xampp\htdocs\agente\_blaze_home.html')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Accept-Language': 'pt-BR,pt;q=0.9'}
OUT.unlink(missing_ok=True)


def log(t):
    with OUT.open('a', encoding='utf-8') as f:
        f.write(t + '\n')


def get(url):
    req = urllib.request.Request(url, headers=dict(UA, Referer='https://blaze.com/'))
    return urllib.request.urlopen(req, timeout=25).read()


def main():
    rotas = set()
    rotas_full = set()
    termos = set()
    try:
        html = get('https://blaze.com/').decode('utf-8', 'replace')
        HOME.write_text(html, encoding='utf-8')
        log('HOME_JS len %d' % len(html))
    except Exception as e:
        log('HOME_ERR ' + str(e)[:120])
        return

    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)', html)
    log('N_SCRIPTS %d' % len(scripts))
    for src in scripts:
        u = src if src.startswith('http') else 'https://blaze.com' + ('' if src.startswith('/') else '/') + src
        try:
            js = get(u).decode('utf-8', 'replace')
        except Exception as e:
            log('JS_ERR %s %s' % (src[:60], str(e)[:60]))
            continue
        log('JS_OK %s len %d' % (u, len(js)))
        # rotas /api/ relativas ou com prefixo
        for m in re.finditer(r'["\'](/api/[A-Za-z0-9_/{}.\-]+)["\']', js):
            rotas.add(m.group(1))
        for m in re.finditer(r'["\'](https?://[^"\']*api[^"\']+)["\']', js):
            rotas_full.add(m.group(1))
        # procura strings de interesse com contexto proximo de /api
        for m in re.finditer(r'["\'](/api/[A-Za-z0-9_/{}.\-]+)["\'](?=.{0,500})', js):
            ctx = m.group(0)[:500]
            if re.search(r'amount|bet|volume|statistics|stats|total|money|roi', ctx, re.I):
                termos.add(m.group(1) + '  <~  ' + re.sub(r'\s+', ' ',
                          re.sub(r'["\'\\`]', '', ctx[-140:]))[:170])

    log('=== ROTAS_API ===')
    for r in sorted(rotas):
        log('R ' + r)
    log('=== ROTAS_FULL ===')
    for r in sorted(rotas_full)[:60]:
        log('Q ' + r)
    log('=== MONTANTE_CONTEXTO (rotas com amount/bet/stat) ===')
    for r in sorted(termos):
        log('A ' + r)
    log('FIM')


if __name__ == '__main__':
    main()
