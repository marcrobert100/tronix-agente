# Resumo Geral de Configurações

## 1. API Clod (Qwen) - Token JWT

### Status
- ✅ Token válido para listagem de modelos
- ⚠️ Cota excedida para requisições de chat

### Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDZjlBOWRPQ1ZJaDkwQVNqNldIT09SZHh4eWQyIiwidXNlcklkIjoiQ2Y5QTlkT0NWSWg5MEFTajZXSE9PUmR4eHlkMiIsInRlYW1JZCI6IjNhMTAwMjMyLTI4M2ItNDc1My05YWNlLWNkMjI2ZjZhMTFiYiIsInRlYW1Sb2xlIjoib3duZXIiLCJwcm9qZWN0SWQiOiI0N2Q1NDlmMS1lYTAwLTRmNDItYWNkYi1kZGViOWFhZmFjZmQiLCJpYXQiOjE3Nzc5NDIzODksImV4cCI6MTgyNzk0MjM4OX0.r-HVoOLf_J89y4_sauYKAHNp33H9HqMrmraGs3bTf6I
```

### Modelos Disponíveis
- Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8 (Recomendado)
- Qwen/Qwen3-235B-A22B-Thinking-2507
- Qwen/Qwen2.5-7B-Instruct-Turbo (Sem permissão)

## 2. API OpenRouter (Xiaomi MiMo)

### Chave de API
```
sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v
```

### Status
- ✅ Chave válida para listagem de modelos
- ⚠️ Apenas leitura (não permite uso dos modelos)

### Modelos Xiaomi Disponíveis
- xiaomi/mimo-v2-flash (MiMo-V2-Flash)
- xiaomi/mimo-v2.5 (MiMo-V2.5)
- xiaomi/mimo-v2.5-pro (MiMo-V2.5-Pro)
- xiaomi/mimo-v2-omni (MiMo-V2-Omni)
- xiaomi/mimo-v2-pro (MiMo-V2-Pro)

## 3. Configuração do OpenClaude

### Perfil do PowerShell
`C:\Users\CHCONTE RECPÇÃO\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
```powershell
$env:CLAUDE_CODE_USE_OPENAI = "1"
$env:OPENAI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$env:OPENAI_BASE_URL = "https://api.clod.io/v1"
$env:OPENAI_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"
```

### Configuração do OpenClaude
`C:\Users\CHCONTE RECPÇÃO\.claude\settings.json`
```json
{
    "provider": "openai",
    "openai": {
        "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "base_url": "https://api.clod.io/v1",
        "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"
    }
}
```

## 4. Servidor de Delivery

### Configuração
- **Arquivo de configuração**: `C:\xampp\htdocs\agente\.opencode\casa\config.json`
- **Serviço Mimo v2**: `C:\xampp\htdocs\agente\.opencode\casa\src\services\mimoService.js`
- **Status**: Configurado para usar a API da Mimo v2

## Como Usar

### OpenClaude com Clod (Qwen)
1. Abra um novo terminal do PowerShell
2. Execute: `openclaude --provider openai --model "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"`

### Testar API da Clod (Listagem de Modelos)
Execute no PowerShell:
```powershell
Invoke-WebRequest -Uri "https://api.clod.io/v1/models" -Headers @{Authorization="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."; "HTTP-Referer"="https://example.com"; "X-Title"="Test"} -Method GET
```

## Resumo das APIs

| API | Serviço | Modelo | Status | Permissão |
|-----|---------|--------|--------|-----------|
| Clod | Qwen | Qwen3-Coder-480B-A35B-Instruct-FP8 | ⚠️ Cota excedida | Completa |
| OpenRouter | Xiaomi | MiMo-V2-Flash | ⚠️ Limitada | Apenas leitura |
| Mimo v2 | Xiaomi | (não acessível) | ❌ Falha | - |

## Próximos Passos

1. **Aguardar reset da cota da Clod**: A cota da equipe pode ser resetada periodicamente
2. **Testar novamente**: Após o reset da cota, testar as requisições de chat
3. **Obter chave completa da OpenRouter**: Para usar os modelos Xiaomi em produção
