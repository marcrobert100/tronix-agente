#!/usr/bin/env python3
"""Gera livro infantil 'Robô Zukinha: O Robô Mais Doido da Galáxia' com SVGs customizados."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from criar_historia import _estrela_corpo

CORES = {
    "ceu_dia": "#e3f2fd",
    "ceu_noite": "#0b081a",
    "creme": "#fdf8f0",
    "coral": "#ff7a5a",
    "dourado": "#f5a623",
    "verde": "#8fbf6b",
    "azul": "#69aee6",
    "azul_vivo": "#2196f3",
    "rosa": "#fce4ec",
    "laranja": "#e8985a",
    "verde_escuro": "#5a8a4a",
    "marrom": "#8b6914",
    "roxo_suave": "#b8a9d4",
    "amarelo_claro": "#fff8dc",
    "coral_claro": "#ff8a80",
    "sombra": "#1a1a2e",
    "vermelho": "#ff1744",
    "ciano": "#00e5ff",
    "amarelo_vivo": "#ffee58",
    "laranja_vivo": "#ff9100",
}

HISTORIA = {
    "titulo": "Robô Zukinha",
    "subtitulo": "O Robô Mais Doido da Galáxia",
    "autor": "Marcos Roberto",
    "faixa_etaria": "3 — 8 anos",
    "lang": "pt-BR",
    "texto_final": "Zukinha aprendeu: ser doido é ser feliz do seu próprio jeito. Fim!",
    "paginas": [
        {"numero": 1, "titulo": "O Despertar",
         "texto": "Lá no laboratório do Vovô Chico, na noite de ontem, um raio muito forte caiu bem na tomada. E de repente... ZUKINHA ACORDOU!",
         "dialogo": "Zzzt! Eu... estou... VIVO! Oba!",
         "cena": "despertar"},
        {"numero": 2, "titulo": "Antenas Trocadas",
         "texto": "Zukinha pulou da mesa e colocou as antenas no lugar errado. Uma no olho e outra na boca!",
         "dialogo": "Puft! Agora eu enxergo pelo nariz e cheiro pelos olhos!",
         "cena": "antenas"},
        {"numero": 3, "titulo": "Misturando Tudo",
         "texto": "Na cozinha, Zukinha tentou fazer café. Mas colocou pasta de dente no bule e café na escova.",
         "dialogo": "Hmm, café com menta! O café mais refrescante do mundo!",
         "cena": "cozinha"},
        {"numero": 4, "titulo": "Roupa Doida",
         "texto": "Zukinha foi se vestir. Calçou a luva no pé, a meia na mão, e usou a calça como cachecol.",
         "dialogo": "Estou elegantemente doido! A moda robô é assim!",
         "cena": "roupa"},
        {"numero": 5, "titulo": "Dança de Robô",
         "texto": "Uma música começou a tocar. Zukinha começou a dançar: chacoalhava as engrenagens, girava a hélice e apitava no ritmo!",
         "dialogo": "Tchum tchum tchá! Sou o robô mais feliz da galáxia!",
         "cena": "danca"},
        {"numero": 6, "titulo": "Criando um Amigo",
         "texto": "Zukinha juntou sucata, parafusos e uma lata velha. Com faíscas e risadas, criou... ROBÔTCHUDO, seu novo amigo!",
         "dialogo": "Você também é doido? Ah, que bom! Vamos bagunçar juntos!",
         "cena": "amigo"},
        {"numero": 7, "titulo": "Festa Maluca",
         "texto": "Os dois robôs fizeram uma festa no laboratório. Jogaram confete de parafuso, soltaram bolhas de sabão elétricas e dançaram até o chão tremer.",
         "dialogo": "Essa é a melhor festa robótica de todos os tempos! Wheee!",
         "cena": "festa"},
        {"numero": 8, "titulo": "Hora de Carregar",
         "texto": "Cansados, Zukinha e Robôtchudo sentaram perto da tomada. Com os olhinhos piscando devagar, deram a mão e foram carregar juntos.",
         "dialogo": "Até amanhã... amigo... Zzzzt...",
         "cena": "carregar"},
    ]
}


def _robo_corpo(cx, cy, escala=1.0, expressao="feliz", uid="", cor_corpo="#69aee6", cor_detalhe="#2196f3"):
    s = escala
    grad_id = f"robo-grad-{uid}" if uid else f"robo-grad-{cx}-{cy}"

    if expressao == "feliz":
        olhos = f'''<ellipse cx="{cx-12*s}" cy="{cy-5*s}" rx="{5*s}" ry="{6*s}" fill="#fff"/>
        <circle cx="{cx-12*s}" cy="{cy-4*s}" r="{3*s}" fill="#1a1a2e"/>
        <circle cx="{cx-13*s}" cy="{cy-6*s}" r="{1.2*s}" fill="#fff"/>
        <ellipse cx="{cx+12*s}" cy="{cy-5*s}" rx="{5*s}" ry="{6*s}" fill="#fff"/>
        <circle cx="{cx+12*s}" cy="{cy-4*s}" r="{3*s}" fill="#1a1a2e"/>
        <circle cx="{cx+11*s}" cy="{cy-6*s}" r="{1.2*s}" fill="#fff"/>'''
        boca = f'<path d="M{cx-8*s} {cy+12*s} Q{cx} {cy+22*s} {cx+8*s} {cy+12*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>'
        bochechas = f'<circle cx="{cx-18*s}" cy="{cy+5*s}" r="{4*s}" fill="#ff8a80" opacity="0.4"/><circle cx="{cx+18*s}" cy="{cy+5*s}" r="{4*s}" fill="#ff8a80" opacity="0.4"/>'
    elif expressao == "louco":
        olhos = f'''<circle cx="{cx-14*s}" cy="{cy-8*s}" r="{6*s}" fill="#fff"/>
        <circle cx="{cx-12*s}" cy="{cy-10*s}" r="{3*s}" fill="#ff1744"/>
        <circle cx="{cx+16*s}" cy="{cy-6*s}" r="{5*s}" fill="#fff"/>
        <circle cx="{cx+18*s}" cy="{cy-8*s}" r="{3*s}" fill="#ff1744"/>'''
        boca = f'<path d="M{cx-12*s} {cy+14*s} Q{cx-2*s} {cy+26*s} {cx+6*s} {cy+12*s} Q{cx+8*s} {cy+18*s} {cx+14*s} {cy+14*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>'
        bochechas = f'<circle cx="{cx-20*s}" cy="{cy+3*s}" r="{5*s}" fill="#ff8a80" opacity="0.5"/><circle cx="{cx+20*s}" cy="{cy+3*s}" r="{5*s}" fill="#ff8a80" opacity="0.5"/>'
    elif expressao == "sono":
        olhos = f'''<path d="M{cx-18*s} {cy-5*s} Q{cx-12*s} {cy+2*s} {cx-6*s} {cy-5*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>
        <path d="M{cx+6*s} {cy-5*s} Q{cx+12*s} {cy+2*s} {cx+18*s} {cy-5*s}" fill="none" stroke="#1a1a2e" stroke-width="{2.5*s}" stroke-linecap="round"/>'''
        boca = f'<path d="M{cx-6*s} {cy+12*s} Q{cx} {cy+16*s} {cx+6*s} {cy+12*s}" fill="none" stroke="#1a1a2e" stroke-width="{2*s}" stroke-linecap="round"/>'
        bochechas = ""
    else:
        olhos = f'''<circle cx="{cx-12*s}" cy="{cy-5*s}" r="{5*s}" fill="#fff"/>
        <circle cx="{cx-12*s}" cy="{cy-4*s}" r="{3*s}" fill="#1a1a2e"/>
        <circle cx="{cx+12*s}" cy="{cy-5*s}" r="{5*s}" fill="#fff"/>
        <circle cx="{cx+12*s}" cy="{cy-4*s}" r="{3*s}" fill="#1a1a2e"/>'''
        boca = f'<path d="M{cx-6*s} {cy+12*s} Q{cx} {cy+16*s} {cx+6*s} {cy+12*s}" fill="none" stroke="#1a1a2e" stroke-width="{2*s}" stroke-linecap="round"/>'
        bochechas = ""

    parafusos = f'''
        <circle cx="{cx-18*s}" cy="{cy-18*s}" r="{2*s}" fill="#555" stroke="#333" stroke-width="1"/>
        <line x1="{cx-20*s}" y1="{cy-18*s}" x2="{cx-16*s}" y2="{cy-18*s}" stroke="#333" stroke-width="1.5"/>
        <circle cx="{cx+18*s}" cy="{cy-18*s}" r="{2*s}" fill="#555" stroke="#333" stroke-width="1"/>
        <line x1="{cx+16*s}" y1="{cy-18*s}" x2="{cx+20*s}" y2="{cy-18*s}" stroke="#333" stroke-width="1.5"/>'''

    antena = f'''
        <line x1="{cx}" y1="{cy-25*s}" x2="{cx}" y2="{cy-38*s}" stroke="#555" stroke-width="{2*s}"/>
        <circle cx="{cx}" cy="{cy-42*s}" r="{4*s}" fill="{cor_detalhe}" opacity="0.9"/>
        <circle cx="{cx}" cy="{cx-42*s}" r="{2*s}" fill="#fff" opacity="0.6"/>'''

    return f'''<g>
    <defs>
        <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="{cor_corpo}"/>
            <stop offset="100%" stop-color="{cor_detalhe}"/>
        </linearGradient>
    </defs>
    {antena}
    {parafusos}
    <rect x="{cx-22*s}" y="{cy-22*s}" width="{44*s}" height="{44*s}" rx="{8*s}" fill="url(#{grad_id})" stroke="#333" stroke-width="{1.5*s}"/>
    <rect x="{cx-20*s}" y="{cy-20*s}" width="{40*s}" height="{40*s}" rx="{6*s}" fill="none" stroke="#fff" stroke-width="{1*s}" opacity="0.3"/>
    {olhos}
    {bochechas}
    {boca}
    <rect x="{cx-8*s}" y="{cy+24*s}" width="{16*s}" height="{8*s}" rx="{2*s}" fill="#555"/>
    <circle cx="{cx-5*s}" cy="{cy+28*s}" r="{1.5*s}" fill="#ff1744"/>
    <circle cx="{cx}" cy="{cy+28*s}" r="{1.5*s}" fill="#00e5ff"/>
    <circle cx="{cx+5*s}" cy="{cy+28*s}" r="{1.5*s}" fill="#ffee58"/>
</g>'''


def gerar_svg_capa(titulo, subtitulo):
    return f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="bg-capa" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="40%" stop-color="#2d1b69"/>
        <stop offset="70%" stop-color="#4a148c"/>
        <stop offset="100%" stop-color="#311b92"/>
    </linearGradient>
    <radialGradient id="glow-capa" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
    <pattern id="circuitos" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M20 0 L20 40 M0 20 L40 20 M10 10 L30 30 M30 10 L10 30" stroke="#00e5ff" stroke-width="0.5" opacity="0.1" fill="none"/>
        <circle cx="20" cy="20" r="2" fill="#00e5ff" opacity="0.15"/>
    </pattern>
</defs>
<rect width="800" height="600" fill="url(#bg-capa)"/>
<rect width="800" height="600" fill="url(#circuitos)"/>
<circle cx="400" cy="200" r="180" fill="url(#glow-capa)"/>
<circle cx="100" cy="80" r="2" fill="#fff" opacity="0.6"/>
<circle cx="200" cy="50" r="1.5" fill="#fff" opacity="0.5"/>
<circle cx="600" cy="60" r="2.5" fill="#fff" opacity="0.6"/>
<circle cx="700" cy="120" r="1.5" fill="#fff" opacity="0.4"/>
<circle cx="150" cy="150" r="1" fill="#fff" opacity="0.5"/>
<circle cx="680" cy="180" r="2" fill="#fff" opacity="0.45"/>
<circle cx="50" cy="200" r="1.5" fill="#fff" opacity="0.4"/>
<circle cx="750" cy="80" r="1" fill="#fff" opacity="0.5"/>
<text x="400" y="430" text-anchor="middle" font-family="'Playfair Display',serif" font-size="52" fill="#00e5ff" font-weight="900" opacity="0.95" filter="url(#glow)">Robô Zukinha</text>
<text x="400" y="472" text-anchor="middle" font-family="'Quicksand',sans-serif" font-size="20" fill="#ffee58" opacity="0.9">O Robô Mais Doido da Galáxia</text>
<g transform="translate(400,200)">
    <circle cx="0" cy="0" r="85" fill="url(#glow-capa)"/>
    {_robo_corpo(0, 0, 1.5, "feliz", "capa", "#00e5ff", "#2196f3")}
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.4"/>
<ellipse cx="200" cy="680" rx="350" ry="140" fill="#2d1b69" opacity="0.3"/>
<ellipse cx="650" cy="670" rx="300" ry="130" fill="#311b92" opacity="0.3"/>
<circle cx="300" cy="520" r="3" fill="#00e5ff" opacity="0.4"/>
<circle cx="350" cy="540" r="2" fill="#00e5ff" opacity="0.3"/>
<circle cx="450" cy="530" r="2.5" fill="#00e5ff" opacity="0.35"/>
<circle cx="500" cy="550" r="2" fill="#00e5ff" opacity="0.3"/>
</svg>'''


def gerar_svg_pagina(numero, cena):
    grad_id = f"bg-{numero:02d}"
    glow_id = f"glow-{numero:02d}"

    cenas = {
        "despertar": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="0.5" stop-color="#2d1b69"/>
        <stop offset="100%" stop-color="#311b92"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ffee58" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#ffee58" stop-opacity="0"/>
    </radialGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<circle cx="400" cy="200" r="120" fill="url(#{glow_id})"/>
<g fill="#fff" opacity="0.5">
    <circle cx="100" cy="50" r="1.5"/><circle cx="250" cy="40" r="2"/>
    <circle cx="450" cy="55" r="1.8"/><circle cx="650" cy="45" r="1.5"/>
    <circle cx="720" cy="80" r="1.2"/><circle cx="180" cy="100" r="1.3"/>
</g>
<line x1="400" y1="0" x2="420" y2="130" stroke="#ffee58" stroke-width="3" opacity="0.6"/>
<line x1="380" y1="0" x2="360" y2="140" stroke="#ffee58" stroke-width="2" opacity="0.4"/>
<line x1="430" y1="0" x2="460" y2="120" stroke="#ffee58" stroke-width="1.5" opacity="0.3"/>
<circle cx="420" cy="0" r="4" fill="#ffee58" opacity="0.8"/>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<rect x="280" y="350" width="240" height="200" rx="10" fill="#2d1b69" stroke="#4a148c" stroke-width="2"/>
<rect x="290" y="360" width="220" height="180" rx="8" fill="#1a1a5e"/>
<circle cx="320" cy="380" r="15" fill="#00e5ff" opacity="0.15"/>
<circle cx="480" cy="380" r="15" fill="#ff1744" opacity="0.15"/>
<rect x="310" y="410" width="180" height="40" rx="5" fill="#311b92"/>
<rect x="330" y="420" width="30" height="20" rx="3" fill="#00e5ff" opacity="0.5"/>
<rect x="370" y="420" width="30" height="20" rx="3" fill="#ff1744" opacity="0.5"/>
<rect x="410" y="420" width="30" height="20" rx="3" fill="#ffee58" opacity="0.5"/>
<rect x="450" y="420" width="30" height="20" rx="3" fill="#8fbf6b" opacity="0.5"/>
<g transform="translate(400,220)">
    {_robo_corpo(0, 0, 1.3, "louco", "p1", "#00e5ff", "#2196f3")}
</g>
<text x="400" y="530" text-anchor="middle" font-family="'Quicksand',sans-serif" font-size="14" fill="#00e5ff" opacity="0.5">⚡ BIP! BOP! BIP! ⚡</text>
</svg>''',

        "antenas": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="0.5" stop-color="#2d1b69"/>
        <stop offset="100%" stop-color="#311b92"/>
    </linearGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#fff" opacity="0.4">
    <circle cx="120" cy="60" r="1.5"/><circle cx="300" cy="45" r="2"/>
    <circle cx="550" cy="50" r="1.8"/><circle cx="700" cy="70" r="1.3"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<rect x="300" y="380" width="200" height="180" rx="8" fill="#311b92" stroke="#4a148c" stroke-width="1"/>
<rect x="310" y="390" width="180" height="160" rx="5" fill="#2d1b69"/>
<g transform="translate(400,220)">
    <line x1="-10" y1="-50" x2="20" y2="-70" stroke="#555" stroke-width="2"/>
    <circle cx="22" cy="-72" r="4" fill="#ff1744"/>
    <line x1="15" y1="-52" x2="-25" y2="-68" stroke="#555" stroke-width="2"/>
    <circle cx="-27" cy="-70" r="4" fill="#00e5ff"/>
    {_robo_corpo(0, 0, 1.3, "louco", "p2", "#e8985a", "#ff7a5a")}
</g>
<ellipse cx="330" cy="380" rx="60" ry="15" fill="#00e5ff" opacity="0.08"/>
<ellipse cx="470" cy="380" rx="60" ry="15" fill="#ff1744" opacity="0.08"/>
</svg>''',

        "cozinha": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#2d1b69"/>
        <stop offset="0.5" stop-color="#1a1a5e"/>
        <stop offset="100%" stop-color="#4a148c"/>
    </linearGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<rect x="0" y="350" width="800" height="250" fill="#311b92"/>
<rect x="100" y="200" width="180" height="150" rx="6" fill="#2d1b69" stroke="#4a148c" stroke-width="1"/>
<rect x="520" y="200" width="180" height="150" rx="6" fill="#2d1b69" stroke="#4a148c" stroke-width="1"/>
<rect x="110" y="210" width="160" height="130" rx="4" fill="#1a1a5e"/>
<rect x="530" y="210" width="160" height="130" rx="4" fill="#1a1a5e"/>
<circle cx="190" cy="260" r="30" fill="#8fbf6b" opacity="0.3"/>
<rect x="175" y="245" width="30" height="30" rx="3" fill="#fff" opacity="0.5"/>
<circle cx="610" cy="260" r="30" fill="#8b6914" opacity="0.3"/>
<circle cx="610" cy="260" r="12" fill="#1a1a5e"/>
<circle cx="610" cy="260" r="8" fill="#8b6914"/>
<g transform="translate(400,220)">
    {_robo_corpo(0, 0, 1.2, "feliz", "p3", "#8fbf6b", "#5a8a4a")}
</g>
<rect x="360" y="350" width="80" height="250" fill="#4a148c" opacity="0.5"/>
<rect x="365" y="355" width="70" height="240" fill="#2d1b69" opacity="0.5"/>
<circle cx="300" cy="365" r="5" fill="#fff" opacity="0.3">  <animate attributeName="opacity" values="0.3;0.6;0.3" dur="1s" repeatCount="indefinite"/></circle>
<circle cx="500" cy="365" r="5" fill="#fff" opacity="0.3">  <animate attributeName="opacity" values="0.3;0.6;0.3" dur="1.3s" repeatCount="indefinite"/></circle>
</svg>''',

        "roupa": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="0.5" stop-color="#311b92"/>
        <stop offset="100%" stop-color="#4a148c"/>
    </linearGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<g fill="#fff" opacity="0.4">
    <circle cx="80" cy="50" r="1.5"/><circle cx="200" cy="40" r="2"/>
    <circle cx="450" cy="55" r="1.8"/><circle cx="680" cy="45" r="1.5"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<ellipse cx="200" cy="680" rx="300" ry="130" fill="#2d1b69" opacity="0.3"/>
<g transform="translate(400,210)">
    {_robo_corpo(0, 0, 1.2, "feliz", "p4", "#ff7a5a", "#ff1744")}
</g>
<rect x="320" y="135" width="60" height="20" rx="5" fill="#ff1744" opacity="0.6" transform="rotate(-15,350,145)"/>
<rect x="420" y="135" width="60" height="20" rx="5" fill="#00e5ff" opacity="0.6" transform="rotate(15,450,145)"/>
<rect x="340" y="350" width="50" height="60" rx="5" fill="#ffee58" opacity="0.4" transform="rotate(-20,365,380)"/>
<rect x="410" y="350" width="50" height="60" rx="5" fill="#8fbf6b" opacity="0.4" transform="rotate(25,435,380)"/>
<path d="M360 340 Q400 330 440 340" fill="none" stroke="#ff1744" stroke-width="4" opacity="0.3"/>
</svg>''',

        "danca": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#311b92"/>
        <stop offset="0.5" stop-color="#4a148c"/>
        <stop offset="100%" stop-color="#1a1a5e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.25"/>
        <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<circle cx="400" cy="250" r="150" fill="url(#{glow_id})"/>
<g fill="#fff" opacity="0.5">
    <circle cx="120" cy="60" r="2"/><circle cx="320" cy="45" r="1.5"/>
    <circle cx="580" cy="55" r="2"/><circle cx="720" cy="70" r="1.3"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<g transform="translate(400,220)">
    {_robo_corpo(0, 0, 1.4, "louco", "p5", "#ff1744", "#ff9100")}
</g>
<text x="300" y="375" font-family="'Quicksand',sans-serif" font-size="22" fill="#00e5ff" opacity="0.6" transform="rotate(-15,300,375)">♪</text>
<text x="480" y="380" font-family="'Quicksand',sans-serif" font-size="28" fill="#ff1744" opacity="0.6" transform="rotate(10,480,380)">♫</text>
<text x="340" y="400" font-family="'Quicksand',sans-serif" font-size="18" fill="#ffee58" opacity="0.5" transform="rotate(-8,340,400)">♪</text>
<text x="460" y="410" font-family="'Quicksand',sans-serif" font-size="24" fill="#8fbf6b" opacity="0.5" transform="rotate(12,460,410)">♫</text>
<circle cx="280" cy="340" r="4" fill="#00e5ff" opacity="0.5">  <animate attributeName="r" values="3;6;3" dur="0.8s" repeatCount="indefinite"/></circle>
<circle cx="520" cy="320" r="3" fill="#ff1744" opacity="0.5">  <animate attributeName="r" values="2;5;2" dur="1s" repeatCount="indefinite"/></circle>
<circle cx="320" cy="360" r="3" fill="#ffee58" opacity="0.4">  <animate attributeName="r" values="2;4;2" dur="1.2s" repeatCount="indefinite"/></circle>
<circle cx="480" cy="350" r="4" fill="#8fbf6b" opacity="0.4">  <animate attributeName="r" values="3;5;3" dur="0.9s" repeatCount="indefinite"/></circle>
</svg>''',

        "amigo": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="0.5" stop-color="#2d1b69"/>
        <stop offset="100%" stop-color="#311b92"/>
    </linearGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<g fill="#fff" opacity="0.4">
    <circle cx="100" cy="50" r="1.5"/><circle cx="280" cy="40" r="2"/>
    <circle cx="500" cy="55" r="1.8"/><circle cx="700" cy="45" r="1.5"/>
</g>
<g transform="translate(280,220)">
    {_robo_corpo(0, 0, 1.1, "feliz", "p6a", "#00e5ff", "#2196f3")}
</g>
<g transform="translate(540,230)">
    <rect x="-25" y="-28" width="50" height="56" rx="10" fill="#8b6914" stroke="#5a8a4a" stroke-width="2"/>
    <rect x="-22" y="-25" width="44" height="50" rx="7" fill="#5a8a4a"/>
    <circle cx="-12" cy="-10" r="5" fill="#fff"/><circle cx="-12" cy="-9" r="3" fill="#1a1a2e"/>
    <circle cx="12" cy="-10" r="5" fill="#fff"/><circle cx="12" cy="-9" r="3" fill="#1a1a2e"/>
    <path d="M-8 4 Q0 10 8 4" fill="none" stroke="#1a1a2e" stroke-width="2" stroke-linecap="round"/>
    <rect x="-5" y="18" width="10" height="10" rx="2" fill="#8b6914"/>
    <rect x="-3" y="20" width="6" height="6" rx="1" fill="#ff1744"/>
    <circle cx="0" cy="-32" r="3" fill="#ff1744"/>
</g>
<path d="M340 280 Q400 310 480 280" fill="none" stroke="#ffee58" stroke-width="2" opacity="0.4" stroke-dasharray="6,4"/>
<circle cx="400" cy="300" r="3" fill="#ffee58" opacity="0.5">  <animate attributeName="r" values="2;5;2" dur="1s" repeatCount="indefinite"/></circle>
<circle cx="420" cy="290" r="2" fill="#00e5ff" opacity="0.4">  <animate attributeName="r" values="1;4;1" dur="1.3s" repeatCount="indefinite"/></circle>
</svg>''',

        "festa": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#311b92"/>
        <stop offset="0.5" stop-color="#4a148c"/>
        <stop offset="100%" stop-color="#1a1a5e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ffee58" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="#ffee58" stop-opacity="0"/>
    </radialGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<circle cx="400" cy="250" r="160" fill="url(#{glow_id})"/>
<g fill="#fff" opacity="0.5">
    <circle cx="80" cy="50" r="1.5"/><circle cx="220" cy="35" r="2"/>
    <circle cx="550" cy="45" r="1.8"/><circle cx="720" cy="60" r="1.5"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<g transform="translate(280,220)">
    {_robo_corpo(0, 0, 1.0, "louco", "p7a", "#00e5ff", "#2196f3")}
</g>
<g transform="translate(540,230)">
    <rect x="-22" y="-25" width="44" height="50" rx="8" fill="#8b6914" stroke="#5a8a4a" stroke-width="1.5"/>
    <rect x="-20" y="-22" width="40" height="44" rx="6" fill="#5a8a4a"/>
    <circle cx="-10" cy="-8" r="4" fill="#fff"/><circle cx="-10" cy="-7" r="2.5" fill="#1a1a2e"/>
    <circle cx="10" cy="-8" r="4" fill="#fff"/><circle cx="10" cy="-7" r="2.5" fill="#1a1a2e"/>
    <path d="M-6 5 Q0 10 6 5" fill="none" stroke="#1a1a2e" stroke-width="2" stroke-linecap="round"/>
    <rect x="-4" y="16" width="8" height="8" rx="2" fill="#8b6914"/>
    <circle cx="0" cy="-28" r="3" fill="#00e5ff"/>
</g>
<circle cx="250" cy="160" r="6" fill="#ff1744" opacity="0.7">
    <animate attributeName="r" values="4;8;4" dur="0.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0.3;0.7" dur="0.6s" repeatCount="indefinite"/>
</circle>
<circle cx="520" cy="150" r="5" fill="#00e5ff" opacity="0.6">
    <animate attributeName="r" values="3;7;3" dur="0.8s" repeatCount="indefinite"/>
</circle>
<circle cx="350" cy="140" r="4" fill="#ffee58" opacity="0.6">
    <animate attributeName="r" values="3;6;3" dur="0.7s" repeatCount="indefinite"/>
</circle>
<circle cx="460" cy="160" r="5" fill="#8fbf6b" opacity="0.6">
    <animate attributeName="r" values="4;7;4" dur="0.9s" repeatCount="indefinite"/>
</circle>
<circle cx="300" cy="180" r="3" fill="#ff9100" opacity="0.5">
    <animate attributeName="r" values="2;5;2" dur="1.1s" repeatCount="indefinite"/>
</circle>
<circle cx="500" cy="180" r="4" fill="#ff1744" opacity="0.5">
    <animate attributeName="r" values="3;6;3" dur="0.7s" repeatCount="indefinite"/>
</circle>
<line x1="280" y1="120" x2="280" y2="140" stroke="#00e5ff" stroke-width="2" opacity="0.5"/>
<line x1="460" y1="110" x2="460" y2="135" stroke="#ff1744" stroke-width="2" opacity="0.5"/>
</svg>''',

        "carregar": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1a1a5e"/>
        <stop offset="0.4" stop-color="#2d1b69"/>
        <stop offset="100%" stop-color="#311b92"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.2"/>
        <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
</defs>
<rect width="800" height="600" fill="url(#{grad_id})"/>
<circle cx="650" cy="100" r="50" fill="#00e5ff" opacity="0.1"/>
<circle cx="642" cy="96" r="45" fill="#1a1a5e" opacity="0.8"/>
<g fill="#fff" opacity="0.3">
    <circle cx="100" cy="55" r="1.2"/><circle cx="280" cy="40" r="1.5"/>
    <circle cx="450" cy="50" r="1.3"/><circle cx="580" cy="35" r="1.5"/>
    <circle cx="720" cy="70" r="1"/>
</g>
<ellipse cx="400" cy="660" rx="580" ry="160" fill="#1a1a5e" opacity="0.5"/>
<ellipse cx="200" cy="690" rx="300" ry="130" fill="#2d1b69" opacity="0.3"/>
<g transform="translate(280,210)">
    {_robo_corpo(0, 0, 1.0, "sono", "p8a", "#00e5ff", "#2196f3")}
</g>
<g transform="translate(540,220)">
    <rect x="-20" y="-22" width="40" height="44" rx="6" fill="#8b6914" stroke="#5a8a4a" stroke-width="1"/>
    <rect x="-18" y="-20" width="36" height="40" rx="4" fill="#5a8a4a"/>
    <path d="M-14 -10 Q-10 -4 -6 -10" fill="none" stroke="#1a1a2e" stroke-width="2" stroke-linecap="round"/>
    <path d="M6 -10 Q10 -4 14 -10" fill="none" stroke="#1a1a2e" stroke-width="2" stroke-linecap="round"/>
    <path d="M-5 5 Q0 9 5 5" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="0" cy="-26" r="2.5" fill="#00e5ff" opacity="0.5"/>
</g>
<text x="380" y="170" font-family="'Quicksand',sans-serif" font-size="28" fill="#00e5ff" opacity="0.25" font-weight="600">z</text>
<text x="420" y="145" font-family="'Quicksand',sans-serif" font-size="20" fill="#00e5ff" opacity="0.18" font-weight="600">z</text>
<text x="450" y="125" font-family="'Quicksand',sans-serif" font-size="14" fill="#00e5ff" opacity="0.12" font-weight="600">z</text>
<rect x="310" y="360" width="180" height="15" rx="5" fill="#311b92"/>
<rect x="320" y="362" width="50" height="11" rx="3" fill="#00e5ff" opacity="0.6">
    <animate attributeName="width" values="50;160;50" dur="2s" repeatCount="indefinite"/>
</rect>
<circle cx="400" cy="367" r="8" fill="#00e5ff" opacity="0.3">
    <animate attributeName="r" values="6;12;6" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite"/>
</circle>
</svg>''',
    }

    return cenas.get(cena, cenas["despertar"])


def montar_livro(historia):
    livro = {
        "titulo": historia["titulo"],
        "subtitulo": historia.get("subtitulo", ""),
        "autor": historia.get("autor", ""),
        "faixa_etaria": historia.get("faixa_etaria", "3 — 8 anos"),
        "lang": historia.get("lang", "pt-BR"),
        "texto_final": historia.get("texto_final", "Fim!"),
        "capa_svg": gerar_svg_capa(historia["titulo"], historia.get("subtitulo", "")),
        "paginas": []
    }
    for pagina in historia["paginas"]:
        svg = gerar_svg_pagina(pagina["numero"], pagina.get("cena", "despertar"))
        livro["paginas"].append({
            "texto": pagina["texto"],
            "dialogo": pagina.get("dialogo", ""),
            "svg": svg,
            "audio": ""
        })
    return livro


def exportar_json(livro, caminho="book_robo.json"):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(livro, f, ensure_ascii=False, indent=2)
    print(f"book.json gerado: {caminho}")
    return caminho


if __name__ == "__main__":
    print("=== InfoEngine — Robô Zukinha ===")
    print(f"Título: {HISTORIA['titulo']}")
    print(f"Páginas: {len(HISTORIA['paginas'])}")

    out_dir = os.path.join(os.path.dirname(__file__), "examples")
    os.makedirs(out_dir, exist_ok=True)

    livro = montar_livro(HISTORIA)
    json_path = exportar_json(livro, os.path.join(out_dir, "book_robo.json"))

    build_script = os.path.join(os.path.dirname(__file__), "build_livro.py")
    output_html = os.path.join(os.path.dirname(__file__), "..", "output", "robo_zukinha.html")
    print(f"\nPara buildar: python {build_script} {json_path} {output_html}")
