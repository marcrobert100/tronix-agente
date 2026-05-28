<?php
// ============================================
// PCsolucoes - Editar Produto
// Programador: Programador PCsolucoes
// ============================================

require_once 'includes/conexao.php';
require_once 'includes/funcoes.php';

$msg = '';
$id = intval($_GET['id'] ?? 0);

if ($id <= 0) {
    header('Location: index.php');
    exit;
}

// Buscar categorias
$categorias = $pdo->query("SELECT * FROM categorias ORDER BY nome")->fetchAll();

// Buscar produto
$stmt = $pdo->prepare("SELECT * FROM produtos WHERE id = :id");
$stmt->execute([':id' => $id]);
$produto = $stmt->fetch();

if (!$produto) {
    header('Location: index.php');
    exit;
}

// Processar formulario
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nome = trim($_POST['nome'] ?? '');
    $descricao = trim($_POST['descricao'] ?? '');
    $categoria_id = $_POST['categoria_id'] ?? null;
    $codigo_barras = trim($_POST['codigo_barras'] ?? '');
    $preco_custo = floatval($_POST['preco_custo'] ?? 0);
    $preco_venda = floatval($_POST['preco_venda'] ?? 0);
    $estoque_minimo = intval($_POST['estoque_minimo'] ?? 5);
    $unidade = trim($_POST['unidade'] ?? 'UN');
    $ativo = isset($_POST['ativo']) ? 1 : 0;

    if (empty($nome)) {
        $msg = mensagem('erro', 'O nome do produto é obrigatório.');
    } else {
        $sql = "UPDATE produtos SET 
                nome = :nome, 
                descricao = :descricao, 
                categoria_id = :categoria_id, 
                codigo_barras = :codigo_barras, 
                preco_custo = :preco_custo, 
                preco_venda = :preco_venda, 
                estoque_minimo = :estoque_minimo, 
                unidade = :unidade,
                ativo = :ativo
                WHERE id = :id";
        
        $stmt = $pdo->prepare($sql);
        $resultado = $stmt->execute([
            ':nome' => $nome,
            ':descricao' => $descricao,
            ':categoria_id' => $categoria_id ?: null,
            ':codigo_barras' => $codigo_barras,
            ':preco_custo' => $preco_custo,
            ':preco_venda' => $preco_venda,
            ':estoque_minimo' => $estoque_minimo,
            ':unidade' => $unidade,
            ':ativo' => $ativo,
            ':id' => $id
        ]);

        if ($resultado) {
            $msg = mensagem('sucesso', 'Produto atualizado com sucesso!');
            // Atualizar dados do produto
            $stmt = $pdo->prepare("SELECT * FROM produtos WHERE id = :id");
            $stmt->execute([':id' => $id]);
            $produto = $stmt->fetch();
        } else {
            $msg = mensagem('erro', 'Erro ao atualizar produto.');
        }
    }
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Produto - PCsoluções</title>
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
                <a href="relatorio.php">Relatório</a>
            </nav>
        </div>
    </header>

    <div class="container">

        <div class="card">
            <div class="card-header">
                <h2>Editar Produto: <?php echo htmlspecialchars($produto['nome']); ?></h2>
                <a href="index.php" class="btn btn-outline">← Voltar</a>
            </div>
            <div style="padding:24px;">

                <?php echo $msg; ?>

                <form method="POST" action="editar.php?id=<?php echo $id; ?>">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="nome">Nome do Produto *</label>
                            <input type="text" id="nome" name="nome" value="<?php echo htmlspecialchars($produto['nome']); ?>" required>
                        </div>
                        <div class="form-group">
                            <label for="categoria_id">Categoria</label>
                            <select id="categoria_id" name="categoria_id">
                                <option value="">Selecione...</option>
                                <?php foreach ($categorias as $cat): ?>
                                    <option value="<?php echo $cat['id']; ?>" <?php echo ($produto['categoria_id'] == $cat['id']) ? 'selected' : ''; ?>>
                                        <?php echo htmlspecialchars($cat['nome']); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="descricao">Descrição</label>
                        <textarea id="descricao" name="descricao" rows="3"><?php echo htmlspecialchars($produto['descricao']); ?></textarea>
                    </div>

                    <div class="form-row-3">
                        <div class="form-group">
                            <label for="codigo_barras">Código de Barras</label>
                            <input type="text" id="codigo_barras" name="codigo_barras" value="<?php echo htmlspecialchars($produto['codigo_barras']); ?>">
                        </div>
                        <div class="form-group">
                            <label for="preco_custo">Preço de Custo (R$)</label>
                            <input type="number" id="preco_custo" name="preco_custo" step="0.01" min="0" value="<?php echo $produto['preco_custo']; ?>">
                        </div>
                        <div class="form-group">
                            <label for="preco_venda">Preço de Venda (R$)</label>
                            <input type="number" id="preco_venda" name="preco_venda" step="0.01" min="0" value="<?php echo $produto['preco_venda']; ?>">
                        </div>
                    </div>

                    <div class="form-row-3">
                        <div class="form-group">
                            <label>Quantidade Atual</label>
                            <input type="text" value="<?php echo $produto['quantidade'] . ' ' . $produto['unidade']; ?>" disabled>
                            <small style="color:#64748b;">Use "Movimentar" para alterar a quantidade</small>
                        </div>
                        <div class="form-group">
                            <label for="estoque_minimo">Estoque Mínimo</label>
                            <input type="number" id="estoque_minimo" name="estoque_minimo" min="0" value="<?php echo $produto['estoque_minimo']; ?>">
                        </div>
                        <div class="form-group">
                            <label for="unidade">Unidade</label>
                            <select id="unidade" name="unidade">
                                <option value="UN" <?php echo $produto['unidade'] === 'UN' ? 'selected' : ''; ?>>Unidade (UN)</option>
                                <option value="KG" <?php echo $produto['unidade'] === 'KG' ? 'selected' : ''; ?>>Quilograma (KG)</option>
                                <option value="MT" <?php echo $produto['unidade'] === 'MT' ? 'selected' : ''; ?>>Metro (MT)</option>
                                <option value="LT" <?php echo $produto['unidade'] === 'LT' ? 'selected' : ''; ?>>Litro (LT)</option>
                                <option value="CX" <?php echo $produto['unidade'] === 'CX' ? 'selected' : ''; ?>>Caixa (CX)</option>
                                <option value="LIC" <?php echo $produto['unidade'] === 'LIC' ? 'selected' : ''; ?>>Licença (LIC)</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group" style="margin-top:16px;">
                        <label>
                            <input type="checkbox" name="ativo" <?php echo $produto['ativo'] ? 'checked' : ''; ?>>
                            Produto ativo
                        </label>
                    </div>

                    <div style="display:flex;gap:12px;margin-top:24px;">
                        <button type="submit" class="btn btn-primary">Salvar Alterações</button>
                        <a href="index.php" class="btn btn-outline">Cancelar</a>
                    </div>
                </form>

            </div>
        </div>

    </div>

</body>
</html>
