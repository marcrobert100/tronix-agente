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

### Acesso ao Código
- **Repositório Git**: `C:\xampp\htdocs\agente\`
- **Dashboard PHP**: `http://localhost/agente/infoengine/dashboard/index.php`
- **Caminhos importantes**:
  - `C:\xampp\htdocs\agente\infoengine\`  
  - `C:\Users\marcos\Desktop\tronix-3d-flowchart.html`
  - `C:\Users\marcos\Desktop\potencial.md`

## Procedimentos para Trabalho com Telefones

### Preparação do Ambiente
1. **Conectar dispositivo Android ao PC via USB**
   - Ativar modo desenvolvedor (Configurações > Sobre o telefone > Toque 7 vezes no número da build)
   - Habilitar depuração por USB (Configurações > Desenvolvedor > Depuração USB)
2. **Verificar conexão**
   - Abrir PowerShell como administrador
   - Executar `adb devices` para verificar se o dispositivo está conectado
   - Se não aparecer, instalar drivers ADB ou usar USB Debugging em modo "MTP"

### Testes de Aplicativo
1. **Instalação do APK**
   - Abrir PowerShell na pasta `C:\xampp\htdocs\agente\infoengine`
   - Executar: `adb install -r dist\app.apk` (se o APK estiver compilado)
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