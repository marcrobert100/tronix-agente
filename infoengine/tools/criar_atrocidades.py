"""
As Atrocidades de um Deus Biblico v2 — InfoEngine
Ebook filosofico com 34 capitulos, SVGs premium dark, questionamento Saramago.
Autor: Marcos Roberto
"""

import json
from pathlib import Path

LIVRO = {
    "titulo": "As Atrocidades de um Deus Biblico",
    "subtitulo": "Um questionamento filosofico no estilo de Jose Saramago",
    "autor": "Marcos Roberto",
    "faixa_etaria": "Adultos - Leitura critica",
    "lang": "pt-BR",
    "texto_final": "Ainda que houvesse um Deus, a humanidade deveria envergonhar-se das historias que conta sobre ele.\n\n- Marcos Roberto",
    "capa_svg": "",
    "paginas": []
}


def gerar_svg_capa():
    parts = [
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '<linearGradient id="bg-cap" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#1a1520"/>',
        '<stop offset="0.3" stop-color="#221d2a"/>',
        '<stop offset="0.7" stop-color="#2a2435"/>',
        '<stop offset="1" stop-color="#302840"/>',
        '</linearGradient>',
        '<radialGradient id="glow-cap" cx="50%" cy="45%" r="45%">',
        '<stop offset="0%" stop-color="#6b0000" stop-opacity="0.25"/>',
        '<stop offset="60%" stop-color="#3a0000" stop-opacity="0.1"/>',
        '<stop offset="100%" stop-color="#1a1520" stop-opacity="0"/>',
        '</radialGradient>',
        '</defs>',
        '<rect width="800" height="600" fill="url(#bg-cap)"/>',
        '<rect width="800" height="600" fill="url(#glow-cap)"/>',
        '<g fill="#fff" opacity="0.03">',
        '<circle cx="95" cy="42" r="0.8"/><circle cx="210" cy="78" r="0.6"/>',
        '<circle cx="340" cy="35" r="1.0"/><circle cx="480" cy="55" r="0.7"/>',
        '<circle cx="620" cy="28" r="0.9"/><circle cx="730" cy="65" r="0.5"/>',
        '<circle cx="140" cy="130" r="0.7"/><circle cx="280" cy="110" r="0.9"/>',
        '<circle cx="420" cy="95" r="0.6"/><circle cx="560" cy="120" r="0.8"/>',
        '</g>',
        '<g transform="translate(400,230)" opacity="0.15">',
        '<rect x="-12" y="-110" width="24" height="220" fill="#6b0000" rx="3"/>',
        '<rect x="-70" y="-35" width="140" height="24" fill="#6b0000" rx="3"/>',
        '</g>',
        '<g transform="translate(400,230) rotate(180)" opacity="0.1">',
        '<rect x="-12" y="-110" width="24" height="220" fill="#8b1a1a" rx="3"/>',
        '<rect x="-70" y="-35" width="140" height="24" fill="#8b1a1a" rx="3"/>',
        '</g>',
        '<circle cx="400" cy="240" r="140" fill="url(#glow-cap)"/>',
        '<ellipse cx="390" cy="280" rx="55" ry="40" fill="#3a0000" opacity="0.4"/>',
        '<g transform="translate(400,220)">',
        '<ellipse cx="0" cy="0" rx="95" ry="55" fill="none" stroke="#6b0000" stroke-width="2.5" opacity="0.7"/>',
        '<circle cx="0" cy="0" r="35" fill="#1a1520" stroke="#6b0000" stroke-width="2"/>',
        '<circle cx="0" cy="0" r="18" fill="#6b0000" opacity="0.85"/>',
        '<circle cx="0" cy="0" r="8" fill="#8b1a1a"/>',
        '<circle cx="0" cy="0" r="3" fill="#b22222"/>',
        '<circle cx="-10" cy="-10" r="4" fill="#fff" opacity="0.3"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.1" font-family="Georgia,serif" font-size="11" letter-spacing="3">',
        '<text x="60" y="85">GENESIS</text>',
        '<text x="620" y="100">EXODO</text>',
        '<text x="80" y="400">LEVITICO</text>',
        '<text x="600" y="420">NUMEROS</text>',
        '<text x="460" y="80">JOSUE</text>',
        '<text x="100" y="280">JUIZES</text>',
        '<text x="640" y="250">SAMUEL</text>',
        '<text x="320" y="130">REIS</text>',
        '<text x="480" y="490">APOCALIPSE</text>',
        '</g>',
        '<text x="400" y="420" text-anchor="middle" font-family="Georgia,serif" font-size="34" fill="#e0dce5" font-weight="700" letter-spacing="3">As Atrocidades de um</text>',
        '<text x="400" y="468" text-anchor="middle" font-family="Georgia,serif" font-size="44" fill="#b22222" font-weight="700" letter-spacing="4">Deus Biblico</text>',
        '<line x1="220" y1="490" x2="580" y2="490" stroke="#6b0000" stroke-width="0.8" opacity="0.5"/>',
        '<text x="400" y="515" text-anchor="middle" font-family="Georgia,serif" font-size="15" fill="#a8a0b0" font-style="italic">Um questionamento filosofico no estilo de Jose Saramago</text>',
        '<text x="400" y="575" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#8a8290">Marcos Roberto</text>',
        '</svg>'
    ]
    return ''.join(parts)


def svg_base(n):
    parts = [
        '<defs>',
        '<linearGradient id="bg{}" x1="0" y1="0" x2="0" y2="1">'.format(n),
        '<stop offset="0" stop-color="#2a2530"/>',
        '<stop offset="0.3" stop-color="#30283a"/>',
        '<stop offset="0.6" stop-color="#352e42"/>',
        '<stop offset="1" stop-color="#3a334a"/>',
        '</linearGradient>',
        '<radialGradient id="glow{}" cx="50%" cy="40%" r="50%">'.format(n),
        '<stop offset="0%" stop-color="#6b0000" stop-opacity="0.15"/>',
        '<stop offset="100%" stop-color="#2a2530" stop-opacity="0"/>',
        '</radialGradient>',
        '<radialGradient id="g2-{}" cx="50%" cy="50%" r="50%">'.format(n),
        '<stop offset="0%" stop-color="#b8860b" stop-opacity="0.08"/>',
        '<stop offset="100%" stop-color="#2a2530" stop-opacity="0"/>',
        '</radialGradient>',
        '</defs>',
        '<rect width="800" height="600" fill="url(#bg{})"/>'.format(n),
        '<rect width="800" height="600" fill="url(#glow{})"/>'.format(n),
        '<g fill="#fff" opacity="0.02">',
        '<circle cx="80" cy="40" r="0.6"/><circle cx="200" cy="70" r="0.5"/>',
        '<circle cx="350" cy="30" r="0.8"/><circle cx="500" cy="55" r="0.6"/>',
        '<circle cx="650" cy="35" r="0.7"/><circle cx="130" cy="140" r="0.5"/>',
        '<circle cx="280" cy="120" r="0.7"/><circle cx="430" cy="100" r="0.5"/>',
        '<circle cx="580" cy="130" r="0.6"/><circle cx="700" cy="110" r="0.5"/>',
        '</g>'
    ]
    return ''.join(parts)


def svg_ref(texto_ref, sub_ref=""):
    parts = [
        '<text x="400" y="505" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="#c0b8c8" font-style="italic">',
        texto_ref, '</text>'
    ]
    if sub_ref:
        parts.append('<text x="400" y="525" text-anchor="middle" font-family="Georgia,serif" font-size="11" fill="#a8a0b0">')
        parts.append(sub_ref)
        parts.append('</text>')
    return ''.join(parts)


def svg_diluvio(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g opacity="0.4">',
        '<path d="M0 280 Q80 250 160 280 Q240 310 320 280 Q400 250 480 280 Q560 310 640 280 Q720 250 800 280 L800 600 L0 600 Z" fill="#3a2830"/>',
        '<path d="M0 320 Q80 290 160 320 Q240 350 320 320 Q400 290 480 320 Q560 350 640 320 Q720 290 800 320 L800 600 L0 600 Z" fill="#40303a" opacity="0.8"/>',
        '<path d="M0 360 Q80 330 160 360 Q240 390 320 360 Q400 330 480 360 Q560 390 640 360 Q720 330 800 360 L800 600 L0 600 Z" fill="#483842" opacity="0.85"/>',
        '<path d="M0 400 Q80 370 160 400 Q240 430 320 400 Q400 370 480 400 Q560 430 640 400 Q720 370 800 400 L800 600 L0 600 Z" fill="#50404a" opacity="0.9"/>',
        '<path d="M0 440 Q80 410 160 440 Q240 470 320 440 Q400 410 480 440 Q560 470 640 440 Q720 410 800 440 L800 600 L0 600 Z" fill="#584852" opacity="0.9"/>',
        '</g>',
        '<g opacity="0.4">',
        '<ellipse cx="280" cy="340" rx="45" ry="14" fill="#4a4250"/>',
        '<circle cx="275" cy="325" r="9" fill="#4a4250"/>',
        '<ellipse cx="520" cy="370" rx="38" ry="12" fill="#4a4250"/>',
        '<circle cx="516" cy="357" r="8" fill="#4a4250"/>',
        '<ellipse cx="160" cy="365" rx="32" ry="10" fill="#4a4250" opacity="0.7"/>',
        '</g>',
        '<g transform="translate(620,230)" opacity="0.2">',
        '<path d="M-50 0 L50 0 L40 35 L-40 35 Z" fill="#6b0000"/>',
        '<rect x="-45" y="-30" width="90" height="30" rx="10" fill="#6b0000"/>',
        '</g>',
        svg_ref("Genesis 7:21-23", "E toda a carne que se movia sobre a terra morreu"),
        '</svg>'
    ])


def svg_fogo(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g opacity="0.5">',
        '<path d="M300 320 Q290 220 320 160 Q305 240 340 320" fill="#6b0000" opacity="0.7"/>',
        '<path d="M350 320 Q355 190 340 130 Q365 210 350 320" fill="#8b1a1a" opacity="0.6"/>',
        '<path d="M400 320 Q410 200 395 140 Q420 220 400 320" fill="#6b0000" opacity="0.65"/>',
        '<path d="M450 320 Q445 230 460 170 Q440 240 470 320" fill="#8b1a1a" opacity="0.55"/>',
        '<path d="M500 320 Q510 240 495 180 Q520 250 500 320" fill="#6b0000" opacity="0.5"/>',
        '</g>',
        '<g fill="#b8860b" opacity="0.4">',
        '<circle cx="370" cy="240" r="5"/><circle cx="430" cy="220" r="4"/>',
        '<circle cx="350" cy="260" r="3.5"/><circle cx="450" cy="250" r="4.5"/>',
        '</g>',
        '<g fill="#5a5260" opacity="0.6">',
        '<rect x="140" y="360" width="55" height="100" rx="3"/>',
        '<rect x="210" y="380" width="40" height="80" rx="3"/>',
        '<rect x="550" y="370" width="50" height="90" rx="3"/>',
        '<rect x="610" y="390" width="35" height="70" rx="3"/>',
        '</g>',
        svg_ref("Genesis 19:24-25", "Choveu fogo e enxofre sobre Sodoma e Gomorra"),
        '</svg>'
    ])


def svg_pragas(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6b0000" opacity="0.3">',
        '<ellipse cx="180" cy="270" rx="30" ry="18"/>',
        '<ellipse cx="330" cy="290" rx="35" ry="20"/>',
        '<ellipse cx="480" cy="265" rx="32" ry="19"/>',
        '<ellipse cx="630" cy="285" rx="28" ry="16"/>',
        '</g>',
        '<g fill="#1a2a1a" opacity="0.35">',
        '<ellipse cx="280" cy="340" rx="18" ry="12"/>',
        '<circle cx="274" cy="332" r="5"/><circle cx="286" cy="332" r="5"/>',
        '<ellipse cx="460" cy="355" rx="15" ry="10"/>',
        '<circle cx="455" cy="349" r="4"/><circle cx="465" cy="349" r="4"/>',
        '</g>',
        '<g fill="#5a5260" opacity="0.4">',
        '<circle cx="220" cy="190" r="4"/>',
        '<circle cx="530" cy="210" r="3.5"/>',
        '<circle cx="380" cy="175" r="3.8"/>',
        '</g>',
        svg_ref("Exodus 7-12", "Dez pragas castigaram o Egito inteiro"),
        '</svg>'
    ])


def svg_primeiro_nascido(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<circle cx="400" cy="130" r="65" fill="#6b0000" opacity="0.15"/>',
        '<circle cx="400" cy="130" r="50" fill="#0a0005"/>',
        '<circle cx="400" cy="130" r="35" fill="#6b0000" opacity="0.12"/>',
        '<g fill="none" stroke="#b8860b" stroke-width="2" opacity="0.4">',
        '<rect x="140" y="290" width="50" height="85" rx="5"/>',
        '<line x1="165" y1="268" x2="165" y2="300"/>',
        '<rect x="340" y="290" width="50" height="85" rx="5"/>',
        '<line x1="365" y1="268" x2="365" y2="300"/>',
        '<rect x="540" y="290" width="50" height="85" rx="5"/>',
        '<line x1="565" y1="268" x2="565" y2="300"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.35">',
        '<ellipse cx="165" cy="210" rx="3" ry="10"/>',
        '<ellipse cx="365" cy="200" rx="3" ry="10"/>',
        '<ellipse cx="565" cy="215" rx="3" ry="10"/>',
        '</g>',
        svg_ref("Exodus 12:29-30", "Morreu todo primogenito do Egito"),
        '</svg>'
    ])


def svg_canaa(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(400,260)">',
        '<rect x="-5" y="-170" width="10" height="300" fill="#8a8290" rx="2"/>',
        '<rect x="-35" y="120" width="70" height="12" fill="#8a8290" rx="4"/>',
        '<polygon points="0,-190 -10,-170 10,-170" fill="#8a8290"/>',
        '</g>',
        '<g fill="#5a5260" opacity="0.5">',
        '<rect x="100" y="360" width="70" height="110" rx="3"/>',
        '<rect x="185" y="385" width="50" height="85" rx="3"/>',
        '<rect x="530" y="370" width="60" height="100" rx="3"/>',
        '<rect x="605" y="395" width="45" height="75" rx="3"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.2">',
        '<path d="M130 350 Q125 315 140 280 Q130 325 150 350"/>',
        '<path d="M560 360 Q555 325 570 290 Q560 335 575 360"/>',
        '</g>',
        svg_ref("Josue 6:21 / 1 Samuel 15:3", "Nao deixaras nada que respira"),
        '</svg>'
    ])


def svg_ursos(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<text x="400" y="180" text-anchor="middle" font-family="Georgia,serif" font-size="80" fill="#6b0000" opacity="0.1">42</text>',
        '<g transform="translate(280,290)" opacity="0.45">',
        '<ellipse cx="0" cy="0" rx="48" ry="35" fill="#1a1510"/>',
        '<circle cx="-24" cy="-30" r="15" fill="#1a1510"/>',
        '<circle cx="24" cy="-30" r="15" fill="#1a1510"/>',
        '<circle cx="-26" cy="-32" r="5" fill="#0a0a12"/>',
        '<circle cx="22" cy="-32" r="5" fill="#0a0a12"/>',
        '<circle cx="-26" cy="-33" r="2" fill="#6b0000"/>',
        '<circle cx="22" cy="-33" r="2" fill="#6b0000"/>',
        '</g>',
        '<g transform="translate(520,290)" opacity="0.45">',
        '<ellipse cx="0" cy="0" rx="48" ry="35" fill="#1a1510"/>',
        '<circle cx="-24" cy="-30" r="15" fill="#1a1510"/>',
        '<circle cx="24" cy="-30" r="15" fill="#1a1510"/>',
        '<circle cx="-26" cy="-32" r="5" fill="#0a0a12"/>',
        '<circle cx="22" cy="-32" r="5" fill="#0a0a12"/>',
        '<circle cx="-26" cy="-33" r="2" fill="#6b0000"/>',
        '<circle cx="22" cy="-33" r="2" fill="#6b0000"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.2">',
        '<circle cx="250" cy="380" r="8"/><rect x="245" y="388" width="10" height="20" rx="4"/>',
        '<circle cx="350" cy="385" r="7"/><rect x="346" y="392" width="8" height="18" rx="3"/>',
        '<circle cx="450" cy="378" r="8"/><rect x="446" y="386" width="8" height="20" rx="4"/>',
        '<circle cx="550" cy="383" r="7"/><rect x="546" y="390" width="8" height="18" rx="3"/>',
        '</g>',
        svg_ref("2 Reis 2:23-25", "Dois ursos rasgaram 42 criancas"),
        '</svg>'
    ])


def svg_escravidao(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g stroke="#8a8290" stroke-width="4" fill="none" opacity="0.4">',
        '<ellipse cx="180" cy="240" rx="22" ry="14"/>',
        '<line x1="202" y1="240" x2="265" y2="275"/>',
        '<ellipse cx="285" cy="275" rx="22" ry="14"/>',
        '<line x1="307" y1="275" x2="370" y2="310"/>',
        '<ellipse cx="390" cy="310" rx="22" ry="14"/>',
        '<line x1="412" y1="310" x2="475" y2="345"/>',
        '<ellipse cx="495" cy="345" rx="22" ry="14"/>',
        '<line x1="517" y1="345" x2="580" y2="380"/>',
        '<ellipse cx="600" cy="380" rx="22" ry="14"/>',
        '</g>',
        '<g transform="translate(400,250)" opacity="0.3">',
        '<ellipse cx="0" cy="0" rx="28" ry="42" fill="#6a6270"/>',
        '<circle cx="0" cy="-52" r="16" fill="#6a6270"/>',
        '<rect x="-24" y="-6" width="48" height="12" fill="#7a7280"/>',
        '</g>',
        svg_ref("Levitico 25:44-46", "Poderao possuir escravos para sempre"),
        '</svg>'
    ])


def svg_sacrificio(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.5">',
        '<rect x="310" y="360" width="180" height="22" rx="5"/>',
        '<rect x="330" y="310" width="140" height="50" rx="5"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.3">',
        '<path d="M365 300 Q358 250 375 210 Q362 260 385 300"/>',
        '<path d="M400 300 Q405 240 395 195 Q415 250 400 300"/>',
        '<path d="M435 300 Q442 260 428 220 Q448 265 435 300"/>',
        '</g>',
        '<g transform="translate(400,280)" opacity="0.25">',
        '<ellipse cx="0" cy="0" rx="16" ry="9" fill="#7a7280"/>',
        '<circle cx="0" cy="-18" r="7" fill="#7a7280"/>',
        '</g>',
        svg_ref("Juizes 11:30-39", "E levou-a e sacrificou-a"),
        '</svg>'
    ])


def svg_lo(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(400,260)" opacity="0.35">',
        '<rect x="-18" y="-130" width="36" height="230" fill="#9a9298" rx="8"/>',
        '<circle cx="0" cy="-145" r="15" fill="#9a9298"/>',
        '<circle cx="-5" cy="-148" r="4" fill="#8a8290"/>',
        '<circle cx="5" cy="-148" r="4" fill="#8a8290"/>',
        '<g fill="#a098a2" opacity="0.25">',
        '<circle cx="-10" cy="-90" r="2"/><circle cx="8" cy="-70" r="1.8"/>',
        '<circle cx="-7" cy="-50" r="1.5"/><circle cx="10" cy="-30" r="2"/>',
        '</g>',
        '</g>',
        '<g fill="#5a5260" opacity="0.2">',
        '<rect x="140" y="390" width="45" height="65" rx="2"/>',
        '<rect x="560" y="395" width="40" height="60" rx="2"/>',
        '</g>',
        svg_ref("Genesis 19:26", "Tornou-se uma coluna de sal"),
        '</svg>'
    ])


def svg_filhas_lo(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(400,270)">',
        '<rect x="-70" y="-90" width="140" height="180" fill="#5a5260" rx="8"/>',
        '<rect x="-58" y="-78" width="116" height="156" fill="#0a0a12" rx="5"/>',
        '<circle cx="48" cy="0" r="7" fill="#8a8290"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.35">',
        '<circle cx="220" cy="300" r="22"/><rect x="204" y="322" width="32" height="55" rx="12"/>',
        '<circle cx="580" cy="300" r="22"/><rect x="564" y="322" width="32" height="55" rx="12"/>',
        '<circle cx="150" cy="310" r="18"/><rect x="137" y="328" width="26" height="48" rx="10"/>',
        '<circle cx="650" cy="310" r="18"/><rect x="637" y="328" width="26" height="48" rx="10"/>',
        '</g>',
        svg_ref("Genesis 19:8, 11", "Tomou suas filhas... e cegou os homens"),
        '</svg>'
    ])


def svg_abraao(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.4">',
        '<rect x="310" y="370" width="180" height="18" rx="4"/>',
        '<rect x="330" y="330" width="140" height="40" rx="4"/>',
        '</g>',
        '<g transform="translate(350,310)" opacity="0.3">',
        '<circle cx="0" cy="-40" r="12" fill="#7a7280"/>',
        '<ellipse cx="0" cy="-10" rx="14" ry="30" fill="#7a7280"/>',
        '<rect x="-18" y="15" width="36" height="8" fill="#8a8290"/>',
        '</g>',
        '<g transform="translate(450,340)" opacity="0.2">',
        '<circle cx="0" cy="-15" r="8" fill="#7a7280"/>',
        '<ellipse cx="0" cy="5" rx="10" ry="18" fill="#7a7280"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.15">',
        '<path d="M430 300 Q425 270 440 240 Q430 275 445 300"/>',
        '<path d="M460 300 Q465 270 450 240 Q460 275 445 300"/>',
        '</g>',
        svg_ref("Genesis 22", "Quase sacrificou o proprio filho"),
        '</svg>'
    ])


def svg_espiritos(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6b0000" opacity="0.15">',
        '<circle cx="180" cy="190" r="35"/><circle cx="180" cy="184" r="22" fill="#050508"/>',
        '<circle cx="174" cy="182" r="5" fill="#6b0000"/><circle cx="186" cy="182" r="5" fill="#6b0000"/>',
        '<circle cx="620" cy="210" r="30"/><circle cx="620" cy="204" r="18" fill="#050508"/>',
        '<circle cx="615" cy="202" r="4.5" fill="#6b0000"/><circle cx="625" cy="202" r="4.5" fill="#6b0000"/>',
        '<circle cx="400" cy="170" r="32"/><circle cx="400" cy="164" r="20" fill="#050508"/>',
        '<circle cx="395" cy="162" r="4.8" fill="#6b0000"/><circle cx="405" cy="162" r="4.8" fill="#6b0000"/>',
        '</g>',
        '<g transform="translate(400,340)" opacity="0.3">',
        '<ellipse cx="0" cy="0" rx="22" ry="38" fill="#6a6270"/>',
        '<circle cx="0" cy="-45" r="14" fill="#6a6270"/>',
        '<circle cx="-5" cy="-47" r="3" fill="#0a0a12"/>',
        '<circle cx="5" cy="-47" r="3" fill="#0a0a12"/>',
        '</g>',
        svg_ref("1 Reis 22:19-23", "Um espirito mentiroso saiu da presenca do Senhor"),
        '</svg>'
    ])


def svg_jo(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g stroke="#8a8290" stroke-width="3" opacity="0.25">',
        '<line x1="180" y1="140" x2="180" y2="460"/>',
        '<line x1="280" y1="140" x2="280" y2="460"/>',
        '<line x1="380" y1="140" x2="380" y2="460"/>',
        '<line x1="480" y1="140" x2="480" y2="460"/>',
        '<line x1="580" y1="140" x2="580" y2="460"/>',
        '<line x1="130" y1="240" x2="630" y2="240"/>',
        '<line x1="130" y1="340" x2="630" y2="340"/>',
        '</g>',
        '<g transform="translate(400,300)" opacity="0.25">',
        '<ellipse cx="0" cy="0" rx="28" ry="45" fill="#6a6270"/>',
        '<circle cx="0" cy="-55" r="17" fill="#6a6270"/>',
        '<circle cx="-6" cy="-57" r="3.5" fill="#0a0a12"/>',
        '<circle cx="6" cy="-57" r="3.5" fill="#0a0a12"/>',
        '<path d="M-10 -44 Q0 -38 10 -44" fill="none" stroke="#0a0a12" stroke-width="2.5"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.15">',
        '<circle cx="375" cy="275" r="5"/><circle cx="425" cy="285" r="4.5"/>',
        '<circle cx="390" cy="310" r="4"/><circle cx="410" cy="325" r="5.5"/>',
        '</g>',
        svg_ref("Jo 1-2", "Apostou com Satanas a vida de um homem justo"),
        '</svg>'
    ])


def svg_cativeiro(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.4">',
        '<rect x="160" y="300" width="28" height="160" rx="3"/>',
        '<rect x="160" y="278" width="28" height="24" rx="5"/>',
        '<rect x="280" y="340" width="22" height="120" rx="3"/>',
        '<rect x="500" y="320" width="25" height="140" rx="3"/>',
        '<rect x="600" y="350" width="20" height="110" rx="3"/>',
        '<rect x="340" y="410" width="160" height="20" rx="5" transform="rotate(-4,420,420)"/>',
        '</g>',
        '<g fill="#8a8290" opacity="0.12">',
        '<ellipse cx="400" cy="190" rx="90" ry="35"/>',
        '<ellipse cx="380" cy="175" rx="65" ry="28"/>',
        '</g>',
        svg_ref("2 Reis 25:8-10", "Incendiaram a casa do Senhor"),
        '</svg>'
    ])


def svg_apocalipse(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="none" stroke="#6b0000" stroke-width="2" opacity="0.2">',
        '<circle cx="400" cy="180" r="50"/><circle cx="400" cy="180" r="38"/>',
        '<circle cx="400" cy="180" r="26"/><circle cx="400" cy="180" r="14"/>',
        '</g>',
        '<g opacity="0.2">',
        '<g transform="translate(150,320)"><ellipse cx="0" cy="0" rx="32" ry="20" fill="#9a9298"/><circle cx="-22" cy="-14" r="11" fill="#9a9298"/></g>',
        '<g transform="translate(310,320)"><ellipse cx="0" cy="0" rx="32" ry="20" fill="#6b0000"/><circle cx="-22" cy="-14" r="11" fill="#6b0000"/></g>',
        '<g transform="translate(470,320)"><ellipse cx="0" cy="0" rx="32" ry="20" fill="#0a0a12"/><circle cx="-22" cy="-14" r="11" fill="#0a0a12"/></g>',
        '<g transform="translate(640,320)"><ellipse cx="0" cy="0" rx="32" ry="20" fill="#8a8290"/><circle cx="-22" cy="-14" r="11" fill="#8a8290"/></g>',
        '</g>',
        svg_ref("Apocalipse 6-9", "Os selos da ira divina"),
        '</svg>'
    ])


def svg_saramago(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<text x="400" y="260" text-anchor="middle" font-family="Georgia,serif" font-size="130" fill="#6b0000" opacity="0.08">?</text>',
        '<g transform="translate(400,380)" opacity="0.2">',
        '<path d="M-70 0 Q-35 -12 0 0 Q35 -12 70 0 L70 48 Q35 36 0 48 Q-35 36 -70 48 Z" fill="#8a8290"/>',
        '<line x1="0" y1="0" x2="0" y2="48" stroke="#7a7280" stroke-width="1.5"/>',
        '<g fill="#4a4a55" opacity="0.4">',
        '<rect x="-55" y="8" width="45" height="2" rx="1"/>',
        '<rect x="-55" y="14" width="35" height="2" rx="1"/>',
        '<rect x="10" y="8" width="45" height="2" rx="1"/>',
        '<rect x="10" y="14" width="35" height="2" rx="1"/>',
        '</g>',
        '</g>',
        svg_ref("Jose Saramago", "O Evangelho Segundo Jesus Cristo"),
        '</svg>'
    ])


def svg_nu(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g opacity="0.2">',
        '<path d="M0 260 Q100 230 200 260 Q300 290 400 260 Q500 230 600 260 Q700 290 800 260 L800 600 L0 600 Z" fill="#0a0a12"/>',
        '<path d="M0 300 Q100 270 200 300 Q300 330 400 300 Q500 270 600 300 Q700 330 800 300 L800 600 L0 600 Z" fill="#5a5260"/>',
        '<path d="M0 340 Q100 310 200 340 Q300 370 400 340 Q500 310 600 340 Q700 370 800 340 L800 600 L0 600 Z" fill="#141420"/>',
        '</g>',
        '<g transform="translate(600,220)" opacity="0.12">',
        '<path d="M-55 0 L55 0 L45 40 L-45 40 Z" fill="#6b0000"/>',
        '<rect x="-50" y="-35" width="100" height="35" rx="12" fill="#6b0000"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.2">',
        '<ellipse cx="200" cy="320" rx="30" ry="10"/>',
        '<circle cx="197" cy="310" r="7"/>',
        '<ellipse cx="350" cy="350" rx="25" ry="8"/>',
        '<circle cx="348" cy="342" r="6"/>',
        '</g>',
        svg_ref("Genesis 6-9", "Deus afoga toda a vida na terra"),
        '</svg>'
    ])


def svg_agar(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(300,300)" opacity="0.25">',
        '<circle cx="0" cy="-45" r="14" fill="#7a7280"/>',
        '<ellipse cx="0" cy="-15" rx="16" ry="35" fill="#7a7280"/>',
        '</g>',
        '<g transform="translate(520,310)" opacity="0.18">',
        '<circle cx="0" cy="-35" r="11" fill="#6a6270"/>',
        '<ellipse cx="0" cy="-10" rx="12" ry="28" fill="#6a6270"/>',
        '<circle cx="8" cy="20" r="6" fill="#6a6270"/>',
        '</g>',
        '<g stroke="#8a8290" stroke-width="1" opacity="0.15" stroke-dasharray="5,8">',
        '<line x1="320" y1="300" x2="500" y2="310"/>',
        '</g>',
        svg_ref("Genesis 16 / 21", "Deus ordena o abandono de Agar e Ismael"),
        '</svg>'
    ])


def svg_mana(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#b8860b" opacity="0.15">',
        '<circle cx="300" cy="120" r="4"/><circle cx="350" cy="100" r="3"/>',
        '<circle cx="400" cy="90" r="5"/><circle cx="450" cy="105" r="3.5"/>',
        '<circle cx="500" cy="115" r="4"/><circle cx="280" cy="150" r="3"/>',
        '<circle cx="330" cy="135" r="4.5"/><circle cx="380" cy="125" r="3"/>',
        '<circle cx="430" cy="130" r="4"/><circle cx="480" cy="145" r="3.5"/>',
        '<circle cx="310" cy="170" r="3.5"/><circle cx="360" cy="155" r="3"/>',
        '<circle cx="410" cy="150" r="4"/><circle cx="460" cy="160" r="3"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.2">',
        '<ellipse cx="400" cy="380" rx="100" ry="35"/>',
        '</g>',
        '<g fill="#7a7280" opacity="0.15">',
        '<circle cx="340" cy="360" r="10"/><rect x="335" y="370" width="10" height="22" rx="4"/>',
        '<circle cx="380" cy="355" r="10"/><rect x="375" y="365" width="10" height="22" rx="4"/>',
        '<circle cx="420" cy="358" r="10"/><rect x="415" y="368" width="10" height="22" rx="4"/>',
        '<circle cx="460" cy="362" r="10"/><rect x="455" y="372" width="10" height="22" rx="4"/>',
        '</g>',
        svg_ref("Exodus 16", "Deus controla quem come e quem morre de fome"),
        '</svg>'
    ])


def svg_brasa(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(400,280)">',
        '<ellipse cx="0" cy="30" rx="50" ry="18" fill="#6a6270" opacity="0.4"/>',
        '<ellipse cx="0" cy="0" rx="14" ry="8" fill="#6b0000" opacity="0.6"/>',
        '<circle cx="0" cy="0" r="6" fill="#b8860b" opacity="0.5"/>',
        '<circle cx="0" cy="0" r="3" fill="#daa520" opacity="0.4"/>',
        '</g>',
        '<g fill="#b8860b" opacity="0.12">',
        '<circle cx="300" cy="200" r="3"/><circle cx="500" cy="210" r="2.5"/>',
        '<circle cx="350" cy="180" r="2.8"/><circle cx="450" cy="190" r="3.2"/>',
        '</g>',
        svg_ref("1 Reis 19:5-7", "Um anjo trouxe brasa do altar para tocar nos labios"),
        '</svg>'
    ])


def svg_leoes(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(320,300)" opacity="0.35">',
        '<ellipse cx="0" cy="0" rx="50" ry="35" fill="#1a1510"/>',
        '<circle cx="-30" cy="-28" r="18" fill="#1a1510"/>',
        '<circle cx="-34" cy="-30" r="6" fill="#0a0a12"/>',
        '<circle cx="-34" cy="-31" r="2.5" fill="#6b0000"/>',
        '<ellipse cx="-50" cy="-15" rx="25" ry="20" fill="#1a1510" opacity="0.5"/>',
        '</g>',
        '<g transform="translate(500,310)" opacity="0.3">',
        '<ellipse cx="0" cy="0" rx="42" ry="28" fill="#1a1510"/>',
        '<circle cx="-25" cy="-22" r="14" fill="#1a1510"/>',
        '<circle cx="-28" cy="-24" r="5" fill="#0a0a12"/>',
        '<circle cx="-28" cy="-25" r="2" fill="#6b0000"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.15">',
        '<circle cx="400" cy="380" r="10"/><rect x="395" y="390" width="10" height="25" rx="4"/>',
        '</g>',
        svg_ref("1 Reis 13:24", "Leoes devoraram o homem de Deus"),
        '</svg>'
    ])


def svg_mosca(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#0a0a12" opacity="0.35">',
        '<circle cx="250" cy="180" r="5"/><circle cx="248" cy="176" r="2.5" opacity="0.3"/>',
        '<circle cx="350" cy="160" r="4.5"/><circle cx="348" cy="156" r="2.2" opacity="0.3"/>',
        '<circle cx="450" cy="175" r="5.5"/><circle cx="448" cy="171" r="2.7" opacity="0.3"/>',
        '<circle cx="550" cy="165" r="4"/><circle cx="548" cy="161" r="2" opacity="0.3"/>',
        '<circle cx="300" cy="220" r="4.5"/><circle cx="400" cy="200" r="5"/>',
        '<circle cx="500" cy="210" r="4.5"/><circle cx="200" cy="250" r="4"/>',
        '<circle cx="600" cy="240" r="4.5"/><circle cx="350" cy="280" r="4"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.15">',
        '<ellipse cx="400" cy="380" rx="120" ry="40"/>',
        '<ellipse cx="400" cy="370" rx="90" ry="30"/>',
        '</g>',
        svg_ref("Exodus 8:20-32", "Mosca mortifera sobre todo o Egito"),
        '</svg>'
    ])


def svg_jose(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.4">',
        '<ellipse cx="400" cy="380" rx="120" ry="40"/>',
        '<ellipse cx="400" cy="370" rx="80" ry="22" fill="#0a0a12"/>',
        '</g>',
        '<g transform="translate(400,340)" opacity="0.2">',
        '<circle cx="0" cy="-12" r="8" fill="#7a7280"/>',
        '<ellipse cx="0" cy="5" rx="10" ry="15" fill="#7a7280"/>',
        '</g>',
        '<g fill="#7a7280" opacity="0.15">',
        '<circle cx="250" cy="320" r="12"/><rect x="243" y="332" width="14" height="30" rx="5"/>',
        '<circle cx="320" cy="315" r="12"/><rect x="313" y="327" width="14" height="30" rx="5"/>',
        '<circle cx="480" cy="318" r="12"/><rect x="473" y="330" width="14" height="30" rx="5"/>',
        '<circle cx="550" cy="322" r="12"/><rect x="543" y="334" width="14" height="30" rx="5"/>',
        '</g>',
        svg_ref("Genesis 37:24-28", "Jogaram Jose numa cova e o venderam"),
        '</svg>'
    ])


def svg_davi(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#5a5260" opacity="0.4">',
        '<rect x="200" y="300" width="180" height="120" rx="5"/>',
        '<rect x="260" y="350" width="40" height="70" rx="3" fill="#0a0a12"/>',
        '</g>',
        '<g transform="translate(340,260)" opacity="0.2">',
        '<circle cx="0" cy="-15" r="9" fill="#7a7280"/>',
        '<ellipse cx="0" cy="5" rx="11" ry="20" fill="#7a7280"/>',
        '</g>',
        '<g transform="translate(440,280)" opacity="0.15">',
        '<circle cx="0" cy="-12" r="7" fill="#6a6270"/>',
        '<ellipse cx="0" cy="3" rx="9" ry="16" fill="#6a6270"/>',
        '</g>',
        svg_ref("2 Samuel 11-12", "Davi aduterou e matou o marido de Betsabe"),
        '</svg>'
    ])


def svg_saul(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.3">',
        '<polygon points="300,450 400,280 500,450"/>',
        '<polygon points="350,450 420,320 490,450" opacity="0.5"/>',
        '</g>',
        '<g fill="#7a7280" opacity="0.15">',
        '<circle cx="340" cy="380" r="10"/><rect x="335" y="390" width="10" height="25" rx="4"/>',
        '<circle cx="380" cy="370" r="10"/><rect x="375" y="380" width="10" height="25" rx="4"/>',
        '<circle cx="420" cy="375" r="10"/><rect x="415" y="385" width="10" height="25" rx="4"/>',
        '<circle cx="460" cy="382" r="10"/><rect x="455" y="392" width="10" height="25" rx="4"/>',
        '</g>',
        svg_ref("1 Samuel 31:2-4", "Saul e seus filhos mortos no Monte Gilboa"),
        '</svg>'
    ])


def svg_sansao(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.35">',
        '<rect x="150" y="200" width="30" height="250" rx="3"/>',
        '<rect x="620" y="200" width="30" height="250" rx="3"/>',
        '<rect x="140" y="180" width="520" height="25" rx="4"/>',
        '</g>',
        '<g fill="#8a8290" opacity="0.15" transform="rotate(-12,400,350)">',
        '<rect x="280" y="300" width="240" height="18" rx="4"/>',
        '</g>',
        '<g transform="translate(400,340)" opacity="0.2">',
        '<circle cx="0" cy="-20" r="10" fill="#7a7280"/>',
        '<ellipse cx="0" cy="5" rx="12" ry="25" fill="#7a7280"/>',
        '</g>',
        svg_ref("Juizes 16:23-30", "Sansao derrubou o templo sobre si e outros"),
        '</svg>'
    ])


def svg_jezabel(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.3">',
        '<rect x="250" y="300" width="120" height="100" rx="5"/>',
        '<rect x="430" y="300" width="120" height="100" rx="5"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.12">',
        '<ellipse cx="310" cy="290" rx="25" ry="8"/>',
        '<ellipse cx="490" cy="290" rx="25" ry="8"/>',
        '</g>',
        svg_ref("1 Reis 21", "Acaabe e Jezabel: assassinato por vinha"),
        '</svg>'
    ])


def svg_baal(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#7a7280" opacity="0.12">',
        '<circle cx="120" cy="350" r="8"/><rect x="116" y="358" width="8" height="18" rx="3"/>',
        '<circle cx="160" cy="345" r="8"/><rect x="156" y="353" width="8" height="18" rx="3"/>',
        '<circle cx="200" cy="355" r="8"/><rect x="196" y="363" width="8" height="18" rx="3"/>',
        '<circle cx="240" cy="340" r="8"/><rect x="236" y="348" width="8" height="18" rx="3"/>',
        '<circle cx="280" cy="350" r="8"/><rect x="276" y="358" width="8" height="18" rx="3"/>',
        '<circle cx="320" cy="345" r="8"/><rect x="316" y="353" width="8" height="18" rx="3"/>',
        '<circle cx="360" cy="355" r="8"/><rect x="356" y="363" width="8" height="18" rx="3"/>',
        '<circle cx="400" cy="340" r="8"/><rect x="396" y="348" width="8" height="18" rx="3"/>',
        '<circle cx="440" cy="350" r="8"/><rect x="436" y="358" width="8" height="18" rx="3"/>',
        '<circle cx="480" cy="345" r="8"/><rect x="476" y="353" width="8" height="18" rx="3"/>',
        '<circle cx="520" cy="355" r="8"/><rect x="516" y="363" width="8" height="18" rx="3"/>',
        '<circle cx="560" cy="340" r="8"/><rect x="556" y="348" width="8" height="18" rx="3"/>',
        '<circle cx="600" cy="350" r="8"/><rect x="596" y="358" width="8" height="18" rx="3"/>',
        '<circle cx="640" cy="345" r="8"/><rect x="636" y="353" width="8" height="18" rx="3"/>',
        '<circle cx="680" cy="355" r="8"/><rect x="676" y="363" width="8" height="18" rx="3"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.15">',
        '<path d="M380 300 Q375 260 390 230 Q380 265 395 300"/>',
        '<path d="M420 300 Q425 260 410 230 Q420 265 405 300"/>',
        '</g>',
        svg_ref("1 Reis 18:19-40", "Elias matou 450 profetas de Baal"),
        '</svg>'
    ])


def svg_reis(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.35">',
        '<rect x="130" y="280" width="35" height="180" rx="3"/>',
        '<rect x="180" y="310" width="28" height="150" rx="3"/>',
        '<rect x="280" y="300" width="32" height="160" rx="3"/>',
        '<rect x="490" y="290" width="30" height="170" rx="3"/>',
        '<rect x="540" y="320" width="25" height="140" rx="3"/>',
        '<rect x="640" y="300" width="30" height="160" rx="3"/>',
        '</g>',
        '<g fill="#6b0000" opacity="0.08">',
        '<path d="M150 270 Q145 240 160 210 Q150 250 165 270"/>',
        '<path d="M300 290 Q295 260 310 230 Q300 270 315 290"/>',
        '<path d="M510 280 Q505 250 520 220 Q510 260 525 280"/>',
        '<path d="M660 290 Q655 260 670 230 Q660 270 675 290"/>',
        '</g>',
        svg_ref("2 Reis 17-25", "Destruicao em massa registrada nos Livros dos Reis"),
        '</svg>'
    ])


def svg_geena(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g opacity="0.45">',
        '<path d="M300 400 Q290 300 320 230 Q305 320 345 400" fill="#6b0000" opacity="0.7"/>',
        '<path d="M350 400 Q355 280 340 210 Q370 300 350 400" fill="#8b1a1a" opacity="0.6"/>',
        '<path d="M400 400 Q410 290 395 220 Q420 310 400 400" fill="#6b0000" opacity="0.65"/>',
        '<path d="M450 400 Q445 310 460 240 Q440 320 470 400" fill="#8b1a1a" opacity="0.55"/>',
        '<path d="M500 400 Q510 320 495 250 Q520 330 500 400" fill="#6b0000" opacity="0.5"/>',
        '</g>',
        '<g fill="#b8860b" opacity="0.2">',
        '<circle cx="370" cy="310" r="5"/><circle cx="430" cy="290" r="4"/>',
        '<circle cx="350" cy="330" r="3.5"/><circle cx="450" cy="320" r="4.5"/>',
        '</g>',
        '<g fill="#0a0a12" opacity="0.2">',
        '<ellipse cx="400" cy="420" rx="180" ry="30"/>',
        '</g>',
        svg_ref("Mateus 25:41 / Marcos 9:43", "Fogo eterno preparado para o diabo"),
        '</svg>'
    ])


def svg_ester(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(400,260)">',
        '<rect x="-8" y="-140" width="16" height="240" fill="#8a8290" rx="2"/>',
        '<rect x="-40" y="90" width="80" height="10" fill="#8a8290" rx="3"/>',
        '<polygon points="0,-160 -10,-140 10,-140" fill="#8a8290"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.2">',
        '<circle cx="200" cy="380" r="12"/><rect x="194" y="392" width="12" height="28" rx="5"/>',
        '<circle cx="300" cy="375" r="12"/><rect x="294" y="387" width="12" height="28" rx="5"/>',
        '<circle cx="500" cy="378" r="12"/><rect x="494" y="390" width="12" height="28" rx="5"/>',
        '<circle cx="600" cy="382" r="12"/><rect x="594" y="394" width="12" height="28" rx="5"/>',
        '</g>',
        svg_ref("Ester 8-9", "Genocidio autorizado contra os amalequitas"),
        '</svg>'
    ])


def svg_salomao(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6a6270" opacity="0.2">',
        '<circle cx="120" cy="360" r="6"/><rect x="117" y="366" width="6" height="14" rx="3"/>',
        '<circle cx="150" cy="355" r="6"/><rect x="147" y="361" width="6" height="14" rx="3"/>',
        '<circle cx="180" cy="365" r="6"/><rect x="177" y="371" width="6" height="14" rx="3"/>',
        '<circle cx="210" cy="350" r="6"/><rect x="207" y="356" width="6" height="14" rx="3"/>',
        '<circle cx="240" cy="360" r="6"/><rect x="237" y="366" width="6" height="14" rx="3"/>',
        '<circle cx="270" cy="355" r="6"/><rect x="267" y="361" width="6" height="14" rx="3"/>',
        '<circle cx="300" cy="365" r="6"/><rect x="297" y="371" width="6" height="14" rx="3"/>',
        '<circle cx="330" cy="350" r="6"/><rect x="327" y="356" width="6" height="14" rx="3"/>',
        '<circle cx="360" cy="360" r="6"/><rect x="357" y="366" width="6" height="14" rx="3"/>',
        '<circle cx="390" cy="355" r="6"/><rect x="387" y="361" width="6" height="14" rx="3"/>',
        '<circle cx="420" cy="365" r="6"/><rect x="417" y="371" width="6" height="14" rx="3"/>',
        '<circle cx="450" cy="350" r="6"/><rect x="447" y="356" width="6" height="14" rx="3"/>',
        '<circle cx="480" cy="360" r="6"/><rect x="477" y="366" width="6" height="14" rx="3"/>',
        '<circle cx="510" cy="355" r="6"/><rect x="507" y="361" width="6" height="14" rx="3"/>',
        '<circle cx="540" cy="365" r="6"/><rect x="537" y="371" width="6" height="14" rx="3"/>',
        '<circle cx="570" cy="350" r="6"/><rect x="567" y="356" width="6" height="14" rx="3"/>',
        '<circle cx="600" cy="360" r="6"/><rect x="597" y="366" width="6" height="14" rx="3"/>',
        '<circle cx="630" cy="355" r="6"/><rect x="627" y="361" width="6" height="14" rx="3"/>',
        '<circle cx="660" cy="365" r="6"/><rect x="657" y="371" width="6" height="14" rx="3"/>',
        '</g>',
        '<g fill="#b8860b" opacity="0.08">',
        '<rect x="350" y="310" width="100" height="60" rx="5"/>',
        '<circle cx="400" cy="300" r="15" fill="#7a7280"/>',
        '</g>',
        svg_ref("1 Reis 11:3", "700 mulheres e 300 concubinas"),
        '</svg>'
    ])


def svg_lia_raquel(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g transform="translate(280,300)" opacity="0.22">',
        '<circle cx="0" cy="-40" r="13" fill="#7a7280"/>',
        '<ellipse cx="0" cy="-10" rx="15" ry="32" fill="#7a7280"/>',
        '</g>',
        '<g transform="translate(520,300)" opacity="0.18">',
        '<circle cx="0" cy="-40" r="13" fill="#6a6270"/>',
        '<ellipse cx="0" cy="-10" rx="15" ry="32" fill="#6a6270"/>',
        '</g>',
        '<g fill="#6a6270" opacity="0.12">',
        '<circle cx="230" cy="370" r="7"/><rect x="226" y="377" width="8" height="16" rx="3"/>',
        '<circle cx="260" cy="368" r="7"/><rect x="256" y="375" width="8" height="16" rx="3"/>',
        '<circle cx="290" cy="372" r="7"/><rect x="286" y="379" width="8" height="16" rx="3"/>',
        '<circle cx="320" cy="366" r="7"/><rect x="316" y="373" width="8" height="16" rx="3"/>',
        '<circle cx="480" cy="369" r="7"/><rect x="476" y="376" width="8" height="16" rx="3"/>',
        '<circle cx="510" cy="371" r="7"/><rect x="506" y="378" width="8" height="16" rx="3"/>',
        '</g>',
        svg_ref("Genesis 29-30", "Duas mulheres competindo por filhos"),
        '</svg>'
    ])


def svg_lucas(n):
    return ''.join([
        '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">',
        svg_base(n),
        '<g fill="#6b0000" opacity="0.15">',
        '<path d="M300 350 Q290 260 320 190 Q305 270 340 350"/>',
        '<path d="M350 350 Q355 240 340 170 Q365 250 350 350"/>',
        '<path d="M400 350 Q410 250 395 180 Q420 260 400 350"/>',
        '<path d="M450 350 Q445 270 460 200 Q440 280 470 350"/>',
        '<path d="M500 350 Q510 280 495 210 Q520 290 500 350"/>',
        '</g>',
        '<g fill="#b8860b" opacity="0.15">',
        '<circle cx="370" cy="280" r="5"/><circle cx="430" cy="260" r="4"/>',
        '<circle cx="350" cy="300" r="3.5"/><circle cx="450" cy="290" r="4.5"/>',
        '</g>',
        svg_ref("Mateus 10:28 / Lucas 12:4-5", "Aquele que pode destruir alma e corpo no inferno"),
        '</svg>'
    ])


SVG_FN = {
    1: svg_nu, 2: svg_diluvio, 3: svg_fogo, 4: svg_pragas,
    5: svg_primeiro_nascido, 6: svg_canaa, 7: svg_ursos,
    8: svg_escravidao, 9: svg_sacrificio, 10: svg_abraao,
    11: svg_lo, 12: svg_filhas_lo, 13: svg_agar,
    14: svg_espiritos, 15: svg_jo, 16: svg_jo,
    17: svg_cativeiro, 18: svg_apocalipse, 19: svg_brasa,
    20: svg_leoes, 21: svg_mosca, 22: svg_mana,
    23: svg_jose, 24: svg_davi, 25: svg_saul,
    26: svg_sansao, 27: svg_jezabel, 28: svg_baal,
    29: svg_reis, 30: svg_ester, 31: svg_salomao,
    32: svg_lia_raquel, 33: svg_geena, 34: svg_lucas,
    35: svg_saramago,
}

CAPITULOS = [
    {"titulo": "I - O Plano Original: O Deus Que Sabia do Diluvio",
     "subtitulo": "Genesis 6-7",
     "texto": "O Senhor viu que a maldade do homem se tornara grande na terra... E o Senhor se arrependeu de ter feito o homem na terra, e isso o entristeceu.",
     "dialogo": "Se Deus sabia desde a eternidade que o mundo se corromperia, por que criou assim? O arrependimento de um ser omnisciente e uma contradição logica. Um deus que se arrepende de suas proprias criacoes nao e onisciente - e um entao amador que cometeu um erro de projeto."},
    {"titulo": "II - O Diluvio: Genocidio Universal",
     "subtitulo": "Genesis 7:21-23",
     "texto": "E toda a carne que se movia sobre a terra morreu: aves, gado, animais selvagens, todas as criaturas rastejantes e todos os seres humanos.",
     "dialogo": "Deus afogou criancas, idosos, enfermos, animais inocentes - tudo porque nao gostou do que o homem fez. Se era onipotente, podia ter mudado o coracao dos homens. Se era bondoso, nao teria matado os inocentes junto com os culpados."},
    {"titulo": "III - Sodoma e Gomorra: Fogo do Ceu",
     "subtitulo": "Genesis 19:24-25",
     "texto": "Entao o Senhor fez chover sobre Sodoma e Gomorra enxofre e fogo do ceu. Destruio aquelas cidades, toda a planicie, todos os habitantes.",
     "dialogo": "Deus destruiu cidades inteiras por causa da homossexualidade - mas nao fez nada quando Lot ofereceu suas filhas virgens para serem estupradas por uma multidao. A homofobia divina e seletiva."},
    {"titulo": "IV - As Pragas do Egito: Tortura Coletiva",
     "subtitulo": "Exodus 7-12",
     "texto": "Agua em sangue. Sapos, moscas, murri nhos, ulceras, granizo, gafanhotos, escuridao. Cada praga castigou o povo egipcio inteiro.",
     "dialogo": "Deus castiga o povo inteiro pelo pecado de um governante. Criancas egipcias morreram com ulceras porque seu farao desobedeceu. Isso nao e justica - e terrorismo divino."},
    {"titulo": "V - O Massacre dos Primeiros-Nascidos",
     "subtitulo": "Exodus 12:29-30",
     "texto": "A meia-noite, o Senhor feriu todo primogenito do Egito, desde o primogenito de Farao ate o primogenito do cativo.",
     "dialogo": "O maior infanticidio da historia: Deus mata todas as criancas primogenitas do Egito. E depois se vangloria disso. Que tipo de entidade celebra a morte de criancas?"},
    {"titulo": "VI - A Conquista de Canaã: Genocidio Etnico",
     "subtitulo": "Josue 6:21 / 1 Samuel 15:3",
     "texto": "'Nao pouparas nada o que respira; destruiras absolutamente aos hivitas, cananeus, perizeus, hititas e jebuseus.'",
     "dialogo": "Deus ordena o exterminio completo de nacoes inteiras. Homens, mulheres, criancas, idosos, animais - tudo. E quando Saul hesita, Deus o rejeita como rei."},
    {"titulo": "VII - Os Urso de Eliseu: 42 Criancas Mortas",
     "subtitulo": "2 Reis 2:23-25",
     "texto": "Uns meninos zombaram de Eliseu: 'Sobe, careca!' Ele os amaldicoou. Dois ursos sairam e despedacaram 42 criancas.",
     "dialogo": "Um profeta invoca ursos para matar criancas porque fizeram piada da careca dele. Que tipo de deus responde a xingamento com morte de menores?"},
    {"titulo": "VIII - A Escravidao: Mandamento Divino",
     "subtitulo": "Levitico 25:44-46",
     "texto": "'Possuireis escravos e escravas das nacoes ao vosso redor... e os deixareis como heranca para vossos filhos.'",
     "dialogo": "Deus nao apenas permite a escravidao - a regulamenta. Da instrucoes detalhadas sobre como bater neles e como passa-los como propriedade."},
    {"titulo": "IX - Jephthah e sua Filha: Sacrificio Humano",
     "subtitulo": "Juizes 11:30-39",
     "texto": "Jephthah fez um voto: 'O que sair da minha casa sera do Senhor, e o queimarei em holocausto.' Sua filha unica lhe saiu ao encontro. E ele a sacrificou.",
     "dialogo": "Um juiz de Israel faz uma aposta com Deus e perde. Em vez de nao cumprir o voto, ele queima sua propria filha. A Biblia apresenta como exemplo de fe."},
    {"titulo": "X - Abraao e Isaque: O Teste Cruel",
     "subtitulo": "Genesis 22",
     "texto": "Deus ordenou a Abraao: 'Toma teu filho, teu unico filho Isaque, e o oferece em holocausto.'",
     "dialogo": "Deus testa a lealdade de Abraao ordenando que ele sacrifice o proprio filho. Um deus que brinca com o sofrimento humano e psicopata."},
    {"titulo": "XI - A Mulher de Lo: Sal por Olhar",
     "subtitulo": "Genesis 19:26",
     "texto": "Mas sua esposa olhou para tras, e tornou-se uma coluna de sal.",
     "dialogo": "Deus destruiu cidades inteiras, mas castiga uma mulher por olhar para tras - um ato humano e compreensivel. Que deus pune curiosidade com aniquilacao total?"},
    {"titulo": "XII - As Filhas de Lo: Violencia Silenciada",
     "subtitulo": "Genesis 19:8, 11",
     "texto": "'Tenho duas filhas que ainda nao conhecem homem; tomarei-as e farei com elas o que vos parecer bom.' E os homens ficaram cegos.",
     "dialogo": "Lot oferece suas filhas virgens para serem estupradas. Deus nao intervem - apenas cega os agressores. As filhas sao tratadas como moeda de troca."},
    {"titulo": "XIII - Sara e Agar: Escravidao e Abandono",
     "subtitulo": "Genesis 16 / 21",
     "texto": "Sara expulsou Agar e Ismael para o deserto, sem agua e comida. Deus nao impediu.",
     "dialogo": "Uma mulher escravizada e usada para produzir um herdeiro. Quando cumpre seu papel, e expulsa com o filho para morrer no deserto."},
    {"titulo": "XIV - Espiritos Mentirosos: O Deus Enganador",
     "subtitulo": "1 Reis 22:19-23",
     "texto": "'Eu porei espirito mentiroso na boca de todos os teus profetas.' E o Senhor disse: 'Seduziras e venceras.'",
     "dialogo": "Deus envia um espirito mentiroso para enganar um rei. Se o proprio Deus mente, como confiar em suas palavras?"},
    {"titulo": "XV - A Aposta de Deus: Sofrimento de Jo",
     "subtitulo": "Jo 1-2",
     "texto": "Satanas perguntou: 'Estende a tua mao e toca tudo o que ele tem.' O Senhor disse: 'Eis que tudo esta em teu poder.'",
     "dialogo": "Deus aposta com Satanás a vida de um homem justo. Perde filhos, propriedades, saude - tudo por uma aposta celestial."},
    {"titulo": "XVI - Jo: Mais Sofrimento, Menos Respostas",
     "subtitulo": "Jo 3-4",
     "texto": "Deus nunca responde diretamente a Jo. Apenas questiona: 'Onde estavas tu quando eu fundei a terra?'",
     "dialogo": "Apos todo o sofrimento, Deus nunca explica o por que. Apenas demonstra poder. Isso nao e consolo - e intimidação."},
    {"titulo": "XVII - O Cativeiro Babilonico",
     "subtitulo": "2 Reis 25:8-10",
     "texto": "Nabuzaradã incendiou a casa do Senhor, a casa real, todas as casas de Jerusalém.",
     "dialogo": "Deus permite a destruicao do proprio templo. Milhares sao deportados, escravizados, mortos. Se e onipotente, por que nao protegeu?"},
    {"titulo": "XVIII - A Ira do Cordeiro: Apocalipse",
     "subtitulo": "Apocalipse 6-9",
     "texto": "Os selos: cavaleiro branco, vermelho, preto e palido. Fome, guerra, morte. Martires clamam vinganca.",
     "dialogo": "No final dos tempos, Deus nao traz paz - traz destruicao em escala planetaria. O Apocalipse nao e redencao - e vinganca divina."},
    {"titulo": "XIX - A Brasa do Altar: Profeta Enganado",
     "subtitulo": "1 Reis 19:5-7",
     "texto": "Um anjo tocou nos labios de Elias com uma brasa tirada do altar.",
     "dialogo": "Deus usa um anjo para tocar nos labios de um profeta com fogo. A brasa nao cura - marca. O toque divino e tambem um toque de fogo."},
    {"titulo": "XX - Os Leoes: Falsos Profetas Mortos",
     "subtitulo": "1 Reis 13:24",
     "texto": "Um leao encontrou o homem de Deus e o matou. E havia muitos leoes na terra.",
     "dialogo": "Deus envia leoes para matar um profeta que desobe deciu. A morte por leoes e apresentada como justica divina."},
    {"titulo": "XXI - A Mosca Mortifera",
     "subtitulo": "Exodus 8:20-32",
     "texto": "Moscas mortiferas entraram na casa de Farao, nos servos e no povo. Todo o Egito foi contaminado.",
     "dialogo": "Deus cria moscas especificas para matar inocentes. A precision da praga mostra intencionalidade. Nao e acidente - e projeto."},
    {"titulo": "XXII - O Mana do Ceu: Controle Alimentar",
     "subtitulo": "Exodus 16",
     "texto": "Deus fornece mana do ceu - mas apenas o suficiente para cada dia. Quem guardou demais apodreceu.",
     "dialogo": "Deus controla quem come e quem morre de fome. Mana que apodrece se guardada e uma forma de controle."},
    {"titulo": "XXIII - Jose na Cova: Traicao Fraterna",
     "subtitulo": "Genesis 37:24-28",
     "texto": "Os irmaos de Jose jogaram-no numa cova vazia. Depois o venderam como escravo por 20 pecas de prata.",
     "dialogo": "Deus permite que Jose seja vendido como escravo pelos proprios irmaos. A Biblia apresenta isso como parte do 'plano divino'."},
    {"titulo": "XXIV - Davi e Betsabe: Aduterio e Assassinato",
     "subtitulo": "2 Samuel 11-12",
     "texto": "Davi aduterou com Betsabe e matou o marido dela. O Senhor enviou fome e morte como punicao.",
     "dialogo": "Davi comete aduterio e assassinato. A punicao divina atinge o povo e o filho - inocentes pagam pelo pecado do rei."},
    {"titulo": "XXV - Saul e seus Filhos: Morte no Gilboa",
     "subtitulo": "1 Samuel 31:2-4",
     "texto": "Saul caiu sobre a propria espada. Seus filhos morreram junto.",
     "dialogo": "Deus rejeitou Saul e permitiu que ele fosse destruido. Os filhos de Saul morreram - inocentes arrastados pela ira divina."},
    {"titulo": "XXVI - Sansao: Suicidio Forçado",
     "subtitulo": "Juizes 16:23-30",
     "texto": "Sansao empurrou as colunas do templo. Morreram mais os que Sansao matou em sua morte.",
     "dialogo": "Deus restaura a forca de Sansao apenas para que ele cometa suicidio e mate milhares. A morte de Sansao e celebrada como fe."},
    {"titulo": "XXVII - Acaabe e Jezabel: Assassinato por Vinha",
     "subtitulo": "1 Reis 21",
     "texto": "Jezabel mandou matar Nabote para que Acaabe pudesse roubar sua vinha.",
     "dialogo": "Acaabe e Jezabel roubam e matam por uma vinha. A Biblia os condena - mas o proprio Deus ordenou genocidio por terras."},
    {"titulo": "XXVIII - Elias e os 450 Profetas de Baal",
     "subtitulo": "1 Reis 18:19-40",
     "texto": "Elias mandou matar todos os 450 profetas de Baal. E o sangue encheu o ribeiro.",
     "dialogo": "Elias mata 450 homens por sua religiao e e elogiado. Se hoje alguem fizesse isso, seria terrorista."},
    {"titulo": "XXIX - Livros dos Reis: Destruicao em Massa",
     "subtitulo": "2 Reis 17-25",
     "texto": "Rei Assirio destruiu Samaria. Rei Babilonico destruiu Jerusalém. Tudo queimado.",
     "dialogo": "Os Livros dos Reis sao um registro de destruicao em massa. Deus permite que reis estrangeiros destruam seu proprio povo."},
    {"titulo": "XXX - Ester e o Genocidio dos Amalequitas",
     "subtitulo": "Ester 8-9",
     "texto": "Os judeus mataram 75.000 homens em um unico dia. E a Biblia celebra isso.",
     "dialogo": "O Livro de Ester celebra o genocidio de 75.000 pessoas. Se o genocidio e pecado quando outros o fazem, por que e virtude quando o povo de Deus o comete?"},
    {"titulo": "XXXI - Salomao: 700 Mulheres e 300 Concubinas",
     "subtitulo": "1 Reis 11:3",
     "texto": "Salomao teve 700 mulheres de nobreza e 300 concubinas.",
     "dialogo": "Deus abençoa Salomao com sabedoria - mas ele acumula 1.000 mulheres como propriedade. As mulheres sao objetos, trofeus."},
    {"titulo": "XXXII - Lia e Raquel: Competicao Reprodutiva",
     "subtitulo": "Genesis 29-30",
     "texto": "Lia teve 6 filhos. Raquel teve 2. A competicao por filhos era intensa.",
     "dialogo": "Duas mulheres competindo por filhos como se fossem trofeus. Deus abre e fecha o ventre de cada uma como ferramenta de poder."},
    {"titulo": "XXXIII - A Geena: Fogo Eterno",
     "subtitulo": "Mateus 25:41 / Marcos 9:43",
     "texto": "'Ide, malditos, para o fogo eterno preparado para o diabo e seus anjos.'",
     "dialogo": "Deus prepara um lugar de sofrimento eterno para a maioria da humanidade. Se Ele sabia que a maioria iria para a Geena, por que criou?"},
    {"titulo": "XXXIV - O Silencio de Deus: Saramago e a Pergunta Final",
     "subtitulo": "Conclusao",
     "texto": "'Nao sou eu um escritor cristao? Sim, mas um escritor cristao que poe em duvida a fe.' - Jose Saramago",
     "dialogo": "Saramago nao negou Deus - negou a imagem que a religiao construiu dele. As atrocidades do Antigo Testamento nao sao acidentes - sao o carater de quem as ordenou."}
]


def montar_livro():
    LIVRO["capa_svg"] = gerar_svg_capa()
    for i, cap in enumerate(CAPITULOS, 1):
        svg_fn = SVG_FN.get(i, lambda n: '<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">' + svg_base(n) + '</svg>')
        svg = svg_fn(i)
        LIVRO["paginas"].append({
            "texto": cap["texto"].strip(),
            "dialogo": cap["dialogo"].strip(),
            "svg": svg,
            "audio": ""
        })
    return LIVRO


def main():
    livro = montar_livro()
    saida = Path(__file__).parent.parent / "examples" / "atrocidades_book.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(livro, f, ensure_ascii=False, indent=2)
    print(f"[criar_atrocidades] OK: {saida}")
    print(f"  Capitulos: {len(livro['paginas'])}")
    print(f"  Build: python tools/build_livro.py {saida} output/atrocidades.html")


if __name__ == "__main__":
    main()
