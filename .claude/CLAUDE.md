# OpenClaude + Antigravity Kit Configuration

Este projeto integra o **Antigravity Kit** com **36 skills** e **11 workflows** para desenvolvimento de software completo.

---

## Skills Disponíveis

Os skills estão localizados em `.claude/skills/antigravity/` e incluem:

### Desenvolvimento Backend & API
- `api-patterns` - REST, GraphQL, tRPC, autenticação
- `nodejs-best-practices` - Node.js patterns e performance
- `database-design` - PostgreSQL, SQLite, ORM, schema design
- `python-patterns` - Python idiomatic patterns
- `rust-pro` - Rust patterns e best practices

### Desenvolvimento Frontend & UI
- `frontend-design` - Design thinking, UX psychology, color/typography
- `tailwind-patterns` - Tailwind CSS patterns
- `nextjs-react-expert` - Next.js 16+, React Server Components
- `web-design-guidelines` - Acessibilidade, performance, audit

### Mobile & Games
- `mobile-design` - iOS, Android, React Native
- `game-development` - 2D, 3D, WebGL, multiplayer

### DevOps & Infrastructure
- `deployment-procedures` - CI/CD, Docker, Kubernetes
- `server-management` - Linux server administration
- `bash-linux` - Bash scripting
- `powershell-windows` - PowerShell scripting

### Qualidade & Testing
- `testing-patterns` - Unit, integration, e2e tests
- `tdd-workflow` - Test-driven development
- `webapp-testing` - Web application testing
- `lint-and-validate` - ESLint, Prettier, type checking

### Architecture & Planning
- `architecture` - System design, scalability
- `plan-writing` - Project planning, PRD, RFC
- `brainstorming` - Creative problem solving
- `code-review-checklist` - Code review best practices

### Specializados
- `app-builder` - Full-stack app scaffolding
- `intelligent-routing` - Multi-agent task routing
- `parallel-agents` - Parallel agent execution
- `behavioral-modes` - AI behavior patterns
- `performance-profiling` - Performance optimization
- `systematic-debugging` - Debugging strategies

### i18n & SEO
- `i18n-localization` - Internationalization
- `seo-fundamentals` - SEO best practices

### Scripts & Tools
- `mcp-builder` - MCP server development
- `documentation-templates` - Technical documentation

---

## Workflows (Slash Commands)

Os workflows estão em `.agent/workflows/`:
- `/brainstorm` - Brainstorming sessions
- `/create` - Project scaffolding
- `/debug` - Debugging workflow
- `/deploy` - Deployment automation
- `/enhance` - Code enhancement
- `/orchestrate` - Multi-agent coordination
- `/plan` - Project planning
- `/preview` - UI preview/testing
- `/status` - Project status
- `/test` - Test generation
- `/ui-ux-pro-max` - Advanced UI/UX design

---

## Como Usar

### Invocar Skills Automaticamente
Quando você pedir algo relacionado a frontend, eu automaticamente lerei `.claude/skills/antigravity/frontend-design/SKILL.md` para aplicar os princípios corretos.

### Exemplos de Uso:
- **Frontend**: "Crie um dashboard" → Usa `frontend-design` + `tailwind-patterns`
- **Backend**: "Crie uma API REST" → Usa `api-patterns` + `nodejs-best-practices`
- **Database**: "Desenhe o schema" → Usa `database-design`
- **Testing**: "Escreva testes" → Usa `testing-patterns` + `tdd-workflow`
- **Debug**: "Debug essa função" → Usa `systematic-debugging`
- **Deploy**: "Faça deploy" → Usa `deployment-procedures`

---

## Arquitetura

```
C:\xampp\htdocs\agente\
├── .claude/
│   ├── CLAUDE.md           # Este arquivo
│   └── skills/
│       └── antigravity/    # 36 skills do Antigravity Kit
│           ├── api-patterns/
│           ├── frontend-design/
│           ├── database-design/
│           └── ... (33+ outros)
├── .agent/
│   ├── workflows/          # 11 workflows
│   ├── agents/            # 20 agents especializados
│   └── rules/             # Regras globais
```

---

## Princípios

1. **Think, don't memorize** - Skills ensinam princípios, não templates
2. **ASK antes de assumir** - Pergunte preferências quando não especificado
3. **Selective reading** - Leia apenas arquivos relevantes
4. **Quality over speed** - Priorize código limpo e testável
