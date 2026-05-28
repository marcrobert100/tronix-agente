<?php
// ============================================
// PCsolucoes - API de Status do Escritorio Virtual
// Comunicacao em tempo real entre opencode e escritorio
// ============================================

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS, DELETE');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$arquivo_status = __DIR__ . '/status.json';
$arquivo_log = __DIR__ . '/logs/atividades_' . date('Y-m-d') . '.txt';

if (!is_dir(__DIR__ . '/logs')) {
    mkdir(__DIR__ . '/logs', 0755, true);
}

// Inicializa status.json se nao existir
if (!file_exists($arquivo_status)) {
    $status_inicial = [
        'equipe' => [
            'gestor' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'designer' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'programador' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'atendente' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'secretaria' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => '']
        ],
        'atividades' => [],
        'projetoAtual' => '',
        'ultimaAtualizacao' => date('Y-m-d H:i:s')
    ];
    file_put_contents($arquivo_status, json_encode($status_inicial, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

// ========== GET: Retorna status atual ==========
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $conteudo = file_get_contents($arquivo_status);
    $status = json_decode($conteudo, true);
    
    if (!$status) {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Erro ao ler status']);
        exit;
    }
    
    echo json_encode(['status' => 'ok', 'dados' => $status]);
    exit;
}

// ========== POST: Atualiza status ==========
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $json = file_get_contents('php://input');
    $dados = json_decode($json, true);

    if (!$dados) {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Dados invalidos']);
        exit;
    }

    $status_atual = json_decode(file_get_contents($arquivo_status), true);
    if (!$status_atual) {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Erro ao ler status atual']);
        exit;
    }

    if (isset($dados['agente']) && isset($dados['acao'])) {
        $agente = $dados['agente'];
        $acao = $dados['acao'];
        $tarefa = isset($dados['tarefa']) ? $dados['tarefa'] : '';
        $detalhes = isset($dados['detalhes']) ? $dados['detalhes'] : '';
        $tipo = isset($dados['tipo']) ? $dados['tipo'] : 'info';

        $mapa = [
            'gestor' => 'gestor',
            'designer' => 'designer',
            'programador' => 'programador',
            'atendente' => 'atendente',
            'secretaria' => 'secretaria',
            'secretária' => 'secretaria'
        ];

        $agente_lower = strtolower($agente);
        $chave = isset($mapa[$agente_lower]) ? $mapa[$agente_lower] : null;

        if ($chave && isset($status_atual['equipe'][$chave])) {
            $status_atual['equipe'][$chave]['status'] = $acao === 'finalizou' ? 'ocioso' : 'trabalhando';
            $status_atual['equipe'][$chave]['tarefa'] = $tarefa;
            $status_atual['equipe'][$chave]['ultimaAcao'] = $detalhes ?: $acao;
            $status_atual['equipe'][$chave]['timestamp'] = date('Y-m-d H:i:s');
        }

        $atividade = [
            'timestamp' => date('Y-m-d H:i:s'),
            'agente' => $agente,
            'acao' => $acao,
            'detalhes' => $detalhes,
            'tarefa' => $tarefa,
            'tipo' => $tipo
        ];

        $status_atual['atividades'][] = $atividade;
        if (count($status_atual['atividades']) > 100) {
            $status_atual['atividades'] = array_slice($status_atual['atividades'], -100);
        }

        $status_atual['ultimaAtualizacao'] = date('Y-m-d H:i:s');

        if (isset($dados['projeto'])) {
            $status_atual['projetoAtual'] = $dados['projeto'];
        }

        file_put_contents($arquivo_status, json_encode($status_atual, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

        $linha_log = date('Y-m-d H:i:s') . " | $agente | $acao | " . ($detalhes ?: $tarefa) . " [$tipo]" . PHP_EOL;
        file_put_contents($arquivo_log, $linha_log, FILE_APPEND | LOCK_EX);

        $novoStatus = null;
        if ($chave && isset($status_atual['equipe'][$chave])) {
            $novoStatus = $status_atual['equipe'][$chave];
        }

        echo json_encode([
            'status' => 'ok',
            'mensagem' => "Status de $agente atualizado",
            'agente' => $chave,
            'novoStatus' => $novoStatus
        ]);
        exit;
    }

    echo json_encode(['status' => 'erro', 'mensagem' => 'Dados insuficientes']);
    exit;
}

// ========== DELETE: Reseta status ==========
if ($_SERVER['REQUEST_METHOD'] === 'DELETE') {
    $status_reset = [
        'equipe' => [
            'gestor' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'designer' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'programador' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'atendente' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => ''],
            'secretaria' => ['status' => 'ocioso', 'tarefa' => '', 'ultimaAcao' => 'Aguardando comandos', 'timestamp' => '']
        ],
        'atividades' => [],
        'projetoAtual' => '',
        'ultimaAtualizacao' => date('Y-m-d H:i:s')
    ];
    file_put_contents($arquivo_status, json_encode($status_reset, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode(['status' => 'ok', 'mensagem' => 'Status resetado']);
    exit;
}

http_response_code(405);
echo json_encode(['status' => 'erro', 'mensagem' => 'Metodo nao permitido']);
?>
