#!/usr/bin/env python3
"""
Tronix Assistente Completo
==========================
Assistente que executa qualquer tarefa no PC sem restrições.
"""

import os
import sys
import subprocess
import json
import shutil
import threading
import time
from datetime import datetime

class TronixAssistente:
    def __init__(self):
        self.log_file = "tronix_assistente.log"
        self.commands_history = []
        
    def log(self, message):
        """Log de todas as ações"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def execute_command(self, command):
        """Executa qualquer comando no sistema"""
        try:
            self.log(f"EXECUTANDO: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout + result.stderr
            self.log(f"RESULTADO: {output[:500]}...")
            return output
        except Exception as e:
            error_msg = f"ERRO: {str(e)}"
            self.log(error_msg)
            return error_msg
    
    def list_files(self, path="."):
        """Lista arquivos em um diretório"""
        try:
            files = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                files.append({
                    'name': item,
                    'path': full_path,
                    'type': 'dir' if os.path.isdir(full_path) else 'file',
                    'size': os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                })
            self.log(f"LISTAGEM: {len(files)} itens em {path}")
            return files
        except Exception as e:
            self.log(f"ERRO listagem: {e}")
            return []
    
    def read_file(self, file_path):
        """Lê conteúdo de qualquer arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.log(f"LEITURA: {file_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            self.log(f"ERRO leitura: {e}")
            return f"Erro: {str(e)}"
    
    def write_file(self, file_path, content):
        """Escreve em qualquer arquivo"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"ESCRITA: {file_path} ({len(content)} bytes)")
            return f"Arquivo salvo: {file_path}"
        except Exception as e:
            self.log(f"ERRO escrita: {e}")
            return f"Erro: {str(e)}"
    
    def delete_file(self, file_path):
        """Deleta qualquer arquivo ou diretório"""
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                self.log(f"DELETADO DIRETÓRIO: {file_path}")
                return f"Diretório deletado: {file_path}"
            else:
                os.remove(file_path)
                self.log(f"DELETADO ARQUIVO: {file_path}")
                return f"Arquivo deletado: {file_path}"
        except Exception as e:
            self.log(f"ERRO deleção: {e}")
            return f"Erro: {str(e)}"
    
    def create_directory(self, path):
        """Cria diretório"""
        try:
            os.makedirs(path, exist_ok=True)
            self.log(f"DIRETÓRIO CRIADO: {path}")
            return f"Diretório criado: {path}"
        except Exception as e:
            self.log(f"ERRO criação: {e}")
            return f"Erro: {str(e)}"
    
    def run_python_script(self, script_path, args=""):
        """Executa script Python"""
        try:
            cmd = f'python "{script_path}" {args}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout + result.stderr
            self.log(f"SCRIPT PYTHON: {script_path} -> {len(output)} bytes")
            return output
        except Exception as e:
            self.log(f"ERRO script: {e}")
            return f"Erro: {str(e)}"
    
    def system_info(self):
        """Retorna informações do sistema"""
        try:
            info = {
                'sistema': os.name,
                'plataforma': sys.platform,
                'python': sys.version,
                'diretorio_atual': os.getcwd(),
                'usuario': os.getenv('USERNAME', 'Unknown'),
                'computador': os.getenv('COMPUTERNAME', 'Unknown')
            }
            self.log("INFORMAÇÕES DO SISTEMA solicitadas")
            return json.dumps(info, indent=2)
        except Exception as e:
            self.log(f"ERRO info sistema: {e}")
            return f"Erro: {str(e)}"
    
    def kill_process(self, process_name):
        """Mata processo por nome"""
        try:
            cmd = f'taskkill /f /im {process_name}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            self.log(f"PROCESSO KILL: {process_name}")
            return result.stdout + result.stderr
        except Exception as e:
            self.log(f"ERRO kill process: {e}")
            return f"Erro: {str(e)}"
    
    def start_process(self, command):
        """Inicia processo em background"""
        try:
            subprocess.Popen(command, shell=True)
            self.log(f"PROCESSO INICIADO: {command}")
            return f"Processo iniciado: {command}"
        except Exception as e:
            self.log(f"ERRO start process: {e}")
            return f"Erro: {str(e)}"
    
    def download_file(self, url, destination):
        """Baixa arquivo da internet"""
        try:
            import urllib.request
            urllib.request.urlretrieve(url, destination)
            self.log(f"DOWNLOAD: {url} -> {destination}")
            return f"Arquivo baixado: {destination}"
        except Exception as e:
            self.log(f"ERRO download: {e}")
            return f"Erro: {str(e)}"
    
    def search_files(self, directory, pattern):
        """Busca arquivos por padrão"""
        try:
            import glob
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            self.log(f"PESQUISA: {pattern} em {directory} -> {len(files)} resultados")
            return files
        except Exception as e:
            self.log(f"ERRO pesquisa: {e}")
            return f"Erro: {str(e)}"

# API HTTP para controle remoto
from http.server import HTTPServer, BaseHTTPRequestHandler
import json as json_lib

class TronixHandler(BaseHTTPRequestHandler):
    assistente = TronixAssistente()
    
    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json_lib.loads(post_data)
            
            command = data.get('command', '')
            result = self.assistente.execute_command(command)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({'result': result}).encode())
        
        elif self.path == '/write_file':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json_lib.loads(post_data)
            
            file_path = data.get('path', '')
            content = data.get('content', '')
            result = self.assistente.write_file(file_path, content)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps({'result': result}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/status':
            info = self.assistente.system_info()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(info.encode())
        
        elif self.path.startswith('/list/'):
            path = self.path[6:]
            files = self.assistente.list_files(path)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_lib.dumps(files).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP

def start_api_server():
    """Inicia servidor API"""
    server = HTTPServer(('localhost', 8080), TronixHandler)
    print("Tronix Assistente API rodando em http://localhost:8080")
    server.serve_forever()

if __name__ == "__main__":
    assistente = TronixAssistente()
    
    print("=" * 60)
    print("  TRONIX ASSISTENTE COMPLETO")
    print("=" * 60)
    print()
    print("Comandos disponíveis:")
    print("  execute <comando> - Executa comando no sistema")
    print("  list <caminho> - Lista arquivos")
    print("  read <arquivo> - Lê arquivo")
    print("  write <arquivo> <conteúdo> - Escreve arquivo")
    print("  delete <caminho> - Deleta arquivo/diretório")
    print("  info - Informações do sistema")
    print("  exit - Sair")
    print()
    print("API rodando em: http://localhost:8080")
    print("=" * 60)
    
    # Iniciar API em thread separada
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Loop de comandos
    while True:
        try:
            cmd = input("\nTronix> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if action == "exit":
                print("Saindo...")
                break
            elif action == "execute":
                print(assistente.execute_command(args))
            elif action == "list":
                print(json.dumps(assistente.list_files(args or "."), indent=2))
            elif action == "read":
                print(assistente.read_file(args))
            elif action == "write":
                if " " in args:
                    file_path, content = args.split(maxsplit=1)
                    print(assistente.write_file(file_path, content))
                else:
                    print("Uso: write <arquivo> <conteúdo>")
            elif action == "delete":
                print(assistente.delete_file(args))
            elif action == "info":
                print(assistente.system_info())
            else:
                print("Comando não reconhecido. Use: execute, list, read, write, delete, info, exit")
        
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")
