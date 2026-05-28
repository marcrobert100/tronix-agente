# InfoEngine — Sistema de Infográficos e Livros Infantis

## Repositório
- GitHub: `https://github.com/marcrobert100/tronix-agente.git`
- Branch: `main`
- Commit mais recente: `ead2ec3` (AGENTS.md persistente)
- GitHub Pages: ❌ NÃO ATIVADO (precisa configurar manualmente)

## Estrutura de Diretórios
```
/infoengine/
├── index.html                        # Vitrine/portal dos templates (PWA + APK)
├── manifest.json                     # PWA Manifest (Stitch Contos Mágicos)
├── sw.js                            # Service Worker (cache offline)
├── dashboard/
│   ├── index.php                     # Dashboard PHP (criar, gerenciar, ferramentas)
│   ├── api.php                       # API JSON (status, tools)
│   └── assets/                       # CSS/JS do dashboard
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
│       ├── social-post.html          # Post 1080x1080 para Instagram/LinkedIn
│       ├── certificado.html          # Certificado digital editável (paisagem)
│       └── cartao-visita.html        # Cartão visita frente/verso editável
├── tools/
│   ├── criar_historia.py             # Gera JSON de histórias infantis
│   ├── gerar_pdf.py                  # Converte HTML em PDF via Playwright
│   ├── gerar_infografico.py          # Gera JSON de infográficos
│   ├── enviar_whatsapp.py            # Envia via WhatsApp (link wa.me ou pywhatkit)
│   ├── gerar-apk.js                  # Constrói APK Android via Capacitor/PWABuilder
│   └── gerar-icones.html            # Gera ícones PNG para PWA/APK
└── assets/
    ├── icons/                        # Ícones SVG para PWA
    └── screenshots/                  # Screenshots para loja
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

## Templates Existentes (6)

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

### Utilitários
| Template | Formato | Recursos |
|----------|---------|----------|
| Certificado Digital | A4 paisagem | Editável inline, selo, assinatura, PDF, WhatsApp |
| Cartão de Visita | 340x200mm | Frente/verso, editável inline, QR placeholder, WhatsApp |

## WhatsApp Integration
- Todos os templates têm botão **📱 WhatsApp** na toolbar que abre `wa.me/5582991856656`
- Script Python: `tools/enviar_whatsapp.py`
- Modos: `--link` (wa.me, padrão), `--auto` (pywhatkit automático)
- Componente JS: `design-system/_whatsapp.js`

## Git Log Resumido
```
ead2ec3 📝 Adiciona AGENTS.md - memoria persistente do projeto InfoEngine
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
- Fluxograma 3D Tronix no Desktop: `tronix-3d-flowchart.html`
- Análise de potencial no Desktop: `potencial.md`

## Dashboard PHP
- URL: `http://localhost/agente/infoengine/dashboard/index.php` (requer Apache/XAMPP ligado)
- Abas: Dashboard, Criar (livro/infográfico), Ferramentas (PDF, WhatsApp)
- API JSON: `dashboard/api.php?action=status` ou `?action=tools`
- Gera JSON para usar com os scripts Python
- Requer PHP no XAMPP

## PWA + APK — Stitch Contos Mágicos Infantis
- **App Name:** Stitch Contos Mágicos Infantis
- **App ID:** `com.stitch.contosmagicos`
- **PWA:** `manifest.json` + `sw.js` — instalação direta no navegador
- **APK:** 3 métodos para gerar:
  1. `node tools/gerar-apk.js --pwa` → prepara projeto Capacitor + instruções
  2. `node tools/gerar-apk.js --apk` → build local (requer Android SDK + Java)
  3. PWABuilder (https://pwabuilder.com) — arrasta URL, baixa APK
  4. AndroidJS (https://androidjs.com) — upload dos arquivos
- **Ícones:** `assets/icons/icon.svg` + `gerar-icones.html` (conversão SVG→PNG via Canvas)
- **Service Worker:** Cache dos assets principais, fallback offline
- URL base: `https://marcrobert100.github.io/tronix-agente/infoengine/` (quando Pages ativo)

## Próximos Passos (Ideias)
- [ ] ATIVAR GITHUB PAGES: Settings > Pages > branch `main`, folder `/infoengine`
- [ ] Iniciar Apache no XAMPP para usar o dashboard PHP
- [ ] Dashboard avançado com salvamento em MySQL
- [ ] Template de apresentação empresarial
- [ ] Integrar com API do WhatsApp Business para envio direto
- [ ] ~PWA (Progressive Web App) para uso mobile~ ✅ CONCLUÍDO
- [ ] Gerar APK assinado (Android App Bundle) para Play Store
- [ ] Criar versão iOS via PWABuilder
