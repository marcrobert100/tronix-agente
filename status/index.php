<?php
// TRONIX SYSTEMS STATUS - painel unico de monitoramento
header('Content-Type: text/html; charset=utf-8');

$SISTEMAS = [
    ['Apache/XAMPP',        'Web local',     80,    'http://localhost/agente/infoengine/', 'xampp'],
    ['MySQL',               'Banco central', 3306, 'http://localhost/phpmyadmin/',         'db'],
    ['Tronix AI',           'Assistant',     7000, 'http://localhost:7000',                'py'],
    ['API Gateway',         'Central API',   8081, 'http://localhost:8081/health',         'py'],
    ['n8n',                 'Automacao',     5678, 'http://localhost:5678',                'node'],
    ['Langflow',            'Agentes visual',7860, 'http://localhost:7860',                'py'],
    ['Dify',                'AI apps',       3000, 'http://localhost:3000',                'docker'],
    ['RAGFlow',             'RAG engine',    9380, 'http://localhost:9380',                'docker'],
    ['NCA-ToolKit',         'Video tools',   8080, 'http://localhost:8080',                'py'],
    ['Moto S3',             'S3 mock',       9090, 'http://localhost:9090',                'py'],
    ['MinIO Console',       'S3 real',       9001, 'http://localhost:9001',                'docker'],
    ['llm-mem',             'Memoria HTTP',  37777,'http://localhost:37777',               'py'],
    ['Jellyfin',            'Midia/Stream',  8096, 'http://localhost:8096',                'homelab'],
    ['Radarr',              'Filmes',        7878, 'http://localhost:7878',                'homelab'],
    ['Sonarr',              'Series',        8989, 'http://localhost:8989',                'homelab'],
    ['Prowlarr',            'Indexers',      9696, 'http://localhost:9696',                'homelab'],
    ['qBittorrent',         'Torrent',       null, 'http://localhost:8080',                'homelab'],
    ['Bazarr',              'Legendas',      6767, 'http://localhost:6767',                'homelab'],
    ['Ombi',                'Pedidos',       3579, 'http://localhost:3579',                'homelab'],
    ['FlareSolverr',        'Proxy',         8191, 'http://localhost:8191',                'homelab'],
];

function checar($porta) {
    if ($porta === null) return false;
    $sock = @fsockopen('127.0.0.1', $porta, $errno, $errstr, 0.2);
    if ($sock) { fclose($sock); return true; }
    return false;
}

function stats() {
    $out = [];
    // MySQL espelho
    try {
        $m = new PDO('mysql:host=127.0.0.1;dbname=tronix_system;charset=utf8mb4', 'root', '', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
        $out['mysql_logs'] = (int) $m->query('SELECT COUNT(*) FROM logs_evolucao')->fetchColumn();
        $out['mysql_ult'] = $m->query('SELECT MAX(timestamp) FROM logs_evolucao')->fetchColumn();
    } catch (Exception $e) { $out['mysql'] = 'off'; }
    // SQLite local
    try {
        $s = new PDO('sqlite:C:/xampp/htdocs/agente/tronix.db');
        $out['sqlite_reflexoes'] = (int) $s->query('SELECT COUNT(*) FROM reflexoes')->fetchColumn();
        $out['sqlite_conteudo'] = (int) $s->query('SELECT COUNT(*) FROM conteudo')->fetchColumn();
        $sqlite_ult = $s->query('SELECT MAX(data) FROM reflexoes')->fetchColumn();
        $out['sqlite_ult'] = $sqlite_ult ?: 'nunca';
    } catch (Exception $e) { $out['sqlite'] = 'off'; }
    return $out;
}

// Endpoint JSON p/ atualizacao viva
if (isset($_GET['q'])) {
    $res = [];
    foreach ($SISTEMAS as $s) {
        $up = checar($s[1] == 'qBittorrent' ? 8080 : $s[2]);
        $res[] = [
            'nome' => $s[0],
            'up'   => $up && $s[1] != 'qBittorrent' ? $up : ($s[0] == 'qBittorrent' ? $up : $up),
        ];
    }
    $res[] = ['nome' => '__stats__', 'up' => stats()];
    header('Content-Type: application/json');
    echo json_encode($res, JSON_UNESCAPED_UNICODE);
    exit;
}

$status = [];
foreach ($SISTEMAS as $s) {
    $status[] = ['nome' => $s[0], 'up' => checar($s[1] == 'qBittorrent' ? 8080 : $s[2])];
}
$stats = stats();
$up = count(array_filter($status, fn($x) => $x['up']));
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TRONIX Systems Status</title>
<style>
:root{--bg:#0b0b10;--card:#15151d;--border:#262633;--up:#22c55e;--down:#ef4444;--acc:#06b6d4;--gold:#eab308;--txt:#e5e7eb;--dim:#6b7280;}
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,'Courier New',monospace;}
body{background:var(--bg);color:var(--txt);padding:24px;min-height:100vh;}
h1{font-size:20px;letter-spacing:2px;margin-bottom:6px;}
h1 .acc{color:var(--acc);}
.sub{color:var(--dim);font-size:12px;margin-bottom:18px;}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;align-items:center;}
.pill{font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:999px;color:var(--dim);}
.pill b{color:var(--txt);}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.up{background:var(--up);box-shadow:0 0 8px var(--up);}
.down{background:var(--down);box-shadow:0 0 8px var(--down);}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;}
.card.off{opacity:.55;}
.nome{font-size:13px;font-weight:bold;margin-bottom:2px;}
.tipo{font-size:10px;color:var(--dim);letter-spacing:1px;text-transform:uppercase;}
.card a{color:var(--acc);font-size:12px;text-decoration:none;display:inline-block;margin-top:8px;word-break:break-all;}
.card a:hover{text-decoration:underline;}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:20px;}
.box{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px;}
.box .k{font-size:10px;color:var(--dim);letter-spacing:1px;text-transform:uppercase;}
.box .v{font-size:16px;color:var(--gold);margin-top:4px;}
.rodape{margin-top:22px;color:var(--dim);font-size:11px;text-align:center;}
.foot a{color:var(--acc);text-decoration:none;}
@media(max-width:600px){body{padding:12px;}h1{font-size:16px;}}
</style>
</head>
<body>
<h1>TRONIX <span class="acc">SYSTEMS</span> STATUS</h1>
<div class="sub">Viçosa-AL &middot; atualização automática a cada 15s &middot; última checagem AGORA</div>
<div class="bar">
  <span class="pill"><b id="upCount"></b>/<?= count($SISTEMAS) ?> online</span>
  <span class="pill">Gateway <b><?= ($stats['mysql_logs'] ?? '?') ?></b> logs evolução</span>
  <span class="pill">SQLite <b><?= $stats['sqlite_reflexoes'] ?? '?' ?></b> reflexões</span>
</div>

<div class="grid" id="grid">
<?php foreach ($SISTEMAS as $i => $s): $ok = checar($s[1] == 'qBittorrent' ? 8080 : $s[2]); ?>
  <div class="card <?= $ok ? '' : 'off' ?>" data-nome="<?= htmlspecialchars($s[0]) ?>">
    <span class="dot <?= $ok ? 'up' : 'down' ?>"></span>
    <div class="nome"><?= htmlspecialchars($s[0]) ?></div>
    <div class="tipo"><?= htmlspecialchars($s[1]) ?></div>
    <?php if ($ok): ?>
      <a href="<?= htmlspecialchars($s[3]) ?>" target="_blank">abrir  ↗</a>
    <?php endif; ?>
  </div>
<?php endforeach; ?>
</div>

<div class="stats">
  <div class="box"><div class="k">Reflexões TRONIX (sqlite)</div><div class="v"><?= $stats['sqlite_reflexoes'] ?? 'off' ?></div></div>
  <div class="box"><div class="k">Última reflexão</div><div class="v"><?= $stats['sqlite_ult'] ?? '—' ?></div></div>
  <div class="box"><div class="k">Logs evolução (mysql)</div><div class="v"><?= $stats['mysql_logs'] ?? 'off' ?></div></div>
  <div class="box"><div class="k">Último log evolução</div><div class="v"><?= $stats['mysql_ult'] ?? '—' ?></div></div>
</div>

<div class="rodape">
  TRONIX 1.6.0 &middot; <a href="http://localhost:8081/health">Gateway API</a> &middot;
  <a href="http://localhost/agente/infoengine/">InfoEngine</a> &middot;
  <a href="https://github.com/anomalyco/opencode">opencode</a>
</div>

<script>
const LINKS = <?= json_encode(array_column($SISTEMAS, 3)) ?>;
const NOMES = <?= json_encode(array_map(fn($s) => $s[0], $SISTEMAS)) ?>;
async function atualiza() {
  try {
    const r = await fetch(location.pathname + '?q=1&t=' + Date.now());
    const dados = await r.json();
    let nUp = 0;
    dados.forEach((d) => {
      if (d.nome === '__stats__') {
        if (d.up.sqlite_reflexoes !== undefined) {
          const boxes = document.querySelectorAll('.stats .box .v');
          if (boxes[0]) boxes[0].textContent = d.up.sqlite_reflexoes;
          if (boxes[1]) boxes[1].textContent = d.up.sqlite_ult || '—';
          if (boxes[2]) boxes[2].textContent = d.up.mysql_logs;
          if (boxes[3]) boxes[3].textContent = d.up.mysql_ult || '—';
        }
        return;
      }
      const card = document.querySelector('.card[data-nome="' + d.nome + '"]');
      if (!card) return;
      const idx = NOMES.indexOf(d.nome);
      const dot = card.querySelector('.dot');
      const a = card.querySelector('a');
      card.classList.toggle('off', !d.up);
      dot.className = 'dot ' + (d.up ? 'up' : 'down');
      a.textContent = d.up && LINKS[idx] ? 'abrir  ↗' : (LINKS[idx] ? LINKS[idx] : '');
      a.href = d.up && LINKS[idx] ? LINKS[idx] : '#';
      if (d.up) nUp++;
    });
    document.getElementById('upCount').textContent = nUp;
  } catch (e) {}
}
atualiza();
setInterval(atualiza, 15000);
</script>
</body>
</html>
