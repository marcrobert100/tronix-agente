#!/usr/bin/env python3
"""Gera livro Robo Zukinha com personagens realistas (SVG metalizado 3D)."""

import json, os, sys

CORES = {
    "prata": "#c0c0c0", "prata_escuro": "#808080", "prata_claro": "#e8e8e8",
    "ouro": "#f5a623", "ouro_escuro": "#c77800",
    "cobre": "#cd7f32", "cobre_escuro": "#8b5e3c",
    "azul_metal": "#2196f3", "azul_escuro": "#1565c0",
    "vermelho": "#ff1744", "vermelho_escuro": "#b71c1c",
    "verde": "#4caf50", "verde_escuro": "#2e7d32",
    "ciano": "#00e5ff", "roxo": "#7c4dff",
    "coral": "#ff7043",
    "dark_bg": "#0d0d2b", "dark_med": "#1a1a4e",
    "sombra": "#1a1a2e", "branco": "#ffffff",
}

HISTORIA = {
    "titulo": "Robo Zukinha",
    "subtitulo": "O Robo Mais Doido da Galaxia",
    "autor": "Marcos Roberto",
    "faixa_etaria": "3 - 8 anos",
    "lang": "pt-BR",
    "texto_final": "Zukinha aprendeu: ser doido e ser feliz do seu proprio jeito. Fim!",
    "paginas": [
        {"numero": 1, "titulo": "O Despertar",
         "texto": "La no laboratorio do Vovo Chico, na noite de ontem, um raio muito forte caiu bem na tomada. E de repente... ZUKINHA ACORDOU!",
         "dialogo": "Zzzt! Eu... estou... VIVO! Oba!", "cena": "despertar"},
        {"numero": 2, "titulo": "Antenas Trocadas",
         "texto": "Zukinha pulou da mesa e colocou as antenas no lugar errado. Uma no olho e outra na boca!",
         "dialogo": "Puft! Agora eu enxergo pelo nariz e cheiro pelos olhos!", "cena": "antenas"},
        {"numero": 3, "titulo": "Misturando Tudo",
         "texto": "Na cozinha, Zukinha tentou fazer cafe. Mas colocou pasta de dente no bule e cafe na escova.",
         "dialogo": "Hmm, cafe com menta! O cafe mais refrescante do mundo!", "cena": "cozinha"},
        {"numero": 4, "titulo": "Roupa Doida",
         "texto": "Zukinha foi se vestir. Calcou a luva no pe, a meia na mao, e usou a calca como cachecol.",
         "dialogo": "Estou elegantemente doido! A moda robo e assim!", "cena": "roupa"},
        {"numero": 5, "titulo": "Danca de Robo",
         "texto": "Uma musica comecou a tocar. Zukinha comecou a dancar: chacoalhava as engrenagens, girava a helice e apitava no ritmo!",
         "dialogo": "Tchum tchum tcha! Sou o robo mais feliz da galaxia!", "cena": "danca"},
        {"numero": 6, "titulo": "Criando um Amigo",
         "texto": "Zukinha juntou sucata, parafusos e uma lata velha. Com faiscas e risadas, criou... ROBOTCHUDO, seu novo amigo!",
         "dialogo": "Voce tambem e doido? Ah, que bom! Vamos baguncar juntos!", "cena": "amigo"},
        {"numero": 7, "titulo": "Festa Maluca",
         "texto": "Os dois robos fizeram uma festa no laboratorio. Jogaram confete de parafuso, soltaram bolhas de sabao eletricas e dancaram ate o chao tremer.",
         "dialogo": "Essa e a melhor festa robotica de todos os tempos! Wheee!", "cena": "festa"},
        {"numero": 8, "titulo": "Hora de Carregar",
         "texto": "Cansados, Zukinha e Robotchudo sentaram perto da tomada. Com os olhinhos piscando devagar, deram a mao e foram carregar juntos.",
         "dialogo": "Ate amanha... amigo... Zzzzt...", "cena": "carregar"},
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


def _specular(gid, cx, cy):
    return f'''<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="50%">
        <stop offset="0%" stop-color="#fff" stop-opacity="0.4"/>
        <stop offset="50%" stop-color="#fff" stop-opacity="0.05"/>
        <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>'''


def _robo_detalhado(cx, cy, s=1.0, expr="feliz", uid="",
                    cor_metal="#2196f3", cor_escuro="#1565c0"):
    """Robo 3D realista com metalizado, parafusos, juntas, visor."""
    g = f"r{uid}" if uid else f"r{cx}{cy}"
    bg = CORES["dark_bg"]
    pm = CORES["prata"]
    pe = CORES["prata_escuro"]
    pc = CORES["prata_claro"]

    cor = cor_metal
    ce = cor_escuro

    # Visor/olhos conforme expressao
    if expr == "feliz":
        olhos = f'''<ellipse cx="{cx-8*s}" cy="{cy-2*s}" rx="{6*s}" ry="{5*s}" fill="#fff" opacity="0.95"/>
        <circle cx="{cx-8*s}" cy="{cy-1*s}" r="{3.5*s}" fill="#1a1a2e"/>
        <circle cx="{cx-9*s}" cy="{cy-3*s}" r="{1.5*s}" fill="#fff"/>
        <ellipse cx="{cx+8*s}" cy="{cy-2*s}" rx="{6*s}" ry="{5*s}" fill="#fff" opacity="0.95"/>
        <circle cx="{cx+8*s}" cy="{cy-1*s}" r="{3.5*s}" fill="#1a1a2e"/>
        <circle cx="{cx+7*s}" cy="{cy-3*s}" r="{1.5*s}" fill="#fff"/>'''
        boca = f'''<path d="M{cx-10*s} {cy+10*s} Q{cx} {cy+20*s} {cx+10*s} {cy+10*s}" fill="none" stroke="#1a1a2e" stroke-width="{2*s}" stroke-linecap="round"/>
        <path d="M{cx-6*s} {cy+12*s} Q{cx-2*s} {cy+18*s} {cx+2*s} {cy+12*s}" fill="#1a1a2e" opacity="0.3"/>'''
    elif expr == "louco":
        olhos = f'''<circle cx="{cx-10*s}" cy="{cy-6*s}" r="{6*s}" fill="#fff"/>
        <circle cx="{cx-8*s}" cy="{cy-8*s}" r="{3.5*s}" fill="#ff1744"/>
        <circle cx="{cx+12*s}" cy="{cy-4*s}" r="{5*s}" fill="#fff"/>
        <circle cx="{cx+14*s}" cy="{cy-6*s}" r="{3.5*s}" fill="#ff1744"/>'''
        boca = f'''<path d="M{cx-14*s} {cy+12*s} Q{cx-4*s} {cy+28*s} {cx+6*s} {cy+12*s} Q{cx+8*s} {cy+18*s} {cx+16*s} {cy+12*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>
        <path d="M{cx-8*s} {cy+15*s} Q{cx-2*s} {cy+24*s} {cx+4*s} {cy+15*s}" fill="#1a1a2e" opacity="0.2"/>'''
    elif expr == "sono":
        olhos = f'''<path d="M{cx-14*s} {cy-2*s} Q{cx-8*s} {cy+4*s} {cx-2*s} {cy-2*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>
        <path d="M{cx+2*s} {cy-2*s} Q{cx+8*s} {cy+4*s} {cx+14*s} {cy-2*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>'''
        boca = f'<path d="M{cx-6*s} {cy+10*s} Q{cx} {cy+14*s} {cx+6*s} {cy+10*s}" fill="none" stroke="#1a1a2e" stroke-width="{1.5*s}" stroke-linecap="round"/>'
    else:
        olhos = f'''<ellipse cx="{cx-8*s}" cy="{cy-2*s}" rx="{5*s}" ry="{6*s}" fill="#fff"/>
        <circle cx="{cx-8*s}" cy="{cy-1*s}" r="{3*s}" fill="#1a1a2e"/>
        <ellipse cx="{cx+8*s}" cy="{cy-2*s}" rx="{5*s}" ry="{6*s}" fill="#fff"/>
        <circle cx="{cx+8*s}" cy="{cy-1*s}" r="{3*s}" fill="#1a1a2e"/>'''
        boca = f'<path d="M{cx-5*s} {cy+10*s} Q{cx} {cy+14*s} {cx+5*s} {cy+10*s}" fill="none" stroke="#1a1a2e" stroke-width="{1.5*s}" stroke-linecap="round"/>'

    mg = f"mg{g}"
    sg = f"sg{g}"
    hg = f"hg{g}"

    return f'''<g>
    <defs>
        {_metal_grad(mg, cor, pc, ce)}
        {_specular(sg, "40%", "30%")}
        {_metal_grad(hg, pm, pc, pe)}
    </defs>

    <!-- SOMBRA DO CORPO -->
    <ellipse cx="{cx}" cy="{cy+36*s}" rx="{30*s}" ry="{6*s}" fill="#000" opacity="0.3"/>

    <!-- PESCOCO - aneis metalicos -->
    <rect x="{cx-8*s}" y="{cy-30*s}" width="{16*s}" height="{10*s}" rx="{2*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <rect x="{cx-7*s}" y="{cy-29*s}" width="{14*s}" height="{2*s}" rx="1" fill="{pc}" opacity="0.5"/>
    <rect x="{cx-7*s}" y="{cy-24*s}" width="{14*s}" height="{2*s}" rx="1" fill="{pc}" opacity="0.5"/>

    <!-- CABECA -->
    <rect x="{cx-22*s}" y="{cy-28*s}" width="{44*s}" height="{44*s}" rx="{10*s}" fill="url(#{mg})" stroke="{ce}" stroke-width="{1.5*s}"/>
    <rect x="{cx-20*s}" y="{cy-26*s}" width="{40*s}" height="{40*s}" rx="{8*s}" fill="url(#{sg})"/>

    <!-- PAINEL FRONTAL -->
    <rect x="{cx-18*s}" y="{cy-22*s}" width="{36*s}" height="{36*s}" rx="{6*s}" fill="none" stroke="{pm}" stroke-width="1" opacity="0.3"/>

    <!-- PARAFUSOS DE CABECA -->
    <circle cx="{cx-18*s}" cy="{cy-22*s}" r="{2.5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <line x1="{cx-20*s}" y1="{cy-22*s}" x2="{cx-16*s}" y2="{cy-22*s}" stroke="{pm}" stroke-width="1.5"/>
    <circle cx="{cx+18*s}" cy="{cy-22*s}" r="{2.5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <line x1="{cx+16*s}" y1="{cy-22*s}" x2="{cx+20*s}" y2="{cy-22*s}" stroke="{pm}" stroke-width="1.5"/>
    <circle cx="{cx-18*s}" cy="{cy+18*s}" r="{2.5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <line x1="{cx-20*s}" y1="{cy+18*s}" x2="{cx-16*s}" y2="{cy+18*s}" stroke="{pm}" stroke-width="1.5"/>
    <circle cx="{cx+18*s}" cy="{cy+18*s}" r="{2.5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <line x1="{cx+16*s}" y1="{cy+18*s}" x2="{cx+20*s}" y2="{cy+18*s}" stroke="{pm}" stroke-width="1.5"/>

    <!-- ANTENAS -->
    <line x1="{cx-6*s}" y1="{cy-28*s}" x2="{cx-10*s}" y2="{cy-40*s}" stroke="{pm}" stroke-width="{2*s}" stroke-linecap="round"/>
    <circle cx="{cx-10*s}" cy="{cy-44*s}" r="{4*s}" fill="{cor}" stroke="{ce}" stroke-width="1"/>
    <circle cx="{cx-11*s}" cy="{cy-45*s}" r="{1.5*s}" fill="#fff" opacity="0.7"/>
    <line x1="{cx+6*s}" y1="{cy-28*s}" x2="{cx+10*s}" y2="{cy-40*s}" stroke="{pm}" stroke-width="{2*s}" stroke-linecap="round"/>
    <circle cx="{cx+10*s}" cy="{cy-44*s}" r="{4*s}" fill="{cor}" stroke="{ce}" stroke-width="1"/>
    <circle cx="{cx+9*s}" cy="{cy-45*s}" r="{1.5*s}" fill="#fff" opacity="0.7"/>

    <!-- OLHOS E BOCA -->
    {olhos}
    {boca}

    <!-- ORELHAS MECANICAS -->
    <rect x="{cx-26*s}" y="{cy-8*s}" width="{6*s}" height="{14*s}" rx="{3*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <rect x="{cx+20*s}" y="{cy-8*s}" width="{6*s}" height="{14*s}" rx="{3*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>

    <!-- OMBROS -->
    <ellipse cx="{cx-28*s}" cy="{cy+22*s}" rx="{10*s}" ry="{6*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <ellipse cx="{cx+28*s}" cy="{cy+22*s}" rx="{10*s}" ry="{6*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <circle cx="{cx-28*s}" cy="{cy+22*s}" r="{2*s}" fill="{ce}"/>
    <circle cx="{cx+28*s}" cy="{cy+22*s}" r="{2*s}" fill="{ce}"/>

    <!-- PISTAO HIDRAULICO ESQUERDO -->
    <rect x="{cx-32*s}" y="{cy+26*s}" width="{6*s}" height="{12*s}" rx="{2*s}" fill="{ce}" stroke="{pm}" stroke-width="0.5"/>
    <rect x="{cx-31*s}" y="{cy+28*s}" width="{4*s}" height="{8*s}" rx="1" fill="{pc}" opacity="0.5"/>

    <!-- PISTAO HIDRAULICO DIREITO -->
    <rect x="{cx+26*s}" y="{cy+26*s}" width="{6*s}" height="{12*s}" rx="{2*s}" fill="{ce}" stroke="{pm}" stroke-width="0.5"/>
    <rect x="{cx+27*s}" y="{cy+28*s}" width="{4*s}" height="{8*s}" rx="1" fill="{pc}" opacity="0.5"/>

    <!-- CORPO / TORAX -->
    <rect x="{cx-18*s}" y="{cy+24*s}" width="{36*s}" height="{20*s}" rx="{5*s}" fill="url(#{mg})" stroke="{ce}" stroke-width="1"/>
    <rect x="{cx-16*s}" y="{cy+26*s}" width="{32*s}" height="{16*s}" rx="{4*s}" fill="url(#{sg})"/>

    <!-- REATOR CENTRAL (circulo brilhante no peito) -->
    <circle cx="{cx}" cy="{cy+34*s}" r="{8*s}" fill="{cor}" opacity="0.4"/>
    <circle cx="{cx}" cy="{cy+34*s}" r="{5*s}" fill="{cor}" opacity="0.7"/>
    <circle cx="{cx-1*s}" cy="{cy+33*s}" r="{2*s}" fill="#fff" opacity="0.8"/>
    <circle cx="{cx}" cy="{cy+34*s}" r="{12*s}" fill="none" stroke="{cor}" stroke-width="1" opacity="0.3">
        <animate attributeName="r" values="8;14;8" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.3;0.1;0.3" dur="1.5s" repeatCount="indefinite"/>
    </circle>

    <!-- BRACOS -->
    <rect x="{cx-30*s}" y="{cy+16*s}" width="{6*s}" height="{14*s}" rx="{3*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <rect x="{cx+24*s}" y="{cy+16*s}" width="{6*s}" height="{14*s}" rx="{3*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>

    <!-- MAOS -->
    <circle cx="{cx-30*s}" cy="{cy+32*s}" r="{5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <circle cx="{cx+30*s}" cy="{cy+32*s}" r="{5*s}" fill="{pe}" stroke="{pm}" stroke-width="1"/>
    <circle cx="{cx-30*s}" cy="{cy+32*s}" r="{2*s}" fill="{ce}"/>
    <circle cx="{cx+30*s}" cy="{cy+32*s}" r="{2*s}" fill="{ce}"/>

    <!-- DEDOS -->
    <rect x="{cx-33*s}" y="{cy+34*s}" width="{3*s}" height="{5*s}" rx="1" fill="{pc}" opacity="0.7"/>
    <rect x="{cx-29*s}" y="{cy+34*s}" width="{3*s}" height="{5*s}" rx="1" fill="{pc}" opacity="0.7"/>
    <rect x="{cx+26*s}" y="{cy+34*s}" width="{3*s}" height="{5*s}" rx="1" fill="{pc}" opacity="0.7"/>
    <rect x="{cx+30*s}" y="{cy+34*s}" width="{3*s}" height="{5*s}" rx="1" fill="{pc}" opacity="0.7"/>
</g>'''


def _fundo_lab(grad_id):
    return f'''<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#fff" opacity="0.35">
    <circle cx="80" cy="50" r="1.5"/><circle cx="200" cy="40" r="2"/>
    <circle cx="350" cy="55" r="1.8"/><circle cx="550" cy="45" r="1.5"/>
    <circle cx="700" cy="65" r="2.2"/><circle cx="150" cy="120" r="1.3"/>
    <circle cx="650" cy="110" r="1.5"/><circle cx="450" cy="35" r="1.2"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="{CORES['dark_med']}" opacity="0.5"/>
<rect x="0" y="380" width="800" height="220" fill="{CORES['dark_bg']}" opacity="0.6"/>
<rect x="0" y="375" width="800" height="10" fill="{CORES['prata_escuro']}" opacity="0.15"/>
<line x1="50" y1="380" x2="50" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="150" y1="380" x2="150" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="250" y1="380" x2="250" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="350" y1="380" x2="350" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="450" y1="380" x2="450" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="550" y1="380" x2="550" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="650" y1="380" x2="650" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>
<line x1="750" y1="380" x2="750" y2="600" stroke="{CORES['prata']}" stroke-width="1" opacity="0.05"/>'''


def gerar_svg_capa(titulo, subtitulo):
    return f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="bg-cap" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0d0d2b"/>
        <stop offset="30%" stop-color="#1a0a4e"/>
        <stop offset="70%" stop-color="#2d0a6e"/>
        <stop offset="100%" stop-color="#0d0d2b"/>
    </linearGradient>
    <radialGradient id="gl-cap" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.25"/>
        <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
    <pattern id="cir" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
        <circle cx="15" cy="15" r="8" fill="none" stroke="#00e5ff" stroke-width="0.3" opacity="0.08"/>
        <path d="M15 0 L15 30 M0 15 L30 15" stroke="#00e5ff" stroke-width="0.3" opacity="0.05"/>
    </pattern>
    <filter id="brilho">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
</defs>
<rect width="800" height="600" fill="url(#bg-cap)"/>
<rect width="800" height="600" fill="url(#cir)"/>
<circle cx="400" cy="220" r="200" fill="url(#gl-cap)"/>
<circle cx="200" cy="80" r="2" fill="#fff" opacity="0.5"/>
<circle cx="550" cy="60" r="2.5" fill="#fff" opacity="0.6"/>
<circle cx="700" cy="120" r="1.5" fill="#fff" opacity="0.4"/>
<circle cx="120" cy="180" r="1.8" fill="#fff" opacity="0.5"/>
<circle cx="680" cy="180" r="2" fill="#fff" opacity="0.45"/>
<text x="400" y="440" text-anchor="middle" font-family="'Playfair Display',serif" font-size="54" fill="#00e5ff" font-weight="900" opacity="0.95" filter="url(#brilho)">Robo Zukinha</text>
<text x="400" y="482" text-anchor="middle" font-family="'Quicksand',sans-serif" font-size="20" fill="#f5a623" opacity="0.9">O Robo Mais Doido da Galaxia</text>
<g transform="translate(400,210)">
    <circle cx="0" cy="0" r="90" fill="url(#gl-cap)"/>
    {_robo_detalhado(0, 0, 1.5, "feliz", "cap", CORES["ciano"], CORES["azul_escuro"])}
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#0d0d2b" opacity="0.6"/>
<ellipse cx="200" cy="680" rx="350" ry="140" fill="#1a0a4e" opacity="0.4"/>
<ellipse cx="650" cy="670" rx="300" ry="130" fill="#2d0a6e" opacity="0.3"/>
</svg>'''


def gerar_svg_pagina(numero, cena):
    bg = f"bg{numero:02d}"
    gl = f"gl{numero:02d}"

    cenas = {
        "despertar": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#0d0d2b"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#2d0a6e"/>
    </linearGradient>
    <radialGradient id="{gl}" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stop-color="#ffee58" stop-opacity="0.5"/><stop offset="100%" stop-color="#ffee58" stop-opacity="0"/>
    </radialGradient>
</defs>
{_fundo_lab(bg)}
<circle cx="400" cy="200" r="140" fill="url({gl})"/>
<line x1="400" y1="0" x2="410" y2="100" stroke="#ffee58" stroke-width="4" opacity="0.7"/>
<line x1="370" y1="0" x2="340" y2="110" stroke="#ffee58" stroke-width="2.5" opacity="0.5"/>
<line x1="440" y1="0" x2="480" y2="90" stroke="#ffee58" stroke-width="2" opacity="0.4"/>
<circle cx="400" cy="0" r="6" fill="#ffee58" opacity="0.9"/>
<rect x="260" y="340" width="280" height="220" rx="12" fill="#1a0a4e" stroke="#7c4dff" stroke-width="2"/>
<rect x="270" y="350" width="260" height="200" rx="8" fill="#0d0d2b"/>
<rect x="290" y="400" width="220" height="40" rx="6" fill="#2d0a6e"/>
<circle cx="310" cy="370" r="12" fill="#00e5ff" opacity="0.2"/>
<circle cx="490" cy="370" r="12" fill="#ff1744" opacity="0.2"/>
<rect x="310" y="410" width="35" height="20" rx="4" fill="#00e5ff" opacity="0.5"/>
<rect x="355" y="410" width="35" height="20" rx="4" fill="#ff1744" opacity="0.5"/>
<rect x="400" y="410" width="35" height="20" rx="4" fill="#ffee58" opacity="0.5"/>
<rect x="445" y="410" width="35" height="20" rx="4" fill="#8fbf6b" opacity="0.5"/>
<g transform="translate(400,220)">
    {_robo_detalhado(0, 0, 1.3, "louco", "p1", CORES["ciano"], CORES["azul_escuro"])}
</g>
<text x="400" y="540" text-anchor="middle" font-family="'Quicksand',sans-serif" font-size="16" fill="#00e5ff" opacity="0.5">BIP! BOP! BIP!</text>
</svg>''',

        "antenas": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d0d2b"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#2d0a6e"/></linearGradient></defs>
{_fundo_lab(bg)}
<g transform="translate(400,200)">
    <line x1="-15" y1="-55" x2="25" y2="-75" stroke="{CORES['prata']}" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="28" cy="-78" r="5" fill="#ff1744" stroke="{CORES['prata_escuro']}" stroke-width="1"/>
    <line x1="15" y1="-55" x2="-30" y2="-72" stroke="{CORES['prata']}" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="-33" cy="-75" r="5" fill="#00e5ff" stroke="{CORES['prata_escuro']}" stroke-width="1"/>
    {_robo_detalhado(0, 0, 1.3, "louco", "p2", CORES["cobre"], CORES["cobre_escuro"])}
</g>
<ellipse cx="320" cy="380" rx="70" ry="20" fill="#00e5ff" opacity="0.06"/>
<ellipse cx="480" cy="380" rx="70" ry="20" fill="#ff1744" opacity="0.06"/>
</svg>''',

        "cozinha": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d0d2b"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#0d0d2b"/></linearGradient></defs>
{_fundo_lab(bg)}
<rect x="80" y="180" width="200" height="170" rx="8" fill="#1a0a4e" stroke="#7c4dff" stroke-width="1.5"/>
<rect x="520" y="180" width="200" height="170" rx="8" fill="#1a0a4e" stroke="#7c4dff" stroke-width="1.5"/>
<rect x="90" y="190" width="180" height="150" rx="6" fill="#0d0d2b"/>
<rect x="530" y="190" width="180" height="150" rx="6" fill="#0d0d2b"/>
<ellipse cx="180" cy="240" rx="35" ry="35" fill="#8fbf6b" opacity="0.4"/>
<rect x="160" y="220" width="40" height="40" rx="5" fill="#fff" opacity="0.6"/>
<ellipse cx="620" cy="240" rx="35" ry="35" fill="#8b6914" opacity="0.4"/>
<circle cx="620" cy="240" r="15" fill="#0d0d2b"/>
<circle cx="620" cy="240" r="10" fill="#8b6914"/>
<g transform="translate(400,220)">
    {_robo_detalhado(0, 0, 1.2, "feliz", "p3", CORES["verde"], CORES["verde_escuro"])}
</g>
<rect x="360" y="340" width="80" height="260" fill="#2d0a6e" opacity="0.6"/>
<rect x="365" y="345" width="70" height="250" fill="#1a0a4e" opacity="0.5"/>
</svg>''',

        "roupa": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d0d2b"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#2d0a6e"/></linearGradient></defs>
{_fundo_lab(bg)}
<g transform="translate(400,210)">
    {_robo_detalhado(0, 0, 1.2, "feliz", "p4", CORES["coral"], CORES["vermelho_escuro"])}
</g>
<rect x="310" y="120" width="70" height="25" rx="6" fill="#ff1744" opacity="0.7" transform="rotate(-15,345,132)"/>
<rect x="420" y="120" width="70" height="25" rx="6" fill="#00e5ff" opacity="0.7" transform="rotate(15,455,132)"/>
<rect x="330" y="360" width="55" height="70" rx="6" fill="#ffee58" opacity="0.5" transform="rotate(-25,357,395)"/>
<rect x="415" y="360" width="55" height="70" rx="6" fill="#8fbf6b" opacity="0.5" transform="rotate(30,442,395)"/>
<path d="M350 330 Q400 320 450 330" fill="none" stroke="#ff1744" stroke-width="5" opacity="0.4"/>
</svg>''',

        "danca": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2d0a6e"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#0d0d2b"/></linearGradient>
    <radialGradient id="{gl}" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00e5ff" stop-opacity="0.3"/><stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/></radialGradient>
</defs>
{_fundo_lab(bg)}
<circle cx="400" cy="250" r="180" fill="url({gl})"/>
<g transform="translate(400,220)">
    {_robo_detalhado(0, 0, 1.4, "louco", "p5", CORES["vermelho"], CORES["vermelho_escuro"])}
</g>
<text x="290" y="380" font-family="'Quicksand',sans-serif" font-size="26" fill="#00e5ff" opacity="0.6" transform="rotate(-15,290,380)">♪</text>
<text x="490" y="390" font-family="'Quicksand',sans-serif" font-size="32" fill="#ff1744" opacity="0.6" transform="rotate(10,490,390)">♫</text>
<text x="330" y="410" font-family="'Quicksand',sans-serif" font-size="20" fill="#ffee58" opacity="0.5" transform="rotate(-8,330,410)">♪</text>
<text x="470" y="420" font-family="'Quicksand',sans-serif" font-size="28" fill="#8fbf6b" opacity="0.5" transform="rotate(12,470,420)">♫</text>
</svg>''',

        "amigo": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d0d2b"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#2d0a6e"/></linearGradient></defs>
{_fundo_lab(bg)}
<g transform="translate(260,220)">
    {_robo_detalhado(0, 0, 1.1, "feliz", "p6a", CORES["ciano"], CORES["azul_escuro"])}
</g>
<g transform="translate(560,230)">
    {_robo_detalhado(0, 0, 0.9, "feliz", "p6b", CORES["cobre"], CORES["cobre_escuro"])}
</g>
<path d="M320 300 Q400 340 500 300" fill="none" stroke="#ffee58" stroke-width="2" opacity="0.5" stroke-dasharray="8,5"/>
<circle cx="400" cy="320" r="4" fill="#ffee58" opacity="0.6"><animate attributeName="r" values="3;7;3" dur="1.2s" repeatCount="indefinite"/></circle>
<circle cx="420" cy="310" r="3" fill="#00e5ff" opacity="0.5"><animate attributeName="r" values="2;5;2" dur="1.5s" repeatCount="indefinite"/></circle>
</svg>''',

        "festa": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2d0a6e"/><stop offset="50%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#0d0d2b"/></linearGradient>
    <radialGradient id="{gl}" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffee58" stop-opacity="0.35"/><stop offset="100%" stop-color="#ffee58" stop-opacity="0"/></radialGradient>
</defs>
{_fundo_lab(bg)}
<circle cx="400" cy="250" r="180" fill="url({gl})"/>
<g transform="translate(260,220)">
    {_robo_detalhado(0, 0, 1.0, "louco", "p7a", CORES["ciano"], CORES["azul_escuro"])}
</g>
<g transform="translate(560,230)">
    {_robo_detalhado(0, 0, 0.85, "feliz", "p7b", CORES["cobre"], CORES["cobre_escuro"])}
</g>
<circle cx="220" cy="150" r="7" fill="#ff1744" opacity="0.7"><animate attributeName="r" values="4;9;4" dur="0.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.7;0.3;0.7" dur="0.6s" repeatCount="indefinite"/></circle>
<circle cx="540" cy="140" r="6" fill="#00e5ff" opacity="0.6"><animate attributeName="r" values="3;8;3" dur="0.8s" repeatCount="indefinite"/></circle>
<circle cx="350" cy="130" r="5" fill="#ffee58" opacity="0.6"><animate attributeName="r" values="3;7;3" dur="0.7s" repeatCount="indefinite"/></circle>
<circle cx="480" cy="150" r="6" fill="#8fbf6b" opacity="0.6"><animate attributeName="r" values="4;8;4" dur="0.9s" repeatCount="indefinite"/></circle>
<circle cx="300" cy="170" r="4" fill="#ff9100" opacity="0.5"><animate attributeName="r" values="2;6;2" dur="1.1s" repeatCount="indefinite"/></circle>
<circle cx="520" cy="170" r="5" fill="#ff1744" opacity="0.5"><animate attributeName="r" values="3;7;3" dur="0.7s" repeatCount="indefinite"/></circle>
<line x1="250" y1="110" x2="255" y2="135" stroke="#00e5ff" stroke-width="2.5" opacity="0.5"/>
<line x1="480" y1="100" x2="485" y2="130" stroke="#ff1744" stroke-width="2.5" opacity="0.5"/>
</svg>''',

        "carregar": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{bg}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d0d2b"/><stop offset="40%" stop-color="#1a0a4e"/><stop offset="100%" stop-color="#0d0d2b"/></linearGradient>
    <radialGradient id="{gl}" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00e5ff" stop-opacity="0.25"/><stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/></radialGradient>
</defs>
{_fundo_lab(bg)}
<circle cx="650" cy="90" r="55" fill="#00e5ff" opacity="0.08"/>
<circle cx="642" cy="86" r="50" fill="#0d0d2b" opacity="0.9"/>
<g transform="translate(260,210)">
    {_robo_detalhado(0, 0, 1.0, "sono", "p8a", CORES["ciano"], CORES["azul_escuro"])}
</g>
<g transform="translate(560,220)">
    {_robo_detalhado(0, 0, 0.85, "sono", "p8b", CORES["cobre"], CORES["cobre_escuro"])}
</g>
<text x="370" y="160" font-family="'Quicksand',sans-serif" font-size="32" fill="#00e5ff" opacity="0.25" font-weight="600">z</text>
<text x="415" y="135" font-family="'Quicksand',sans-serif" font-size="24" fill="#00e5ff" opacity="0.18" font-weight="600">z</text>
<text x="450" y="115" font-family="'Quicksand',sans-serif" font-size="16" fill="#00e5ff" opacity="0.12" font-weight="600">z</text>
<rect x="300" y="370" width="200" height="20" rx="6" fill="#2d0a6e"/>
<rect x="305" y="373" width="60" height="14" rx="4" fill="#00e5ff" opacity="0.7">
    <animate attributeName="width" values="60;190;60" dur="2.5s" repeatCount="indefinite"/>
</rect>
<circle cx="400" cy="380" r="12" fill="#00e5ff" opacity="0.3">
    <animate attributeName="r" values="8;18;8" dur="2.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.3;0.08;0.3" dur="2.5s" repeatCount="indefinite"/>
</circle>
</svg>''',
    }

    return cenas.get(cena, list(cenas.values())[0])


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "examples")
    os.makedirs(out, exist_ok=True)
    livro = {
        "titulo": HISTORIA["titulo"], "subtitulo": HISTORIA.get("subtitulo", ""),
        "autor": HISTORIA.get("autor", ""), "faixa_etaria": HISTORIA.get("faixa_etaria", "3 - 8 anos"),
        "lang": HISTORIA.get("lang", "pt-BR"), "texto_final": HISTORIA.get("texto_final", "Fim!"),
        "capa_svg": gerar_svg_capa(HISTORIA["titulo"], HISTORIA.get("subtitulo", "")),
        "paginas": []
    }
    posicoes = {1:"tr", 2:"tl", 3:"br", 4:"bl", 5:"tr", 6:"tr", 7:"br", 8:"bl"}
    for p in HISTORIA["paginas"]:
        livro["paginas"].append({"texto": p["texto"], "dialogo": p.get("dialogo", ""),
                                 "dialogo_pos": posicoes.get(p["numero"], "tr"),
                                 "svg": gerar_svg_pagina(p["numero"], p.get("cena", "despertar")), "audio": ""})

    json_path = os.path.join(out, "book_robo_realista.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(livro, f, ensure_ascii=False, indent=2)

    build = os.path.join(os.path.dirname(__file__), "build_livro.py")
    html_path = os.path.join(os.path.dirname(__file__), "..", "output", "robo_zukinha_realista.html")
    print(f"book.json: {json_path}")
    print(f"Build: python \"{build}\" \"{json_path}\" \"{html_path}\"")
