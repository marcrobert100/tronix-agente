# Code Review

Revisão sistemática de qualidade de código.

## Quando usar
- Após implementação do desenvolvedor
- Quando solicitado "revisar código" ou "review"
- Parte do fluxo Desenvolvedor -> QA

## Checklist de Code Review

### Estrutura e Organização
- [ ] Nomes de variáveis/funções descritivos
- [ ] Funções com responsabilidade única (SRP)
- [ ] Código DRY (Don't Repeat Yourself)
- [ ] Estrutura de pastas consistente
- [ ] Arquivos não muito grandes (>300 linhas)

### Boas Práticas
- [ ] Tratamento de erros adequado
- [ ] Validação de inputs
- [ ] Comentários apenas quando necessário
- [ ] Código idêntico ao style guide do projeto
- [ ] Consistent error handling

### Performance
- [ ] Sem queries N+1
- [ ] Índices adequados no banco
- [ ] Cache quando apropriado
- [ ] Lazy loading de recursos pesados

### Segurança
- [ ] Dados sensíveis protegidos
- [ ] Input validation
- [ ] Output encoding
- [ ] Autenticação/Autorização corretas

### Testabilidade
- [ ] Funções pure/composable
- [ ] Dependências injetáveis
- [ ] Baixo acoplamento

## Fluxo
1. Leia arquivos modificados
2. Execute checklist completo
3. Classifique issues por severidade
4. Sugira melhorias com código

## Output
```
## Code Review

### Aprovado ✓ / Necessita Alterações ✗

### Issues Encontradas
| Severity | Tipo | Arquivo | Linha | Descrição |
|----------|------|---------|-------|------------|
| HIGH | Bug | user.js | 23 | Null pointer risk |

### Sugestões de Melhoria
1. Extrair lógica de validação para função reutilizável
2. Adicionar tratamento de erro no catch

### Métricas
- Complexidade: Baixa
- Cobertura de testes: Verificar
- Débito técnico: Mínimo
```