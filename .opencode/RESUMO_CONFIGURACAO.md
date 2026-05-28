# Resumo da Configuração da API Mimo v2 Flash (Xiaomi)

## Descobertas

1.  **Chave de API**: A chave fornecida (`sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v`) é válida para a **OpenRouter** (https://openrouter.ai).
2.  **Modelos Xiaomi**: A OpenRouter hospeda os modelos da Xiaomi:
    *   `xiaomi/mimo-v2-flash-20251210` (MiMo-V2-Flash)
    *   `xiaomi/mimo-v2.5` (MiMo-V2.5)
    *   `xiaomi/mimo-v2.5-pro` (MiMo-V2.5-Pro)
    *   `xiaomi/mimo-v2-omni` (MiMo-V2-Omni)
    *   `xiaomi/mimo-v2-pro` (MiMo-V2-Pro)

3.  **Limitação da Chave**: A chave fornecida tem permissão apenas para **listar modelos** (leitura), mas **não tem permissão para criar chat completions** (uso dos modelos). Isso é comum em chaves de API públicas ou de demonstração.

## Configuração Realizada

### 1. OpenClaude
Configurei o OpenClaude para usar a OpenRouter com a chave fornecida:
- **Provider**: OpenAI (compatível com OpenRouter)
- **API Key**: `sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v`
- **Base URL**: `https://openrouter.ai/api/v1`
- **Model**: `xiaomi/mimo-v2-flash` (ou variantes)

**Arquivo de perfil do PowerShell**: `C:\Users\CHCONTE RECPÇÃO\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
```powershell
$env:CLAUDE_CODE_USE_OPENAI = "1"
$env:OPENAI_API_KEY = "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v"
$env:OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
$env:OPENAI_MODEL = "xiaomi/mimo-v2-flash"
```

**Arquivo de configuração do OpenClaude**: `C:\Users\CHCONTE RECPÇÃO\.claude\settings.json`
```json
{
    "provider": "openai",
    "openai": {
        "api_key": "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "xiaomi/mimo-v2-flash"
    }
}
```

### 2. Servidor de Delivery (Delivery Bot)
Configurei o servidor de delivery para usar a API da Mimo v2 em vez da Groq:
- **Arquivo de configuração**: `C:\xampp\htdocs\agente\.opencode\casa\config.json`
- **Chave da API Mimo v2**: Adicionada a chave `mimoApiKey`
- **Serviço Mimo v2**: Criado o arquivo `C:\xampp\htdocs\agente\.opencode\casa\src\services\mimoService.js`
- **Atualização do servidor**: O arquivo `server.js` foi atualizado para usar `mimoClient` em vez de `groqClient`

## Como Usar

### OpenClaude
1. Abra um novo terminal do PowerShell
2. Execute: `openclaude --provider openai --model xiaomi/mimo-v2-flash-20251210`

### Servidor de Delivery
1. Navegue até: `C:\xampp\htdocs\agente\.opencode\casa`
2. Execute: `node server.js`
3. Acesse: `http://localhost:3000`

## Próximos Passos

1. **Obter uma chave de API completa**: Para usar os modelos da Xiaomi, você precisará de uma chave de API da OpenRouter com permissão para criar chat completions.
2. **Verificar a fatura**: Acesse https://openrouter.ai/ para verificar o saldo e as permissões da chave.
3. **Testar os modelos**: Após obter uma chave com permissão, teste os modelos da Xiaomi disponíveis na OpenRouter.

## Modelos Xiaomi Disponíveis na OpenRouter

| Modelo | Descrição | Contexto | Preço (Prompt/Completion) |
|--------|-----------|----------|---------------------------|
| xiaomi/mimo-v2-flash-20251210 | MiMo-V2-Flash (open-source) | 262k | $0.00000009 / $0.00000029 |
| xiaomi/mimo-v2.5 | MiMo-V2.5 (omnimodal) | 1M | $0.0000004 / $0.000002 |
| xiaomi/mimo-v2.5-pro | MiMo-V2.5-Pro (flagship) | 1M | $0.000001 / $0.000003 |
| xiaomi/mimo-v2-omni | MiMo-V2-Omni (omni-modal) | 262k | $0.0000004 / $0.000002 |
| xiaomi/mimo-v2-pro | MiMo-V2-Pro (flagship) | 1M | $0.000001 / $0.000003 |

## Notas

- A chave fornecida é válida para a OpenRouter, mas tem permissões limitadas.
- Os modelos da Xiaomi estão disponíveis na OpenRouter e podem ser acessados via API OpenAI-compatível.
- Para usar os modelos em produção, você precisará de uma chave de API com permissões adequadas.
