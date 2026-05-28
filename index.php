<?php
$titulo = "Tronix Media Gallery";

function encontrar_imagem_origem($video_timestamp, $imagens) {
    $melhor_dist = PHP_INT_MAX;
    $melhor_img = null;
    foreach ($imagens as $img) {
        $dist = abs($img['timestamp'] - $video_timestamp);
        if ($dist < $melhor_dist) {
            $melhor_dist = $dist;
            $melhor_img = $img;
        }
    }
    return ($melhor_dist < 600) ? $melhor_img : null;
}

function tipo_super($nome) {
    if (str_contains($nome, '_super_voz.')) return 'voz';
    if (str_contains($nome, '_super.')) return 'texto';
    return null;
}

$imagens = [];
foreach (glob(__DIR__ . "/uploads/*.{png,jpg,jpeg}", GLOB_BRACE) as $arq) {
    $nome = basename($arq);
    preg_match('/\b(\d{10})\b/', $nome, $matches);
    $imagens[] = [
        "path" => "uploads/" . $nome,
        "nome" => $nome,
        "timestamp" => $matches[1] ?? filemtime($arq),
    ];
}

$pastas = ["videos_saida", "uploads/videos"];
$videos = [];
foreach ($pastas as $pasta) {
    foreach (glob(__DIR__ . "/$pasta/*.mp4") as $arq) {
        $nome = basename($arq);
        preg_match('/(\d{10})/', $nome, $matches);
        $ts = (int)($matches[1] ?? filemtime($arq));
        $videos[] = [
            "path" => "$pasta/$nome",
            "nome" => $nome,
            "tamanho" => filesize($arq),
            "data" => date("d/m/Y H:i", filemtime($arq)),
            "timestamp" => $ts,
            "imagem" => encontrar_imagem_origem($ts, $imagens),
        ];
    }
}

rsort($videos);
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $titulo ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0f0f1a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 2rem;
            text-align: center;
            border-bottom: 2px solid #e63946;
        }
        header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #e63946, #f4a261);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: 2px;
        }
        header p {
            color: #888;
            margin-top: .5rem;
            font-size: 1.1rem;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stats {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .stat-card {
            background: #1a1a2e;
            padding: 1rem 2rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #2a2a4a;
        }
        .stat-card .num {
            font-size: 2rem;
            font-weight: 700;
            color: #e63946;
        }
        .stat-card .label {
            font-size: .85rem;
            color: #888;
            margin-top: .25rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 1.5rem;
        }
        .card {
            background: #1a1a2e;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #2a2a4a;
            transition: transform .2s, box-shadow .2s;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(230, 57, 70, .15);
        }
        .media-row {
            display: flex;
            gap: 0;
            background: #000;
        }
        .media-row > * {
            flex: 1;
            width: 50%;
            aspect-ratio: 1/1;
            object-fit: cover;
            display: block;
        }
        .media-row video {
            border-left: 2px solid #e63946;
        }
        .media-row .img-wrap {
            position: relative;
            overflow: hidden;
        }
        .media-row .img-wrap img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .media-row .badge {
            position: absolute;
            top: 8px;
            font-size: .7rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .badge-original { left: 8px; background: #264653; color: #e9c46a; }
        .badge-animado { right: 8px; background: #e63946; color: #fff; }
        .badge-super { right: 8px; background: #f4a261; color: #1a1a2e; }
        .arrow-divider {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            color: #e63946;
            text-shadow: 0 0 12px rgba(230,57,70,.6);
            z-index: 2;
            pointer-events: none;
        }
        .card-body {
            padding: 1rem 1.25rem 1.25rem;
        }
        .card-body h3 {
            font-size: .85rem;
            font-weight: 600;
            color: #f0f0f0;
            word-break: break-all;
            margin-bottom: .5rem;
        }
        .card-body .meta {
            display: flex;
            justify-content: space-between;
            font-size: .8rem;
            color: #888;
            margin-bottom: .75rem;
        }
        .card-body .btn-group {
            display: flex;
            gap: .5rem;
        }
        .btn {
            flex: 1;
            padding: .6rem 1rem;
            border: none;
            border-radius: 8px;
            font-size: .85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            transition: opacity .2s;
        }
        .btn:hover { opacity: .85; }
        .btn-play { background: #e63946; color: #fff; }
        .btn-dl { background: #2a2a4a; color: #e0e0e0; }
        .btn-open { background: #2d6a4f; color: #fff; }
        .btn-n8n { background: #e63946; color: #fff; }
        .empty {
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            color: #666;
        }
        .empty h2 { font-size: 2rem; margin-bottom: 1rem; }
        .empty p { font-size: 1.1rem; }
        .sem-imagem {
            display: flex; align-items: center; justify-content: center;
            width: 50%; background: #111; color: #444;
            font-size: .85rem; text-align: center; padding: 1rem;
        }
        .status-bar {
            display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
            margin: 1rem auto 0; max-width: 600px;
        }
        .status-item {
            background: #1a1a2e; border: 1px solid #2a2a4a;
            padding: .4rem 1rem; border-radius: 20px;
            font-size: .75rem; color: #aaa;
        }
        .status-item.on { border-color: #2d6a4f; color: #52b788; }
        footer {
            text-align: center;
            padding: 2rem;
            color: #444;
            font-size: .85rem;
        }
        @media (max-width: 600px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <h1>Tronix Media</h1>
        <p>Pipeline de animacao com IA — Multi-agente CrewAI + n8n</p>
        <div class="status-bar">
            <span class="status-item on">CrewAI 1.14.4</span>
            <span class="status-item on">n8n 2.20.6</span>
            <span class="status-item on">Langflow 1.9.2</span>
            <span class="status-item on">SQLite</span>
            <span class="status-item">v1.2.0</span>
        </div>
    </header>
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="num"><?= count($videos) ?></div>
                <div class="label">Vídeos Gerados</div>
            </div>
            <div class="stat-card">
                <div class="num">
                    <?php
                    $total = array_sum(array_column($videos, 'tamanho'));
                    echo $total > 1e6 ? round($total / 1e6, 1) . ' MB' : round($total / 1e3, 1) . ' KB';
                    ?>
                </div>
                <div class="label">Espaço Ocupado</div>
            </div>
            <div class="stat-card">
                <div class="num"><?= count($imagens) ?></div>
                <div class="label">Imagens em Uploads</div>
            </div>
        </div>
        <div style="text-align:center;margin-bottom:2rem;display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
            <a href="http://localhost:5678" target="_blank" class="btn btn-n8n" style="display:inline-block;width:auto;padding:.6rem 2rem;">n8n</a>
            <a href="http://localhost:3000" target="_blank" class="btn btn-open" style="display:inline-block;width:auto;padding:.6rem 2rem;text-decoration:none;">Dify</a>
            <a href="http://localhost:9380" target="_blank" class="btn btn-play" style="display:inline-block;width:auto;padding:.6rem 2rem;text-decoration:none;">RAGFlow</a>
        </div>
        <div class="grid">
            <?php if (empty($videos)): ?>
                <div class="empty">
                    <h2>📹 Nenhum vídeo ainda</h2>
                    <p>Execute o pipeline Tronix: <code>python produtor.py "seu tema"</code></p>
                </div>
            <?php else: ?>
                <?php foreach ($videos as $v): ?>
                    <div class="card">
                        <?php
                        $t_super = tipo_super($v['nome']);
                        $origem_video = $t_super
                            ? str_replace(['_super_voz.mp4', '_super.mp4'], '.mp4', $v['path'])
                            : null;
                        $badge_label = match ($t_super) {
                            'voz' => 'Super + Voz',
                            'texto' => 'Super Editor',
                            default => 'Animado'
                        };
                        $badge_class = match ($t_super) {
                            'voz' => 'badge-super',
                            'texto' => 'badge-super',
                            default => 'badge-animado'
                        };
                        ?>
                        <div class="media-row">
                            <?php if ($v['imagem']): ?>
                                <div class="img-wrap">
                                    <img src="<?= htmlspecialchars($v['imagem']['path']) ?>" alt="Original" loading="lazy">
                                    <span class="badge badge-original">Original</span>
                                    <span class="arrow-divider">→</span>
                                </div>
                            <?php else: ?>
                                <div class="sem-imagem">Imagem<br>não encontrada</div>
                            <?php endif; ?>
                            <video src="<?= htmlspecialchars($v['path']) ?>" preload="metadata" controls></video>
                            <span class="badge <?= $badge_class ?>" style="position:absolute;top:8px;right:8px;z-index:2;"><?= $badge_label ?></span>
                        </div>
                        <div class="card-body">
                            <h3><?= htmlspecialchars($v['nome']) ?></h3>
                            <div class="meta">
                                <span><?= $v['data'] ?></span>
                                <span><?= round($v['tamanho'] / 1e6, 2) ?> MB</span>
                            </div>
                            <div class="btn-group">
                                <a href="<?= htmlspecialchars($v['path']) ?>" class="btn btn-play" target="_blank">▶ Assistir</a>
                                <a href="<?= htmlspecialchars($v['path']) ?>" class="btn btn-dl" download>⬇ Baixar</a>
                                <?php if ($v['imagem'] && !$t_super): ?>
                                    <a href="<?= htmlspecialchars($v['imagem']['path']) ?>" class="btn btn-open" target="_blank">🖼 Original</a>
                                <?php endif; ?>
                                <?php if ($t_super && $origem_video && file_exists(__DIR__ . '/' . $origem_video)): ?>
                                    <a href="<?= htmlspecialchars($origem_video) ?>" class="btn btn-open" target="_blank">🎬 Base</a>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>
    <footer style="display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;">
        <span>PCsolucoes — Vicosa, AL</span>
        <span>Tronix v1.1.0</span>
        <a href="dashboard.php" style="color:#f4a261;text-decoration:none;">Dashboard</a>
        <a href="http://localhost:5678" target="_blank" style="color:#e63946;text-decoration:none;">n8n</a>
    </footer>
</body>
</html>
