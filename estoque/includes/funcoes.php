<?php
// ============================================
// PCsolucoes - Funcoes Utilitarias
// Programador: Programador PCsolucoes
// ============================================

// Formata valor para Real brasileiro
function formatarMoeda($valor) {
    return 'R$ ' . number_format($valor, 2, ',', '.');
}

// Formata data
function formatarData($data) {
    return date('d/m/Y H:i', strtotime($data));
}

// Retorna classe CSS conforme nivel de estoque
function classeEstoque($quantidade, $minimo) {
    if ($quantidade <= 0) return 'estoque-zero';
    if ($quantidade <= $minimo) return 'estoque-baixo';
    return 'estoque-ok';
}

// Retorna texto do nivel de estoque
function textoEstoque($quantidade, $minimo) {
    if ($quantidade <= 0) return 'Sem estoque';
    if ($quantidade <= $minimo) return 'Estoque baixo';
    return 'Normal';
}

// Mensagem de feedback
function mensagem($tipo, $texto) {
    return "<div class='msg msg-$tipo'>$texto</div>";
}
?>
