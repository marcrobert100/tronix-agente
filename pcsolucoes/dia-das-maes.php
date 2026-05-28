<?php
header('Content-Type: image/png');

// Criar uma imagem
$width = 800;
$height = 400;
$image = imagecreatetruecolor($width, $height);

// Cores
$background = imagecolorallocate($image, 15, 23, 42); // #0f172a
$textColor = imagecolorallocate($image, 236, 72, 153); // #ec4899
$white = imagecolorallocate($image, 255, 255, 255);

// Preencher fundo
imagefill($image, 0, 0, $background);

// Adicionar texto
$text = 'Feliz Dia das Mães!';
$font = 5; // Fonte padrão do GD
$textWidth = imagefontwidth($font) * strlen($text);
$textHeight = imagefontheight($font);

$x = ($width - $textWidth) / 2;
$y = ($height - $textHeight) / 2;

// Desenhar texto
imagestring($image, $font, $x, $y, $text, $textColor);

// Enviar imagem
imagepng($image);
imagedestroy($image);
?>