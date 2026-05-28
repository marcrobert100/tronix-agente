# Automated Testing

Execução e criação de testes automatizados.

## Quando usar
- Quando solicitado "testar", "rodar testes" ou "coverage"
- Após implementações do desenvolvedor
- Parte do fluxo QA

## Tipos de Testes

### Unit Tests
- Testam funções/métodos isolados
- Mock de dependências externas
- Cover edge cases

### Integration Tests
- Testam comunicação entre módulos
- Conexão com banco real ou mock
- Fluxos completo de funcionalidades

### E2E Tests
- Testam a aplicação completa
- Simulam usuário real
- Browser automation quando necessário

## Checklist de Testes
- [ ] Testes cobrem funcionalidades principais
- [ ] Coverage > 70% em código de negócio
- [ ] Testes de borda (edge cases)
- [ ] Testes de erro (o que acontece quando falha)
- [ ] Assertions significativas
- [ ] Testes são rápidos (< 100ms cada)

## Comandos Úteis
```bash
# npm
npm test
npm run test:coverage
npm run test:watch

# Python
pytest
pytest --cov
pytest -v

# Playwright
npx playwright test
```

## Fluxo
1. Identifique funcionalidades alteradas
2. Verifique testes existentes
3. Execute testes existentes
4. Identifique gaps de cobertura
5. Crie novos testes se necessário
6. Reporte coverage

## Output
```
## Test Results

### Execucao
- Total: 45
- Passed: 42
- Failed: 3
- Skipped: 0

### Falhas
| Test | Arquivo | Erro |
|------|---------|------|
| test_create_user | user.spec.js | Expected 201, got 500 |

### Cobertura
- Statements: 78%
- Branches: 65%
- Functions: 82%
- Lines: 77%

### Recomendacoes
1. Adicionar testes para função validateEmail
2. Criar teste de edge case para limite de caracteres
```