# Configuração do Claude Code com Ollama

## Resumo da Configuração

### Modelo Instalado
- **qwen2:0.5b** (352 MB)
- Modelo leve e rápido para CPU
- Ideal para seu i5-3570

### Configuração do Claude Code
Arquivo: `C:\Users\CHCONTE RECPÇÃO\.claude.json`

```json
{
  "providerProfiles": [
    {
      "id": "provider_qwen2_05b",
      "name": "Ollama Qwen2 0.5B",
      "provider": "openai",
      "baseUrl": "http://localhost:11434/v1",
      "model": "qwen2:0.5b"
    }
  ],
  "activeProviderProfileId": "provider_qwen2_05b"
}
```

### Variáveis de Ambiente
- `CLAUDE_CODE_USE_OLLAMA=1`
- `OLLAMA_API_KEY=ollama-local`
- `OLLAMA_HOST=0.0.0.0`
- `OLLAMA_MODEL=qwen2:0.5b`
- `OLLAMA_NUM_THREAD=4`

### Como Usar

1. **Iniciar Ollama** (se não estiver rodando):
   ```bash
   ollama serve
   ```

2. **Usar no Claude Code**:
   - O Claude Code automaticamente usará o modelo qwen2:0.5b via Ollama
   - A API está disponível em: `http://localhost:11434/v1`

3. **Testar a API**:
   ```powershell
   $body = @{model="qwen2:0.5b";messages=@(@{role="user";content="Olá"});stream=$false} | ConvertTo-Json
   Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -Body $body -ContentType "application/json"
   ```

### Modelos Disponíveis
- `qwen2:0.5b` (352 MB) - **Ativo**
- `gemma2:2b` (1.7 GB)
- `llama3.2:1b` (1.3 GB)
- `llama3.1:8b` (4.9 GB)
- `gemma4:e2b` (7.2 GB)

### Dicas de Uso
1. Use modelos pequenos (1B-3B) para respostas rápidas
2. Feche aplicativos desnecessários antes de usar Ollama
3. Para tarefas complexas, use `gemma2:2b` (1.7 GB)
4. A API é compatível com padrões OpenAI

### Solução de Problemas
- Se a API não responder, verifique se o Ollama está rodando: `ollama ps`
- Para reiniciar o Ollama: `ollama serve`
- Para ver logs: `ollama --verbose serve`

### Próximos Passos
1. Teste o Claude Code com o novo modelo
2. Ajuste `OLLAMA_NUM_THREAD` se necessário (4 é ideal para seu i5-3570)
3. Considere adicionar mais modelos se precisar de mais capacidade