import requests
import time
import random
import json
import sys

SERVER_URL = "http://localhost:8765"

DESK_POSITIONS = {
    "Frontend": (350, 180),
    "Backend": (550, 180),
    "Database": (750, 180),
    "Explore": (150, 180),
    "Test": (150, 380),
    "Deploy": (350, 380),
    "Debug": (550, 380),
    "Review": (750, 380),
}

def get_state():
    r = requests.get(f"{SERVER_URL}/state")
    return r.json()

def register_agent(name, color, x, y):
    r = requests.post(f"{SERVER_URL}/register", json={
        "name": name, "color": color, "x": x, "y": y
    })
    return r.json()["agent"]

def add_task(description, assigned_to, desk=None):
    r = requests.post(f"{SERVER_URL}/task", json={
        "description": description, "assigned_to": assigned_to, "desk": desk or assigned_to
    })
    return r.json()

def update_status(agent_id, status, task=None, x=None, y=None):
    data = {"agent_id": agent_id, "status": status}
    if task: data["task"] = task
    if x is not None: data["x"] = x
    if y is not None: data["y"] = y
    r = requests.post(f"{SERVER_URL}/status", json=data)
    return r.json()

print("=== Tarefa de 3 minutos ===")

state = get_state()
agents_list = list(state.get("agents", {}).values())

if not agents_list:
    agents_list = [
        register_agent("Frontend", "#00aaff", 350, 180),
        register_agent("Backend", "#ffaa00", 550, 180),
    ]
    print(f"Agentes registrados: {[a['name'] for a in agents_list]}")
    
    tasks = [
        ("Criar botao login", "Frontend"),
        ("Criar API /login", "Backend"),
    ]
    for desc, assignee in tasks:
        add_task(desc, assignee)
else:
    print(f"Usando agentes existentes: {[a['name'] for a in agents_list]}")

for agent in agents_list:
    task = "Trabalhando..."
    desk_x, desk_y = DESK_POSITIONS.get(agent["name"], (agent["x"], agent["y"]))
    update_status(agent["id"], "working", task, desk_x, desk_y)
    print(f"{agent['name']}: trabalhando na mesa ({desk_x}, {desk_y})")

print("\nAgentes trabalhando! Atualize a pagina index.html")

for i in range(180):
    time.sleep(1)
    if i % 30 == 0 and i > 0:
        print(f" Tempo: {i//60}:{i%60:02d}")

for agent in agents_list:
    update_status(agent["id"], "idle")

print("\nTrabalho finalizado!")