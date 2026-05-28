# Virtual Office - Sistema de Agentes Visuais

Sistema que mostra agentes trabalhando num escritório virtual 2D, integrado com opencode.

## Arquivos

```
virtual_office/
├── server.py    # Servidor API (aiohttp)
├── client.py    # Cliente Python para opencode
├── index.html   # Interface visual do escritório
└── README.md    # Este arquivo
```

## Como Usar

### 1. Iniciar o Servidor

```bash
cd virtual_office
pip install aiohttp
python server.py
```

O servidor rodará em `http://localhost:8765`

### 2. Abrir a Interface Visual

Abra o arquivo `index.html` no navegador:
- Chrome/Firefox: arraste o arquivo para o navegador
- Ou use um servidor local: `python -m http.server 8000`

### 3. Usar com Opencode

No seu código Python, importe o cliente:

```python
from virtual_office.client import VirtualOfficeClient

# Criar cliente
office = VirtualOfficeClient()

# Registrar agente
agent = office.register("MeuAgente", "#00ff88")

# Adicionar tarefa
office.add_task("Descrição da tarefa", "Agente")

# Atualizar status
office.start_working("Trabalhando em algo...")

# Mover agente
office.move_to(200, 150)

# Finalizar trabalho
office.finish_work()
```

### 4. Demo

```bash
python client.py demo
```

## API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/register` | POST | Registrar agente |
| `/task` | POST | Adicionar tarefa |
| `/status` | POST | Atualizar status |
| `/state` | GET | Ver estado atual |
| `/ws` | WS | WebSocket para updates em tempo real |

## Desk Positions

- Explore: (150, 180)
- Frontend: (350, 180)
- Backend: (550, 180)
- Database: (750, 180)
- Test: (150, 380)
- Deploy: (350, 380)
- Debug: (550, 380)
- Review: (750, 380)