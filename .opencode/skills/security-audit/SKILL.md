# Security Audit

Revisão automática de segurança em código.

## Quando usar
- Após implementação de novas funcionalidades
- Antes de commits/deployments
- Quando solicitado "revisar segurança" ou "audit"

## Checklist de Segurança

### OWASP Top 10
- [ ] Injection (SQL, NoSQL, Command)
- [ ] Broken Authentication
- [ ] Sensitive Data Exposure
- [ ] XML External Entities (XXE)
- [ ] Broken Access Control
- [ ] Security Misconfiguration
- [ ] Cross-Site Scripting (XSS)
- [ ] Insecure Deserialization
- [ ] Using Components with Known Vulnerabilities
- [ ] Insufficient Logging & Monitoring

### Validações Técnicas
- [ ] Credenciais não expostas em código
- [ ] Tokens/API keys em variáveis de ambiente
- [ ] Input validation em todos os endpoints
- [ ] Prepared statements para queries SQL
- [ ] HTTPS em todas as rotas sensíveis
- [ ] Headers de segurança (CORS, CSP, etc)
- [ ] Rate limiting implementado
- [ ] Sanitização de dados de entrada

## Fluxo de Execução
1. Leia todos os arquivos modificados
2. Execute checklist OWASP
3. Identifique vulnerabilidades
4. Reporte com severity (CRITICAL/HIGH/MEDIUM/LOW)
5. Sugira correções

## Output
```
## Security Audit

### Vulnerabilidades Encontradas
| Severity | Arquivo | Linha | Issue | Correção |
|----------|---------|-------|------|----------|
| HIGH | auth.js | 45 | SQL Injection | Use parameterized query |

### Recomendacoes
- Implementar rate limiting em /api/login
- Adicionar CSP headers
```