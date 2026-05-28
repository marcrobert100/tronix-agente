<?php
// ============================================
// PCsolucoes - Cadastro de Produto
// Programador: Programador PCsolucoes
// ============================================

require_once 'includes/conexao.php';
require_once 'includes/funcoes.php';

$msg = '';

// Buscar categorias
$categorias = $pdo->query("SELECT * FROM categorias ORDER BY nome")->fetchAll();

// Processar formulario
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nome = trim($_POST['nome'] ?? '');
    $descricao = trim($_POST['descricao'] ?? '');
    $categoria_id = $_POST['categoria_id'] ?? null;
    $codigo_barras = trim($_POST['codigo_barras'] ?? '');
    $preco_custo = floatval($_POST['preco_custo'] ?? 0);
    $preco_venda = floatval($_POST['preco_venda'] ?? 0);
    $quantidade = intval($_POST['quantidade'] ?? 0);
    $estoque_minimo = intval($_POST['estoque_minimo'] ?? 5);
    $unidade = trim($_POST['unidade'] ?? 'UN');

    if (empty($nome)) {
        $msg = mensagem('erro', 'O nome do produto é obrigatório.');
    } else {
        $sql = "INSERT INTO produtos (nome, descricao, categoria_id, codigo_barras, preco_custo, preco_venda, quantidade, estoque_minimo, unidade) 
                VALUES (:nome, :descricao, :categoria_id, :codigo_barras, :preco_custo, :preco_venda, :quantidade, :estoque_minimo, :unidade)";
        
        $stmt = $pdo->prepare($sql);
        $resultado = $stmt->execute([
            ':nome' => $nome,
            ':descricao' => $descricao,
            ':categoria_id' => $categoria_id ?: null,
            ':codigo_barras' => $codigo_barras,
            ':preco_custo' => $preco_custo,
            ':preco_venda' => $preco_venda,
            ':quantidade' => $quantidade,
            ':estoque_minimo' => $estoque_minimo,
            ':unidade' => $unidade
        ]);

        if ($resultado) {
            // Registrar movimentacao inicial se quantidade > 0
            if ($quantidade > 0) {
                $produto_id = $pdo->lastInsertId();
                $sqlMov = "INSERT INTO movimentacoes (produto_id, tipo, quantidade, motivo, usuario) VALUES (:produto_id, 'entrada', :quantidade, 'Estoque inicial', 'sistema')";
                $stmtMov = $pdo->prepare($sqlMov);
                $stmtMov->execute([':produto_id' => $produto_id, ':quantidade' => $quantidade]);
            }
            $msg = mensagem('sucesso', 'Produto cadastrado com sucesso!');
            // Limpar campos
            $_POST = [];
        } else {
            $msg = mensagem('erro', 'Erro ao cadastrar produto.');
        }
    }
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastrar Produto - PCsoluções</title>
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
                <a href="cadastrar.php" class="active">Cadastrar</a>
                <a href="movimentar.php">Movimentar</a>
                <a href="relatorio.php">Relatório</a>
            </nav>
        </div>
    </header>

    <div class="container">

        <div class="card">
            <div class="card-header">
                <h2>Cadastrar Novo Produto</h2>
            </div>
            <div style="padding:24px;">

                <?php echo $msg; ?>

                <form method="POST" action="cadastrar.php">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="nome">Nome do Produto *</label>
                            <input type="text" id="nome" name="nome" placeholder="Ex: Mouse USB" value="<?php echo htmlspecialchars($_POST['nome'] ?? ''); ?>" required>
                        </div>
                        <div class="form-group">
                            <label for="categoria_id">Categoria</label>
                            <select id="categoria_id" name="categoria_id">
                                <option value="">Selecione...</option>
                                <?php foreach ($categorias as $cat): ?>
                                    <option value="<?php echo $cat['id']; ?>" <?php echo (isset($_POST['categoria_id']) && $_POST['categoria_id'] == $cat['id']) ? 'selected' : ''; ?>>
                                        <?php echo htmlspecialchars($cat['nome']); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="descricao">Descrição</label>
                        <textarea id="descricao" name="descricao" rows="3" placeholder="Descrição detalhada do produto"><?php echo htmlspecialchars($_POST['descricao'] ?? ''); ?></textarea>
                    </div>

                    <div class="form-row-3">
                        <div class="form-group">
                            <label for="codigo_barras">Código de Barras</label>
                            <input type="text" id="codigo_barras" name="codigo_barras" placeholder="7891234567890" value="<?php echo htmlspecialchars($_POST['codigo_barras'] ?? ''); ?>">
                        </div>
                        <div class="form-group">
                            <label for="preco_custo">Preço de Custo (R$)</label>
                            <input type="number" id="preco_custo" name="preco_custo" step="0.01" min="0" placeholder="0.00" value="<?php echo $_POST['preco_custo'] ?? ''; ?>">
                        </div>
                        <div class="form-group">
                            <label for="preco_venda">Preço de Venda (R$)</label>
                            <input type="number" id="preco_venda" name="preco_venda" step="0.01" min="0" placeholder="0.00" value="<?php echo $_POST['preco_venda'] ?? ''; ?>">
                        </div>
                    </div>

                    <div class="form-row-3">
                        <div class="form-group">
                            <label for="quantidade">Quantidade Inicial</label>
                            <input type="number" id="quantidade" name="quantidade" min="0" placeholder="0" value="<?php echo $_POST['quantidade'] ?? '0'; ?>">
                        </div>
                        <div class="form-group">
                            <label for="estoque_minimo">Estoque Mínimo</label>
                            <input type="number" id="estoque_minimo" name="estoque_minimo" min="0" placeholder="5" value="<?php echo $_POST['estoque_minimo'] ?? '5'; ?>">
                        </div>
                        <div class="form-group">
                            <label for="unidade">Unidade</label>
                            <select id="unidade" name="unidade">
                                <option value="UN" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'UN') ? 'selected' : ''; ?>>Unidade (UN)</option>
                                <option value="KG" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'KG') ? 'selected' : ''; ?>>Quilograma (KG)</option>
                                <option value="MT" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'MT') ? 'selected' : ''; ?>>Metro (MT)</option>
                                <option value="LT" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'LT') ? 'selected' : ''; ?>>Litro (LT)</option>
                                <option value="CX" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'CX') ? 'selected' : ''; ?>>Caixa (CX)</option>
                                <option value="LIC" <?php echo (isset($_POST['unidade']) && $_POST['unidade'] === 'LIC') ? 'selected' : ''; ?>>Licença (LIC)</option>
                            </select>
                        </div>
                    </div>

                    <div style="display:flex;gap:12px;margin-top:24px;">
                        <button type="submit" class="btn btn-primary">Cadastrar Produto</button>
                        <a href="index.php" class="btn btn-outline">Cancelar</a>
                    </div>
                </form>

            </div>
        </div>

    </div>

</body>
</html>
