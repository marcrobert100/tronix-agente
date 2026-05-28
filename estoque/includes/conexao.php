<?php
// ============================================
// PCsolucoes - Conexao com MySQL (XAMPP)
// Programador: Programador PCsolucoes
// ============================================

$servidor = 'localhost';
$usuario = 'root';
$senha = '';
$banco = 'estoque_pcsolucoes';

// Conexao PDO
try {
    $pdo = new PDO("mysql:host=$servidor;dbname=$banco;charset=utf8mb4", $usuario, $senha);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Erro ao conectar ao banco: " . $e->getMessage());
}
?>
