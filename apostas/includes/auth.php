<?php
/**
 * Middleware de Autenticação
 */

require_once __DIR__ . '/../config/functions.php';

function requireAuth(string $tipo): array {
    requireLogin($tipo);
    $usuario = getUsuarioLogado($tipo);
    if (!$usuario) {
        session_destroy();
        $urls = ['admin' => ADMIN_URL, 'bar' => BAR_URL, 'cliente' => CLIENTE_URL];
        header("Location: {$urls[$tipo]}/login.php");
        exit;
    }
    return $usuario;
}

function isBarOwner(): bool {
    return isLoggedIn('bar');
}

function getBarId(): ?int {
    return $_SESSION['bar_id'] ?? null;
}
