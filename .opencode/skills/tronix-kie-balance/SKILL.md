---
name: tronix-kie-balance
description: Consulta o saldo de creditos da conta Kie AI do Tronix. Use quando o usuario perguntar sobre saldo, creditos ou status da conta Kie/Grok Imagine.
---

# Saldo Kie AI

## Ação

Execute o script de status:

```
cd C:\xampp\htdocs\agente
python tronix_kie.py status
```

## Resposta

- Mostre ao usuario o saldo de creditos retornado.
- Se o saldo for menor que 20, avise que esta baixo e recomende recarga em https://kie.ai
- Se o comando falhar (ex: chave invalida), avise o usuario para verificar a KIE_API_KEY no .env
