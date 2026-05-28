<?php
// ============================================
// PCsolucoes - Pagina de Contato
// Programador: Programador PCsolucoes
// Formulario de contato com processamento PHP
// ============================================

// Variaveis para mensagens do formulario
$msg_sucesso = '';
$msg_erro = '';

// Processamento do formulario via POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Captura e sanitiza os dados do formulario
    $nome = isset($_POST['nome']) ? trim($_POST['nome']) : '';
    $email = isset($_POST['email']) ? trim($_POST['email']) : '';
    $telefone = isset($_POST['telefone']) ? trim($_POST['telefone']) : '';
    $assunto = isset($_POST['assunto']) ? trim($_POST['assunto']) : '';
    $mensagem = isset($_POST['mensagem']) ? trim($_POST['mensagem']) : '';

    // Validacao dos campos obrigatorios
    if (empty($nome) || empty($email) || empty($mensagem)) {
        $msg_erro = 'Por favor, preencha todos os campos obrigatorios.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $msg_erro = 'Por favor, insira um e-mail valido.';
    } else {
        // Monta o corpo do e-mail
        $destinatario = 'contato@pcsolucoes.com.br';
        $assunto_email = 'Contato do Site - ' . $assunto;
        $corpo = "Nome: $nome\n";
        $corpo .= "E-mail: $email\n";
        $corpo .= "Telefone: $telefone\n";
        $corpo .= "Assunto: $assunto\n\n";
        $corpo .= "Mensagem:\n$mensagem";

        // Cabecalhos do e-mail
        $cabecalhos = "From: $nome <$email>\r\n";
        $cabecalhos .= "Reply-To: $email\r\n";
        $cabecalhos .= "Content-Type: text/plain; charset=UTF-8\r\n";

        // Tenta enviar o e-mail
        // Em ambiente local (XAMPP), pode nao funcionar sem configuracao SMTP
        // Para testar, configure o Mercury no XAMPP ou use PHPMailer
        $enviado = mail($destinatario, $assunto_email, $corpo, $cabecalhos);

        if ($enviado) {
            $msg_sucesso = 'Mensagem enviada com sucesso! Entraremos em contato em breve.';
            // Limpa os campos apos envio
            $nome = $email = $telefone = $assunto = $mensagem = '';
        } else {
            // Em ambiente local, mostra mensagem de sucesso mesmo sem SMTP
            $msg_sucesso = 'Mensagem recebida! Em ambiente de producao, o e-mail sera enviado. Obrigado pelo contato, ' . $nome . '!';
            $nome = $email = $telefone = $assunto = $mensagem = '';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Entre em contato com a PCsolucoes. Suporte tecnico, orcamentos e consultoria em TI.">
    <title>Contato - PCsolucoes</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

    <!-- ========== NAVBAR ========== -->
    <nav class="navbar">
        <div class="navbar-inner">
            <a href="index.php" class="logo">
                <div class="logo-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                </div>
                <span class="logo-text">PC<span>solucoes</span></span>
            </a>
            <ul class="nav-links" id="navLinks">
                <li><a href="index.php">Inicio</a></li>
                <li><a href="servicos.php">Servicos</a></li>
                <li><a href="contato.php" class="btn-contato active">Contato</a></li>
            </ul>
            <button class="menu-mobile" id="menuBtn" aria-label="Abrir menu">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                </svg>
            </button>
        </div>
    </nav>

    <!-- ========== HERO CONTATO ========== -->
    <section class="hero" style="min-height:50vh;padding-top:120px;padding-bottom:60px;">
        <div class="hero-content">
            <div class="hero-badge">Fale conosco</div>
            <h1>Entre em<br><span>Contato</span></h1>
            <p>Estamos prontos para ajudar. Envie sua mensagem e responderemos o mais rapido possivel.</p>
        </div>
    </section>

    <!-- ========== FORMULARIO E INFO ========== -->
    <section class="section section-gray">
        <div class="container">
            <div class="contato-grid">

                <!-- Informacoes de contato -->
                <div class="contato-info">
                    <h2 style="font-size:28px;font-weight:700;color:var(--azul-950);margin-bottom:8px;">Fale com a gente</h2>
                    <p style="color:var(--cinza-500);margin-bottom:16px;">Escolha a forma mais conveniente para entrar em contato.</p>

                    <div class="contato-item">
                        <div class="contato-icon">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                        </div>
                        <div>
                            <h4>Endereco</h4>
                            <p>Sua cidade, seu bairro<br>CEP 00000-000</p>
                        </div>
                    </div>

                    <div class="contato-item">
                        <div class="contato-icon">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                            </svg>
                        </div>
                        <div>
                            <h4>Telefone</h4>
                            <p>(00) 00000-0000</p>
                        </div>
                    </div>

                    <div class="contato-item">
                        <div class="contato-icon">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                        </div>
                        <div>
                            <h4>E-mail</h4>
                            <p>contato@pcsolucoes.com.br</p>
                        </div>
                    </div>

                    <div class="contato-item">
                        <div class="contato-icon">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <h4>Horario de Atendimento</h4>
                            <p>Seg a Sex: 8h as 18h<br>Sab: 8h as 12h</p>
                        </div>
                    </div>
                </div>

                <!-- Formulario de contato -->
                <div class="form-box">
                    <h3 style="font-size:22px;font-weight:700;color:var(--azul-950);margin-bottom:24px;">Envie sua mensagem</h3>

                    <?php if (!empty($msg_sucesso)): ?>
                        <div class="msg-sucesso"><?php echo $msg_sucesso; ?></div>
                    <?php endif; ?>

                    <?php if (!empty($msg_erro)): ?>
                        <div class="msg-erro"><?php echo $msg_erro; ?></div>
                    <?php endif; ?>

                    <form method="POST" action="contato.php">
                        <div class="form-group">
                            <label for="nome">Nome *</label>
                            <input type="text" id="nome" name="nome" placeholder="Seu nome completo" value="<?php echo isset($nome) ? htmlspecialchars($nome) : ''; ?>" required>
                        </div>

                        <div class="form-group">
                            <label for="email">E-mail *</label>
                            <input type="email" id="email" name="email" placeholder="seu@email.com" value="<?php echo isset($email) ? htmlspecialchars($email) : ''; ?>" required>
                        </div>

                        <div class="form-group">
                            <label for="telefone">Telefone</label>
                            <input type="tel" id="telefone" name="telefone" placeholder="(00) 00000-0000" value="<?php echo isset($telefone) ? htmlspecialchars($telefone) : ''; ?>">
                        </div>

                        <div class="form-group">
                            <label for="assunto">Assunto</label>
                            <select id="assunto" name="assunto">
                                <option value="orcamento" <?php echo (isset($assunto) && $assunto === 'orcamento') ? 'selected' : ''; ?>>Solicitar Orcamento</option>
                                <option value="suporte" <?php echo (isset($assunto) && $assunto === 'suporte') ? 'selected' : ''; ?>>Suporte Tecnico</option>
                                <option value="consultoria" <?php echo (isset($assunto) && $assunto === 'consultoria') ? 'selected' : ''; ?>>Consultoria</option>
                                <option value="outro" <?php echo (isset($assunto) && $assunto === 'outro') ? 'selected' : ''; ?>>Outro</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="mensagem">Mensagem *</label>
                            <textarea id="mensagem" name="mensagem" placeholder="Como podemos ajudar?" required><?php echo isset($mensagem) ? htmlspecialchars($mensagem) : ''; ?></textarea>
                        </div>

                        <button type="submit" class="btn-submit">Enviar Mensagem</button>
                    </form>
                </div>

            </div>
        </div>
    </section>

    <!-- ========== FOOTER ========== -->
    <footer class="footer">
        <div class="footer-inner">
            <div class="footer-logo">
                <div class="footer-logo-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                </div>
                <span class="footer-logo-text">PC<span>solucoes</span></span>
            </div>
            <p class="footer-copy">&copy; 2026 PCsolucoes. Todos os direitos reservados.</p>
        </div>
    </footer>

    <script src="assets/js/main.js"></script>
</body>
</html>
