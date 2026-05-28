<?php
/**
 * Configurações Gerais do Sistema
 * Sistema de Apostas
 */

// Iniciar sessão se não estiver ativa
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Fuso horário
date_default_timezone_set('America/Sao_Paulo');

// URL base do projeto
define('BASE_URL', '/apostas');
define('ADMIN_URL', BASE_URL . '/admin');
define('BAR_URL', BASE_URL . '/bar');
define('CLIENTE_URL', BASE_URL . '/cliente');
define('ASSETS_URL', BASE_URL . '/assets');

// Nome do sistema
define('SISTEMA_NOME', 'BetScore');
define('SISTEMA_DESCRICAO', 'Sistema de Apostas - Copa do Mundo & Jogos');

// Configurações de aposta
define('APOSTA_MINIMA', 5.00);
define('APOSTA_MAXIMA', 1000.00);

// Configurações PIX
define('PIX_TEMPO_EXPIRACAO', 30); // minutos
define('PIX_CHAVE', '00.000.000/0001-00'); // Chave PIX do sistema (trocar)
define('PIX_NOME', 'BetScore Pagamentos');

// Uploads
define('UPLOAD_DIR', __DIR__ . '/../assets/img/uploads/');
define('MAX_UPLOAD_SIZE', 2 * 1024 * 1024); // 2MB

// Mensagens flash
function setFlash(string $tipo, string $mensagem): void {
    $_SESSION['flash'] = ['tipo' => $tipo, 'mensagem' => $mensagem];
}

function getFlash(): ?array {
    if (isset($_SESSION['flash'])) {
        $flash = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $flash;
    }
    return null;
}

// CSRF Token
function generateCSRF(): string {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function verifyCSRF(string $token): bool {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

// Sanitização
function sanitize(string $input): string {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}
