<?php
// ============================================
// PCsolucoes - API de Logs do Escritorio Virtual
// Programador: Programador PCsolucoes
// Salva logs de atividades em arquivo .txt
// ============================================

// Configuracao de CORS para aceitar requisicoes do frontend
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Responde OPTIONS (preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Pasta onde os logs serao salvos
$pasta_logs = __DIR__ . '/logs/';

// Cria a pasta se nao existir
if (!is_dir($pasta_logs)) {
    mkdir($pasta_logs, 0755, true);
}

// Arquivo de log do dia atual
$arquivo_log = $pasta_logs . 'atividades_' . date('Y-m-d') . '.txt';

// ========== GET: Retorna os ultimos logs ==========
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $limite = isset($_GET['limite']) ? intval($_GET['limite']) : 50;

    if (!file_exists($arquivo_log)) {
        echo json_encode(['status' => 'ok', 'logs' => [], 'total' => 0]);
        exit;
    }

    $linhas = file($arquivo_log, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $linhas = array_reverse($linhas); // Mais recentes primeiro
    $linhas = array_slice($linhas, 0, $limite);

    $logs = [];
    foreach ($linhas as $linha) {
        $parts = explode(' | ', $linha, 4);
        if (count($parts) >= 4) {
            $logs[] = [
                'timestamp' => $parts[0],
                'agente' => $parts[1],
                'acao' => $parts[2],
                'detalhes' => $parts[3]
            ];
        }
    }

    echo json_encode([
        'status' => 'ok',
        'logs' => $logs,
        'total' => count(file($arquivo_log, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES))
    ]);
    exit;
}

// ========== POST: Salva novo log ==========
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $json = file_get_contents('php://input');
    $dados = json_decode($json, true);

    if (!$dados) {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Dados invalidos']);
        exit;
    }

    // Campos obrigatorios
    $agente = isset($dados['agente']) ? trim($dados['agente']) : 'Sistema';
    $acao = isset($dados['acao']) ? trim($dados['acao']) : 'acao';
    $detalhes = isset($dados['detalhes']) ? trim($dados['detalhes']) : '';
    $tipo = isset($dados['tipo']) ? trim($dados['tipo']) : 'info'; // info, tarefa, alerta, sucesso

    // Monta a linha do log
    $timestamp = date('Y-m-d H:i:s');
    $linha = "$timestamp | $agente | $acao | $detalhes [$tipo]" . PHP_EOL;

    // Salva no arquivo
    $salvo = file_put_contents($arquivo_log, $linha, FILE_APPEND | LOCK_EX);

    if ($salvo) {
        echo json_encode([
            'status' => 'ok',
            'mensagem' => 'Log salvo com sucesso',
            'arquivo' => basename($arquivo_log)
        ]);
    } else {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Erro ao salvar log']);
    }
    exit;
}

// ========== Metodo nao permitido ==========
http_response_code(405);
echo json_encode(['status' => 'erro', 'mensagem' => 'Metodo nao permitido']);
?>
