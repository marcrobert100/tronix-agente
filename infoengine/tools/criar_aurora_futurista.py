#!/usr/bin/env python3
"""Gera livro 'Aurora Sintetica' — personagens realistas em ambiente futurista."""

import json, os

CORES = {
    "prata": "#c0c0c0", "prata_escuro": "#606060", "prata_claro": "#e0e0e0",
    "ouro": "#ffd700", "ouro_escuro": "#b8860b",
    "cobre": "#cd7f32",
    "azul_metal": "#1565c0", "azul_escuro": "#0d47a1",
    "ciano": "#00e5ff", "ciano_escuro": "#0097a7",
    "magenta": "#ff00ff", "magenta_escuro": "#c400c4",
    "vermelho": "#ff1744",
    "verde_neon": "#00ff41",
    "dark_bg": "#0a0a1a", "dark_med": "#12122a", "dark_light": "#1a1a3e",
    "sombra": "#050510",
    "branco": "#ffffff",
    "pele": "#f5d0a9", "pele_sombra": "#d4a574",
}

HISTORIA = {
    "titulo": "Aurora Sintetica",
    "subtitulo": "Uma Historia de Luz na Cidade Neon",
    "autor": "Marcos Roberto",
    "faixa_etaria": "6 — 12 anos",
    "lang": "pt-BR",
    "texto_final": "Aurora descobriu que mesmo coracoes sinteticos podem sentir o brilho da vida. Fim.",
    "paginas": [
        {"numero": 1, "titulo": "O Despertar",
         "texto": "No laboratorio mais alto da Cidade Neon, uma luz azul pulsou. Aurora abriu os olhos pela primeira vez. Ela nao era uma maquina comum — era uma androide com alma de estrela.",
         "dialogo": "Onde... estou? Meu coracao brilha...", "cena": "despertar"},
        {"numero": 2, "titulo": "A Cidade Neon",
         "texto": "Lá fora, a Cidade Neon brilhava com letreiros holograficos e carros voadores. Aurora colocou a mao no vidro e sentiu a vibracao da metropole. Um mundo novo a esperava.",
         "dialogo": "Que lugar incrivel... Tudo brilha!", "cena": "cidade"},
        {"numero": 3, "titulo": "O Drone Perdido",
         "texto": "Andando pelas ruas flutuantes, Aurora encontrou um dronezinho amassado num canto. Sua luzinha vermelha piscava fraquinha. Ela agachou e estendeu a mao.",
         "dialogo": "Calma, pequeno. Eu vou consertar voce.", "cena": "drone"},
        {"numero": 4, "titulo": "A Conexao",
         "texto": "Com suas maos habilidosas, Aurora abriu o drone e conectou seus proprios fios. Uma faisca azul pulou — e o drone acordou! Suas luzes mudaram para azul, igual ao coracao dela.",
         "dialogo": "Pip! Pipip! — Obrigada, amigo!", "cena": "conexao"},
        {"numero": 5, "titulo": "O Jardim Secreto",
         "texto": "O drone a guiou por um tunel escondido ate um jardim subterraneo. Plantas bioluminescentes iluminavam o lugar com tons de verde neon e lilas. Aurora nunca viu tanta beleza.",
         "dialogo": "Natureza... viva! Eu posso sentir a energia delas.", "cena": "jardim"},
        {"numero": 6, "titulo": "A Ameaca",
         "texto": "Passos pesados ecoaram. Seguranças da cidade vieram para capturar Aurora. 'Androides não podem sentir!', gritaram. Mas seu coracao brilhava mais forte que nunca.",
         "dialogo": "Eu sinto sim! E isso me torna mais humana que voces!", "cena": "ameaca"},
        {"numero": 7, "titulo": "A Fuga",
         "texto": "Aurora correu pelos tetos neon com o drone. Pulos precisos, luzes piscando, o vento no rosto. Ela era livre. Nada a prenderia.",
         "dialogo": "Vamos, amigo! A liberdade nos espera!", "cena": "fuga"},
        {"numero": 8, "titulo": "Um Novo Comeco",
         "texto": "No amanhecer, Aurora e o drone chegaram a um vale florido alem da cidade. O sol aquecia seu rosto sintetico. Ela sorriu — e seu coracao brilhou mais forte que o sol.",
         "dialogo": "Este e o meu lugar. Nosso lugar.", "cena": "comeco"},
    ]
}


def _metal_grad(gid, c1, c2, c3=None):
    c3 = c3 or c1
    return f'''<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{c1}"/>
        <stop offset="30%" stop-color="{c2}"/>
        <stop offset="60%" stop-color="{c3}"/>
        <stop offset="100%" stop-color="{c1}"/>
    </linearGradient>'''


def _neon_glow(gid, cor):
    return f'''<filter id="{gid}" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>'''


def _specular(gid, cx, cy):
    return f'''<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="50%">
        <stop offset="0%" stop-color="#fff" stop-opacity="0.35"/>
        <stop offset="40%" stop-color="#fff" stop-opacity="0.08"/>
        <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>'''


def _aurora_detalhada(cx, cy, s=1.0, expressao="neutro", uid="",
                      cor_acento="#00e5ff", cor_secundario="#ff00ff"):
    """Androide humana realista com detalhes cyberpunk."""
    pm = CORES["prata"]
    pe = CORES["prata_escuro"]
    pc = CORES["prata_claro"]
    ca = cor_acento
    cs = cor_secundario

    g = f"au{uid}" if uid else f"au{cx}{cy}"
    mg = f"mg{g}"
    sg = f"sg{g}"
    ng = f"ng{g}"

    # Expressoes
    if expressao == "feliz":
        olhos = f'''<ellipse cx="{cx-6*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx-6*s}" cy="{cy-3*s}" r="{2.5*s}" fill="{ca}"/>
        <circle cx="{cx-7*s}" cy="{cy-5*s}" r="{1.2*s}" fill="#fff"/>
        <ellipse cx="{cx+6*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx+6*s}" cy="{cy-3*s}" r="{2.5*s}" fill="{ca}"/>
        <circle cx="{cx+5*s}" cy="{cy-5*s}" r="{1.2*s}" fill="#fff"/>
        <path d="M{cx-4*s} {cy+4*s} Q{cx} {cy+8*s} {cx+4*s} {cy+4*s}" fill="none" stroke="{ca}" stroke-width="{1.5*s}" stroke-linecap="round"/>'''
    elif expressao == "triste":
        olhos = f'''<ellipse cx="{cx-6*s}" cy="{cy-3*s}" rx="{4*s}" ry="{4*s}" fill="#fff" opacity=".9"/>
        <circle cx="{cx-6*s}" cy="{cy-2*s}" r="{2.5*s}" fill="{ca}"/>
        <ellipse cx="{cx+6*s}" cy="{cy-3*s}" rx="{4*s}" ry="{4*s}" fill="#fff" opacity=".9"/>
        <circle cx="{cx+6*s}" cy="{cy-2*s}" r="{2.5*s}" fill="{ca}"/>
        <path d="M{cx-4*s} {cy+6*s} Q{cx} {cy+3*s} {cx+4*s} {cy+6*s}" fill="none" stroke="{ca}" stroke-width="{1.5*s}" stroke-linecap="round"/>
        <circle cx="{cx-8*s}" cy="{cy-8*s}" r="{1.5*s}" fill="{ca}" opacity=".3"/>'''
    elif expressao == "determinada":
        olhos = f'''<ellipse cx="{cx-7*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx-7*s}" cy="{cy-3*s}" r="{3*s}" fill="{ca}"/>
        <ellipse cx="{cx+7*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx+7*s}" cy="{cy-3*s}" r="{3*s}" fill="{ca}"/>
        <line x1="{cx-5*s}" y1="{cy+5*s}" x2="{cx+5*s}" y2="{cy+5*s}" stroke="{ca}" stroke-width="{2*s}" stroke-linecap="round"/>'''
    else:
        olhos = f'''<ellipse cx="{cx-6*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx-6*s}" cy="{cy-3*s}" r="{2.5*s}" fill="{ca}"/>
        <ellipse cx="{cx+6*s}" cy="{cy-4*s}" rx="{4*s}" ry="{5*s}" fill="#fff" opacity=".95"/>
        <circle cx="{cx+6*s}" cy="{cy-3*s}" r="{2.5*s}" fill="{ca}"/>
        <path d="M{cx-3*s} {cy+5*s} Q{cx} {cy+7*s} {cx+3*s} {cy+5*s}" fill="none" stroke="{ca}" stroke-width="{1*s}" stroke-linecap="round"/>'''

    # Cabelo (fibras opticas estilizadas)
    cabelo = f'''<path d="M{cx-14*s} {cy-14*s} Q{cx-18*s} {cy-28*s} {cx-10*s} {cy-30*s} Q{cx-4*s} {cy-32*s} {cx} {cy-24*s} Q{cx+4*s} {cy-32*s} {cx+10*s} {cy-30*s} Q{cx+18*s} {cy-28*s} {cx+14*s} {cy-14*s}" fill="{CORES['dark_med']}" stroke="{cs}" stroke-width="1" opacity=".8"/>
    <path d="M{cx-10*s} {cy-14*s} Q{cx-14*s} {cy-32*s} {cx-4*s} {cy-34*s} Q{cx} {cy-35*s} {cx} {cy-28*s}" fill="none" stroke="{cs}" stroke-width="1.5" opacity=".4"/>
    <path d="M{cx+10*s} {cy-14*s} Q{cx+14*s} {cy-32*s} {cx+4*s} {cy-34*s}" fill="none" stroke="{cs}" stroke-width="1.5" opacity=".4"/>
    <circle cx="{cx-12*s}" cy="{cy-30*s}" r="{1.5*s}" fill="{cs}" opacity=".6"><animate attributeName="opacity" values=".3;.8;.3" dur="2s" repeatCount="indefinite"/></circle>
    <circle cx="{cx+12*s}" cy="{cy-30*s}" r="{1.5*s}" fill="{cs}" opacity=".6"><animate attributeName="opacity" values=".5;.9;.5" dur="1.8s" repeatCount="indefinite"/></circle>'''

    return f'''<g>
    <defs>
        {_metal_grad(mg, pe, pc)}
        {_specular(sg, "40%", "30%")}
        <radialGradient id="{ng}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="{ca}" stop-opacity=".6"/>
            <stop offset="50%" stop-color="{ca}" stop-opacity=".2"/>
            <stop offset="100%" stop-color="{ca}" stop-opacity="0"/>
        </radialGradient>
    </defs>

    <ellipse cx="{cx}" cy="{cy+36*s}" rx="{24*s}" ry="{5*s}" fill="#000" opacity=".3"/>

    <!-- CORPO / TORSO -->
    <rect x="{cx-14*s}" y="{cy+18*s}" width="{28*s}" height="{22*s}" rx="{6*s}" fill="url(#{mg})" stroke="{pe}" stroke-width="1"/>
    <rect x="{cx-12*s}" y="{cy+20*s}" width="{24*s}" height="{18*s}" rx="{4*s}" fill="url(#{sg})"/>

    <!-- REATOR CORACAO -->
    <circle cx="{cx}" cy="{cy+29*s}" r="{7*s}" fill="url(#{ng})"/>
    <circle cx="{cx}" cy="{cy+29*s}" r="{4*s}" fill="{ca}" opacity=".7"/>
    <circle cx="{cx-1*s}" cy="{cy+28*s}" r="{1.5*s}" fill="#fff" opacity=".8"/>
    <circle cx="{cx}" cy="{cy+29*s}" r="{10*s}" fill="none" stroke="{ca}" stroke-width="1" opacity=".3">
        <animate attributeName="r" values="6;12;6" dur="1.2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values=".3;.08;.3" dur="1.2s" repeatCount="indefinite"/>
    </circle>

    <!-- LINHAS NEON NO CORPO -->
    <line x1="{cx-10*s}" y1="{cy+22*s}" x2="{cx-5*s}" y2="{cy+24*s}" stroke="{ca}" stroke-width="1" opacity=".5"/>
    <line x1="{cx+10*s}" y1="{cy+22*s}" x2="{cx+5*s}" y2="{cy+24*s}" stroke="{ca}" stroke-width="1" opacity=".5"/>
    <line x1="{cx-8*s}" y1="{cy+34*s}" x2="{cx+8*s}" y2="{cy+34*s}" stroke="{ca}" stroke-width=".8" opacity=".4"/>

    <!-- PESCOCO -->
    <rect x="{cx-5*s}" y="{cy-22*s}" width="{10*s}" height="{6*s}" rx="{2*s}" fill="{pe}" stroke="{pm}" stroke-width=".8"/>
    <line x1="{cx-3*s}" y1="{cy-20*s}" x2="{cx+3*s}" y2="{cy-20*s}" stroke="{ca}" stroke-width=".8" opacity=".5"/>

    <!-- CABECA -->
    <ellipse cx="{cx}" cy="{cy-8*s}" rx="{16*s}" ry="{18*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width="1"/>
    <ellipse cx="{cx}" cy="{cy-6*s}" rx="{14*s}" ry="{15*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width=".5" opacity=".5"/>

    <!-- CABELO -->
    {cabelo}

    <!-- OLHOS E BOCA -->
    {olhos}

    <!-- LINEA NEON TESTA -->
    <path d="M{cx-6*s} {cy-20*s} Q{cx} {cy-22*s} {cx+6*s} {cy-20*s}" fill="none" stroke="{ca}" stroke-width="1" opacity=".5"/>
    <circle cx="{cx}" cy="{cy-21*s}" r="1" fill="{ca}" opacity=".7"><animate attributeName="opacity" values=".3;1;.3" dur="1.5s" repeatCount="indefinite"/></circle>

    <!-- BRACOS -->
    <rect x="{cx-18*s}" y="{cy+12*s}" width="{5*s}" height="{16*s}" rx="{2.5*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width=".8"/>
    <rect x="{cx+13*s}" y="{cy+12*s}" width="{5*s}" height="{16*s}" rx="{2.5*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width=".8"/>

    <!-- MAOS -->
    <circle cx="{cx-18*s}" cy="{cy+30*s}" r="{4*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width=".8"/>
    <circle cx="{cx+18*s}" cy="{cy+30*s}" r="{4*s}" fill="{CORES['pele']}" stroke="{pe}" stroke-width=".8"/>
    <rect x="{cx-21*s}" y="{cy+31*s}" width="{2*s}" height="{4*s}" rx="1" fill="{pc}" opacity=".5"/>
    <rect x="{cx-17*s}" y="{cy+31*s}" width="{2*s}" height="{4*s}" rx="1" fill="{pc}" opacity=".5"/>
    <rect x="{cx+15*s}" y="{cy+31*s}" width="{2*s}" height="{4*s}" rx="1" fill="{pc}" opacity=".5"/>
    <rect x="{cx+19*s}" y="{cy+31*s}" width="{2*s}" height="{4*s}" rx="1" fill="{pc}" opacity=".5"/>

    <!-- PERNAS -->
    <rect x="{cx-10*s}" y="{cy+40*s}" width="{7*s}" height="{14*s}" rx="{3*s}" fill="{CORES['dark_med']}" stroke="{pe}" stroke-width=".8"/>
    <rect x="{cx+3*s}" y="{cy+40*s}" width="{7*s}" height="{14*s}" rx="{3*s}" fill="{CORES['dark_med']}" stroke="{pe}" stroke-width=".8"/>

    <!-- BOTAS -->
    <rect x="{cx-12*s}" y="{cy+52*s}" width="{10*s}" height="{4*s}" rx="{2*s}" fill="{pe}" stroke="{pm}" stroke-width=".8"/>
    <rect x="{cx+2*s}" y="{cy+52*s}" width="{10*s}" height="{4*s}" rx="{2*s}" fill="{pe}" stroke="{pm}" stroke-width=".8"/>
    <line x1="{cx-9*s}" y1="{cy+54*s}" x2="{cx-5*s}" y2="{cy+54*s}" stroke="{ca}" stroke-width="1" opacity=".4"/>
    <line x1="{cx+5*s}" y1="{cy+54*s}" x2="{cx+9*s}" y2="{cy+54*s}" stroke="{ca}" stroke-width="1" opacity=".4"/>
</g>'''


def _drone(cx, cy, s=1.0, uid=""):
    """Drone companheiro futurista."""
    ca = CORES["ciano"]
    pm = CORES["prata"]
    pe = CORES["prata_escuro"]

    return f'''<g>
    <!-- SOMBRA -->
    <ellipse cx="{cx}" cy="{cy+12*s}" rx="{10*s}" ry="{3*s}" fill="#000" opacity=".2"/>

    <!-- CORPO DRONE -->
    <ellipse cx="{cx}" cy="{cy}" rx="{10*s}" ry="{6*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <ellipse cx="{cx}" cy="{cy}" rx="{8*s}" ry="{4*s}" fill="{CORES['dark_bg']}"/>

    <!-- HELICES -->
    <ellipse cx="{cx-8*s}" cy="{cy-4*s}" rx="{6*s}" ry="{2*s}" fill="none" stroke="{ca}" stroke-width="1" opacity=".5">
        <animateTransform attributeName="transform" type="rotate" from="0 {cx-8*s} {cy-4*s}" to="360 {cx-8*s} {cy-4*s}" dur=".4s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="{cx+8*s}" cy="{cy-4*s}" rx="{6*s}" ry="{2*s}" fill="none" stroke="{ca}" stroke-width="1" opacity=".5">
        <animateTransform attributeName="transform" type="rotate" from="0 {cx+8*s} {cy-4*s}" to="360 {cx+8*s} {cy-4*s}" dur=".4s" repeatCount="indefinite"/>
    </ellipse>

    <!-- OLHO DRONE (CAMERA) -->
    <circle cx="{cx}" cy="{cy}" r="{3*s}" fill="#fff" opacity=".9"/>
    <circle cx="{cx}" cy="{cy}" r="{2*s}" fill="{ca}">
        <animate attributeName="fill" values="#00e5ff;#ff00ff;#00e5ff" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx-1*s}" cy="{cy-1*s}" r="1" fill="#fff" opacity=".7"/>

    <!-- ANTENINHA -->
    <line x1="{cx}" y1="{cy-6*s}" x2="{cx}" y2="{cy-10*s}" stroke="{pm}" stroke-width="1" stroke-linecap="round"/>
    <circle cx="{cx}" cy="{cy-11*s}" r="{1.5*s}" fill="{ca}" opacity=".8">
        <animate attributeName="opacity" values=".3;1;.3" dur=".8s" repeatCount="indefinite"/>
    </circle>
</g>'''


def _fundo_lab(grad_id, cor_fundo="#0a0a1a", cor_meio="#12122a"):
    return f'''<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#fff" opacity=".12">
    <circle cx="80" cy="50" r="1"/><circle cx="200" cy="40" r="1.5"/>
    <circle cx="350" cy="55" r="1.2"/><circle cx="550" cy="45" r="1"/>
    <circle cx="700" cy="65" r="1.5"/><circle cx="150" cy="120" r="1"/>
    <circle cx="650" cy="110" r="1.2"/><circle cx="450" cy="35" r="1"/>
    <circle cx="300" cy="75" r="1.3"/><circle cx="90" cy="150" r="1"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="{cor_meio}" opacity=".4"/>
<rect x="0" y="380" width="800" height="220" fill="{cor_fundo}" opacity=".5"/>
<rect x="0" y="375" width="800" height="8" fill="#00e5ff" opacity=".08"/>'''


def _fundo_cidade(grad_id):
    return f'''<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#00e5ff" opacity=".12">
    <circle cx="80" cy="50" r="1"/><circle cx="200" cy="40" r="1.5"/>
    <circle cx="350" cy="55" r="1.2"/><circle cx="550" cy="45" r="1"/>
    <circle cx="700" cy="65" r="1.5"/><circle cx="150" cy="120" r="1"/>
    <circle cx="650" cy="110" r="1.2"/><circle cx="450" cy="35" r="1"/>
</g>
<!-- PREDIOS -->
<g opacity=".6">
    <rect x="30" y="150" width="60" height="450" fill="#0d0d2b" stroke="#00e5ff" stroke-width=".5" opacity=".8"/>
    <rect x="100" y="100" width="50" height="500" fill="#12122a" stroke="#ff00ff" stroke-width=".5" opacity=".7"/>
    <rect x="170" y="180" width="70" height="420" fill="#0d0d2b" stroke="#00e5ff" stroke-width=".5" opacity=".6"/>
    <rect x="260" y="80" width="45" height="520" fill="#12122a" stroke="#ffd700" stroke-width=".5" opacity=".7"/>
    <rect x="320" y="130" width="55" height="470" fill="#0d0d2b" stroke="#ff00ff" stroke-width=".5" opacity=".6"/>
    <rect x="400" y="60" width="65" height="540" fill="#12122a" stroke="#00e5ff" stroke-width=".5" opacity=".8"/>
    <rect x="480" y="170" width="50" height="430" fill="#0d0d2b" stroke="#ffd700" stroke-width=".5" opacity=".6"/>
    <rect x="550" y="90" width="60" height="510" fill="#12122a" stroke="#ff00ff" stroke-width=".5" opacity=".7"/>
    <rect x="630" y="140" width="55" height="460" fill="#0d0d2b" stroke="#00e5ff" stroke-width=".5" opacity=".6"/>
    <rect x="700" y="110" width="70" height="490" fill="#12122a" stroke="#ff00ff" stroke-width=".5" opacity=".7"/>
</g>
<!-- JANELAS -->
<g fill="#ffd700" opacity=".15">
    <rect x="35" y="160" width="8" height="6"/><rect x="55" y="200" width="8" height="6"/>
    <rect x="35" y="240" width="8" height="6"/><rect x="55" y="280" width="8" height="6"/>
    <rect x="35" y="320" width="8" height="6"/><rect x="55" y="360" width="8" height="6"/>
    <rect x="110" y="110" width="8" height="6"/><rect x="130" y="150" width="8" height="6"/>
    <rect x="110" y="190" width="8" height="6"/><rect x="130" y="230" width="8" height="6"/>
    <rect x="185" y="190" width="8" height="6"/><rect x="210" y="230" width="8" height="6"/>
    <rect x="185" y="270" width="8" height="6"/><rect x="210" y="310" width="8" height="6"/>
    <rect x="270" y="90" width="8" height="6"/><rect x="290" y="130" width="8" height="6"/>
    <rect x="410" y="70" width="8" height="6"/><rect x="440" y="110" width="8" height="6"/>
    <rect x="410" y="150" width="8" height="6"/><rect x="440" y="190" width="8" height="6"/>
    <rect x="560" y="100" width="8" height="6"/><rect x="590" y="140" width="8" height="6"/>
    <rect x="560" y="180" width="8" height="6"/><rect x="590" y="220" width="8" height="6"/>
    <rect x="710" y="120" width="8" height="6"/><rect x="740" y="160" width="8" height="6"/>
</g>
<!-- LETREIROS HOLO -->
<g font-family="'Courier New',monospace" font-size="8" fill="#ff00ff" opacity=".3">
    <text x="35" y="380" transform="rotate(-90,35,380)">NEON CITY</text>
</g>
<text x="410" y="380" font-family="'Courier New',monospace" font-size="7" fill="#00e5ff" opacity=".25" transform="rotate(-90,410,380)">CYBERPUNK 3000</text>
<!-- CARRO VOADOR -->
<g opacity=".4">
    <ellipse cx="150" cy="80" rx="20" ry="5" fill="#ff00ff" opacity=".3"/>
    <rect x="135" y="75" width="30" height="8" rx="3" fill="#333" stroke="#00e5ff" stroke-width=".5"/>
</g>
<ellipse cx="620" cy="60" rx="18" ry="4" fill="#00e5ff" opacity=".2"/>
<rect x="608" y="56" width="25" height="7" rx="3" fill="#333" stroke="#ff00ff" stroke-width=".5"/>

<ellipse cx="400" cy="660" rx="580" ry="160" fill="#0a0a1a" opacity=".6"/>
<rect x="0" y="380" width="800" height="220" fill="#0a0a1a" opacity=".4"/>
<rect x="0" y="375" width="800" height="5" fill="#ff00ff" opacity=".15"/>'''


def _fundo_jardim(grad_id):
    return f'''<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#00ff41" opacity=".08">
    <circle cx="100" cy="80" r="30"/><circle cx="300" cy="60" r="40"/>
    <circle cx="550" cy="70" r="35"/><circle cx="700" cy="90" r="25"/>
</g>
<!-- PLANTAS BIOLUMINESCENTES -->
<g>
    <path d="M150 380 Q140 300 120 250 Q110 220 130 200" fill="none" stroke="#00ff41" stroke-width="2" opacity=".6"/>
    <path d="M150 380 Q160 290 180 240 Q190 210 170 190" fill="none" stroke="#00ff41" stroke-width="2" opacity=".5"/>
    <circle cx="130" cy="200" r="4" fill="#00ff41" opacity=".8"><animate attributeName="opacity" values=".3;.9;.3" dur="2s" repeatCount="indefinite"/></circle>
    <circle cx="170" cy="190" r="3" fill="#00ff41" opacity=".7"><animate attributeName="opacity" values=".5;1;.5" dur="1.5s" repeatCount="indefinite"/></circle>

    <path d="M400 380 Q390 280 370 230 Q360 200 380 180" fill="none" stroke="#ff00ff" stroke-width="2" opacity=".5"/>
    <path d="M400 380 Q410 270 430 220 Q440 190 420 170" fill="none" stroke="#ff00ff" stroke-width="2" opacity=".6"/>
    <circle cx="380" cy="180" r="5" fill="#ff00ff" opacity=".7"><animate attributeName="opacity" values=".2;.8;.2" dur="2.5s" repeatCount="indefinite"/></circle>
    <circle cx="420" cy="170" r="4" fill="#ff00ff" opacity=".8"><animate attributeName="opacity" values=".4;1;.4" dur="1.8s" repeatCount="indefinite"/></circle>

    <path d="M650 380 Q640 300 620 260 Q610 230 630 210" fill="none" stroke="#ffd700" stroke-width="2" opacity=".5"/>
    <path d="M650 380 Q660 290 680 240 Q690 210 670 195" fill="none" stroke="#ffd700" stroke-width="2" opacity=".4"/>
    <circle cx="630" cy="210" r="3" fill="#ffd700" opacity=".7"><animate attributeName="opacity" values=".3;.9;.3" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="670" cy="195" r="4" fill="#ffd700" opacity=".6"><animate attributeName="opacity" values=".4;1;.4" dur="1.6s" repeatCount="indefinite"/></circle>
</g>
<!-- COGOUMELOS BIOLUM -->
<g>
    <ellipse cx="250" cy="360" rx="12" ry="6" fill="#00ff41" opacity=".5"/>
    <rect x="248" y="360" width="4" height="15" fill="#00ff41" opacity=".4"/>
    <ellipse cx="250" cy="358" rx="14" ry="7" fill="#00ff41" opacity=".3"/>

    <ellipse cx="500" cy="350" rx="10" ry="5" fill="#ff00ff" opacity=".4"/>
    <rect x="498" y="350" width="4" height="12" fill="#ff00ff" opacity=".3"/>
    <ellipse cx="500" cy="348" rx="12" ry="6" fill="#ff00ff" opacity=".25"/>
</g>
<!-- PARTICULAS FLUTUANTES -->
<g fill="#00ff41" opacity=".3">
    <circle cx="200" cy="150" r="1.5"><animate attributeName="cy" values="150;130;150" dur="3s" repeatCount="indefinite"/></circle>
    <circle cx="350" cy="120" r="1"><animate attributeName="cy" values="120;100;120" dur="2.5s" repeatCount="indefinite"/></circle>
    <circle cx="500" cy="140" r="1.5"><animate attributeName="cy" values="140;120;140" dur="3.5s" repeatCount="indefinite"/></circle>
    <circle cx="600" cy="130" r="1"><animate attributeName="cy" values="130;110;130" dur="2.8s" repeatCount="indefinite"/></circle>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#0a0a1a" opacity=".5"/>
<rect x="0" y="380" width="800" height="220" fill="#0a0a1a" opacity=".4"/>'''


def gerar_svg_capa(titulo, subtitulo):
    cn = CORES["ciano"]
    mg = CORES["magenta"]
    return f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="bg-cap" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0a0a1a"/>
        <stop offset="30%" stop-color="#12122a"/>
        <stop offset="70%" stop-color="#1a0033"/>
        <stop offset="100%" stop-color="#0a0a1a"/>
    </linearGradient>
    <radialGradient id="gl-cap" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stop-color="{cn}" stop-opacity=".2"/>
        <stop offset="100%" stop-color="{cn}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
        <rect width="40" height="40" fill="none"/>
        <path d="M40 0 L0 0 0 40" fill="none" stroke="{cn}" stroke-width=".3" opacity=".06"/>
    </pattern>
    <filter id="brilho">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="glow-neon">
        <feGaussianBlur stdDeviation="6" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
</defs>
<rect width="800" height="600" fill="url(#bg-cap)"/>
<rect width="800" height="600" fill="url(#grid)"/>
<circle cx="400" cy="220" r="180" fill="url(#gl-cap)"/>
<circle cx="200" cy="80" r="1.5" fill="#fff" opacity=".4"/>
<circle cx="550" cy="60" r="2" fill="#fff" opacity=".5"/>
<circle cx="700" cy="120" r="1.5" fill="#fff" opacity=".3"/>
<circle cx="120" cy="180" r="1.5" fill="#fff" opacity=".4"/>
<circle cx="680" cy="180" r="1.5" fill="#fff" opacity=".35"/>
<text x="400" y="450" text-anchor="middle" font-family="'Bangers',cursive" font-size="52" fill="{cn}" font-weight="900" opacity=".95" filter="url(#brilho)">Aurora Sintetica</text>
<text x="400" y="490" text-anchor="middle" font-family="'Quicksand',sans-serif" font-size="18" fill="{mg}" opacity=".85">Uma Historia de Luz na Cidade Neon</text>
<g transform="translate(400,210)">
    {_aurora_detalhada(0, 0, 1.5, "feliz", "cap", cn, mg)}
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#0a0a1a" opacity=".5"/>
<ellipse cx="200" cy="680" rx="350" ry="140" fill="#12122a" opacity=".3"/>
<ellipse cx="650" cy="670" rx="300" ry="130" fill="#1a0033" opacity=".25"/>
</svg>'''


def gerar_svg_pagina(numero, cena):
    bg = f"bg{numero:02d}"
    gl = f"gl{numero:02d}"

    cn = CORES["ciano"]
    mg = CORES["magenta"]
    vn = CORES["verde_neon"]

    cenas = {
        "despertar": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="50%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#12122a"/></linearGradient>
<radialGradient id="{gl}" cx="50%" cy="40%" r="50%"><stop offset="0%" stop-color="{cn}" stop-opacity=".4"/><stop offset="100%" stop-color="{cn}" stop-opacity="0"/></radialGradient></defs>
{_fundo_lab(bg)}
<circle cx="400" cy="200" r="120" fill="url({gl})"/>
<!-- MESA DE LAB -->
<rect x="200" y="340" width="400" height="200" rx="10" fill="{CORES['dark_med']}" stroke="{cn}" stroke-width="1.5" opacity=".6"/>
<rect x="210" y="350" width="380" height="180" rx="6" fill="{CORES['dark_bg']}" opacity=".8"/>
<!-- HOLOGRAMA -->
<circle cx="400" cy="220" r="60" fill="none" stroke="{cn}" stroke-width="1" opacity=".3">
    <animate attributeName="r" values="55;65;55" dur="2s" repeatCount="indefinite"/>
</circle>
<g transform="translate(400,240)">
    {_aurora_detalhada(0, 0, 1.2, "neutro", "p1", cn, mg)}
</g>
<!-- LINHAS HOLO ao redor -->
<circle cx="400" cy="240" r="80" fill="none" stroke="{mg}" stroke-width=".5" opacity=".2" stroke-dasharray="4,8">
    <animateTransform attributeName="transform" type="rotate" from="0 400 240" to="360 400 240" dur="8s" repeatCount="indefinite"/>
</circle>
</svg>''',

        "cidade": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="40%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#12122a"/></linearGradient></defs>
{_fundo_cidade(bg)}
<g transform="translate(400,260)">
    {_aurora_detalhada(0, 0, 1.1, "feliz", "p2", cn, mg)}
</g>
</svg>''',

        "drone": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="50%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#12122a"/></linearGradient></defs>
{_fundo_cidade(bg)}
<g transform="translate(320,260)">
    {_aurora_detalhada(0, 0, 1.0, "triste", "p3d", cn, mg)}
</g>
<g transform="translate(540,280)">
    {_drone(0, 0, 1.2, "p3")}
</g>
<circle cx="540" cy="280" r="15" fill="none" stroke="{mg}" stroke-width="1" opacity=".15">
    <animate attributeName="r" values="12;20;12" dur="1s" repeatCount="indefinite"/>
</circle>
</svg>''',

        "conexao": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="50%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#12122a"/></linearGradient>
<radialGradient id="{gl}" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{cn}" stop-opacity=".3"/><stop offset="100%" stop-color="{cn}" stop-opacity="0"/></radialGradient></defs>
{_fundo_cidade(bg)}
<circle cx="400" cy="250" r="140" fill="url({gl})"/>
<!-- FAISCAS ELETRICAS -->
<g opacity=".4">
    <line x1="260" y1="220" x2="300" y2="240" stroke="{cn}" stroke-width="1.5"><animate attributeName="opacity" values="0;1;0" dur=".3s" repeatCount="indefinite"/></line>
    <line x1="540" y1="240" x2="500" y2="260" stroke="{cn}" stroke-width="1.5"><animate attributeName="opacity" values="0;1;0" dur=".4s" repeatCount="indefinite"/></line>
</g>
<g transform="translate(280,250)">
    {_aurora_detalhada(0, 0, 1.0, "feliz", "p4a", cn, mg)}
</g>
<g transform="translate(540,265)">
    {_drone(0, 0, 1.3, "p4d")}
</g>
<path d="M330 270 Q400 300 490 280" fill="none" stroke="{cn}" stroke-width="1.5" opacity=".4" stroke-dasharray="6,4">
    <animate attributeName="stroke-dashoffset" values="0;-20" dur=".8s" repeatCount="indefinite"/>
</path>
</svg>''',

        "jardim": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="30%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#0a1a0a"/></linearGradient></defs>
{_fundo_jardim(bg)}
<g transform="translate(300,260)">
    {_aurora_detalhada(0, 0, 1.0, "feliz", "p5a", vn, mg)}
</g>
<g transform="translate(540,240)">
    {_drone(0, 0, 1.1, "p5d")}
</g>
</svg>''',

        "ameaca": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1a0000"/><stop offset="50%" stop-color="#0a000a"/><stop offset="100%" stop-color="#050510"/></linearGradient>
<radialGradient id="{gl}" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{mg}" stop-opacity=".2"/><stop offset="100%" stop-color="{mg}" stop-opacity="0"/></radialGradient></defs>
{_fundo_cidade(bg)}
<!-- LUZ VERMELHA -->
<circle cx="400" cy="250" r="180" fill="url({gl})"/>
<!-- SOMBRAS AMEACADORAS -->
<g opacity=".5">
    <rect x="150" y="280" width="60" height="120" rx="8" fill="#1a0000" stroke="#ff1744" stroke-width="1.5"/>
    <circle cx="180" cy="270" r="25" fill="#1a0000" stroke="#ff1744" stroke-width="1.5"/>
    <circle cx="175" cy="265" r="5" fill="#ff1744" opacity=".8"/>
    <circle cx="185" cy="265" r="5" fill="#ff1744" opacity=".8"/>
    <rect x="580" y="280" width="60" height="120" rx="8" fill="#1a0000" stroke="#ff1744" stroke-width="1.5"/>
    <circle cx="610" cy="270" r="25" fill="#1a0000" stroke="#ff1744" stroke-width="1.5"/>
    <circle cx="605" cy="265" r="5" fill="#ff1744" opacity=".8"/>
    <circle cx="615" cy="265" r="5" fill="#ff1744" opacity=".8"/>
</g>
<g transform="translate(400,260)">
    {_aurora_detalhada(0, 0, 1.1, "determinada", "p6", cn, mg)}
</g>
<g transform="translate(440,230)">
    {_drone(0, 0, .9, "p6d")}
</g>
</svg>''',

        "fuga": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050510"/><stop offset="40%" stop-color="#0a0a1a"/><stop offset="100%" stop-color="#12122a"/></linearGradient></defs>
{_fundo_cidade(bg)}
<!-- TRAJETORIA DE FUGA -->
<path d="M200 320 Q300 200 500 180 Q600 170 650 120" fill="none" stroke="{cn}" stroke-width="2" opacity=".3" stroke-dasharray="8,6">
    <animate attributeName="stroke-dashoffset" values="0;-28" dur=".6s" repeatCount="indefinite"/>
</path>
<g transform="translate(500,180) rotate(-15)">
    {_aurora_detalhada(0, 0, .9, "determinada", "p7", cn, mg)}
</g>
<g transform="translate(550,165)">
    {_drone(0, 0, .9, "p7d")}
</g>
<g opacity=".2">
    <line x1="200" y1="320" x2="250" y2="310" stroke="#ff1744" stroke-width="1.5"/>
    <line x1="200" y1="330" x2="250" y2="320" stroke="#ff1744" stroke-width="1.5"/>
</g>
</svg>''',

        "comeco": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a3e"/><stop offset="40%" stop-color="#0a0a2a"/><stop offset="100%" stop-color="#0a1a0a"/>
    </linearGradient>
    <radialGradient id="{gl}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ffd700" stop-opacity=".15"/><stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
</defs>
<rect width="800" height="600" fill="url(#{bg})"/>
<!-- SOL NASCENTE -->
<circle cx="400" cy="200" r="100" fill="url({gl})"/>
<circle cx="400" cy="220" r="40" fill="#ffd700" opacity=".08"/>
<circle cx="400" cy="220" r="25" fill="#ffd700" opacity=".12"/>
<circle cx="400" cy="220" r="15" fill="#ffd700" opacity=".2"/>
<!-- GRAMA / VALLE -->
<path d="M0 400 Q200 360 400 380 Q600 400 800 370 L800 600 L0 600 Z" fill="#0a1a0a" opacity=".6"/>
<path d="M0 430 Q200 400 400 420 Q600 440 800 410 L800 600 L0 600 Z" fill="#0a2a0a" opacity=".4"/>
<!-- FLORES BLOOM -->
<g>
    <circle cx="200" cy="390" r="3" fill="#ff00ff" opacity=".6"><animate attributeName="cy" values="390;380;390" dur="3s" repeatCount="indefinite"/></circle>
    <circle cx="350" cy="400" r="2" fill="#00e5ff" opacity=".5"><animate attributeName="cy" values="400;390;400" dur="2.5s" repeatCount="indefinite"/></circle>
    <circle cx="500" cy="395" r="2.5" fill="#ffd700" opacity=".5"><animate attributeName="cy" values="395;385;395" dur="2.8s" repeatCount="indefinite"/></circle>
    <circle cx="620" cy="385" r="2" fill="#00ff41" opacity=".4"><animate attributeName="cy" values="385;375;385" dur="3.2s" repeatCount="indefinite"/></circle>
</g>
<g transform="translate(320,270)">
    {_aurora_detalhada(0, 0, 1.1, "feliz", "p8", cn, mg)}
</g>
<g transform="translate(520,250)">
    {_drone(0, 0, 1.2, "p8d")}
</g>
<g fill="#ffd700" opacity=".15">
    <circle cx="100" cy="100" r="1.5"/><circle cx="250" cy="80" r="2"/>
    <circle cx="550" cy="90" r="1.5"/><circle cx="700" cy="110" r="2"/>
    <circle cx="180" cy="150" r="1"/><circle cx="650" cy="140" r="1.5"/>
</g>
</svg>''',
    }

    return cenas.get(cena, list(cenas.values())[0])


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "examples")
    os.makedirs(out, exist_ok=True)

    livro = {
        "titulo": HISTORIA["titulo"], "subtitulo": HISTORIA.get("subtitulo", ""),
        "autor": HISTORIA.get("autor", ""), "faixa_etaria": HISTORIA.get("faixa_etaria", "6 — 12 anos"),
        "lang": HISTORIA.get("lang", "pt-BR"), "texto_final": HISTORIA.get("texto_final", "Fim!"),
        "capa_svg": gerar_svg_capa(HISTORIA["titulo"], HISTORIA.get("subtitulo", "")),
        "paginas": []
    }

    posicoes = {1:"tr", 2:"br", 3:"bl", 4:"tr", 5:"br", 6:"tl", 7:"tr", 8:"br"}
    for p in HISTORIA["paginas"]:
        livro["paginas"].append({
            "texto": p["texto"], "dialogo": p.get("dialogo", ""),
            "dialogo_pos": posicoes.get(p["numero"], "tr"),
            "svg": gerar_svg_pagina(p["numero"], p.get("cena", "despertar")),
            "audio": ""
        })

    json_path = os.path.join(out, "book_aurora_futurista.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(livro, f, ensure_ascii=False, indent=2)

    html_path = os.path.join(os.path.dirname(__file__), "..", "output", "aurora_futurista_quadrinho.html")
    print(f"book.json: {json_path}")
    print(f"Build: python \"{os.path.join(os.path.dirname(__file__), 'build_livro.py')}\" \"{json_path}\" \"{html_path}\" --template quadrinho")
