"""
Servidor local de video para o iPad 1 (iOS 5.1.1).

Problema: o Safari do iOS 5 e de 2011, nao roda o JavaScript do YouTube de hoje.
Solucao: servir uma pagina minima com <video> em MP4/H.264, que o WebKit antigo
toca nativamente. Sem framework, sem TLS (que e justamente o que mata o iOS 5
em sites modernos).

Uso:
  python ytserver.py                  # porta 8099
  python ytserver.py --port 8080
"""

import argparse
import http.server
import json
import mimetypes
import os
import re
import shutil
import socketserver
import subprocess
import threading
import urllib.parse
from http import HTTPStatus
from pathlib import Path

BASE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'ytserver'
VIDEOS = BASE / 'videos'
TMP = BASE / 'tmp'

PORT = 8099
H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0 Safari/537.36',
}

PAGINA = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Videos</title>
<style>
body{font-family:-apple-system,Helvetica,Arial,sans-serif;background:#111;color:#eee;margin:0;padding:14px}
h1{font-size:19px;margin:0 0 12px}
video{width:100%%;background:#000;border-radius:8px}
.bar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
input[type=text]{flex:1;min-width:180px;padding:9px;border-radius:6px;border:1px solid #444;
  background:#1c1c1c;color:#fff;font-size:14px}
button{padding:9px 15px;border:0;border-radius:6px;background:#cc0000;color:#fff;font-weight:600;font-size:14px}
ul{list-style:none;padding:0;margin:0}
li{padding:9px 0;border-bottom:1px solid #2a2a2a;font-size:14px}
a{color:#4da6ff;text-decoration:none}
a:visited{color:#8f7fd4}
p.vazio{color:#888;font-size:13px}
</style></head><body>
<h1>Videos</h1>
<form id="f" onsubmit="return false">
 <div class="bar">
  <input type="text" id="u" placeholder="https://www.youtube.com/watch?v=...">
  <button onclick="add()">Adicionar</button>
 </div>
</form>
<div id="r"><p class="vazio">Adicione um link do YouTube acima.</p></div>
<script>
function add(){
 var u=document.getElementById('u').value.trim();
 if(!u)return;
 var r=document.getElementById('r');
 fetch('/api/add?u='+encodeURIComponent(u))
  .then(function(x){return x.json()})
  .then(function(j){
    if(j.erro){ r.innerHTML='<p style="color:#ff6666">'+j.erro+'</p>'; }
    else { r.innerHTML=''; load(); }
  });
 document.getElementById('u').value='';
}
function load(){
 fetch('/api/list')
  .then(function(x){return x.json()})
  .then(function(j){
    var r=document.getElementById('r');
    if(!j.videos.length){ r.innerHTML='<p class="vazio">Nenhum video ainda.</p>'; return; }
    var h='';
    j.videos.slice().reverse().forEach(function(v){
      h+='<li><b>'+v.titulo+'</b><br><video controls preload="metadata" src="'+v.url+'"></video>'+
         '<br><small>'+v.tam+' MB</small></li>';
    });
    r.innerHTML=h;
  });
}
load();
</script></body></html>"""


def log(*a):
    print(*a, flush=True)


def ytdlp_existe() -> bool:
    return shutil.which('yt-dlp') is not None or shutil.which('yt-dlp.exe') is not None


def baixa(url: str) -> tuple[str, str | None]:
    """Baixa video. Retorna (arquivo, titulo) ou lanca."""
    if not ytdlp_existe():
        raise RuntimeError('yt-dlp nao encontrado no PATH (pip install yt-dlp)')

    TMP.mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)

    base = re.sub(r'[^A-Za-z0-9_-]+', '_', url)[-40:]
    alvo = TMP / f'{base}.mp4'

    cmd = [
        'yt-dlp', '--no-warnings', '--no-playlist',
        '--no-check-certificate',
        '-f', 'best[height<=480][ext=mp4]/best[ext=mp4]/18',
        '--merge-output-format', 'mp4',
        '-o', str(alvo),
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, env={**os.environ})

    if not alvo.exists():
        # tenta renomear de webm/mkv
        for p in TMP.glob(f'{base}.*'):
            if p.suffix.lower() in ('.mp4', '.webm', '.mkv', '.m4a', '.part'):
                alvo = p.with_suffix('.mp4')
                p.rename(alvo)
                break

    if not alvo.exists():
        erro = (proc.stderr or proc.stdout or '').strip().splitlines()
        msg = erro[-1] if erro else 'falha desconhecida'
        raise RuntimeError(msg[:200])

    final = VIDEOS / alvo.name
    shutil.move(str(alvo), str(final))

    titulo = final.stem.replace('_', ' ')
    try:
        p2 = subprocess.run(['yt-dlp', '--no-warnings', '--print', '%(title)s',
                             '-f', 'best[height<=480][ext=mp4]/18', '--skip-download', url],
                            capture_output=True, text=True, timeout=180)
        if p2.stdout.strip():
            titulo = p2.stdout.strip().splitlines()[0][:120]
    except Exception:
        pass

    return final.name, titulo


def handler_factory(lock):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            caminho = urllib.parse.urlparse(self.path)
            rota = caminho.path

            if rota in ('/', '/index.html'):
                self._send(200, PAGINA.encode('utf-8'), 'text/html; charset=utf-8')
                return

            if rota == '/api/list':
                vids = []
                if VIDEOS.exists():
                    for p in sorted(VIDEOS.glob('*.mp4'), key=lambda x: x.stat().st_mtime):
                        vids.append({
                            'titulo': p.stem.replace('_', ' ')[:120],
                            'url': f'/v/{urllib.parse.quote(p.name)}',
                            'tam': round(p.stat().st_size / 1048576, 1),
                        })
                self._send(200, json.dumps({'videos': vids}).encode(),
                           'application/json')
                return

            if rota == '/api/add':
                q = urllib.parse.parse_qs(caminho.query)
                url = (q.get('u', [''])[0] or '').strip()
                if not url:
                    self._send(400, json.dumps({'erro': 'sem url'}).encode(),
                               'application/json')
                    return
                if not lock.acquire(blocking=False):
                    self._send(409, json.dumps({'erro': 'ja baixando, aguarde'}).encode(),
                               'application/json')
                    return
                try:
                    nome, titulo = baixa(url)
                    log(f'  ok: {titulo} -> {nome}')
                    self._send(200, json.dumps({'ok': True, 'arquivo': nome}).encode(),
                               'application/json')
                except Exception as e:
                    log(f'  ERRO: {e}')
                    self._send(200, json.dumps({'erro': str(e)[:180]}).encode(),
                               'application/json')
                finally:
                    lock.release()
                return

            if rota.startswith('/v/'):
                nome = urllib.parse.unquote(rota[3:])
                p = VIDEOS / Path(nome).name
                if not p.exists():
                    self._send(404, b'nao encontrado', 'text/plain')
                    return
                tipo = mimetypes.guess_type(str(p))[0] or 'video/mp4'
                tam = p.stat().st_size
                rng = self.headers.get('Range')
                if rng:
                    m = re.match(r'bytes=(\d*)-(\d*)', rng)
                    ini = int(m.group(1)) if m and m.group(1) else 0
                    fim = int(m.group(2)) if m and m.group(2) else tam - 1
                    fim = min(fim, tam - 1)
                    if ini > fim:
                        self.send_response(416)
                        self.end_headers()
                        return
                    self.send_response(206)
                    self.send_header('Content-Type', tipo)
                    self.send_header('Content-Range', f'bytes {ini}-{fim}/{tam}')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Length', str(fim - ini + 1))
                    self.end_headers()
                    with p.open('rb') as f:
                        f.seek(ini)
                        shutil.copyfileobj(f, self.wfile, 128 * 1024)
                else:
                    self._send(200, p.read_bytes(), tipo)
                return

            self._send(404, b'nao encontrado', 'text/plain')

    return Handler


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    global PORT
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8099)
    args = ap.parse_args()
    PORT = args.port

    import socket
    ip = socket.gethostbyname(socket.gethostname())

    log(f'videos em : {VIDEOS}')
    log(f'yt-dlp    : {"OK" if ytdlp_existe() else "AUSENTE (pip install yt-dlp)"}')
    log(f'')
    log(f'  No iPad, abra:  http://{ip}:{PORT}/')
    log(f'  (o iPad precisa estar na mesma rede do PC)')
    log(f'')
    log('Ctrl+C para parar')

    lock = threading.Lock()
    with Server(('0.0.0.0', PORT), handler_factory(lock)) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log('\nparado')


if __name__ == '__main__':
    main()