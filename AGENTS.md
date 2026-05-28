# InfoEngine — Sistema de Infográficos e Livros Infantis

## Repositório
- GitHub: `https://github.com/marcrobert100/tronix-agente.git`
- Branch: `main`
- Commit mais recente: `cbac3b7` (WhatsApp integration)

## Estrutura de Diretórios
```
/infoengine/
├── index.html                        # Vitrine/portal dos templates
├── design-system/
│   ├── _variables.css                # Tokens de design (cores, tipografia, espaçamento)
│   ├── _typography.css               # Sistema tipográfico
│   ├── _components.css               # Componentes reutilizáveis (cards, botões, tabelas)
│   └── _whatsapp.js                  # Componente JS de compartilhamento WhatsApp
├── templates/
│   ├── infantil/
│   │   ├── o-sonho-da-estrelinha-lua.html       # 10 páginas + capa + infográfico vendas
│   │   └── o-dragao-que-aprendeu-a-abracar.html # 11 páginas + capa + narração voz
│   └── infografico/
│       ├── vendas.html               # Infográfico vendas profissional
│       └── social-post.html          # Post 1080x1080 para Instagram/LinkedIn
└── tools/
    ├── criar_historia.py             # Gera JSON de histórias infantis
    ├── gerar_pdf.py                  # Converte HTML em PDF via Playwright
    ├── gerar_infografico.py          # Gera JSON de infográficos
    └── enviar_whatsapp.py            # Envia via WhatsApp (link wa.me ou pywhatkit)
```

## Regras de Design (Sempre Seguir)
1. **Sem fontes cursivas/script** para diálogos — usar Playfair Display Italic
2. **Letras grandes e legíveis** para público infantil (mínimo 1.15rem)
3. **Ilustrações SVG grandes** em full bleed (70-80% da página)
4. **Paleta de cores quentes** (laranja `#ff7a30`, dourado `#ffd700`/`#ffb347`, azul noturno `#0f0c2e`/`#1a1a5e`)
5. **Evitar roxo** — paleta proibida
6. **Exportação PDF** via html2pdf.js
7. **SVG inline** em vez de imagens externas
8. **Diálogos em itálico** com a classe `.fala` ou tag `<em>` usando Playfair Display

## Templates Existentes

### Infantil
| Template | Páginas | Recursos |
|----------|---------|----------|
| O Sonho da Estrelinha Lua | 10 + capa + infográfico | SVG animado, PDF, WhatsApp |
| O Dragão que Aprendeu a Abraçar | 11 + capa | SVG animado, narração voz (SpeechSynthesis), PDF, WhatsApp |

### Infográfico
| Template | Formato | Recursos |
|----------|---------|----------|
| Vendas Profissional | A4 | Cards, stats, tabela specs, preço, depoimento, CTA, PDF, WhatsApp |
| Social Post | 1080x1080px | Avatar, cards, citação, QR placeholder, exportação PNG, WhatsApp |

## WhatsApp Integration
- Todos os templates têm botão **📱 WhatsApp** na toolbar que abre `wa.me/5582991856656`
- Script Python: `tools/enviar_whatsapp.py`
- Modos: `--link` (wa.me, padrão), `--auto` (pywhatkit automático)
- Componente JS: `design-system/_whatsapp.js`

## Git Log Resumido
```
cbac3b7 ✨ Adiciona integracao com WhatsApp: compartilhar templates via wa.me
34b0145 ✨ Adiciona livro O Dragao que Aprendeu a Abracar, infograficos vendas/social-post e ferramenta gerar_infografico.py
e61820a ✨ InfoEngine — Sistema de Infográficos e Livros Infantis
```

## Preferências do Usuário
- Nome: Marcos Roberto
- WhatsApp: 5582991856656
- Prefere executar comandos manualmente no PowerShell
- Código hospedado em `C:\xampp\htdocs\agente\infoengine\`
- Git repo root: `C:\xampp\htdocs\agente`
- O livro "O Dragão que Aprendeu a Abraçar" também fica salvo no Desktop

## Próximos Passos (Ideias)
- [ ] Ativar GitHub Pages nas settings: branch `main`, pasta `/infoengine`
- [ ] Dashboard web para configurar templates sem editar HTML
- [ ] Criar página de vendas dedicada (landing page do livro)
- [ ] Template de cartão de visita digital
- [ ] Template de apresentação empresarial
- [ ] Integrar com API do WhatsApp Business para envio direto
