/* ============================================
   PCsolucoes - Scripts JavaScript
   Programador: Programador PCsolucoes
   Funcoes de interacao do site
   ============================================ */

// Menu mobile - abre/fecha ao clicar no botao
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('menuBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (menuBtn && navLinks) {
        menuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Fecha o menu mobile ao clicar em um link
    const links = document.querySelectorAll('.nav-links a');
    links.forEach(function(link) {
        link.addEventListener('click', function() {
            navLinks.classList.remove('active');
        });
    });

    // Scroll suave para links com ancora
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Destacar link ativo na navbar baseado na pagina atual
    const paginaAtual = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-links a').forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === paginaAtual || (paginaAtual === '' && href === 'index.php')) {
            link.classList.add('active');
        }
    });
});
