import requests
import json
import sys
import time
import random

SERVER_URL = "http://localhost:8765"

DESK_POSITIONS = {
    "explore": (150, 180),
    "frontend": (350, 180),
    "backend": (550, 180),
    "database": (750, 180),
    "test": (150, 380),
    "deploy": (350, 380),
    "debug": (550, 380),
    "review": (750, 380),
}

class VirtualOfficeClient:
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.agent_id = None
        self.agent_name = None
        
    def register(self, name, color=None):
        """Registra um agente no escritório"""
        response = requests.post(f"{self.server_url}/register", json={
            "name": name,
            "color": color or f"#{random.randint(0, 0xFFFFFF):06x}"
        })
        data = response.json()
        if data.get('success'):
            self.agent_id = data['agent']['id']
            self.agent_name = name
            print(f"[OK] Agente '{name}' registrado no escritorio virtual")
            return data['agent']
        return None
    
    def add_task(self, description, assigned_to=None):
        """Adiciona uma tarefa"""
        response = requests.post(f"{self.server_url}/task", json={
            "description": description,
            "assigned_to": assigned_to
        })
        return response.json()
    
    def update_status(self, status, task=None, x=None, y=None):
        """Atualiza o status do agente"""
        if not self.agent_id:
            print("Erro: Agente não registrado")
            return
            
        response = requests.post(f"{self.server_url}/status", json={
            "agent_id": self.agent_id,
            "status": status,
            "task": task,
            "x": x,
            "y": y
        })
        return response.json()
    
    def get_state(self):
        """Pega o estado atual do escritório"""
        response = requests.get(f"{self.server_url}/state")
        return response.json()
    
    def move_to(self, x, y):
        """Move o agente para uma posição"""
        return self.update_status(None, None, x, y)
    
    def start_working(self, task_description, desk_position=None):
        """Inicia o trabalho numa tarefa"""
        if desk_position and desk_position.lower() in DESK_POSITIONS:
            x, y = DESK_POSITIONS[desk_position.lower()]
        else:
            x, y = random.randint(100, 800), random.randint(100, 400)
        return self.update_status("working", task_description, x, y)
    
    def finish_work(self):
        """Finaliza o trabalho"""
        return self.update_status("idle", None, None, None)


def demo():
    """Demonstração do sistema"""
    client = VirtualOfficeClient()
    
    print("\n[Demo] Virtual Office Client")
    print("=" * 40)
    
    print("\n1. Registrando agentes...")
    agents = [
        ("Explore", "#00ff88"),
        ("Frontend", "#00aaff"),
        ("Backend", "#ffaa00"),
        ("Database", "#ff00aa"),
    ]
    
    registered = []
    for name, color in agents:
        agent = client.register(name, color)
        if agent:
            registered.append(agent)
            time.sleep(0.3)
    
    print(f"\n[OK] {len(registered)} agentes registrados")
    
    print("\n2. Adicionando tarefas...")
    tasks = [
        ("Analisar codebase", "Explore"),
        ("Criar componente UI", "Frontend"),
        ("Implementar API", "Backend"),
        ("Otimizar schema", "Database"),
    ]
    
    for task_desc, assignee in tasks:
        result = client.add_task(task_desc, assignee)
        print(f"   [OK] {task_desc} -> {assignee}")
        time.sleep(0.3)
    
    print("\n3. Atualizando status dos agentes...")
    for agent in registered:
        client.agent_id = agent['id']
        task = random.choice(["Analisando código", "Implementando", "Testando", "Deployando"])
        client.start_working(task)
        print(f"   {agent['name']}: {task}")
        time.sleep(0.5)
    
    print("\n4. Estado atual do escritório:")
    state = client.get_state()
    print(f"   Agentes: {len(state.get('agents', {}))}")
    print(f"   Tarefas: {len(state.get('tasks', {}))}")
    
    print("\n" + "=" * 40)
    print("Demo concluída! Abra index.html para visualizar")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo()
        else:
            print("Uso: python client.py [demo]")
    else:
        print("Virtual Office Client")
        print("Usage: python client.py [demo]")