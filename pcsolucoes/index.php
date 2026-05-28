<?php
// ============================================
// PCsolucoes - Pagina Inicial
// Programador: Programador PCsolucoes
// Pagina principal do site institucional
// ============================================
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="PCsolucoes - Solucoes em Tecnologia para sua empresa. Suporte tecnico, redes, seguranca digital e desenvolvimento web.">
    <title>PCsolucoes - Solucoes em Tecnologia</title>
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
                <li><a href="index.php" class="active">Inicio</a></li>
                <li><a href="servicos.php">Servicos</a></li>
                <li><a href="contato.php" class="btn-contato">Contato</a></li>
            </ul>
            <button class="menu-mobile" id="menuBtn" aria-label="Abrir menu">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                </svg>
            </button>
        </div>
    </nav>

    <!-- ========== HERO ========== -->
    <section class="hero" id="inicio">
        <div class="hero-content">
            <div class="hero-badge">Tecnologia que transforma</div>
            <h1>Solucoes em<br><span>Tecnologia</span></h1>
            <p>Na PCsolucoes, cuidamos da sua tecnologia para voce focar no que realmente importa: o crescimento do seu negocio.</p>
            <div class="hero-buttons">
                <a href="servicos.php" class="btn-primary">Nossos Servicos</a>
                <a href="contato.php" class="btn-secondary">Fale Conosco</a>
            </div>
        </div>
    </section>

    <!-- ========== SERVICOS RESUMO ========== -->
    <section class="section section-white">
        <div class="container">
            <div class="section-header">
                <div class="section-label">O que fazemos</div>
                <h2 class="section-title">Nossos Servicos</h2>
                <p class="section-subtitle">Oferecemos solucoes completas em tecnologia para empresas de todos os tamanhos.</p>
            </div>

            <div class="servicos-grid">
                <!-- Suporte Tecnico -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                        </svg>
                    </div>
                    <h3>Suporte Tecnico</h3>
                    <p>Assistencia tecnica especializada para computadores, notebooks e perifericos. Diagnostico rapido e solucoes eficientes.</p>
                </div>

                <!-- Redes e Infraestrutura -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                        </svg>
                    </div>
                    <h3>Redes e Infraestrutura</h3>
                    <p>Instalacao e configuracao de redes, servidores e infraestrutura de TI. Conectividade estavel e segura.</p>
                </div>

                <!-- Seguranca Digital -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                    </div>
                    <h3>Seguranca Digital</h3>
                    <p>Protecao de dados, antivirus, backup e seguranca corporativa contra ameacas digitais.</p>
                </div>

                <!-- Desenvolvimento Web -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                        </svg>
                    </div>
                    <h3>Desenvolvimento Web</h3>
                    <p>Sites, sistemas e aplicacoes web sob medida com as melhores tecnologias do mercado.</p>
                </div>

                <!-- Consultoria em TI -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                        </svg>
                    </div>
                    <h3>Consultoria em TI</h3>
                    <p>Planejamento estrategico de tecnologia para otimizar processos e reduzir custos.</p>
                </div>

                <!-- Manutencao Preventiva -->
                <div class="servico-card">
                    <div class="servico-icon">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                        </svg>
                    </div>
                    <h3>Manutencao Preventiva</h3>
                    <p>Manutencao regular de equipamentos para evitar problemas e garantir o melhor desempenho.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- ========== STATS ========== -->
    <section class="stats">
        <div class="container">
            <div class="stats-grid">
                <div>
                    <div class="stat-numero">500+</div>
                    <div class="stat-label">Clientes Atendidos</div>
                </div>
                <div>
                    <div class="stat-numero">10+</div>
                    <div class="stat-label">Anos de Experiencia</div>
                </div>
                <div>
                    <div class="stat-numero">24h</div>
                    <div class="stat-label">Suporte Disponivel</div>
                </div>
                <div>
                    <div class="stat-numero">98%</div>
                    <div class="stat-label">Satisfacao dos Clientes</div>
                </div>
            </div>
        </div>
    </section>

    <!-- ========== CTA ========== -->
    <section class="section section-white">
        <div class="container" style="text-align:center;">
            <h2 class="section-title">Pronto para transformar sua tecnologia?</h2>
            <p class="section-subtitle" style="margin-bottom:32px;">Entre em contato e descubra como a PCsolucoes pode ajudar seu negocio.</p>
            <a href="contato.php" class="btn-primary" style="background:var(--azul-600);color:var(--branco);">Solicitar Orcamento</a>
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
