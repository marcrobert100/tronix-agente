import json
import asyncio
from aiohttp import web
import random
import time
from datetime import datetime

MOVEMENT_SPEED = 2
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

class VirtualOfficeServer:
    def __init__(self, port=8765):
        self.port = port
        self.agents = {}
        self.tasks = {}
        self.app = web.Application()
        self._setup_routes()
        self._start_movement_task()
        
    def _start_movement_task(self):
        async def move_agents():
            while True:
                await asyncio.sleep(0.1)
                for agent in self.agents.values():
                    if agent.get('target_x') is not None and agent.get('target_y') is not None:
                        dx = agent['target_x'] - agent['x']
                        dy = agent['target_y'] - agent['y']
                        dist = (dx**2 + dy**2) ** 0.5
                        if dist > MOVEMENT_SPEED:
                            agent['x'] += int(dx * MOVEMENT_SPEED / dist)
                            agent['y'] += int(dy * MOVEMENT_SPEED / dist)
                        else:
                            agent['x'] = agent['target_x']
                            agent['y'] = agent['target_y']
                            agent['target_x'] = None
                            agent['target_y'] = None
        
        asyncio.create_task(move_agents())
        
    def _setup_routes(self):
        self.app.router.add_post('/register', self.register_agent)
        self.app.router.add_post('/task', self.add_task)
        self.app.router.add_post('/status', self.update_status)
        self.app.router.add_get('/state', self.get_state)
        self.app.router.add_get('/ws', self.websocket_handler)
        
    async def register_agent(self, request):
        data = await request.json()
        agent_id = data.get('id', f"agent_{len(self.agents)+1}")
        self.agents[agent_id] = {
            'id': agent_id,
            'name': data.get('name', agent_id),
            'x': data.get('x', random.randint(100, 700)),
            'y': data.get('y', random.randint(100, 400)),
            'target_x': None,
            'target_y': None,
            'status': 'idle',
            'task': None,
            'color': data.get('color', f"#{random.randint(0, 0xFFFFFF):06x}"),
            'last_update': time.time()
        }
return web.json_response({'success': True, 'agent': self.agents[agent_id]})
    
    async def add_task(self, request):
        data = await request.json()
        task_id = f"task_{len(self.tasks)+1}"
        self.tasks[task_id] = {
            'id': task_id,
            'description': data.get('description', ''),
            'assigned_to': data.get('assigned_to'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        if data.get('assigned_to') and data['assigned_to'] in self.agents:
            agent = self.agents[data['assigned_to']]
            desk_name = data.get('desk', agent['name']).lower()
            if desk_name in DESK_POSITIONS:
                agent['target_x'], agent['target_y'] = DESK_POSITIONS[desk_name]
            agent['status'] = 'working'
            agent['task'] = data.get('description', '')
        return web.json_response({'success': True, 'task_id': task_id})
    
    async def update_status(self, request):
        data = await request.json()
        agent_id = data.get('agent_id')
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            if data.get('status') == 'working':
                desk_name = data.get('desk', '').lower()
                if desk_name in DESK_POSITIONS:
                    target_x, target_y = DESK_POSITIONS[desk_name]
                elif data.get('x') is not None and data.get('y') is not None:
                    target_x, target_y = data.get('x'), data.get('y')
                else:
                    target_x, target_y = agent['x'], agent['y']
                
                agent['target_x'] = target_x
                agent['target_y'] = target_y
            else:
                agent['target_x'] = None
                agent['target_y'] = None
            
            agent.update({
                'status': data.get('status', agent['status']),
                'task': data.get('task', agent['task']),
                'x': data.get('x', agent['x']),
                'y': data.get('y', agent['y']),
                'last_update': time.time()
            })
            return web.json_response({'success': True})
        return web.json_response({'success': False, 'error': 'Agent not found'})
    
    async def get_state(self, request):
        return web.json_response({
            'agents': self.agents,
            'tasks': self.tasks,
            'timestamp': time.time()
        })
    
    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get('type') == 'move':
                        agent_id = data.get('agent_id')
                        if agent_id in self.agents:
                            self.agents[agent_id]['x'] = data.get('x', self.agents[agent_id]['x'])
                            self.agents[agent_id]['y'] = data.get('y', self.agents[agent_id]['y'])
                    await ws.send_json({'type': 'state', 'data': {'agents': self.agents, 'tasks': self.tasks}})
                elif msg.type == web.WSMsgType.ERROR:
                    break
        finally:
            return ws
    
    def run(self):
        print(f"Virtual Office Server running at http://localhost:{self.port}")
        print(f"API endpoints:")
        print(f"   POST /register - Register agent")
        print(f"   POST /task - Add task")
        print(f"   POST /status - Update status")
        print(f"   GET /state - Get current state")
        web.run_app(self.app, host='0.0.0.0', port=self.port)

if __name__ == '__main__':
    server = VirtualOfficeServer()
    server.run()