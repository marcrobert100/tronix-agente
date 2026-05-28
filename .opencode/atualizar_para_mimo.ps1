# Script PowerShell para atualizar o servidor para usar a API da Mimo v2
# Execute este script como administrador

Write-Host "Atualizando servidor para usar a API da Mimo v2..." -ForegroundColor Green

# Caminho para o arquivo do servidor
$serverPath = "C:\xampp\htdocs\agente\.opencode\casa\server.js"

# Verificar se o arquivo existe
if (Test-Path $serverPath) {
    Write-Host "Arquivo do servidor encontrado: $serverPath" -ForegroundColor Yellow
    
    # Ler o conteúdo atual
    $serverContent = Get-Content $serverPath -Raw
    
    # Verificar se já existe a importação do mimoService
    if ($serverContent -notmatch "require.*mimoService") {
        Write-Host "Adicionando importação do mimoService..." -ForegroundColor Yellow
        
        # Adicionar a importação após a linha do groqService
        $serverContent = $serverContent -replace '(const.*require\(".\/services\/groqService"\);)', '$1' + "`nconst { mimoClient, initMimo } = require('./services/mimoService');"
        
        # Salvar o arquivo
        Set-Content -Path $serverPath -Value $serverContent
        Write-Host "Importação do mimoService adicionada!" -ForegroundColor Green
    } else {
        Write-Host "Importação do mimoService já existe!" -ForegroundColor Green
    }
    
    # Verificar se já existe a função initMimo
    if ($serverContent -notmatch "function initMimo") {
        Write-Host "Adicionando função initMimo..." -ForegroundColor Yellow
        
        # Adicionar a função initMimo após a função initGroq
        $serverContent = $serverContent -replace '(function initGroq\(\) \{[\s\S]*?initGroq\(\);)', '$1' + "`n`n// ═══════════════════════`n//  MIMO V2`n// ═══════════════════════`nlet mimoClient = null;`nfunction initMimo() {`n  const key = (config.mimoApiKey || \"\").trim();`n  if (key.startsWith(\"sk_\")) {`n    mimoClient = new OpenAI({ apiKey: key, baseURL: \"https://api.mimo.ai/v1\" });`n    console.log(\"[IA] Mimo v2 OK:\", config.model || \"mimo-model\");`n  } else {`n    mimoClient = null;`n    if (key) console.warn(\"[IA] Chave inválida — deve começar com sk_\");`n  }`n}`ninitMimo();"
        
        # Salvar o arquivo
        Set-Content -Path $serverPath -Value $serverContent
        Write-Host "Função initMimo adicionada!" -ForegroundColor Green
    } else {
        Write-Host "Função initMimo já existe!" -ForegroundColor Green
    }
    
    # Atualizar a função chamarIA para usar mimoClient em vez de groqClient
    Write-Host "Atualizando função chamarIA para usar Mimo v2..." -ForegroundColor Yellow
    
    # Substituir groqClient por mimoClient na função chamarIA
    $serverContent = $serverContent -replace 'if \(!groqClient \|\| !cfg\.useAI\)', 'if (!mimoClient || !cfg.useAI)'
    $serverContent = $serverContent -replace 'const r = await groqClient\.chat\.completions\.create\(', 'const r = await mimoClient.chat.completions.create('
    
    # Salvar o arquivo
    Set-Content -Path $serverPath -Value $serverContent
    Write-Host "Função chamarIA atualizada para usar Mimo v2!" -ForegroundColor Green
    
    # Atualizar a rota de status para usar mimoClient
    Write-Host "Atualizando rota de status para usar Mimo v2..." -ForegroundColor Yellow
    
    # Substituir groqClient por mimoClient na rota de status
    $serverContent = $serverContent -replace 'iaAtiva: !!groqClient && !!config\.useAI', 'iaAtiva: !!mimoClient && !!config.useAI'
    $serverContent = $serverContent -replace 'groqConfigurada: !!\(config\.groqApiKey \|\| ""\)\.startsWith\("gsk_"\)', 'mimoConfigurada: !!(config.mimoApiKey || "").startsWith("sk_")'
    
    # Salvar o arquivo
    Set-Content -Path $serverPath -Value $serverContent
    Write-Host "Rota de status atualizada para usar Mimo v2!" -ForegroundColor Green
    
} else {
    Write-Host "Arquivo do servidor não encontrado em: $serverPath" -ForegroundColor Red
}

Write-Host "Atualização concluída!" -ForegroundColor Green
Write-Host "Agora o servidor usará a API da Mimo v2 em vez da Groq." -ForegroundColor Yellow
