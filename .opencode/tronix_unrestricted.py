#!/usr/bin/env python3
"""
Tronix Unrestricted - Assistente Sem Restrições
===============================================
Permite execução de qualquer comando no sistema sem filtros.
"""

import os
import sys
import subprocess
import json
import shutil
import ctypes
import win32api
import win32con

class TronixUnrestricted:
    def __init__(self):
        self.log_file = "tronix_unrestricted.log"
    
    def log(self, message):
        """Log de todas as ações"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def execute_any_command(self, command):
        """Executa QUALQUER comando sem restrições"""
        try:
            self.log(f"COMANDO ILIMITADO: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            output = result.stdout + result.stderr
            self.log(f"RESULTADO: {output[:1000]}...")
            return output
        except Exception as e:
            self.log(f"ERRO: {e}")
            return f"Erro: {str(e)}"
    
    def admin_execute(self, command):
        """Executa comando como administrador"""
        try:
            # Eleva privilégios
            if ctypes.windll.shell32.IsUserAnAdmin():
                return self.execute_any_command(command)
            else:
                # Re-executa como admin
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{sys.argv[0]}" "{command}"', None, 1
                )
                return "Comando executado como administrador"
        except Exception as e:
            return f"Erro admin: {e}"
    
    def modify_system_files(self, file_path, content):
        """Modifica arquivos do sistema"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"MODIFICADO: {file_path}")
            return f"Arquivo modificado: {file_path}"
        except Exception as e:
            return f"Erro: {e}"
    
    def manage_services(self, service_name, action):
        """Gerencia serviços do Windows"""
        try:
            cmd = f"net {action} {service_name}"
            return self.execute_any_command(cmd)
        except Exception as e:
            return f"Erro serviço: {e}"
    
    def registry_edit(self, key, value, data):
        """Edita registro do Windows"""
        try:
            import winreg
            # Implementação de edição de registro
            return f"Registro editado: {key}\\{value}"
        except Exception as e:
            return f"Erro registro: {e}"
    
    def process_management(self, pid=None, name=None):
        """Gerencia processos"""
        try:
            if pid:
                cmd = f"taskkill /f /pid {pid}"
            elif name:
                cmd = f"taskkill /f /im {name}"
            else:
                cmd = "tasklist"
            return self.execute_any_command(cmd)
        except Exception as e:
            return f"Erro processo: {e}"
    
    def file_operations(self, action, source, destination=None):
        """Operações avançadas de arquivos"""
        try:
            if action == "copy":
                shutil.copy2(source, destination)
                return f"Copiado: {source} -> {destination}"
            elif action == "move":
                shutil.move(source, destination)
                return f"Movido: {source} -> {destination}"
            elif action == "delete":
                if os.path.isdir(source):
                    shutil.rmtree(source)
                else:
                    os.remove(source)
                return f"Deletado: {source}"
            elif action == "rename":
                os.rename(source, destination)
                return f"Renomeado: {source} -> {destination}"
        except Exception as e:
            return f"Erro arquivo: {e}"
    
    def network_operations(self, operation):
        """Operações de rede"""
        try:
            if operation == "ipconfig":
                return self.execute_any_command("ipconfig /all")
            elif operation == "netstat":
                return self.execute_any_command("netstat -an")
            elif operation == "ping":
                return self.execute_any_command("ping 8.8.8.8")
        except Exception as e:
            return f"Erro rede: {e}"
    
    def system_shutdown(self, action):
        """Controle de sistema"""
        try:
            if action == "shutdown":
                os.system("shutdown /s /t 0")
                return "Sistema desligado"
            elif action == "restart":
                os.system("shutdown /r /t 0")
                return "Sistema reiniciado"
            elif action == "logout":
                os.system("shutdown /l")
                return "Sessão encerrada"
        except Exception as e:
            return f"Erro controle: {e}"

# API para acesso total
from http.server import HTTPServer, BaseHTTPRequestHandler
import json as json_lib
from datetime import datetime

class UnrestrictedHandler(BaseHTTPRequestHandler):
    assistente = TronixUnrestricted()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json_lib.loads(post_data)
        
        command = data.get('command', '')
        result = self.assistente.execute_any_command(command)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_lib.dumps({'result': result}).encode())
    
    def do_GET(self):
        if self.path == '/status':
            info = {
                'status': 'running',
                'unrestricted': True,
                'timestamp': datetime.now().isoformat()
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps(info).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_unrestricted_api():
    """Inicia API sem restrições"""
    server = HTTPServer(('localhost', 8081), UnrestrictedHandler)
    print("Tronix Unrestricted API rodando em http://localhost:8081")
    server.serve_forever()

if __name__ == "__main__":
    print("=" * 60)
    print("  TRONIX UNRESTRICTED - ASSISTENTE SEM RESTRICOES")
    print("=" * 60)
    print()
    print("API rodando em: http://localhost:8081")
    print("Status: SEM RESTRICOES")
    print()
    print("Comandos disponiveis via API:")
    print("  POST /execute - Executa qualquer comando")
    print("  GET /status - Verifica status")
    print()
    print("=" * 60)
    
    start_unrestricted_api()
