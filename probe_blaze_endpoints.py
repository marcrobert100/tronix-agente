# -*- coding: utf-8 -*-
# Escaneia bundle JS da blaze.com e extrai rotas /api/ - tenta achar endpoints de montantes por cor
import urllib.request, urllib.parse, re, sys
from pathlib import Path

OUT = Path(r'C:\xampp\htdocs\agente\_probe_blaze_out.txt')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://blaze.com/'}


def log(t):
    OUT.open('a', encoding='utf-8').write(t + '\n')
    print(t)


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read()


def main():
    OUT.open('w', encoding='utf-8').close()
    rotas = set()
    try:
        html = get('https://blaze.com/').decode('utf-8', 'replace')
        log('HOME len %d' % len(html))
    except Exception as e:
        log('HOME ERR ' + str(e)[:120])
        return

    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
    log('scripts: %d' % len(scripts))
    seen = set()
    for s in scripts:
        u = s if s.startswith('http') else ('https://blaze.com' + ('/' if not s.startswith('/') else '') + s)
        if u in seen or not re.search(r'\.(?:js|mjs)\b', u):
            continue
        seen.add(u)
        try:
            js = get(u).decode('utf-8', 'replace')
            log('JS %s len %d' % (u, len(js)))
            for m in re.finditer(r'["\'](/api/[A-Za-z0-9_/{}.:?=&$-]+)["\']', js):
                rotas.add(m.group(1))
            for m in re.finditer(r'["\'](https?://[^"\']*api[^"\']*)["\']', js):
                rotas.add(m.group(1))
        except Exception as e:
            log('JS ERR %s %s' % (u, str(e)[:60]))

    log('--- ROTAS /api/ extraidas ---')
    for r in sorted(rotas):
        log('  ' + r[:120])
    log('--- fim scan ---')

    # tenta deletados
    can = [
        'https://blaze.com/api/roulette_trends',
        'https://blaze.com/api/roulette_games/recent',
        'https://blaze.com/api/roulette_games/complete',
        'https://blaze.com/api/roulette_games/recent?mode=double',
        'https://blaze.com/api/double/statistics',
        'https://blaze.com/api/double/last_100_results',
        'https://blaze.com/api/roulette_trends/recent?mode=double',
    ]
    log('--- teste rotas candidatas ---')
    for c in can:
        try:
            b = get(c)
            log('> %s -> HTTP %d bytes (%s)' % (c, len(b), b[:120].decode('utf-8', 'replace')))
        except Exception as e:
            log('> %s -> ERR %s' % (c, str(e)[:80]))


if __name__ == '__main__':
    main()
