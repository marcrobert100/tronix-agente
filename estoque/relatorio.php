<?php
// ============================================
// PCsolucoes - Relatorio de Estoque
// Programador: Programador PCsolucoes
// ============================================

require_once 'includes/conexao.php';
require_once 'includes/funcoes.php';

// Buscar produtos com categoria
$sql = "SELECT p.*, c.nome as categoria_nome 
        FROM produtos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        WHERE p.ativo = 1
        ORDER BY p.nome ASC";
$produtos = $pdo->query($sql)->fetchAll();

// Estatisticas gerais
$total_produtos = count($produtos);
$total_itens = 0;
$total_custo = 0;
$total_venda = 0;
$estoque_baixo = 0;
$sem_estoque = 0;

foreach ($produtos as $p) {
    $total_itens += $p['quantidade'];
    $total_custo += $p['preco_custo'] * $p['quantidade'];
    $total_venda += $p['preco_venda'] * $p['quantidade'];
    if ($p['quantidade'] <= 0) $sem_estoque++;
    elseif ($p['quantidade'] <= $p['estoque_minimo']) $estoque_baixo++;
}

$lucro_potencial = $total_venda - $total_custo;

// Buscar categorias
$categorias = $pdo->query("SELECT * FROM categorias ORDER BY nome")->fetchAll();

// Buscar movimentacoes do dia
$hoje = date('Y-m-d');
$sqlHoje = "SELECT COUNT(*) as total FROM movimentacoes WHERE DATE(criado_em) = '$hoje'";
$movs_hoje = $pdo->query($sqlHoje)->fetch()['total'];

// Buscar movimentacoes da semana
$sqlSemana = "SELECT COUNT(*) as total FROM movimentacoes WHERE criado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)";
$movs_semana = $pdo->query($sqlSemana)->fetch()['total'];
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Estoque - PCsoluções</title>
    <link rel="stylesheet" href="css/estilo.css">
</head>
<body>

    <header>
        <div class="header-inner">
            <a href="index.php" class="logo">
                <div class="logo-icon">📦</div>
                <div class="logo-text">
                    <h1>PCsoluções</h1>
                    <span>Controle de Estoque</span>
                </div>
            </a>
            <nav>
                <a href="index.php">Produtos</a>
                <a href="cadastrar.php">Cadastrar</a>
                <a href="movimentar.php">Movimentar</a>
                <a href="relatorio.php" class="active">Relatório</a>
            </nav>
        </div>
    </header>

    <div class="container">

        <!-- Cards de Resumo Financeiro -->
        <div class="resumo-cards">
            <div class="resumo-card">
                <div class="resumo-icon azul">💰</div>
                <div class="resumo-info">
                    <h3><?php echo formatarMoeda($total_custo); ?></h3>
                    <p>Valor em custo</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon verde">📈</div>
                <div class="resumo-info">
                    <h3><?php echo formatarMoeda($total_venda); ?></h3>
                    <p>Valor em venda</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon amarelo">🎯</div>
                <div class="resumo-info">
                    <h3><?php echo formatarMoeda($lucro_potencial); ?></h3>
                    <p>Lucro potencial</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon azul">🔄</div>
                <div class="resumo-info">
                    <h3><?php echo $movs_hoje; ?> / <?php echo $movs_semana; ?></h3>
                    <p>Mov. hoje / semana</p>
                </div>
            </div>
        </div>

        <!-- Relatorio por Categoria -->
        <div class="card">
            <div class="card-header">
                <h2>Estoque por Categoria</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Categoria</th>
                        <th>Produtos</th>
                        <th>Itens</th>
                        <th>Valor Custo</th>
                        <th>Valor Venda</th>
                        <th>Lucro</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($categorias as $cat): 
                        $cat_produtos = array_filter($produtos, function($p) use ($cat) { return $p['categoria_id'] == $cat['id']; });
                        $cat_itens = 0;
                        $cat_custo = 0;
                        $cat_venda = 0;
                        foreach ($cat_produtos as $p) {
                            $cat_itens += $p['quantidade'];
                            $cat_custo += $p['preco_custo'] * $p['quantidade'];
                            $cat_venda += $p['preco_venda'] * $p['quantidade'];
                        }
                        if (count($cat_produtos) == 0) continue;
                    ?>
                        <tr>
                            <td><strong><?php echo htmlspecialchars($cat['nome']); ?></strong></td>
                            <td><?php echo count($cat_produtos); ?></td>
                            <td><?php echo $cat_itens; ?></td>
                            <td><?php echo formatarMoeda($cat_custo); ?></td>
                            <td><?php echo formatarMoeda($cat_venda); ?></td>
                            <td style="color:#059669;font-weight:600;"><?php echo formatarMoeda($cat_venda - $cat_custo); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <!-- Produtos com Estoque Baixo -->
        <div class="card">
            <div class="card-header">
                <h2>⚠️ Produtos com Estoque Baixo</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Categoria</th>
                        <th>Estoque Atual</th>
                        <th>Estoque Mínimo</th>
                        <th>Status</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
                    <?php 
                    $baixos = array_filter($produtos, function($p) { return $p['quantidade'] <= $p['estoque_minimo']; });
                    if (empty($baixos)): ?>
                        <tr>
                            <td colspan="6" style="text-align:center;padding:30px;color:#059669;">
                                ✅ Todos os produtos estão com estoque adequado!
                            </td>
                        </tr>
                    <?php else: ?>
                        <?php foreach ($baixos as $p): ?>
                            <tr>
                                <td><strong><?php echo htmlspecialchars($p['nome']); ?></strong></td>
                                <td><?php echo htmlspecialchars($p['categoria_nome'] ?? '-'); ?></td>
                                <td><strong><?php echo $p['quantidade']; ?> <?php echo $p['unidade']; ?></strong></td>
                                <td><?php echo $p['estoque_minimo']; ?> <?php echo $p['unidade']; ?></td>
                                <td>
                                    <span class="badge <?php echo classeEstoque($p['quantidade'], $p['estoque_minimo']); ?>">
                                        <?php echo textoEstoque($p['quantidade'], $p['estoque_minimo']); ?>
                                    </span>
                                </td>
                                <td>
                                    <a href="movimentar.php?produto=<?php echo $p['id']; ?>" class="btn btn-sm btn-primary">Repor</a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <!-- Relatorio Completo -->
        <div class="card">
            <div class="card-header">
                <h2>📋 Relatório Completo de Produtos</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Produto</th>
                        <th>Categoria</th>
                        <th>Custo</th>
                        <th>Venda</th>
                        <th>Margem</th>
                        <th>Qtd</th>
                        <th>Total Custo</th>
                        <th>Total Venda</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($produtos as $p): 
                        $margem = $p['preco_custo'] > 0 ? (($p['preco_venda'] - $p['preco_custo']) / $p['preco_custo']) * 100 : 0;
                    ?>
                        <tr>
                            <td><?php echo $p['id']; ?></td>
                            <td><strong><?php echo htmlspecialchars($p['nome']); ?></strong></td>
                            <td><?php echo htmlspecialchars($p['categoria_nome'] ?? '-'); ?></td>
                            <td><?php echo formatarMoeda($p['preco_custo']); ?></td>
                            <td><?php echo formatarMoeda($p['preco_venda']); ?></td>
                            <td style="color:#059669;"><?php echo number_format($margem, 0); ?>%</td>
                            <td><?php echo $p['quantidade']; ?> <?php echo $p['unidade']; ?></td>
                            <td><?php echo formatarMoeda($p['preco_custo'] * $p['quantidade']); ?></td>
                            <td><?php echo formatarMoeda($p['preco_venda'] * $p['quantidade']); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
                <tfoot>
                    <tr style="background:#f1f5f9;font-weight:700;">
                        <td colspan="3">TOTAIS</td>
                        <td colspan="3"></td>
                        <td><?php echo $total_itens; ?> itens</td>
                        <td><?php echo formatarMoeda($total_custo); ?></td>
                        <td><?php echo formatarMoeda($total_venda); ?></td>
                    </tr>
                </tfoot>
            </table>
        </div>

    </div>

</body>
</html>
