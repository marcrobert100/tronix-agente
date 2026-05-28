# Script PowerShell para testar a conexão com a API da NVIDIA com SSL/TLS correto

Write-Host "Testando conexão com a API da NVIDIA (com SSL/TLS)..." -ForegroundColor Green

# Habilitar TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Configurar headers
$headers = @{
    "Authorization" = "Bearer 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"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Configurar payload
$payload = @{
    "model" = "moonshotai/kimi-k2.6"
    "messages" = @(
        @{
            "role" = "user"
            "content" = "Hello, connection test"
        }
    )
    "max_tokens" = 16384
    "temperature" = 1.00
    "top_p" = 1.00
    "stream" = $false
} | ConvertTo-Json -Depth 10

Write-Host "Sending request to API..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "https://api.nvidia.com/v1/chat/completions" -Method Post -Headers $headers -Body $payload -ContentType "application/json" -UseBasicParsing
    
    Write-Host "API Response:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor Cyan
    
    if ($response.choices) {
        Write-Host "Connection successful!" -ForegroundColor Green
        Write-Host "Response: $($response.choices[0].message.content)" -ForegroundColor Cyan
    } else {
        Write-Host "API responded but no choices returned." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error connecting to API:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $streamReader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $streamReader.BaseStream.Position = 0
        $streamReader.DiscardBufferedData()
        $errorResponse = $streamReader.ReadToEnd()
        Write-Host "API Error Response:" -ForegroundColor Yellow
        Write-Host $errorResponse -ForegroundColor Red
    }
}

Write-Host "Test completed!" -ForegroundColor Green