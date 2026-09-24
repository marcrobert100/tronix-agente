import http.server
import json
import subprocess
import os
from urllib.parse import urlparse, parse_qs

PORT = 8765
ADB = r"C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\adb.exe"
SCRCPY = r"C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\scrcpy.exe"
DESKTOP = os.path.join(os.environ['USERPROFILE'], 'Desktop')

class TronixHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/status':
            self.send_status()
        elif parsed.path == '/api/exec':
            params = parse_qs(parsed.query)
            cmd = params.get('cmd', [''])[0]
            self.exec_command(cmd)
        else:
            super().do_GET()
    
    def send_status(self):
        try:
            result = subprocess.run([ADB, 'devices'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            devices = [l for l in lines[1:] if l.strip() and 'device' in l]
            
            ip = battery = wifi = ''
            if devices:
                ip_r = subprocess.run([ADB, 'shell', 'ip', 'addr', 'show', 'wlan0'], capture_output=True, text=True, timeout=5)
                for line in ip_r.stdout.split('\n'):
                    if 'inet ' in line:
                        ip = line.strip().split('inet ')[1].split('/')[0]
                        break
                
                bat_r = subprocess.run([ADB, 'shell', 'dumpsys', 'battery'], capture_output=True, text=True, timeout=5)
                for line in bat_r.stdout.split('\n'):
                    if 'level:' in line:
                        battery = line.split(':')[1].strip()
                        break
                
                wifi_r = subprocess.run([ADB, 'shell', 'dumpsys', 'wifi'], capture_output=True, text=True, timeout=5)
                for line in wifi_r.stdout.split('\n'):
                    if 'mWifiInfo' in line and 'SSID' in line:
                        try:
                            wifi = line.split('SSID: "')[1].split('"')[0]
                        except:
                            pass
                        break
            
            response = {'connected': len(devices) > 0, 'ip': ip, 'battery': battery, 'wifi': wifi}
        except:
            response = {'connected': False, 'ip': '', 'battery': '', 'wifi': ''}
        
        self.send_json(response)
    
    def adb(self, *args, timeout=10):
        return subprocess.run([ADB] + list(args), capture_output=True, text=True, timeout=timeout)
    
    def adb_shell(self, *args, timeout=10):
        return self.adb('shell', *args, timeout=timeout)
    
    def exec_command(self, cmd):
        try:
            # === NAVIGATION ===
            if cmd == 'nav up':
                self.adb_shell('input', 'keyevent', '19')
                self.send_json({'ok': True, 'msg': '▲'})
            elif cmd == 'nav down':
                self.adb_shell('input', 'keyevent', '20')
                self.send_json({'ok': True, 'msg': '▼'})
            elif cmd == 'nav left':
                self.adb_shell('input', 'keyevent', '21')
                self.send_json({'ok': True, 'msg': '◄'})
            elif cmd == 'nav right':
                self.adb_shell('input', 'keyevent', '22')
                self.send_json({'ok': True, 'msg': '►'})
            elif cmd == 'nav home':
                self.adb_shell('input', 'keyevent', '3')
                self.send_json({'ok': True, 'msg': 'Home'})
            elif cmd == 'nav back':
                self.adb_shell('input', 'keyevent', '4')
                self.send_json({'ok': True, 'msg': 'Voltar'})
            elif cmd == 'nav recent':
                self.adb_shell('input', 'keyevent', '187')
                self.send_json({'ok': True, 'msg': 'Tarefas'})
            
            # === VOLUME ===
            elif cmd == 'vol up':
                self.adb_shell('input', 'keyevent', '24')
                self.send_json({'ok': True, 'msg': 'Volume +'})
            elif cmd == 'vol down':
                self.adb_shell('input', 'keyevent', '25')
                self.send_json({'ok': True, 'msg': 'Volume -'})
            elif cmd == 'vol mute':
                self.adb_shell('input', 'keyevent', '164')
                self.send_json({'ok': True, 'msg': 'Mudo'})
            elif cmd == 'vol max':
                for _ in range(15):
                    self.adb_shell('input', 'keyevent', '24')
                self.send_json({'ok': True, 'msg': 'Volume máx'})
            elif cmd.startswith('vol set '):
                level = cmd.split(' ')[2]
                self.adb_shell('media', 'volume', '--set', level)
                self.send_json({'ok': True, 'msg': f'Volume: {level}'})
            
            # === BRIGHTNESS ===
            elif cmd.startswith('bright set '):
                val = cmd.split(' ')[2]
                self.adb_shell('settings', 'put', 'system', 'screen_brightness', val)
                self.send_json({'ok': True, 'msg': f'Brilho: {val}'})
            
            # === MEDIA ===
            elif cmd == 'media play':
                self.adb_shell('input', 'keyevent', '85')
                self.send_json({'ok': True, 'msg': '▶ Play/Pause'})
            elif cmd == 'media pause':
                self.adb_shell('input', 'keyevent', '85')
                self.send_json({'ok': True, 'msg': '⏸ Pausa'})
            elif cmd == 'media stop':
                self.adb_shell('input', 'keyevent', '86')
                self.send_json({'ok': True, 'msg': '⏹ Parar'})
            elif cmd == 'media next':
                self.adb_shell('input', 'keyevent', '87')
                self.send_json({'ok': True, 'msg': '⏭ Próximo'})
            elif cmd == 'media prev':
                self.adb_shell('input', 'keyevent', '88')
                self.send_json({'ok': True, 'msg': '⏮ Anterior'})
            elif cmd == 'media ff':
                self.adb_shell('input', 'keyevent', '90')
                self.send_json({'ok': True, 'msg': '⏩ FF 10s'})
            elif cmd == 'media rw':
                self.adb_shell('input', 'keyevent', '89')
                self.send_json({'ok': True, 'msg': '⏪ RW 10s'})
            elif cmd == 'media mute':
                self.adb_shell('input', 'keyevent', '164')
                self.send_json({'ok': True, 'msg': '🔇 Mudo'})
            
            # === SCREEN ===
            elif cmd == 'scrcpy':
                subprocess.Popen([SCRCPY, '--stay-awake'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.send_json({'ok': True, 'msg': 'Espelhamento iniciado'})
            elif cmd == 'scrcpy-full':
                subprocess.Popen([SCRCPY, '--stay-awake', '--fullscreen'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.send_json({'ok': True, 'msg': 'Espelhamento fullscreen'})
            elif cmd == 'scrcpy-720':
                subprocess.Popen([SCRCPY, '--stay-awake', '--max-size=720', '--video-codec=h264'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.send_json({'ok': True, 'msg': 'Espelhamento 720p'})
            elif cmd == 'scrcpy-h265':
                subprocess.Popen([SCRCPY, '--stay-awake', '--video-codec=h265'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.send_json({'ok': True, 'msg': 'Espelhamento H265'})
            elif cmd == 'screen-on':
                self.adb_shell('input', 'keyevent', '224')
                self.send_json({'ok': True, 'msg': 'Tela ligada'})
            elif cmd == 'screen-off':
                self.adb_shell('input', 'keyevent', '223')
                self.send_json({'ok': True, 'msg': 'Tela apagada'})
            
            # === POWER ===
            elif cmd == 'power menu':
                self.adb_shell('input', 'keyevent', '26')
                self.send_json({'ok': True, 'msg': 'Menu energia'})
            elif cmd == 'power sleep':
                self.adb_shell('input', 'keyevent', '223')
                self.send_json({'ok': True, 'msg': 'Tela dormindo'})
            elif cmd == 'power reboot':
                self.adb('reboot')
                self.send_json({'ok': True, 'msg': 'Reiniciando...'})
            elif cmd == 'power off':
                self.adb('reboot', '-p')
                self.send_json({'ok': True, 'msg': 'Desligando...'})
            elif cmd == 'lock':
                self.adb_shell('input', 'keyevent', '26')
                self.send_json({'ok': True, 'msg': 'Travando tela'})
            
            # === EXPAND ===
            elif cmd == 'expand notifications':
                self.adb_shell('cmd', 'statusbar', 'expand-notifications')
                self.send_json({'ok': True, 'msg': 'Notificações'})
            elif cmd == 'expand settings':
                self.adb_shell('cmd', 'statusbar', 'expand-settings')
                self.send_json({'ok': True, 'msg': 'Configurações'})
            
            # === CLIPBOARD ===
            elif cmd.startswith('clip set '):
                text = cmd[9:]
                self.adb_shell('am', 'broadcast', '-a', 'clipper.set', '-e', 'text', text)
                self.send_json({'ok': True, 'msg': 'Texto enviado'})
            elif cmd == 'clip pull':
                r = self.adb_shell('dumpsys', 'clipboard')
                self.send_json({'ok': True, 'output': r.stdout[:200]})
            
            # === SCREENSHOT ===
            elif cmd == 'screenshot':
                self.adb_shell('screencap', '-p', '/sdcard/screen.png')
                self.adb('pull', '/sdcard/screen.png', os.path.join(DESKTOP, 'screenshot.png'))
                self.adb_shell('rm', '/sdcard/screen.png')
                self.send_json({'ok': True, 'msg': 'Screenshot → Desktop'})
            
            # === APPS ===
            elif cmd.startswith('open '):
                app = cmd[5:]
                apps = {
                    'camera': 'com.android.camera',
                    'chrome': 'com.android.chrome',
                    'youtube': 'com.google.android.youtube',
                    'whatsapp': 'com.whatsapp',
                    'settings': 'com.android.settings',
                    'files': 'com.android.documentsui',
                    'play store': 'com.android.vending',
                    'gallery': 'com.google.android.apps.photos',
                    'clock': 'com.google.android.deskclock',
                    'calculator': 'com.android.calculator2',
                    'maps': 'com.google.android.apps.maps',
                    'spotify': 'com.spotify.music',
                }
                pkg = apps.get(app, app)
                self.adb_shell('am', 'start', '-n', f'{pkg}/.MainActivity')
                self.send_json({'ok': True, 'msg': f'Abrindo {app}'})
            
            # === SYSTEM ===
            elif cmd == 'restart adb':
                self.adb('kill-server')
                self.adb('start-server')
                self.send_json({'ok': True, 'msg': 'ADB reiniciado'})
            elif cmd == 'wifi adb':
                self.adb('tcpip', '5555')
                self.send_json({'ok': True, 'msg': 'Ative WiFi ADB no celular'})
            elif cmd == 'terminal':
                subprocess.Popen([ADB, 'shell'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.send_json({'ok': True, 'msg': 'Terminal aberto'})
            elif cmd == 'app list':
                r = self.adb_shell('pm', 'list', 'packages', '-3')
                self.send_json({'ok': True, 'output': r.stdout[:300]})
            elif cmd == 'file-manager':
                subprocess.Popen(['explorer', 'http://127.0.0.1:8080'])
                self.send_json({'ok': True, 'msg': 'Gerenciador aberto'})
            
            # === KEYBOARD ===
            elif cmd.startswith('input text '):
                text = cmd[11:]
                self.adb_shell('input', 'text', text)
                self.send_json({'ok': True, 'msg': 'Texto enviado'})
            elif cmd.startswith('keycode '):
                code = cmd.split(' ')[1]
                self.adb_shell('input', 'keyevent', code)
                self.send_json({'ok': True, 'msg': f'Keycode {code}'})
            
            else:
                self.send_json({'ok': False, 'msg': f'Comando desconhecido: {cmd}'})
        
        except Exception as e:
            self.send_json({'ok': False, 'msg': f'Erro: {str(e)}'})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print(f"Tronix Remote Server v2.0 — http://localhost:{PORT}")
    server = http.server.HTTPServer(('0.0.0.0', PORT), TronixHandler)
    server.serve_forever()
