# -*- coding: utf-8 -*-
# Sonda endpoints de websocket/mqtt publicos do Blaze procurando campo amount/bet por cor
import socket, ssl, base64, json, threading, time, re

OUT = r'C:\xampp\htdocs\agente\_probe_ws_out.txt'


def log(t):
    import pathlib
    with pathlib.Path(OUT).open('a', encoding='utf-8') as f:
        f.write(t + '\n')
    print(t)


CANDIDATOS = [
    'wss://api-blaze.playbet.io/replication/?group=roulette_games',
    'wss://api-blaze.playbet.io/replication/?group=double_platform',
    'wss://api-blaze.playbet.io/replication/?group=roulette_trends',
    'wss://api-blaze.playbet.io/consumer/roulette_games',
    'wss://blaze.com/ws',
]


def ws_handshake(host, path, subproto=None):
    key = base64.b64encode(__import__('os').urandom(16)).decode()
    headers = (f'GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n'
               f'Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n'
               f'Sec-WebSocket-Version: 13\r\n'
               f'Origin: https://blaze.com\r\nTeam-Name: ir-mwyivw77bi\r\n\r\n')
    ctx = ssl.create_default_context()
    s = socket.create_connection((host, 443), timeout=12)
    s = ctx.wrap_socket(s, server_hostname=host)
    s.sendall(headers.encode())
    resp = b''
    while b'\r\n\r\n' not in resp:
        b = s.recv(4096)
        if not b:
            break
        resp += b
    if b'101' not in resp.split(b'\r\n', 1)[0]:
        raise RuntimeError(resp.split(b'\r\n', 1)[0].decode('utf-8', 'replace'))
    return s


def ws_send(s, text):
    data = text.encode()
    ln = len(data)
    if ln < 126:
        f = b'\x81' + bytes([0x80 | ln])
    else:
        f = b'\x81' + bytes([0x80 | 126]) + ln.to_bytes(2, 'big')
    s.sendall(f + data)


def main():
    import pathlib
    pathlib.Path(OUT).unlink(missing_ok=True)
    for u in CANDIDATOS:
        try:
            host = u.split('://')[1].split('/')[0]
            path = '/' + u.split('://', 1)[1].split('/', 1)[1]
            s = ws_handshake(host, path)
            log('CONECTADO ' + u)
            s.settimeout(7)
            data = b''
            achou = []
            t0 = time.time()
            while time.time() - t0 < 12:
                try:
                    data += s.recv(8192)
                except socket.timeout:
                    if data:
                        break
                    continue
                except Exception:
                    break
                if data.endswith(b'\x01'):
                    pass
                # procura fields amount/bet/statistics nas frames capturadas
                try:
                    text = data.decode('utf-8', 'replace')
                    for kw in ('amount', 'bet', 'statistics', 'total', 'money', 'volume'):
                        if kw in text.lower():
                            idx = text.lower().find(kw)
                            achou.append(text[max(0, idx - 60): idx + 90])
                except Exception:
                    pass
                if len(data) > 400000:
                    break
            s.close()
            if achou:
                log('FOUND FIELDS %s -> %d ocorrencias' % (u, len(achou)))
                for a in achou[:4]:
                    log('   ...' + a.replace('\n', ' ')[:150])
            else:
                log('SEM amount/bet no stream ' + u + ' | bytes ' + str(len(data)))
        except Exception as e:
            log('ERR ' + u + ' -> ' + str(e)[:90])
    log('FIM')


if __name__ == '__main__':
    main()
