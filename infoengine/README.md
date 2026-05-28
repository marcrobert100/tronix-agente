
# InfoEngine — Sistema Profissional de Infográficos e Livros Infantis

Motor de criação de materiais visuais profissionais com templates HTML/CSS/SVG de alta qualidade, exportáveis para PDF.

## Funcionalidades

- **Templates prontos** — Livros infantis, infográficos de vendas, currículos
- **Design System** — Tokens de cores, tipografia, componentes reutilizáveis
- **Exportação PDF** — Geração via html2pdf.js com qualidade vetorial
- **Ilustrações SVG** — Arte vetorial original, responsiva e animada
- **Código limpo** — HTML+CSS+JS puro, sem dependências pesadas

## Estrutura

```
infoengine/
├── templates/           # Templates visuais prontos
│   ├── infantil/        # Livros infantis ilustrados
│   └── infografico/     # Infográficos profissionais
├── design-system/       # Tokens de design reutilizáveis
│   ├── _variables.css   # Cores, espaçamentos, breakpoints
│   ├── _typography.css  # Sistema tipográfico
│   └── _components.css  # Componentes visuais
├── tools/               # Ferramentas de geração
│   ├── gerar_pdf.py     # Geração programática de PDF
│   └── criar_historia.py # Criação de histórias com IA
├── assets/              # Recursos estáticos
├── docs/                # Documentação
└── .github/workflows/   # Automação CI/CD
```

## Como usar

1. Clone o repositório
2. Abra qualquer template HTML no navegador
3. Clique em "Baixar PDF" para exportar
4. Ou use os tools Python para geração automatizada

## Licença

MIT — use, modifique e distribua livremente.
