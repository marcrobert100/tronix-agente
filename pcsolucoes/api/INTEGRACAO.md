# Escritório Virtual PCsoluções - Integração com opencode

## Como Funciona

O escritório virtual se conecta ao opencode em tempo real. Quando a equipe trabalha, o escritório reflete as atividades automaticamente.

## Arquitetura

```
opencode (CLI)
    ↓ escreve
api/status.json  ← lido por → escritorio-virtual.html
    ↓ salva
api/logs/atividades_YYYY-MM-DD.txt
```

## API de Status

### URL Base
```
http://localhost/agente/pcsolucoes/api/status.php
```

### Enviar Atualização de Agente

**POST** `api/status.php`

```json
{
    "agente": "Programador",
    "acao": "desenvolvendo",
    "tarefa": "Criando API REST em PHP",
    "detalhes": "Módulo de autenticação com JWT",
    "tipo": "tarefa",
    "projeto": "Sistema de Gestão PCsolucoes"
}
```

**Campos:**
| Campo | Obrigatório | Valores |
|-------|-------------|---------|
| agente | Sim | Gestor, Designer, Programador, Atendente, Secretária |
| acao | Sim | desenvolvendo, criando, analisando, finalizou, deploy, etc |
| tarefa | Não | Descrição curta da tarefa |
| detalhes | Não | Descrição detalhada |
| tipo | Não | info, tarefa, sucesso, alerta, erro |
| projeto | Não | Nome do projeto atual |

### Ler Status Atual

**GET** `api/status.php`

Retorna o status de todos os agentes e últimas atividades.

### Resetar Status

**DELETE** `api/status.php`

Reseta todos os agentes para "ocioso".

## Exemplos de Uso no opencode

### Quando o Designer criar um layout:
```bash
curl -X POST http://localhost/agente/pcsolucoes/api/status.php \
  -H "Content-Type: application/json" \
  -d '{"agente":"Designer","acao":"criando","tarefa":"Layout da homepage","detalhes":"Identidade visual com tema azul tecnologia","tipo":"tarefa"}'
```

### Quando o Programador fizer deploy:
```bash
curl -X POST http://localhost/agente/pcsolucoes/api/status.php \
  -H "Content-Type: application/json" \
  -d '{"agente":"Programador","acao":"deploy","tarefa":"Sistema publicado","detalhes":"Versão 2.1 disponível em produção","tipo":"sucesso"}'
```

### Quando o Gestor coordenar:
```bash
curl -X POST http://localhost/agente/pcsolucoes/api/status.php \
  -H "Content-Type: application/json" \
  -d '{"agente":"Gestor","acao":"coordenando","tarefa":"Reunião com equipe","detalhes":"Alinhamento do sprint semanal","tipo":"info"}'
```

### Atualizar projeto atual:
```bash
curl -X POST http://localhost/agente/pcsolucoes/api/status.php \
  -H "Content-Type: application/json" \
  -d '{"agente":"Sistema","acao":"projeto","detalhes":"Novo projeto iniciado","projeto":"Site Institucional PCsolucoes"}'
```

## Como o Escritório Funciona

1. **Polling** a cada 2 segundos: O escritório lê `status.json` via PHP
2. **Atualização automática**: Agentes mudam de cor e mostram tarefas
3. **Log em tempo real**: Cada atividade aparece no painel lateral
4. **Notificações**: Alertas visuais para novas atividades
5. **Indicador LIVE**: Verde quando conectado, vermelho quando desconectado

## Arquivos

```
pcsolucoes/
├── escritorio-virtual.html    ← Interface visual
├── api/
│   ├── status.php             ← API principal
│   ├── status.json            ← Dados em tempo real
│   ├── salvar-log.php         ← API de logs
│   └── logs/
│       └── atividades_2026-05-10.txt
```
