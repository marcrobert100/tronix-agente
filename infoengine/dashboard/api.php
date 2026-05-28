<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'status':
        echo json_encode([
            'status' => 'ok',
            'php_version' => PHP_VERSION,
            'timestamp' => date('Y-m-d H:i:s'),
            'templates' => [
                'infantil' => glob('../templates/infantil/*.html') ?: [],
                'infografico' => glob('../templates/infografico/*.html') ?: [],
                'outros' => glob('../templates/*.html') ?: [],
            ]
        ]);
        break;

    case 'tools':
        echo json_encode([
            'status' => 'ok',
            'tools' => [
                'criar_historia.py' => 'Gera JSON de história infantil',
                'gerar_infografico.py' => 'Gera JSON de infográfico',
                'gerar_pdf.py' => 'Converte HTML para PDF (requer Playwright)',
                'enviar_whatsapp.py' => 'Envia link via WhatsApp',
            ]
        ]);
        break;

    default:
        echo json_encode(['status' => 'error', 'message' => 'Ação desconhecida']);
}
