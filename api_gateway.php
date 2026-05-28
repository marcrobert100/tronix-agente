<?php
// Gateway de Comando Tronix v1.3
if (isset($_POST['action']) && $_POST['action'] == 'disparar_pipeline') {
    $tema = $_POST['tema'] ?? 'Hambúrguer';
    
    // Comando para rodar o pipeline em segundo plano no Windows
    // O 'start /B' permite que o PHP não fique travado esperando o vídeo terminar
    $comando = "start /B python pipeline.py --tema " . escapeshellarg($tema);
    
    exec($comando);
    
    echo json_encode(["status" => "disparado", "tema" => $tema]);
    exit;
}
?>
