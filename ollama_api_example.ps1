# Configuração da API Ollama
$OLLAMA_URL = "http://localhost:11434/api/generate"
$MODEL = "qwen2:0.5b"

function Generate-Text {
    param(
        [string]$Prompt,
        [string]$Model = $MODEL
    )
    
    $payload = @{
        model = $Model
        prompt = $Prompt
        stream = $false
    }
    
    try {
        $response = Invoke-RestMethod -Uri $OLLAMA_URL -Method Post -Body ($payload | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 60
        return $response.response
    }
    catch {
        return "Erro: $_"
    }
}

# Exemplos de uso
Write-Host "=== Exemplo 1: Conversa simples ==="
$resposta = Generate-Text "Olá, como você está?"
Write-Host "Resposta: $resposta`n"

Write-Host "=== Exemplo 2: Tradução ==="
$resposta = Generate-Text 'Traduza para inglês: "Bom dia, mundo!"'
Write-Host "Resposta: $resposta`n"

Write-Host "=== Exemplo 3: Resumo ==="
$texto = "A inteligência artificial está transformando indústrias ao automatizar tarefas e analisar grandes volumes de dados."
$resposta = Generate-Text "Resuma este texto em uma frase: $texto"
Write-Host "Resposta: $resposta`n"

Write-Host "=== Exemplo 4: Geração de código ==="
$resposta = Generate-Text "Escreva uma função Python que calcula o fatorial de um número."
Write-Host "Resposta: $resposta`n"