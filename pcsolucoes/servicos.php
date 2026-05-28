<?php
// ============================================
// PCsolucoes - Pagina de Servicos
// Programador: Programador PCsolucoes
// Detalhamento de todos os servicos oferecidos
// ============================================
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Servicos da PCsolucoes - Suporte tecnico, redes, seguranca digital, desenvolvimento web, consultoria e manutencao.">
    <title>Servicos - PCsolucoes</title>
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
                <li><a href="servicos.php" class="active">Servicos</a></li>
                <li><a href="contato.php" class="btn-contato">Contato</a></li>
            </ul>
            <button class="menu-mobile" id="menuBtn" aria-label="Abrir menu">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                </svg>
            </button>
        </div>
    </nav>

    <!-- ========== HERO SERVICOS ========== -->
    <section class="hero" style="min-height:50vh;padding-top:120px;padding-bottom:60px;">
        <div class="hero-content">
            <div class="hero-badge">O que fazemos</div>
            <h1>Nossos<br><span>Servicos</span></h1>
            <p>Solucoes completas em tecnologia sob medida para as necessidades do seu negocio.</p>
        </div>
    </section>

    <!-- ========== SERVICOS DETALHADOS ========== -->
    <section class="section section-white">
        <div class="container">
            <div class="servicos-categorias">

                <!-- Suporte Tecnico -->
                <div class="servico-detalhe">
                    <div class="servico-detalhe-conteudo">
                        <h3>Suporte Tecnico</h3>
                        <p>Nossa equipe especializada esta pronta para resolver qualquer problema tecnico com agilidade e eficiencia. Atendemos presencialmente e remotamente.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Diagnostico e reparo de hardware
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Formatacao e instalacao de sistemas
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Remocao de virus e malware
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Suporte remoto e presencial
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                        </svg>
                    </div>
                </div>

                <!-- Redes e Infraestrutura -->
                <div class="servico-detalhe reverse">
                    <div class="servico-detalhe-conteudo">
                        <h3>Redes e Infraestrutura</h3>
                        <p>Projetamos, implementamos e gerenciamos a infraestrutura de rede da sua empresa com foco em performance e seguranca.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Instalacao de redes cabeadas e Wi-Fi
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Configuracao de servidores
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Firewall e roteamento avancado
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Monitoramento de rede 24/7
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                        </svg>
                    </div>
                </div>

                <!-- Seguranca Digital -->
                <div class="servico-detalhe">
                    <div class="servico-detalhe-conteudo">
                        <h3>Seguranca Digital</h3>
                        <p>Protegemos os dados e sistemas da sua empresa contra ameacas digitais com solucoes robustas e atualizadas.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Instalacao e gestao de antivirus
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Backup automatizado em nuvem
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Politicas de seguranca corporativa
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Auditoria e relatorios de seguranca
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                    </div>
                </div>

                <!-- Desenvolvimento Web -->
                <div class="servico-detalhe reverse">
                    <div class="servico-detalhe-conteudo">
                        <h3>Desenvolvimento Web</h3>
                        <p>Criamos sites, sistemas e aplicacoes web profissionais que geram resultados para o seu negocio.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Sites institucionais e landing pages
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Sistemas web personalizados
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                E-commerce e lojas virtuais
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Integracao com APIs e sistemas
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                        </svg>
                    </div>
                </div>

                <!-- Consultoria em TI -->
                <div class="servico-detalhe">
                    <div class="servico-detalhe-conteudo">
                        <h3>Consultoria em TI</h3>
                        <p>Planejamento estrategico de tecnologia alinhado aos objetivos do seu negocio para maximizar resultados.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Diagnostico de infraestrutura
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Plano diretor de tecnologia
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Reducao de custos com TI
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Modernizacao de processos
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                        </svg>
                    </div>
                </div>

                <!-- Manutencao Preventiva -->
                <div class="servico-detalhe reverse">
                    <div class="servico-detalhe-conteudo">
                        <h3>Manutencao Preventiva</h3>
                        <p>Evite problemas antes que acontecam. Manutencao regular garante o melhor desempenho dos seus equipamentos.</p>
                        <ul class="servico-lista">
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Limpeza interna de equipamentos
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Atualizacao de software e drivers
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Verificacao de saude do disco
                            </li>
                            <li>
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Relatorios de performance
                            </li>
                        </ul>
                    </div>
                    <div class="servico-visual">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                        </svg>
                    </div>
                </div>

            </div>
        </div>
    </section>

    <!-- ========== CTA ========== -->
    <section class="stats">
        <div class="container" style="text-align:center;">
            <h2 style="font-size:36px;font-weight:700;color:#fff;margin-bottom:16px;">Precisa de algum servico?</h2>
            <p style="color:var(--azul-200);font-size:18px;margin-bottom:32px;">Entre em contato e receba um orcamento personalizado.</p>
            <a href="contato.php" class="btn-primary">Solicitar Orcamento</a>
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
