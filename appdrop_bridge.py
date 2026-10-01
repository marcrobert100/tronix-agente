"""
AppDrop Bridge — instala no iPad os IPAs que o AppDrop baixa mas nao consegue
instalar (falta /usr/bin/appinst no aparelho).

Diagnostico
-----------
O AppDrop termina o download (100%) e depois chama, via NSTask, um destes
binarios:

    /usr/bin/appinst
    /usr/bin/ipainstaller
    /var/jb/usr/bin/appinst          (rootless)
    /opt/procursus/bin/ipainstaller  (procursus)

Neste iPad (iOS 5.1.1) NENHUM existe: o pacote `appinst` nao esta instalado e
nao ha como instalar remotamente (sem SSH, sem exec no diagnostics_relay, AFC
padrao sem root, repo cydia.akemi.ai fora do ar - HTTP 522).

Por isso o AppDrop mostra a mensagem enganadora "Pode acontecer com apps muito
grandes, ou quando falta espaco ou memoria" quando o erro real e so esse.

Solucao
-------
A instalacao em si funciona: depende do InstallationProxyService, que o
pymobiledevice3 usa, e o AppSync esta ativo no aparelho (instalamos o proprio
AppDrop sem assinatura). Este script faz a parte que o AppDrop nao consegue:

    1. le /Library/Caches/jobs.plist no container do AppDrop (HouseArrest)
    2. acha jobs com state=failed e pega a URL do IPA
    3. baixa o IPA, detecta FairPlay/DRM
    4. instala via InstallationProxyService
    5. registra tudo num SQLite local

Recursos
--------
    historico SQLite  -- tudo que foi instalado, com data/bundle/tamanho
    busca por nome    -- consulta o catalogo do AppDrop (43k apps) e instala
    notificacao       -- avisa no Windows quando termina
    modo servico      -- --monitorar para rodar em background

Uso
---
    python appdrop_bridge.py                      instala o que falhou e sai
    python appdrop_bridge.py --monitorar          fica instalando em background
    python appdrop_bridge.py --instalar URL       instala uma URL especifica
    python appdrop_bridge.py --buscar "nome"      busca no catalogo do AppDrop
    python appdrop_bridge.py --instalar-nome "x"  busca e instala o 1o resultado
    python appdrop_bridge.py --listar             historico de jobs do AppDrop
    python appdrop_bridge.py --historico          tudo que ja foi instalado
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import plistlib
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

UDID = os.environ.get('IPAD_UDID') or None
BUNDLE = 'ca.adrien.appdrop'
JOBS_PLIST = '/Library/Caches/jobs.plist'
CATALOG_REMOTO = '/Library/Caches/appdrop_catalog.db'

BASE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'appdrop_bridge'
CACHE = BASE / 'cache'
CATALOGO = BASE / 'appdrop_catalog.db'
HISTORICO = BASE / 'historico.db'

UA = 'Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46'
ESTADOS_FALHA = {'failed', 'error', 'failed_install'}


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- historico

def abre_historico() -> sqlite3.Connection:
    BASE.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(HISTORICO)
    con.execute("""
        CREATE TABLE IF NOT EXISTS installs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            quando    TEXT NOT NULL,
            origem    TEXT NOT NULL,
            job_id    TEXT,
            url       TEXT,
            bundle_id TEXT,
            nome      TEXT,
            min_os    TEXT,
            tamanho   INTEGER,
            fairplay  INTEGER,
            resultado TEXT NOT NULL,
            detalhe   TEXT
        )""")
    con.commit()
    return con


def registra(con, *, origem, resultado, job_id=None, url=None, bid=None,
             nome=None, minos=None, tamanho=None, fairplay=None, detalhe=None):
    con.execute(
        'INSERT INTO installs (quando, origem, job_id, url, bundle_id, nome,'
        ' min_os, tamanho, fairplay, resultado, detalhe)'
        ' VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (datetime.now().isoformat(timespec='seconds'), origem, job_id, url, bid,
         nome, minos, tamanho, None if fairplay is None else int(fairplay),
         resultado, detalhe))
    con.commit()


def mostra_historico(limite: int):
    con = abre_historico()
    rows = con.execute(
        'SELECT quando, resultado, nome, bundle_id, tamanho, origem, detalhe'
        ' FROM installs ORDER BY id DESC LIMIT ?', (limite,)).fetchall()
    if not rows:
        log('historico vazio — nada instalado ainda por este bridge')
        return
    log(f'{len(rows)} registro(s) mais recentes:\n')
    for quando, res, nome, bid, tam, orig, det in rows:
        marca = {'instalado': 'OK  ', 'pulado': 'SKIP', 'erro': 'ERRO'}.get(res, '?   ')
        tam_txt = f'{tam/1048576:.1f} MB' if tam else '-'
        log(f'  {marca} {quando}  {nome or "?"}  [{bid or "?"}]  {tam_txt}')
        log(f'        origem={orig}' + (f'  {det}' if det else ''))
    log('')


# ------------------------------------------------------------- notificacao

def _esc(s: str) -> str:
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;'))


def notifica(titulo: str, mensagem: str):
    """Toast no Windows. Silencioso se nao houver suporte."""
    if os.name != 'nt':
        try:
            os.system(f'notify-send "{titulo}" "{mensagem}" 2>/dev/null')
        except Exception:
            pass
        return
    try:
        import subprocess
        xml = (
            '<toast><visual><binding template="ToastGeneric">'
            f'<text>{_esc(titulo)}</text>'
            f'<text>{_esc(mensagem)}</text>'
            '</binding></visual></toast>')
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager,"
            " Windows.UI.Notifications, ContentType=WindowsRuntime] > $null;"
            f"$x = [xml]@'\n{xml}\n'@;"
            "$n = [Windows.UI.Notifications.ToastNotificationManager]::"
            "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastGeneric);"
            "$n.GetElementsByTagName('text')[0].AppendChild($n.CreateTextNode("
            f"'{_esc(titulo)}')) > $null;"
            "$n.GetElementsByTagName('text')[1].AppendChild($n.CreateTextNode("
            f"'{_esc(mensagem)}')) > $null;"
            "[Windows.UI.Notifications.ToastNotificationManager]::"
            "CreateToastNotifier('AppDrop Bridge').Show("
            "[Windows.UI.Notifications.ToastNotification]::new($n))"
        )
        subprocess.run(['powershell', '-NoProfile', '-WindowStyle', 'Hidden',
                        '-Command', ps], check=False, timeout=30,
                       capture_output=True)
    except Exception as e:
        log(f'  (notificacao falhou: {type(e).__name__})')


# ------------------------------------------------------------------ catalogo

def catalogo() -> sqlite3.Connection | None:
    if not CATALOGO.exists():
        return None
    try:
        return sqlite3.connect('file:' + str(CATALOGO) + '?mode=ro', uri=True)
    except sqlite3.Error:
        return None


def pontua(titulo: str, bid: str, termo: str) -> int:
    """Ranking: titulo exato > comeca com termo > contem > so bundle id."""
    t = (titulo or '').lower().strip()
    b = (bid or '').lower()
    alvo = termo.lower().strip()
    if t == alvo:
        return 0
    if t.startswith(alvo):
        return 1
    if alvo in t:
        return 2
    if alvo in b:
        return 3
    return 4


def busca_catalogo(termo: str, limite: int = 15, somente_compativel: bool = False) -> list[dict]:
    """Busca no catalogo do AppDrop. Retorna lista com nome/bid/url/minos.

    No catalogo, `urls.url` e o PREFIXO da pasta (ex: .../ipacollection.zip/Downloads)
    e `entries.filename` e o arquivo. A URL real e a juncao dos dois.
    """
    con = catalogo()
    if con is None:
        return []
    alvo = f'%{termo.lower()}%'
    sql = """
        SELECT e.title, e.bid, e.version, e.minos, e.size_kb,
               u.url, e.filename, e.min_minos
        FROM entries_unique e
        LEFT JOIN urls u ON u.idx = e.base_idx
        WHERE e.title_lower LIKE ? OR e.bid_lower LIKE ?
        ORDER BY e.title
        LIMIT ?"""
    try:
        rows = con.execute(sql, (alvo, alvo, limite * 4)).fetchall()
    except sqlite3.Error as e:
        log(f'  busca falhou: {e}')
        return []

    MAX_IOS5 = 50000
    saida = []
    for titulo, bid, versao, minos, size_kb, url, filename, min_minos in rows:
        completo = None
        if url:
            completo = url.rstrip('/') + '/' + urllib.parse.quote(filename or '', safe='')
        mm = min_minos if min_minos is not None else minos
        ok_ios5 = mm is not None and mm <= MAX_IOS5
        if somente_compativel and not ok_ios5:
            continue
        saida.append({'titulo': titulo, 'bid': bid, 'versao': versao, 'minos': minos,
                      'size_kb': size_kb, 'url': completo, 'ios5': ok_ios5,
                      'filename': filename,
                      'rank': pontua(titulo, bid, termo)})
    saida.sort(key=lambda a: (a['rank'], a['titulo'] or ''))
    return saida[:limite]


async def baixa_catalogo():
    """Puxa o catalogo do container do AppDrop."""
    from pymobiledevice3.services.house_arrest import HouseArrestService
    ld = await conecta()
    svc = await HouseArrestService.create(lockdown=ld, bundle_id=BUNDLE, documents_only=False)
    try:
        BASE.mkdir(parents=True, exist_ok=True)
        await svc.pull(CATALOGO_REMOTO, str(CATALOGO), progress_bar=False)
    finally:
        await svc.close()


# ------------------------------------------------------------------ download

def normaliza_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    caminho = urllib.parse.quote(p.path, safe='/')
    return urllib.parse.urlunsplit((p.scheme, p.netloc, caminho, p.query, p.fragment))


def _checa_arquivo(url: str) -> int:
    """HEAD na URL. Retorna codigo HTTP ou 0 se falhou."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA}, method='HEAD')
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _corrige_archive_org(url: str, filename: str | None) -> str | None:
    """URL 404 no archive.org: consulta os metadados do item e procura o arquivo.

    O catalogo do AppDrop tem URLs velhas (itens renomeados/removidos). Em vez de
    desistir, lista os arquivos reais do item e casa por nome.
    """
    try:
        p = urllib.parse.urlsplit(url)
    except Exception:
        return None
    partes = [x for x in p.path.split('/') if x]
    if 'download' not in partes:
        return None
    i = partes.index('download')
    item = partes[i + 1] if len(partes) > i + 1 else None
    if not item:
        return None

    api = f'https://archive.org/metadata/{urllib.parse.quote(item)}'
    try:
        req = urllib.request.Request(api, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            meta = json.loads(r.read().decode('utf-8', 'replace'))
    except Exception as e:
        log(f'      metadata indisponivel: {type(e).__name__}')
        return None

    arquivos = [f.get('name') for f in meta.get('files', []) if f.get('name')]
    if not arquivos:
        log('      item sem arquivos')
        return None

    alvo = (filename or '').lower()
    base = f'https://archive.org/download/{urllib.parse.quote(item)}'

    def norm(s):
        return ''.join(c for c in s.lower() if c.isalnum())

    # 1) nome exato, 2) sem extensao, 3) so o bundle id, 4) primeiro .ipa
    n_alvo = norm(alvo)
    tentativas = []
    if alvo:
        tentativas.append(alvo)
        tentativas.append(alvo.rsplit('.', 1)[0])
        bid = n_alvo.split('v')[0]
        if bid:
            tentativas.append(bid)
    cands = []
    for cand in tentativas:
        nc = norm(cand)
        for a in arquivos:
            if not a.lower().endswith('.ipa'):
                continue
            na = norm(a)
            score = 0
            if nc and nc == na:
                score = 100
            elif nc and (nc in na or na in nc):
                score = 50
            if score:
                cands.append((score, a))
    if cands:
        cands.sort(reverse=True)
        melhor = cands[0][1]
        log(f'      corrigido via archive.org: {melhor}')
        return f'{base}/{urllib.parse.quote(melhor)}'

    ipas = [a for a in arquivos if a.lower().endswith('.ipa')]
    if len(ipas) == 1:
        log(f'      unico IPA do item: {ipas[0]}')
        return f'{base}/{urllib.parse.quote(ipas[0])}'
    log(f'      {len(ipas)} IPAs no item, nenhum casou com o nome')
    return None


def baixa(url: str, filename: str | None = None, validar: bool = True) -> Path | None:
    """Baixa IPA com retry. Retorna caminho ou None."""
    CACHE.mkdir(parents=True, exist_ok=True)

    def _nome_de(u):
        n = Path(urllib.parse.unquote(urllib.parse.urlsplit(u).path)).name or 'app.ipa'
        return n if n.endswith('.ipa') else n + '.ipa'

    nome = _nome_de(url)
    alvo = CACHE / nome

    def tentar(u):
        for tentativa in range(1, 3):
            if alvo.exists() and alvo.stat().st_size > 0:
                log(f'      cache: {alvo.name} ({alvo.stat().st_size} bytes)')
                return alvo
            try:
                log(f'      baixando (tentativa {tentativa})...')
                req = urllib.request.Request(u, headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=300) as r, open(alvo, 'wb') as f:
                    total = int(r.headers.get('Content-Length') or 0)
                    lido = 0
                    while True:
                        bloco = r.read(262144)
                        if not bloco:
                            break
                        f.write(bloco)
                        lido += len(bloco)
                        if total:
                            pct = lido * 100 // total
                            print(f'\r      {pct}%  {lido/1048576:.1f}/{total/1048576:.1f} MB',
                                  end='', flush=True)
                if total:
                    print()
                log(f'      ok: {alvo.name} ({alvo.stat().st_size} bytes)')
                return alvo
            except Exception as e:
                log(f'      falhou: {type(e).__name__}: {e}')
                if alvo.exists():
                    alvo.unlink()
                if tentativa == 1:
                    return None
                time.sleep(3)
        return None

    got = tentar(normaliza_url(url))
    if got:
        return got

    if not validar:
        return None

    log('      tentando corrigir URL (404 no archive.org)...')
    corrigida = _corrige_archive_org(url, filename or Path(nome).name)
    if corrigida:
        alt = CACHE / _nome_de(corrigida)
        alvo_backup = alvo
        alvo = alt
        got = tentar(corrigida)
        if got:
            return got
        alvo = alvo_backup
    return None


def inspeciona_ipa(caminho: Path) -> tuple[str, str, str, bool]:
    with zipfile.ZipFile(caminho) as z:
        names = z.namelist()
        info_name = next((n for n in names if n.startswith('Payload/')
                          and n.endswith('.app/Info.plist')), None)
        if not info_name:
            return ('?', '?', '?', False)
        info = plistlib.loads(z.read(info_name))
        app_dir = info_name.rsplit('/', 1)[0]
        fairplay = any(n.endswith('/iTunesMetadata.plist') for n in names)
        if not fairplay:
            fairplay = f'{app_dir}/SC_Info/' in ' '.join(names)
        return (info.get('CFBundleIdentifier', '?'),
                info.get('CFBundleDisplayName') or info.get('CFBundleName', '?'),
                info.get('MinimumOSVersion', '?'), fairplay)


# ------------------------------------------------------------------ device

async def conecta():
    from pymobiledevice3.exceptions import NoDeviceConnectedError
    from pymobiledevice3.lockdown import create_using_usbmux

    if UDID:
        return await create_using_usbmux(serial=UDID)

    try:
        return await create_using_usbmux()
    except NoDeviceConnectedError:
        raise SystemExit(
            'nenhum iPad/iPhone conectado por USB.\n'
            '  - plugue o aparelho e desbloqueie a tela\n'
            '  - se houver mais de um, defina IPAD_UDID no ambiente'
        )


async def apps_instalados() -> set[str]:
    from pymobiledevice3.services.installation_proxy import InstallationProxyService
    ld = await conecta()
    ips = InstallationProxyService(lockdown=ld)
    try:
        return set(await ips.get_apps())
    finally:
        await ips.close()


async def le_jobs() -> list[dict]:
    from pymobiledevice3.services.house_arrest import HouseArrestService
    ld = await conecta()
    svc = await HouseArrestService.create(lockdown=ld, bundle_id=BUNDLE, documents_only=False)
    try:
        raw = await svc.get_file_contents(JOBS_PLIST)
    except Exception:
        return []
    finally:
        await svc.close()
    try:
        jobs = plistlib.loads(raw)
    except Exception:
        return []
    return jobs if isinstance(jobs, list) else []


async def instala(caminho: Path):
    from pymobiledevice3.services.installation_proxy import InstallationProxyService
    ld = await conecta()
    ips = InstallationProxyService(lockdown=ld)
    try:
        await ips.install_from_local(str(caminho))
    finally:
        await ips.close()


# ------------------------------------------------------------------ instalar

async def instala_url(url: str, forcar: bool = False,
                      instalados: set[str] | None = None,
                      origem: str = 'manual', job_id: str | None = None,
                      filename: str | None = None) -> bool:
    con = abre_historico()
    log(f'\n==> {url}')
    ipa = baixa(url, filename=filename)
    if not ipa:
        log('    FALHOU no download')
        registra(con, origem=origem, resultado='erro', job_id=job_id, url=url,
                 detalhe='download falhou')
        return False

    try:
        bid, nome, minos, fairplay = inspeciona_ipa(ipa)
    except Exception as e:
        log(f'    IPA invalido: {e}')
        registra(con, origem=origem, resultado='erro', job_id=job_id, url=url,
                 detalhe=f'IPA invalido: {e}')
        return False

    tam = ipa.stat().st_size
    log(f'    {nome} ({bid})  minOS {minos}  {tam/1048576:.1f} MB')

    if not forcar and instalados is not None and bid in instalados:
        log('    ja instalado, pulando (use --forcar para reinstalar)')
        registra(con, origem=origem, resultado='pulado', job_id=job_id, url=url,
                 bid=bid, nome=nome, minos=minos, tamanho=tam, fairplay=fairplay)
        return True

    if fairplay:
        log('    *** IPA tem FairPlay/DRM (iTunesMetadata) — instalacao vai falhar.')
        log('        Precisa decifrar antes (conta Apple) ou enviar o .ipa decifrado.')
        registra(con, origem=origem, resultado='erro', job_id=job_id, url=url, bid=bid,
                 nome=nome, minos=minos, tamanho=tam, fairplay=True,
                 detalhe='FairPlay/DRM presente')
        if not forcar:
            return False

    try:
        await instala(ipa)
        log(f'    INSTALADO: {nome}')
        registra(con, origem=origem, resultado='instalado', job_id=job_id, url=url,
                 bid=bid, nome=nome, minos=minos, tamanho=tam, fairplay=fairplay)
        notifica('AppDrop Bridge', f'{nome} instalado no iPad')
        return True
    except Exception as e:
        log(f'    FALHOU: {type(e).__name__}: {str(e)[:160]}')
        registra(con, origem=origem, resultado='erro', job_id=job_id, url=url, bid=bid,
                 nome=nome, minos=minos, tamanho=tam, fairplay=fairplay,
                 detalhe=f'{type(e).__name__}: {str(e)[:120]}')
        return False


# ---------------------------------------------------------------- modos CLI

async def tabela_jobs():
    jobs = await le_jobs()
    if not jobs:
        log('nenhum job no AppDrop')
        return []
    log(f'{len(jobs)} job(s) no historico do AppDrop:\n')
    for j in jobs[-15:]:
        log(f"  [{j.get('state', '?'):8}] {j.get('progress', '?')}%  "
            f"{j.get('name') or j.get('url', '?')}")
        if j.get('message'):
            log(f"             msg: {j['message'][:120]}")
    log('')
    return jobs


async def modo_lista():
    await tabela_jobs()
    return 0


async def modo_pendentes(forcar: bool, silencioso: bool = False):
    if not silencioso:
        jobs = await tabela_jobs()
    else:
        jobs = await le_jobs()
    alvos = [j for j in jobs if j.get('state') in ESTADOS_FALHA and j.get('url')]
    if not alvos:
        if not silencioso:
            log('nada para instalar.')
        return 0
    log(f'{len(alvos)} job(s) com falha para instalar:\n')
    instalados = None if forcar else await apps_instalados()
    ok = 0
    for j in alvos:
        if await instala_url(j['url'], forcar=forcar, instalados=instalados,
                             origem='appdrop', job_id=j.get('jobId')):
            ok += 1
    log(f'\n=== {ok}/{len(alvos)} instalados ===')
    return 0 if ok else 1


async def modo_buscar(termo: str, todos: bool):
    if catalogo() is None:
        log('catalogo ausente — baixando do iPad...')
        try:
            await baixa_catalogo()
            log(f'catalogo baixado: {CATALOGO.stat().st_size/1048576:.1f} MB')
        except Exception as e:
            log(f'ERRO ao baixar catalogo: {type(e).__name__}: {e}')
            return 1

    achados = busca_catalogo(termo)
    if not achados:
        log(f'nada encontrado para "{termo}"')
        return 1

    compativeis = [a for a in achados if a['ios5']]
    if not todos and compativeis:
        achados = compativeis

    log(f'\n{len(achados)} resultado(s) para "{termo}":\n')
    for i, a in enumerate(achados, 1):
        tam = f'{a["size_kb"]/1024:.1f} MB' if a['size_kb'] else '?'
        marca = '' if a['ios5'] else '   [INCOMPATIVEL com iOS 5]'
        log(f'  {i:2}. {a["titulo"]}{marca}')
        log(f'      {a["bid"]}  v{a["versao"]}  minOS {a["minos"]}  {tam}')
        if a['url']:
            log(f'      {a["url"][:110]}')
        else:
            log('      (sem URL)')
    log('')
    log('  --buscar mostra so compativeis com iOS 5; use --todos para ver tudo\n')
    return 0


async def modo_instalar_nome(termo: str, forcar: bool):
    if catalogo() is None:
        log('catalogo ausente — baixando do iPad...')
        try:
            await baixa_catalogo()
        except Exception as e:
            log(f'ERRO ao baixar catalogo: {type(e).__name__}: {e}')
            return 1

    achados = [a for a in busca_catalogo(termo, somente_compativel=True) if a['url']]
    if not achados:
        log(f'nada compativel com iOS 5 encontrado para "{termo}"')
        log('tente --buscar para ver as versoes disponiveis')
        return 1
    if len(achados) > 1:
        log(f'{len(achados)} resultados compativeis — instalando o primeiro:')
        log(f'  {achados[0]["titulo"]} ({achados[0]["bid"]})  minOS {achados[0]["minos"]}\n')

    instalados = None if forcar else await apps_instalados()
    return 0 if await instala_url(achados[0]['url'], forcar=forcar,
                                  instalados=instalados,
                                  origem='catalogo',
                                  filename=achados[0].get('filename')) else 1


async def modo_monitorar(intervalo: int, forcar: bool):
    log(f'AppDrop Bridge em execucao... (Ctrl+C para sair)\n')
    vistos: set[str] = set()
    while True:
        try:
            jobs = await le_jobs()
            novos = [j for j in jobs
                     if j.get('state') in ESTADOS_FALHA and j.get('url')
                     and (j.get('jobId') or j['url']) not in vistos]
            if novos:
                instalados = None if forcar else await apps_instalados()
                for j in novos:
                    vistos.add(j.get('jobId') or j['url'])
                    log(f"\n[{time.strftime('%H:%M:%S')}] falha detectada no AppDrop")
                    await instala_url(j['url'], forcar=forcar, instalados=instalados,
                                      origem='appdrop', job_id=j.get('jobId'))
        except Exception as e:
            log(f'  ciclo erro: {type(e).__name__}: {str(e)[:120]}')
        await asyncio.sleep(intervalo)


def main():
    ap = argparse.ArgumentParser(
        description='Instala no iPad o que o AppDrop nao consegue instalar')
    ap.add_argument('--instalar', metavar='URL', help='instala uma URL de IPA direto')
    ap.add_argument('--buscar', metavar='TERMO', help='busca no catalogo do AppDrop')
    ap.add_argument('--todos', action='store_true',
                    help='--buscar mostra tambem os incompativeis com iOS 5')
    ap.add_argument('--instalar-nome', metavar='TERMO', help='busca e instala o 1o resultado')
    ap.add_argument('--pendentes', action='store_true', help='instala os jobs que falharam e sai')
    ap.add_argument('--listar', action='store_true', help='mostra o historico de jobs do AppDrop')
    ap.add_argument('--historico', action='store_true', help='mostra o que ja foi instalado')
    ap.add_argument('--monitorar', action='store_true', help='fica instalando em background')
    ap.add_argument('--intervalo', type=int, default=15, help='segundos entre checagens')
    ap.add_argument('--forcar', action='store_true', help='ignora FairPlay e reinstala')
    ap.add_argument('--puxar-catalogo', action='store_true', help='baixa o catalogo do iPad')
    ap.add_argument('--limite', type=int, default=25, help='registros no --historico')
    a = ap.parse_args()

    try:
        if a.puxar_catalogo:
            asyncio.run(baixa_catalogo())
            log(f'catalogo: {CATALOGO} ({CATALOGO.stat().st_size/1048576:.1f} MB)')
            return 0
        if a.historico:
            mostra_historico(a.limite)
            return 0
        if a.buscar:
            return asyncio.run(modo_buscar(a.buscar, a.todos))
        if a.instalar_nome:
            return asyncio.run(modo_instalar_nome(a.instalar_nome, a.forcar))
        if a.instalar:
            return 0 if asyncio.run(instala_url(a.instalar, forcar=a.forcar)) else 1
        if a.listar:
            return asyncio.run(modo_lista())
        if a.monitorar:
            try:
                return asyncio.run(modo_monitorar(a.intervalo, a.forcar))
            except KeyboardInterrupt:
                log('\nparado.')
                return 0
        return asyncio.run(modo_pendentes(a.forcar))
    except KeyboardInterrupt:
        log('\ninterrompido.')
        return 130


if __name__ == '__main__':
    sys.exit(main())