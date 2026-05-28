<?php
// ============================================
// PCsolucoes - Controle de Estoque
// Pagina Principal - Listagem de Produtos
// Programador: Programador PCsolucoes
// ============================================

require_once 'includes/conexao.php';
require_once 'includes/funcoes.php';

// Buscar produtos com categoria
$sql = "SELECT p.*, c.nome as categoria_nome 
        FROM produtos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        ORDER BY p.nome ASC";
$produtos = $pdo->query($sql)->fetchAll();

// Contadores para resumo
$total_produtos = count($produtos);
$estoque_baixo = 0;
$sem_estoque = 0;
$total_itens = 0;

foreach ($produtos as $p) {
    $total_itens += $p['quantidade'];
    if ($p['quantidade'] <= 0) $sem_estoque++;
    elseif ($p['quantidade'] <= $p['estoque_minimo']) $estoque_baixo++;
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estoque - PCsoluções</title>
    <link rel="stylesheet" href="css/estilo.css">
</head>
<body>

    <!-- Header -->
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
                <a href="index.php" class="active">Produtos</a>
                <a href="cadastrar.php">Cadastrar</a>
                <a href="movimentar.php">Movimentar</a>
                <a href="relatorio.php">Relatório</a>
            </nav>
        </div>
    </header>

    <div class="container">

        <!-- Cards de Resumo -->
        <div class="resumo-cards">
            <div class="resumo-card">
                <div class="resumo-icon azul">📋</div>
                <div class="resumo-info">
                    <h3><?php echo $total_produtos; ?></h3>
                    <p>Produtos cadastrados</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon verde">📊</div>
                <div class="resumo-info">
                    <h3><?php echo $total_itens; ?></h3>
                    <p>Itens em estoque</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon amarelo">⚠️</div>
                <div class="resumo-info">
                    <h3><?php echo $estoque_baixo; ?></h3>
                    <p>Estoque baixo</p>
                </div>
            </div>
            <div class="resumo-card">
                <div class="resumo-icon vermelho">❌</div>
                <div class="resumo-info">
                    <h3><?php echo $sem_estoque; ?></h3>
                    <p>Sem estoque</p>
                </div>
            </div>
        </div>

        <!-- Tabela de Produtos -->
        <div class="card">
            <div class="card-header">
                <h2>Produtos em Estoque</h2>
                <div class="acoes">
                    <a href="cadastrar.php" class="btn btn-primary">+ Novo Produto</a>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Produto</th>
                        <th>Categoria</th>
                        <th>Preço Custo</th>
                        <th>Preço Venda</th>
                        <th>Qtd</th>
                        <th>Status</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($produtos)): ?>
                        <tr>
                            <td colspan="8" style="text-align:center;padding:40px;color:#94a3b8;">
                                Nenhum produto cadastrado. <a href="cadastrar.php">Cadastrar primeiro produto</a>
                            </td>
                        </tr>
                    <?php else: ?>
                        <?php foreach ($produtos as $p): ?>
                            <tr>
                                <td><strong>#<?php echo $p['id']; ?></strong></td>
                                <td>
                                    <strong><?php echo htmlspecialchars($p['nome']); ?></strong>
                                    <?php if ($p['descricao']): ?>
                                        <br><small style="color:#94a3b8;"><?php echo htmlspecialchars($p['descricao']); ?></small>
                                    <?php endif; ?>
                                </td>
                                <td><?php echo htmlspecialchars($p['categoria_nome'] ?? '-'); ?></td>
                                <td><?php echo formatarMoeda($p['preco_custo']); ?></td>
                                <td><?php echo formatarMoeda($p['preco_venda']); ?></td>
                                <td><strong><?php echo $p['quantidade']; ?> <?php echo $p['unidade']; ?></strong></td>
                                <td>
                                    <span class="badge <?php echo classeEstoque($p['quantidade'], $p['estoque_minimo']); ?>">
                                        <?php echo textoEstoque($p['quantidade'], $p['estoque_minimo']); ?>
                                    </span>
                                </td>
                                <td>
                                    <a href="movimentar.php?produto=<?php echo $p['id']; ?>" class="btn btn-sm btn-outline">Movimentar</a>
                                    <a href="editar.php?id=<?php echo $p['id']; ?>" class="btn btn-sm btn-outline">Editar</a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

    </div>

</body>
</html>
