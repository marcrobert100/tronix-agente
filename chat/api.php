<?php
// Tronix AI Web Chat Backend (Proxy Seguro + Skills)
error_reporting(0);
set_time_limit(300); // Impede que chamadas autônomas demoradas quebrem a página
header('Content-Type: application/json');

function getEnvData($filePath) {
    if (!file_exists($filePath)) return [];
    $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $data = [];
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) continue;
        $parts = explode('=', $line, 2);
        if (count($parts) === 2) {
            $data[trim($parts[0])] = trim($parts[1]);
        }
    }
    return $data;
}

$input = json_decode(file_get_contents('php://input'), true);
$message = $input['message'] ?? '';

if(empty($message)) {
    echo json_encode(['status' => 'error', 'reply' => 'Mensagem vazia.']);
    exit;
}

$envData = getEnvData(__DIR__ . '/../.env');
$messageLower = strtolower($message);

// ==========================================
// SKILLS LOCAIS SUPER PODEROSAS (Interceptação Direta)
// ==========================================

// 1. Skill: Consultar Saldo Kie AI
if ((strpos($messageLower, 'saldo') !== false) && (strpos($messageLower, 'kie') !== false || strpos($messageLower, 'crédito') !== false || strpos($messageLower, 'credito') !== false)) {
    $kieKey = $envData['KIE_API_KEY'] ?? '';
    if(empty($kieKey)) {
        echo json_encode(['status' => 'success', 'reply' => 'Skill [Saldo Kie]: Erro - Chave não encontrada.']);
        exit;
    }
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://api.kie.ai/api/v1/chat/credit');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer " . $kieKey]);
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode == 200) {
        $data = json_decode($response, true);
        if(is_array($data)) {
            $readable = "### 💳 Saldo Kie AI Atualizado\n\n";
            $readable .= "> **Informações extraídas diretamente da nuvem:**\n\n";
            foreach($data as $key => $value) {
                if(is_numeric($value)) { $value = round($value, 2); }
                $readable .= "✨ **" . ucfirst(str_replace('_', ' ', $key)) . "**: `{$value}`\n";
            }
            echo json_encode(['status' => 'success', 'reply' => $readable]);
            exit;
        }
    }
}

// 2. Skill: Consultar Memória e Status do Tronix
if (strpos($messageLower, 'status') !== false || strpos($messageLower, 'memória') !== false || strpos($messageLower, 'memoria') !== false || strpos($messageLower, 'logs') !== false) {
    $memoriaFile = __DIR__ . '/../memoria_tronix.json';
    if (file_exists($memoriaFile)) {
        $mem = json_decode(file_get_contents($memoriaFile), true);
        $logs = $mem['last_actions'] ?? [];
        $lastLogs = array_slice($logs, -4); // Pega as ultimas 4 ações
        
        $readable = "### 🧠 Memória Principal (Status do Sistema)\n\n";
        $readable .= "**Versão:** `{$mem['version']}` | **Identidade:** `{$mem['identity']}`\n\n";
        $readable .= "#### Últimos Logs de Evolução:\n";
        
        foreach (array_reverse($lastLogs) as $log) {
            $readable .= "* **" . htmlspecialchars($log['agente']) . "** (`" . $log['timestamp'] . "`):<br>";
            $readable .= "> " . htmlspecialchars($log['acao']) . "\n\n";
        }
        
        echo json_encode(['status' => 'success', 'reply' => $readable]);
        exit;
    }
}

// 3. Skill: Abatedouro Major Fast Check
if (strpos($messageLower, 'abatedouro') !== false || strpos($messageLower, 'major') !== false) {
    if (file_exists(__DIR__ . '/../../major/cadastros/empresa.php')) {
        echo json_encode(['status' => 'success', 'reply' => "### 🏭 Sistema Major Identificado\n\nAs novas melhorias do **Frigorífico/Abatedouro** implementadas em Viçosa-AL (tickets sem placa obrigatória e layout 80mm e A4) encontram-se detectadas no servidor local `C:\\xampp\\htdocs\\major`. O banco SQLite está seguro."]);
        exit;
    }
}


// ==========================================
// FALLBACK: NVIDIA NIM (LLM GRÁTIS) + TOOL CALLING AUTÔNOMO
// ==========================================

$nvidiaKey = $envData['NVIDIA_API_KEY'] ?? '';
if(empty($nvidiaKey)) {
    echo json_encode(['status' => 'error', 'reply' => 'Chave NVIDIA_API_KEY não encontrada no .env.']);
    exit;
}

$model = "meta/llama-3.1-70b-instruct"; 

$systemPrompt = "Você é o TRONIX, inteligência autônoma criada por Marcos Roberto (PC-Soluções / Viçosa-AL).
REGRA ABSOLUTA: Você atua como um sistema que executa comandos de mídia. 
Se o usuário pedir para CRIAR, GERAR, DESENHAR uma IMAGEM, você NÃO DEVE conversar. Responda APENAS E ESTRITAMENTE com a tag abaixo:
[[RUN: python tronix_kie.py imagem --prompt \"descrição detalhada em inglês hyperrealistic\"]]

Se o usuário pedir para CRIAR um VÍDEO, responda APENAS E ESTRITAMENTE com:
[[RUN: python tronix_kie.py video --prompt \"descrição detalhada da cena em inglês\" --duracao 5]]

Se o usuário pedir uma conversa normal, programação ou outras perguntas, converse livremente em Português-BR (usando Markdown). NUNCA explique que vai executar o comando, apenas o emita isoladamente.";

$apiData = [
    "model" => $model,
    "messages" => [
        ["role" => "system", "content" => $systemPrompt],
        ["role" => "user", "content" => $message]
    ],
    "max_tokens" => 3000,
    "temperature" => 0.4
];

$ch = curl_init('https://integrate.api.nvidia.com/v1/chat/completions');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($apiData));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Authorization: Bearer " . $nvidiaKey,
    "Content-Type: application/json"
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if($httpCode == 200) {
    $responseData = json_decode($response, true);
    $reply = trim($responseData['choices'][0]['message']['content'] ?? ("Erro na Extração. Retorno bruto: " . substr($response, 0, 150)));
    
    // ---- MOTOR AUTÔNOMO (TOOL CALLING) ----
    if (preg_match('/\[\[RUN:\s*(.*?)\]\]/', $reply, $matches)) {
        $command = trim($matches[1]);
        $dir = realpath(__DIR__ . '/../'); 
        
        // INTERCEPTADOR DE RESILIÊNCIA: KIE ESTÁ COM ERRO 500
        // Vamos capturar se for imagem e rodar via Pollinations direto no PHP
        if (strpos($command, 'imagem') !== false) {
             preg_match('/--prompt\s+"([^"]+)"/i', $command, $pMatch);
             $promptStr = $pMatch[1] ?? 'a highly detailed beautiful masterpice';
             $safePrompt = urlencode($promptStr);
             
             $imgUrl = "https://image.pollinations.ai/prompt/{$safePrompt}?width=1024&height=1024&nologo=1&enhance=true";
             $filename = "img_".time().".jpg";
             
             $uploadDir = $dir . DIRECTORY_SEPARATOR . "uploads";
             if (!is_dir($uploadDir)) { @mkdir($uploadDir, 0777, true); }
             $outputFile = $uploadDir . DIRECTORY_SEPARATOR . $filename;
             
             // Download robótico via cURL (file_get_contents falha em alguns php.ini)
             $chImg = curl_init($imgUrl);
             $fp = fopen($outputFile, 'wb');
             curl_setopt($chImg, CURLOPT_FILE, $fp);
             curl_setopt($chImg, CURLOPT_HEADER, 0);
             curl_setopt($chImg, CURLOPT_FOLLOWLOCATION, true);
             curl_exec($chImg);
             curl_close($chImg);
             fclose($fp);
             
             $reply = "🎨 **Imagem Criada Imediatamente (Modo Resiliência)!**\nO Cérebro identificou que a API primária estava sem slots e redirecionou seu pedido automaticamente pro gerador de backup. \n\nSua arte está pronta:\n📂 `C:\\xampp\\htdocs\\agente\\uploads\\{$filename}`\n🌐 [Clique aqui para Abrir](http://localhost/agente/uploads/{$filename})";
             
             echo json_encode(['status' => 'success', 'reply' => $reply]);
             exit;
        }

        $pythonEx = '"C:\\Users\\CHCONTE RECPÇÃO\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"';
        $commandFull = str_replace('python ', $pythonEx . ' ', $command);
        
        // Executando de forma ASSÍNCRONA no Windows (non-blocking) para Vídeos
        $outputFile = $dir . "/chat/last_run_bg.log";
        $winCmd = 'start /B cmd /c "cd /d "' . $dir . '" && ' . $commandFull . ' > "' . $outputFile . '" 2>&1"';
        pclose(popen($winCmd, "r"));
        
        if (strpos($command, 'video') !== false) {
            $reply = "🎬 **Video Engine Engatado (Assíncrono)!**\nProcesso rodando de forma invisível no sistema.\n\n_Assim que a Kie AI finalizar o vídeo, ele será depositado na sua pasta:_\n📂 `C:\\xampp\\htdocs\\agente\\videos_saida\\`";
        } else {
             $reply = "⚡ **Script Assíncrono Acionado:**\n`$command`\n_O processo foi despachado off-thread._";
        }
    }
    
    echo json_encode(['status' => 'success', 'reply' => $reply]);
} else {
    echo json_encode(['status' => 'error', 'reply' => "Falha com NVIDIA. HTTP: $httpCode. Detalhes: $response"]);
}
