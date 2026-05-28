# Resumo da Configuração da API Clod (Qwen)

## Descobertas

1.  **Token JWT**: O token fornecido é válido para a API da Clod (https://api.clod.io).
2.  **Modelos Qwen**: A Clod hospeda os modelos da Qwen:
    *   `Qwen/Qwen3-235B-A22B-Thinking-2507` (Qwen3 235B A22B Thinking 2507)
    *   `Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8` (Qwen3 Coder 480B A35B Instruct FP8)
    *   `Qwen/Qwen2.5-7B-Instruct-Turbo` (Qwen2.5 7B Instruct Turbo)

3.  **Token JWT Decodificado**:
    *   `sub`: `Cf9A9dOCVIh90ASj6WHOORdxxyd2`
    *   `userId`: `Cf9A9dOCVIh90ASj6WHOORdxxyd2`
    *   `teamId`: `3a100232-283b-4753-9ace-cd226f6a11bb`
    *   `teamRole`: `owner` (proprietário)
    *   `projectId`: `47d549f1-ea00-4f42-acdb-ddeb9aafacfd`
    *   `iat`: 1777942389 (data de emissão)
    *   `exp`: 1827942389 (data de expiração - 5 anos)

## Configuração Realizada

### 1. OpenClaude
Configurei o OpenClaude para usar a API da Clod com o token JWT fornecido:
- **Provider**: OpenAI (compatível com Clod)
- **API Key**: Token JWT fornecido
- **Base URL**: `https://api.clod.io/v1`
- **Model**: `Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8`

**Arquivo de perfil do PowerShell**: `C:\Users\CHCONTE RECPÇÃO\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
```powershell
$env:CLAUDE_CODE_USE_OPENAI = "1"
$env:OPENAI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$env:OPENAI_BASE_URL = "https://api.clod.io/v1"
$env:OPENAI_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"
```

## Como Usar

### OpenClaude
1. Abra um novo terminal do PowerShell
2. Execute: `openclaude --provider openai --model "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"`

### Teste da API
Execute o seguinte comando no PowerShell:
```powershell
Invoke-WebRequest -Uri "https://api.clod.io/v1/chat/completions" -Method POST -Headers @{Authorization="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."; "Content-Type"="application/json"} -Body '{"model": "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8", "messages": [{"role": "user", "content": "Olá, teste da API Clod"}]}'
```

## Modelos Qwen Disponíveis na Clod

| Modelo | Descrição | Proprietário |
|--------|-----------|--------------|
| Qwen/Qwen3-235B-A22B-Thinking-2507 | Qwen3 235B A22B Thinking 2507 | Qwen |
| Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8 | Qwen3 Coder 480B A35B Instruct FP8 | Qwen |
| Qwen/Qwen2.5-7B-Instruct-Turbo | Qwen2.5 7B Instruct Turbo | Qwen |

## Notas

- O token JWT é válido por 5 anos (expira em 1827942389).
- A API da Clod suporta modelos da Qwen (Alibaba Cloud).
- O token tem permissões de proprietário da equipe e acesso ao projeto.
- A API da Clod tem um limite de 5 requisições por minuto (x-ratelimit-limit: 5).
