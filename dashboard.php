<?php
$db_path = __DIR__ . '/tronix.db';
try {
    $db = new PDO("sqlite:$db_path");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stats = $db->query("SELECT COUNT(*) as total, SUM(CASE WHEN status_post='pendente' THEN 1 ELSE 0 END) as pendentes, SUM(CASE WHEN status_post='postado' THEN 1 ELSE 0 END) as postados FROM conteudo")->fetch(PDO::FETCH_ASSOC);
    $hoje = $db->query("SELECT COUNT(*) as total FROM conteudo WHERE DATE(data_criacao) = DATE('now')")->fetch(PDO::FETCH_ASSOC);
    $log_count = $db->query("SELECT COUNT(*) as total FROM pipeline_log")->fetch(PDO::FETCH_ASSOC);
    $db_human = "Online (" . round(filesize($db_path)/1024) . " KB)";
} catch (Exception $e) {
    $stats = ['total'=>0,'pendentes'=>0,'postados'=>0];
    $hoje = ['total'=>0];
    $log_count = ['total'=>0];
    $db_human = "Erro: " . $e->getMessage();
}
$version = "1.4.0";
$core = json_decode(file_get_contents(__DIR__.'/tronix_core.json'), true);
$agentes = $core['multi_agente']['agentes'] ?? [];
$gateway_v2 = file_exists(__DIR__.'/dashboard_v2.html');
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tronix v<?= $version ?> - PC Soluções</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',system-ui,sans-serif; background:#0d1117; color:#e6edf3; }
        .topbar { background:linear-gradient(135deg,#0d1117,#161b22); border-bottom:1px solid #30363d; padding:12px 24px; display:flex; align-items:center; justify-content:space-between; }
        .topbar h1 { font-size:1.2rem; }
        .topbar h1 span { color:#58a6ff; }
        .topbar .links { display:flex; gap:12px; }
        .topbar .links a { color:#58a6ff; text-decoration:none; font-size:0.85rem; padding:4px 12px; border:1px solid #30363d; border-radius:6px; }
        .topbar .links a:hover { background:#1c2128; }
        .container { max-width:1200px; margin:0 auto; padding:20px; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:20px; }
        .card { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; }
        .card .label { font-size:0.75rem; color:#8b949e; text-transform:uppercase; }
        .card .value { font-size:1.8rem; font-weight:700; margin-top:4px; }
        .card .value.blue { color:#58a6ff; }
        .card .value.green { color:#3fb950; }
        .card .value.yellow { color:#d29922; }
        h2 { font-size:1rem; color:#8b949e; text-transform:uppercase; letter-spacing:.5px; margin:16px 0 12px; }
        .agent-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:8px; }
        .agent-chip { background:#21262d; border:1px solid #30363d; border-radius:6px; padding:8px 12px; font-size:0.8rem; text-align:center; }
        .agent-chip .name { color:#58a6ff; font-weight:600; }
        .agent-chip .count { color:#8b949e; font-size:0.7rem; margin-top:2px; }
        .info-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
        .info-item { display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #21262d; font-size:0.85rem; }
        .info-item .label { color:#8b949e; }
        .info-item .value { color:#e6edf3; }
        .alert { background:#d2992222; border:1px solid #d2992244; border-radius:8px; padding:16px; margin-bottom:16px; font-size:0.9rem; }
        .alert a { color:#58a6ff; }
        @media (max-width:600px) { .info-grid { grid-template-columns:1fr; } }
    </style>
</head>
<body>
    <div class="topbar">
        <h1><span>Tronix</span> v<?= $version ?> · PC Soluções</h1>
        <div class="links">
            <?php if ($gateway_v2): ?><a href="dashboard_v2.html">Dashboard V2 (Tempo Real)</a><?php endif; ?>
            <a href="http://localhost:8081/health" target="_blank">Gateway</a>
            <a href="http://localhost:8081/versao" target="_blank">Versão</a>
        </div>
    </div>
    <div class="container">
        <?php if ($gateway_v2): ?>
        <div class="alert">
            Novo dashboard disponível: <a href="dashboard_v2.html">Dashboard V2</a> com WebSocket em tempo real, gráficos dinâmicos e monitoramento ao vivo.
        </div>
        <?php endif; ?>

        <div class="grid">
            <div class="card"><div class="label">Conteudos</div><div class="value blue"><?= $stats['total'] ?? 0 ?></div></div>
            <div class="card"><div class="label">Pendentes</div><div class="value yellow"><?= $stats['pendentes'] ?? 0 ?></div></div>
            <div class="card"><div class="label">Postados</div><div class="value green"><?= $stats['postados'] ?? 0 ?></div></div>
            <div class="card"><div class="label">Hoje</div><div class="value"><?= $hoje['total'] ?? 0 ?></div></div>
        </div>

        <h2>🤖 Agentes (<?= count($agentes) ?>)</h2>
        <div class="agent-grid">
            <?php foreach ($agentes as $a): ?>
            <div class="agent-chip"><div class="name"><?= htmlspecialchars($a) ?></div></div>
            <?php endforeach; ?>
        </div>

        <h2>⚙️ Sistema</h2>
        <div class="card info-grid">
            <div class="info-item"><span class="label">Gateway</span><span class="value">FastAPI v2.0.0 (porta 8081)</span></div>
            <div class="info-item"><span class="label">WebSocket</span><span class="value">ws://localhost:8081/ws</span></div>
            <div class="info-item"><span class="label">MCP Server</span><span class="value">11 ferramentas</span></div>
            <div class="info-item"><span class="label">Banco</span><span class="value"><?= $db_human ?></span></div>
            <div class="info-item"><span class="label">Pipeline Logs</span><span class="value"><?= $log_count['total'] ?? 0 ?></span></div>
            <div class="info-item"><span class="label">Framework</span><span class="value">CrewAI + n8n</span></div>
            <div class="info-item"><span class="label">Memória</span><span class="value">JSON + SQLite archive</span></div>
            <div class="info-item"><span class="label">TRAE SOLO</span><span class="value">.trae/mcp.json ativo</span></div>
        </div>

        <h2>📋 Comandos Úteis</h2>
        <div class="card" style="font-family:monospace; font-size:0.8rem; line-height:1.8;">
            <div>python tronix_check.py <span style="color:#8b949e;"># Verificar sistema</span></div>
            <div>python api_gateway.py <span style="color:#8b949e;"># Iniciar gateway (porta 8081)</span></div>
            <div>python tronix_mcp_server.py <span style="color:#8b949e;"># Iniciar MCP Server (stdio)</span></div>
            <div>python tronix_memoria_manager.py <span style="color:#8b949e;"># Arquivar memória</span></div>
            <div>python tronix_crew.py <span style="color:#8b949e;"># Iniciar time multi-agente</span></div>
        </div>

        <h2>🎨 Santinho Generator</h2>
        <div class="card info-grid">
            <div class="info-item"><span class="label">Modelos</span><span class="value">14 templates visuais</span></div>
            <div class="info-item"><span class="label">Resolução</span><span class="value">300 DPI · 70x100mm</span></div>
            <div class="info-item"><span class="label">Grid A4</span><span class="value">6/8/9/10 por folha</span></div>
            <div class="info-item"><span class="label">Frente e Verso</span><span class="value">Sim · com QR Code</span></div>
            <div class="info-item"><span class="label">Lote</span><span class="value">Até 10.000 santinhos</span></div>
            <div class="info-item"><span class="label">Interface</span><a href="santinho_generator/" style="color:#ff3366;">Abrir editor visual →</a></div>
        </div>
    </div>
</body>
</html>
