<?php
try {
    $db = new PDO("sqlite:C:/xampp/htdocs/agente/tronix.db");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Contagem para o gráfico
    $res = $db->query("SELECT status, COUNT(*) as qtd FROM tarefas GROUP BY status");
    $dados = ["sucesso" => 0, "pendente" => 0, "executando" => 0];
    while($row = $res->fetch(PDO::FETCH_ASSOC)) {
        $st = strtolower($row['status']);
        if(isset($dados[$st])) $dados[$st] = $row['qtd'];
    }
    
    // Busca as colunas reais para evitar o erro "Undefined Index"
    $ultimas = $db->query("SELECT * FROM tarefas ORDER BY id DESC LIMIT 5")->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) { $erro = $e->getMessage(); }
?>
<!DOCTYPE html>
<html>
<head>
    <title>Tronix v1.3 - PCsoluções</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; text-align: center; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        .card { background: #1e1e1e; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #252525; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; border-bottom: 1px solid #333; text-align: left; }
        th { background: #333; color: #2ecc71; }
        .status-badge { padding: 4px 10px; border-radius: 4px; font-size: 0.75em; font-weight: bold; text-transform: uppercase; }
        .sucesso { background: #2ecc71; color: #121212; }
        .pendente { background: #f1c40f; color: #121212; }
        .executando { background: #3498db; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 Monitoramento Tronix</h1>
            <div style="width: 250px; margin: auto;"><canvas id="graficoStatus"></canvas></div>
        </div>

        <div class="card">
            <h3>📂 Últimas Atividades</h3>
            <table>
                <thead><tr><th>ID</th><th>Título/Tema</th><th>Status</th></tr></thead>
                <tbody>
                    <?php foreach($ultimas as $t): 
                        // Tenta encontrar o nome do tema em várias colunas possíveis
                        $displayTema = $t['tema'] ?? $t['topic'] ?? $t['prompt'] ?? $t['titulo'] ?? "Vídeo #".$t['id'];
                    ?>
                    <tr>
                        <td>#<?= $t['id'] ?></td>
                        <td><?= $displayTema ?></td>
                        <td><span class="status-badge <?= strtolower($t['status']) ?>"><?= $t['status'] ?></span></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
    <script>
        const ctx = document.getElementById('graficoStatus').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Sucesso', 'Pendente', 'Executando'],
                datasets: [{
                    data: [<?= $dados['sucesso'] ?>, <?= $dados['pendente'] ?>, <?= $dados['executando'] ?>],
                    backgroundColor: ['#2ecc71', '#f1c40f', '#3498db'],
                    borderWidth: 0
                }]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: 'white', padding: 15 } } } }
        });
    </script>
</body>
</html>
