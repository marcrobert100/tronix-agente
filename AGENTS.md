# PROTOCOLO DE INÍCIO DE SESSÃO (OBRIGATÓRIO)
**Antes de qualquer ação, SEMPRE ler:**
1. `C:\xampp\htdocs\agente\memoria_tronix.json` — estado do projeto Tronix
2. `C:\xampp\htdocs\agente\AGENTS.md` — este arquivo (contexto InfoEngine + PCsoluções)
3. `C:\xampp\htdocs\agente\opencode.json` — definições de agentes
4. `mysql -u root tronix_system -e "SELECT * FROM logs_evolucao ORDER BY id DESC LIMIT 10"` — últimas ações
5. `sqlite3 C:\xampp\htdocs\agente\tronix.db ".tables"` — banco local de conteúdo

**Ao terminar a sessão, SEMPRE gravar:**
- `INSERT INTO tronix_system.logs_evolucao (agente, acao) VALUES (...)` com timestamp
- Atualizar `memoria_tronix.json` com `last_actions` se mudanças relevantes

---

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
│   ├── criar_historia.py             # Gera JSON de histórias infantis com SVGs
│   ├── build_livro.py                # Build HTML auto-contido a partir de book.json
│   ├── gerar_pdf.py                  # Converte HTML em PDF via Playwright
│   ├── gerar_infografico.py          # Gera JSON de infográficos
│   ├── enviar_whatsapp.py            # Envia via WhatsApp (link wa.me ou pywhatkit)
│   ├── gerar-apk.js                  # Constrói APK Android via Capacitor/PWABuilder
│   └── gerar-icones.html            # Gera ícones PNG para PWA/APK
├── references/
│   └── svg_guide.md                  # Guia de ilustração SVG para livros infantis
├── examples/
│   └── book.json                     # Exemplo de livro gerado
├── output/
│   └── livro.html                    # Livro HTML gerado (auto-contido)
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

## Sistema de Build de Livros (Novo)
- **Baseado em:** picture-book-skill (GitHub)
- **Fluxo:** `criar_historia.py` → `book.json` → `build_livro.py` → `livro.html`
- **Comandos:**
  ```bash
  python tools/criar_historia.py                    # Gera book.json de exemplo
  python tools/build_livro.py book.json output/livro.html  # Monta HTML
  ```
- **Features do HTML gerado:**
  - SVG inline (sem imagens externas)
  - Narração por página (Web Speech API pt-BR)
  - Auto-leitura sequencial
  - Navegação por setas e dots
  - Botão WhatsApp integrado
  - Exportação PDF via html2pdf.js
  - Design system InfoEngine (cores, tipografia)
- **Guia SVG:** `references/svg_guide.md` — regras para ilustrações infantis
- **Template:** `templates/_livro_template.html` — base HTML com player/navegação

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

## Identidade do Agente CLI
- **Nome:** TRONIX
- **Operador:** opencode CLI
- **Persona canônica:** agente DEV/MEDIA/SUPER do projeto Marcos Roberto
- **Domínio:** PCsoluções, InfoEngine, geração de conteúdo, automação
- **Localização base:** Viçosa-AL

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

---
# Bancada de Trabalho e Equipamentos

## Configuração da Bancada
- **Computador principal**: Dell XPS 15 (2023) com Windows 11 Pro
- **Processador**: Intel Core i7-13700H
- **Memória RAM**: 32GB DDR5
- **Armazenamento**: 1TB NVMe SSD
- **Monitor**: Dell UltraSharp 27" 4K UHD (U2723QE)
- **Placa de vídeo**: NVIDIA RTX 4060 Laptop
- **Teclado**: Logitech MX Keys
- **Mouse**: Logitech MX Master 3S
- **Conectividade**: Ethernet, WiFi 6E, Bluetooth 5.2

## Software e Ferramentas
### Ambiente de Desenvolvimento
- **IDE**: Visual Studio Code 1.85+
- **PHP**: XAMPP v8.2
- **Node.js**: LTS 20.x
- **Python**: 3.11.x com Virtual Environments
- **Git**: GitHub Desktop e linha de comando
- **Browser**: Chrome 120+, Edge 120+, Firefox 120+

### Ferramentas Específicas do Projeto
- **Gerador de APKs**: Capacitor + PWABuilder (node tools/gerar-apk.js)
- **Conversor SVG para PNG**: gerar-icones.html com Canvas API
- **Ferramenta WhatsApp**: pywhatkit e scripts Python
- **Build de livros**: Picture-book-skill (GitHub)
- **Geração de PDF**: Playwright + html2pdf.js

### Ferramentas de Bancada (kit completo)
- **ADB (Android Debug Bridge)**: localização padrão no Windows via winget
  - `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe`
  - ⚠️ Sempre use o ADB deste caminho específico, pois outros podem falhar por causa do "Ç" no nome do usuário
- **scrcpy** (espelhamento de tela): 
  - `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Genymobile.scrcpy_Microsoft.Winget.Source_8wekyb3d8bbwe\scrcpy-win64-v4.1\scrcpy.exe`
- **Python 3.12**: 
  - `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`
- **JDK 17**: para compilar o Evo
  - `C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot`
- **Gradle 9.3.1**: para compilar o Evo
  - `%USERPROFILE%\.gradle\wrapper\dists\gradle-9.3.1-bin\23ovyewtku6u96viwx3xl3oks\gradle-9.3.1\bin\gradle.bat`
- **Drivers de celular instalados no Windows**:
  - Google USB Driver (oem42.inf) — via pnputil ✓
  - Xiaomi/MIUI (VID_2717) — nativo do sistema ✓

### Acesso ao Código
- **Repositório Git**: `C:\xampp\htdocs\agente\`
- **Dashboard PHP**: `http://localhost/agente/infoengine/dashboard/index.php`
- **Caminhos importantes**:
  - `C:\xampp\htdocs\agente\infoengine\`  
  - `C:\Users\marcos\Desktop\tronix-3d-flowchart.html`
  - `C:\Users\marcos\Desktop\potencial.md`
  - `C:\Users\CHCONTE RECPÇÃO\Desktop\MANUAL-DA-BANCADA.md` (manual completo da bancada)

## Procedimentos para Trabalho com Telefones

### Preparação do Ambiente
1. **Conectar dispositivo Android ao PC via USB**
   - Ativar modo desenvolvedor (Configurações > Sobre o telefone > Toque 7 vezes no número da build)
   - Habilitar depuração por USB (Configurações > Desenvolvedor > Depuração USB)
2. **Verificar conexão**
   - Abrir PowerShell como administrador
   - Executar `adb devices` para verificar se o dispositivo está conectado
   - Se não aparecer, instalar drivers ADB ou usar USB Debugging em modo "MTP"

### Conexão Wi-Fi do Celular (Passo a Passo)
1. **Conectar USB** ao celular + PC
2. **Executar comandos ADB**:
   - `adb tcpip 5555`
   - `adb shell svc wifi enable`
   - Aguardar 30s até o celular reconectar automaticamente
   - `adb connect 192.168.3.39:5555` → conectado sem cabo ✓
3. **Usar a variável de ambiente** para comandos ADB:
   - `ANDROID_SERIAL=192.168.3.39:5555 adb shell getprop` (exemplo de comando)
4. **Verificar conexão Wi-Fi**:
   - `adb devices` → o celular deve aparecer com IP e porta

### Testes de Aplicativo
1. **Instalação do APK**
   - Abrir PowerShell na pasta `C:\xampp\htdocs\agente\infoengine`
   - Executar: `adb install -r "C:\caminho\para\app.apk"`
2. **Verificação do funcionamento**
   - Abrir aplicativo no dispositivo
   - Verificar logs usando: `adb logcat | findstr "tronix"`
3. **Debugging**
   - Usar Chrome DevTools (`chrome://inspect/#devices`) para inspeção em tempo real
   - Acessar o app pelo caminho: `http://localhost:8080` (se servidor local estiver ativo)

### Gerenciamento de Dispositivos
- **Backup de dados importantes**: `/data/data/com.stitch.contosmagicos/files/`
- **Limpeza após testes**: Apagar cache e dados do app do dispositivo
- **Manutenção periódica**: Desinstalar apps desnecessários

## Comandos Úteis para PowerShell
```powershell
# Iniciar Apache no XAMPP
Start-Process -FilePath "C:\xampp\xampp-control.exe"

# Verificar portas em uso
Get-NetTCPConnection -LocalPort 80

# Conectar USB com ADB
adb start-server
adb devices

# Reiniciar dispositivo
adb reboot

# Copiar arquivos do dispositivo
adb pull /sdcard/Download /local/path/

# Instalar APK
adb install -r "C:\caminho\para\app.apk"

# Conexão Wi-Fi do celular (passo a passo)
adb tcpip 5555
adb shell svc wifi enable
adb connect 192.168.3.39:5555
```

## Atualizações e Manutenção
- **Atualizar XAMPP**: Semanalmente verificar novas versões
- **Manter Node.js atualizado**: Usar NVM para gerenciar versões
- **Ferramentas Python**: Manter virtual environments atualizados com `pip list --outdated`
- **Verificar logs de sistema**: Monitorar `logs_evolucao` no MySQL e `tronix.db`

## Procedimento de Resolução de Problemas

### Problema com Apache/XAMPP
1. Testar porta 80
2. Verificar se outra aplicação está usando a porta
3. Reiniciar serviço do Apache pelo painel XAMPP

### Problema com ADB/Android
1. Verificar USB debugging ativado
2. Instalar drivers adequados
3. Executar `adb kill-server` seguido por `adb start-server`

### Erros no PHP
1. Verificar logs de erro do Apache em `/xampp/apache/logs/error.log`
2. Testar conexão com MySQL
3. Validar arquivos com `php -l arquivo.php`