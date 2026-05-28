<?php
/**
 * TRONIX - Video Generation Orchestrator
 * Desenvolvido por: Marcos Roberto (PCsoluções)
 */

$inputDir = 'uploads/';
$outputDir = 'videos_saida/';

// 1. Busca a imagem mais recente
$files = glob($inputDir . "*.{png,jpg,jpeg,PNG}", GLOB_BRACE);
if (empty($files)) {
    die("❌ ERRO: Nenhuma imagem encontrada em $inputDir");
}

// Ordena por data de modificação (mais recente primeiro)
usort($files, function($a, $b) {
    return filemtime($b) - filemtime($a);
});

$ultimaImagem = $files[0];
$imagemEscapada = escapeshellarg($ultimaImagem);

echo "🎬 Iniciando processamento: " . basename($ultimaImagem) . "\n";

// 2. Execução segura via Python
$comando = "python animar_opencode.py $imagemEscapada 2>&1";
exec($comando, $output, $returnCode);

// 3. Validação de QA
if ($returnCode === 0 && !empty($output)) {
    $result = implode("\n", $output);
    if (strpos($result, 'SUCESSO|') !== false) {
        $path = explode('|', $result)[1];
        echo "✅ SUCESSO: Vídeo gerado em " . trim($path) . "\n";
    } else {
        echo "⚠️ ALERTA: Script executou mas o retorno foi inesperado: \n" . $result;
    }
} else {
    echo "❌ FALHA CRÍTICA: Erro ao executar o motor Python.\n";
    echo "LOG DE ERRO: " . implode("\n", $output);
}
?>
