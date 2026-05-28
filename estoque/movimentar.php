<?php
// ============================================
// PCsolucoes - Movimentacao de Estoque
// Programador: Programador PCsolucoes
// Entrada e Saida de produtos
// ============================================

require_once 'includes/conexao.php';
require_once 'includes/funcoes.php';

$msg = '';

// Buscar produtos
$produtos = $pdo->query("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")->fetchAll();

// Produto pre-selecionado (vindo da listagem)
$produto_selecionado = $_GET['produto'] ?? '';

// Processar movimentacao
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $produto_id = intval($_POST['produto_id'] ?? 0);
    $tipo = $_POST['tipo'] ?? '';
    $quantidade = intval($_POST['quantidade'] ?? 0);
    $motivo = trim($_POST['motivo'] ?? '');

    if ($produto_id <= 0) {
        $msg = mensagem('erro', 'Selecione um produto.');
    } elseif (!in_array($tipo, ['entrada', 'saida'])) {
        $msg = mensagem('erro', 'Tipo de movimentação inválido.');
    } elseif ($quantidade <= 0) {
        $msg = mensagem('erro', 'A quantidade deve ser maior que zero.');
    } else {
        // Verificar estoque atual para saida
        $stmt = $pdo->prepare("SELECT quantidade, nome FROM produtos WHERE id = :id");
        $stmt->execute([':id' => $produto_id]);
        $produto = $stmt->fetch();

        if ($tipo === 'saida' && $produto['quantidade'] < $quantidade) {
            $msg = mensagem('erro', "Estoque insuficiente. Disponível: {$produto['quantidade']} unidades.");
        } else {
            // Iniciar transacao
            $pdo->beginTransaction();

            try {
                // Atualizar quantidade do produto
                if ($tipo === 'entrada') {
                    $sqlUpdate = "UPDATE produtos SET quantidade = quantidade + :qtd WHERE id = :id";
                } else {
                    $sqlUpdate = "UPDATE produtos SET quantidade = quantidade - :qtd WHERE id = :id";
                }

                $stmtUpdate = $pdo->prepare($sqlUpdate);
                $stmtUpdate->execute([':qtd' => $quantidade, ':id' => $produto_id]);

                // Registrar movimentacao
                $sqlMov = "INSERT INTO movimentacoes (produto_id, tipo, quantidade, motivo, usuario) VALUES (:produto_id, :tipo, :quantidade, :motivo, 'admin')";
                $stmtMov = $pdo->prepare($sqlMov);
                $stmtMov->execute([
                    ':produto_id' => $produto_id,
                    ':tipo' => $tipo,
                    ':quantidade' => $quantidade,
                    ':motivo' => $motivo
                ]);

                $pdo->commit();

                $tipo_texto = $tipo === 'entrada' ? 'Entrada' : 'Saída';
                $msg = mensagem('sucesso', "{$tipo_texto} registrada com sucesso! {$quantidade} unidades de " . htmlspecialchars($produto['nome']));
                $_POST = [];
            } catch (Exception $e) {
                $pdo->rollBack();
                $msg = mensagem('erro', 'Erro ao registrar movimentação: ' . $e->getMessage());
            }
        }
    }
}

// Buscar ultimas movimentacoes
$sqlMovs = "SELECT m.*, p.nome as produto_nome 
            FROM movimentacoes m 
            JOIN produtos p ON m.produto_id = p.id 
            ORDER BY m.criado_em DESC 
            LIMIT 20";
$movimentacoes = $pdo->query($sqlMovs)->fetchAll();
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movimentar Estoque - PCsoluções</title>
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
                <a href="movimentar.php" class="active">Movimentar</a>
                <a href="relatorio.php">Relatório</a>
            </nav>
        </div>
    </header>

    <div class="container">

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">

            <!-- Formulario de Movimentacao -->
            <div class="card">
                <div class="card-header">
                    <h2>Registrar Movimentação</h2>
                </div>
                <div style="padding:24px;">

                    <?php echo $msg; ?>

                    <form method="POST" action="movimentar.php">
                        <div class="form-group">
                            <label for="produto_id">Produto *</label>
                            <select id="produto_id" name="produto_id" required>
                                <option value="">Selecione um produto...</option>
                                <?php foreach ($produtos as $p): ?>
                                    <option value="<?php echo $p['id']; ?>" 
                                        <?php echo ($produto_selecionado == $p['id']) ? 'selected' : ''; ?>
                                        <?php echo (isset($_POST['produto_id']) && $_POST['produto_id'] == $p['id']) ? 'selected' : ''; ?>>
                                        <?php echo htmlspecialchars($p['nome']); ?> (Estoque: <?php echo $p['quantidade']; ?> <?php echo $p['unidade']; ?>)
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="tipo">Tipo de Movimentação *</label>
                                <select id="tipo" name="tipo" required>
                                    <option value="entrada" <?php echo (isset($_POST['tipo']) && $_POST['tipo'] === 'entrada') ? 'selected' : ''; ?>>📥 Entrada</option>
                                    <option value="saida" <?php echo (isset($_POST['tipo']) && $_POST['tipo'] === 'saida') ? 'selected' : ''; ?>>📤 Saída</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="quantidade">Quantidade *</label>
                                <input type="number" id="quantidade" name="quantidade" min="1" placeholder="0" value="<?php echo $_POST['quantidade'] ?? ''; ?>" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="motivo">Motivo / Observação</label>
                            <textarea id="motivo" name="motivo" rows="3" placeholder="Ex: Compra de fornecedor, Venda para cliente..."><?php echo htmlspecialchars($_POST['motivo'] ?? ''); ?></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary">Registrar Movimentação</button>
                    </form>

                </div>
            </div>

            <!-- Historico de Movimentacoes -->
            <div class="card">
                <div class="card-header">
                    <h2>Últimas Movimentações</h2>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Produto</th>
                            <th>Tipo</th>
                            <th>Qtd</th>
                            <th>Motivo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (empty($movimentacoes)): ?>
                            <tr>
                                <td colspan="5" style="text-align:center;padding:30px;color:#94a3b8;">Nenhuma movimentação</td>
                            </tr>
                        <?php else: ?>
                            <?php foreach ($movimentacoes as $m): ?>
                                <tr>
                                    <td><small><?php echo formatarData($m['criado_em']); ?></small></td>
                                    <td><strong><?php echo htmlspecialchars($m['produto_nome']); ?></strong></td>
                                    <td>
                                        <?php if ($m['tipo'] === 'entrada'): ?>
                                            <span class="badge estoque-ok">📥 Entrada</span>
                                        <?php else: ?>
                                            <span class="badge estoque-zero">📤 Saída</span>
                                        <?php endif; ?>
                                    </td>
                                    <td><strong><?php echo $m['quantidade']; ?></strong></td>
                                    <td><small><?php echo htmlspecialchars($m['motivo'] ?? '-'); ?></small></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>

        </div>

    </div>

</body>
</html>
