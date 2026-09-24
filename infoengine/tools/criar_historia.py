"""
Criador de Histórias Infantis — InfoEngine
Gera estrutura JSON com SVGs ricos e detalhados para livros infantis.
"""

import json
import sys
from pathlib import Path

# Paleta InfoEngine
CORES = {
    "ceu_dia": "#e3f2fd",
    "ceu_noite": "#0b081a",
    "creme": "#fdf8f0",
    "coral": "#ff7a5a",
    "dourado": "#f5a623",
    "verde": "#8fbf6b",
    "azul": "#69aee6",
    "rosa": "#fce4ec",
    "laranja": "#e8985a",
    "verde_escuro": "#5a8a4a",
    "marrom": "#8b6914",
    "roxo_suave": "#b8a9d4",
    "amarelo_claro": "#fff8dc",
    "coral_claro": "#ff8a80",
    "sombra": "#1a1a2e",
}

HISTORIA_PADRAO = {
    "titulo": "O Sonho da Estrelinha Lua",
    "subtitulo": "Uma história para embalar os sonhos",
    "autor": "Marcos Roberto",
    "faixa_etaria": "2 — 6 anos",
    "lang": "pt-BR",
    "texto_final": "Algumas coisas bonitas precisam de um pouquinho de paciência. Boa noite, estrelinha.",
    "paginas": [
        {
            "numero": 1,
            "titulo": "Lá no céu...",
            "texto": "Lá no céu, bem alto, morava uma estrelinha chamada Lua. Ela era a menor de todas, mas tinha o brilho mais bonito que já existiu.",
            "dialogo": "Ai, que soninho! Será que as crianças lá embaixo também estão com sono?",
            "cena": "estrela_ceu"
        },
        {
            "numero": 2,
            "titulo": "A Fada dos Sonhos",
            "texto": "Foi quando uma luz suave e dourada apareceu ao seu lado. Era a Fada dos Sonhos, com seu vestido feito de névoa e cabelos de luar.",
            "dialogo": "Estrelinha Lua, por que você está tão cansada?",
            "cena": "fada_magica"
        },
        {
            "numero": 3,
            "titulo": "O segredo do sono",
            "texto": "Lua arregalou os olhos. A Fada sorriu e contou um segredo que só as estrelas conhecem.",
            "dialogo": "Querida estrelinha, quando você dorme, seu brilho descansa. E quando descansa, ele fica ainda mais forte!",
            "cena": "segredos"
        },
        {
            "numero": 4,
            "titulo": "A criança acordada",
            "texto": "Lua olhou para baixo e viu uma casinha com uma luz acesa. Dentro, um menino chamado Pedro estava sentado na cama, olhando pela janela.",
            "dialogo": "Oi, estrelinha...",
            "cena": "quarto_crianca"
        },
        {
            "numero": 5,
            "titulo": "Um brilho de amizade",
            "texto": "Lá no céu, a Estrelinha Lua entendeu. Ela se sentou bem pertinho da janela de Pedro e começou a brilhar com toda a força do seu coração.",
            "dialogo": "Vou ficar comigo até eu dormir.",
            "cena": "conexao"
        },
        {
            "numero": 6,
            "titulo": "A dança das estrelas",
            "texto": "Uma a uma, as outras estrelas foram acordando. Viram Lua brilhando com tanto carinho e resolveram ajudar.",
            "dialogo": "Olha só — quando a gente se junta, a noite fica mais bonita!",
            "cena": "danca_estrelas"
        },
        {
            "numero": 7,
            "titulo": "O sono chegou",
            "texto": "O quarto de Pedro foi ficando mais quentinho. Seu cobertor parecia uma nuvem macia. Ele estava sonhando.",
            "dialogo": "Obrigado, estrelinha...",
            "cena": "sonho"
        },
        {
            "numero": 8,
            "titulo": "Hora de descansar",
            "texto": "E assim, a Estrelinha Lua fechou os olhos. Seu brilho foi ficando suave, suave, como a respiração de um bebê dormindo.",
            "dialogo": "Viu só? Você conseguiu! Agora pode dormir tranquila.",
            "cena": "dormindo"
        }
    ]
}


def _estrela_corpo(cx: int, cy: int, escala: float = 1.0, opacidade: float = 1.0, 
                   expressao: str = "feliz", cor: str = CORES["dourado"], 
                   uid: str = "") -> str:
    """Gera corpo de estrela reutilizável com sombreado e expressões."""
    s = escala
    pontas = f"{cx},{cy-35*s} {cx+6*s},{cy-12*s} {cx+34*s},{cy-12*s} {cx+10*s},{cy+4*s} " \
             f"{cx+20*s},{cy+30*s} {cx},{cy+14*s} {cx-20*s},{cy+30*s} {cx-10*s},{cy+4*s} " \
             f"{cx-34*s},{cy-12*s} {cx-6*s},{cy-12*s}"
    grad_id = f"star-grad-{uid}" if uid else f"star-grad-{cx}-{cy}"
    
    # Expressões
    if expressao == "feliz":
        olho_e = f'<circle cx="{cx-8*s}" cy="{cy-2*s}" r="{3.5*s}" fill="{CORES["sombra"]}"/>'
        olho_d = f'<circle cx="{cx+8*s}" cy="{cy-2*s}" r="{3.5*s}" fill="{CORES["sombra"]}"/>'
        bochecha_e = f'<ellipse cx="{cx-14*s}" cy="{cy+6*s}" rx="{5*s}" ry="{3*s}" fill="{CORES["coral_claro"]}" opacity="0.5"/>'
        bochecha_d = f'<ellipse cx="{cx+14*s}" cy="{cy+6*s}" rx="{5*s}" ry="{3*s}" fill="{CORES["coral_claro"]}" opacity="0.5"/>'
        boca = f'<path d="M{cx-8*s} {cy+10*s} Q{cx} {cy+18*s} {cx+8*s} {cy+10*s}" fill="none" stroke="{CORES["sombra"]}" stroke-width="{2.5*s}" stroke-linecap="round"/>'
    elif expressao == "sono":
        olho_e = f'<path d="M{cx-12*s} {cy-2*s} Q{cx-8*s} {cy+2*s} {cx-4*s} {cy-2*s}" fill="none" stroke="{CORES["sombra"]}" stroke-width="{2*s}" stroke-linecap="round"/>'
        olho_d = f'<path d="M{cx+4*s} {cy-2*s} Q{cx+8*s} {cy+2*s} {cx+12*s} {cy-2*s}" fill="none" stroke="{CORES["sombra"]}" stroke-width="{2*s}" stroke-linecap="round"/>'
        bochecha_e = ""
        bochecha_d = ""
        boca = f'<path d="M{cx-5*s} {cy+10*s} Q{cx} {cy+14*s} {cx+5*s} {cy+10*s}" fill="none" stroke="{CORES["sombra"]}" stroke-width="{2*s}" stroke-linecap="round"/>'
    elif expressao == "surpreso":
        olho_e = f'<circle cx="{cx-8*s}" cy="{cy-2*s}" r="{4.5*s}" fill="{CORES["sombra"]}"/>'
        olho_d = f'<circle cx="{cx+8*s}" cy="{cy-2*s}" r="{4.5*s}" fill="{CORES["sombra"]}"/>'
        bochecha_e = f'<ellipse cx="{cx-15*s}" cy="{cy+6*s}" rx="{5*s}" ry="{3*s}" fill="{CORES["coral_claro"]}" opacity="0.5"/>'
        bochecha_d = f'<ellipse cx="{cx+15*s}" cy="{cy+6*s}" rx="{5*s}" ry="{3*s}" fill="{CORES["coral_claro"]}" opacity="0.5"/>'
        boca = f'<circle cx="{cx}" cy="{cy+12*s}" r="{4*s}" fill="{CORES["sombra"]}"/>'
    else:  # neutro
        olho_e = f'<circle cx="{cx-8*s}" cy="{cy-2*s}" r="{3*s}" fill="{CORES["sombra"]}"/>'
        olho_d = f'<circle cx="{cx+8*s}" cy="{cy-2*s}" r="{3*s}" fill="{CORES["sombra"]}"/>'
        bochecha_e = ""
        bochecha_d = ""
        boca = f'<path d="M{cx-5*s} {cy+10*s} Q{cx} {cy+13*s} {cx+5*s} {cy+10*s}" fill="none" stroke="{CORES["sombra"]}" stroke-width="{2*s}" stroke-linecap="round"/>'
    
    brilho_e = f'<circle cx="{cx-9*s}" cy="{cy-3*s}" r="{1.2*s}" fill="#fff"/>' if "circle" in olho_e else ""
    brilho_d = f'<circle cx="{cx+7*s}" cy="{cy-3*s}" r="{1.2*s}" fill="#fff"/>' if "circle" in olho_d else ""
    
    return f'''<g opacity="{opacidade}">
  <!-- Sombra -->
  <ellipse cx="{cx}" cy="{cy+38*s}" rx="{30*s}" ry="{6*s}" fill="#000" opacity="0.1"/>
  <!-- Corpo com gradiente -->
  <defs>
    <radialGradient id="{grad_id}" cx="40%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#fff8dc"/>
      <stop offset="50%" stop-color="{cor}"/>
      <stop offset="100%" stop-color="{CORES["dourado"]}" stop-opacity="0.85"/>
    </radialGradient>
  </defs>
  <polygon points="{pontas}" fill="url(#{grad_id})" stroke="{CORES["dourado"]}" stroke-width="{1.5*s}"/>
  <!-- Brilho interno -->
  <polygon points="{pontas}" fill="url(#{grad_id})" opacity="0.3"/>
  {olho_e}{olho_d}{brilho_e}{brilho_d}{bochecha_e}{bochecha_d}{boca}
</g>'''


def gerar_svg_capa(titulo: str, subtitulo: str) -> str:
    """Gera SVG da capa com ilustração rica."""
    return f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky-cover" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.45" stop-color="#15123a"/>
      <stop offset="0.75" stop-color="#1f1b4e"/>
      <stop offset="1" stop-color="#2a235a"/>
    </linearGradient>
    <radialGradient id="glow-cover" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#sky-cover)"/>
  
  <!-- Estrelas de fundo com tamanhos variados -->
  <g fill="#fff">
    <circle cx="80" cy="60" r="1.5" opacity="0.8"/>
    <circle cx="150" cy="120" r="1" opacity="0.5"/>
    <circle cx="220" cy="40" r="2" opacity="0.7"/>
    <circle cx="300" cy="90" r="1.2" opacity="0.6"/>
    <circle cx="380" cy="30" r="1.8" opacity="0.65"/>
    <circle cx="450" cy="70" r="1" opacity="0.5"/>
    <circle cx="520" cy="45" r="2.2" opacity="0.75"/>
    <circle cx="600" cy="110" r="1.3" opacity="0.55"/>
    <circle cx="680" cy="50" r="1.6" opacity="0.6"/>
    <circle cx="750" cy="90" r="1" opacity="0.45"/>
    <circle cx="100" cy="200" r="1.4" opacity="0.5"/>
    <circle cx="200" cy="160" r="1" opacity="0.4"/>
    <circle cx="350" cy="140" r="1.6" opacity="0.55"/>
    <circle cx="500" cy="160" r="1.2" opacity="0.5"/>
    <circle cx="620" cy="190" r="1.8" opacity="0.6"/>
    <circle cx="720" cy="150" r="1" opacity="0.4"/>
  </g>
  
  <!-- Nuvens com profundidade -->
  <g opacity="0.1">
    <ellipse cx="140" cy="180" rx="90" ry="28" fill="#fff"/>
    <ellipse cx="180" cy="168" rx="70" ry="22" fill="#fff"/>
    <ellipse cx="100" cy="174" rx="55" ry="20" fill="#fff"/>
    <ellipse cx="140" cy="186" rx="75" ry="24" fill="#fff"/>
  </g>
  <g opacity="0.08">
    <ellipse cx="620" cy="210" rx="100" ry="32" fill="#fff"/>
    <ellipse cx="670" cy="196" rx="75" ry="25" fill="#fff"/>
    <ellipse cx="570" cy="202" rx="60" ry="22" fill="#fff"/>
    <ellipse cx="620" cy="218" rx="85" ry="26" fill="#fff"/>
  </g>
  
  <!-- Lua cheia ao fundo -->
  <circle cx="660" cy="95" r="58" fill="#ffd700" opacity="0.9"/>
  <circle cx="648" cy="88" r="52" fill="#0b081a" opacity="0.95"/>
  <circle cx="654" cy="92" r="47" fill="#ffd700" opacity="0.85"/>
  <circle cx="660" cy="95" r="85" fill="url(#glow-cover)"/>
  <!-- Crateras -->
  <circle cx="640" cy="85" r="6" fill="#f5a623" opacity="0.3"/>
  <circle cx="665" cy="105" r="4" fill="#f5a623" opacity="0.25"/>
  <circle cx="655" cy="115" r="3" fill="#f5a623" opacity="0.2"/>
  
  <!-- Colinas em camadas -->
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  <ellipse cx="200" cy="690" rx="320" ry="130" fill="#15123a"/>
  <ellipse cx="620" cy="680" rx="350" ry="140" fill="#15123a"/>
  
  <!-- Árvores silhueta -->
  <g fill="#0b081a" opacity="0.6">
    <rect x="120" y="500" width="8" height="40" rx="3"/>
    <circle cx="124" cy="495" r="22"/>
    <circle cx="110" cy="500" r="16"/>
    <circle cx="138" cy="500" r="16"/>
    
    <rect x="680" y="510" width="7" height="35" rx="3"/>
    <circle cx="683" cy="505" r="18"/>
    <circle cx="672" cy="510" r="13"/>
    <circle cx="694" cy="510" r="13"/>
  </g>
  
  <!-- Estrela Lua (protagonista) -->
  <g transform="translate(320,230)">
    <circle cx="80" cy="80" r="90" fill="url(#glow-cover)"/>
    {_estrela_corpo(80, 80, 1.3, 1.0, "feliz", uid="capa-lua")}
  </g>
  
  <!-- Texto -->
  <text x="400" y="430" text-anchor="middle" font-family="'Playfair Display',serif" 
        font-size="40" fill="#ffd700" font-weight="700" opacity="0.95">O Sonho da Estrelinha Lua</text>
  <text x="400" y="468" text-anchor="middle" font-family="'Quicksand',sans-serif" 
        font-size="17" fill="#a0886b" opacity="0.9">Uma história para embalar os sonhos</text>
  
  <!-- Estrelas caindo -->
  <circle cx="300" cy="520" r="3" fill="#ffd700" opacity="0.4"/>
  <circle cx="340" cy="540" r="2" fill="#ffd700" opacity="0.3"/>
  <circle cx="460" cy="530" r="2.5" fill="#ffd700" opacity="0.35"/>
  <circle cx="510" cy="550" r="2" fill="#ffd700" opacity="0.3"/>
  <circle cx="400" cy="560" r="1.5" fill="#ffd700" opacity="0.25"/>
</svg>'''


def gerar_svg_pagina(numero: int, cena: str) -> str:
    """Gera SVG rico para cada cena da história."""
    grad_id = f"sky-{numero:02d}"
    glow_id = f"glow-{numero:02d}"

    cenas = {
        "estrela_ceu": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#1f1b4e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <g fill="#fff">
    <circle cx="80" cy="50" r="1.5" opacity="0.8"/>
    <circle cx="180" cy="80" r="1" opacity="0.5"/>
    <circle cx="280" cy="40" r="2" opacity="0.7"/>
    <circle cx="380" cy="70" r="1.2" opacity="0.6"/>
    <circle cx="480" cy="35" r="1.8" opacity="0.65"/>
    <circle cx="580" cy="60" r="1" opacity="0.5"/>
    <circle cx="680" cy="45" r="2.2" opacity="0.75"/>
    <circle cx="740" cy="90" r="1.3" opacity="0.55"/>
    <circle cx="120" cy="140" r="1.4" opacity="0.5"/>
    <circle cx="350" cy="120" r="1.6" opacity="0.55"/>
    <circle cx="520" cy="130" r="1.2" opacity="0.5"/>
    <circle cx="650" cy="100" r="1.5" opacity="0.6"/>
    <circle cx="720" cy="150" r="1" opacity="0.45"/>
  </g>
  
  <!-- Nuvens -->
  <g opacity="0.1">
    <ellipse cx="150" cy="170" rx="80" ry="25" fill="#fff"/>
    <ellipse cx="185" cy="160" rx="60" ry="20" fill="#fff"/>
    <ellipse cx="115" cy="165" rx="50" ry="18" fill="#fff"/>
    <ellipse cx="150" cy="178" rx="70" ry="22" fill="#fff"/>
  </g>
  
  <!-- Colinas -->
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  <ellipse cx="200" cy="690" rx="320" ry="130" fill="#15123a"/>
  
  <!-- Árvores -->
  <g fill="#0b081a" opacity="0.5">
    <rect x="120" y="500" width="7" height="35" rx="3"/>
    <circle cx="123" cy="495" r="20"/>
    <circle cx="110" cy="500" r="14"/>
    <circle cx="136" cy="500" r="14"/>
  </g>
  
  <!-- Estrela Lua -->
  <g transform="translate(300,200)">
    <circle cx="80" cy="80" r="80" fill="url(#{glow_id})"/>
    {_estrela_corpo(80, 80, 1.15, 1.0, "sono", uid="p1-lua")}
  </g>
  
  <!-- "z z z" -->
  <text x="430" y="280" font-family="'Quicksand',sans-serif" font-size="24" fill="#ffd700" opacity="0.3" font-weight="600">z</text>
  <text x="460" y="260" font-family="'Quicksand',sans-serif" font-size="18" fill="#ffd700" opacity="0.25" font-weight="600">z</text>
</svg>''',

        "fada_magica": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#2a235a"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="asa-{numero:02d}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fce4ec" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#fce4ec" stop-opacity="0.2"/>
    </linearGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <g fill="#fff">
    <circle cx="100" cy="55" r="1.8" opacity="0.7"/>
    <circle cx="250" cy="35" r="2" opacity="0.65"/>
    <circle cx="450" cy="50" r="1.5" opacity="0.6"/>
    <circle cx="620" cy="40" r="2.2" opacity="0.7"/>
    <circle cx="740" cy="80" r="1.3" opacity="0.5"/>
    <circle cx="350" cy="90" r="1.2" opacity="0.5"/>
    <circle cx="550" cy="100" r="1.5" opacity="0.55"/>
  </g>
  
  <!-- Colinas -->
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  
  <!-- Lua -->
  <g transform="translate(280,210)">
    <circle cx="80" cy="80" r="75" fill="url(#{glow_id})"/>
    {_estrela_corpo(80, 80, 1.1, 1.0, "neutro", uid="p2-lua")}
  </g>
  
  <!-- Fada -->
  <g transform="translate(480,190)">
    <!-- Asas -->
    <path d="M50 30 Q-10 10 -20 60 Q10 90 50 70 Z" fill="url(#asa-{numero:02d})" stroke="#fce4ec" stroke-width="1" opacity="0.8"/>
    <path d="M50 30 Q110 10 120 60 Q90 90 50 70 Z" fill="url(#asa-{numero:02d})" stroke="#fce4ec" stroke-width="1" opacity="0.8"/>
    <!-- Véu de fada -->
    <ellipse cx="50" cy="40" rx="35" ry="55" fill="#fce4ec" opacity="0.15"/>
    
    <!-- Corpo -->
    <ellipse cx="50" cy="90" rx="20" ry="40" fill="#fce4ec" opacity="0.85"/>
    <!-- Vestido -->
    <path d="M30 75 Q50 70 70 75 L75 130 Q50 140 25 130 Z" fill="#fce4ec" opacity="0.7"/>
    
    <!-- Cabeça -->
    <circle cx="50" cy="45" r="22" fill="#ffd9c0"/>
    <circle cx="44" cy="42" r="3" fill="#1a1a2e"/>
    <circle cx="56" cy="42" r="3" fill="#1a1a2e"/>
    <circle cx="45" cy="41" r="1" fill="#fff"/>
    <circle cx="57" cy="41" r="1" fill="#fff"/>
    <path d="M46 50 Q50 54 54 50" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <!-- Bochechas -->
    <ellipse cx="40" cy="48" rx="5" ry="3" fill="#ff8a80" opacity="0.4"/>
    <ellipse cx="60" cy="48" rx="5" ry="3" fill="#ff8a80" opacity="0.4"/>
    <!-- Cabelo -->
    <path d="M28 45 Q22 10 50 18 Q78 10 72 45 Q65 25 50 30 Q35 25 28 45 Z" fill="#ffd700" opacity="0.9"/>
    <!-- Coroa de estrelas -->
    <polygon points="40,20 42,25 47,25 43,29 45,34 40,31 35,34 37,29 33,25 38,25" fill="#ffd700" opacity="0.8"/>
    
    <!-- Varinha mágica -->
    <line x1="75" y1="60" x2="105" y2="30" stroke="#f5a623" stroke-width="2.5"/>
    <circle cx="105" cy="30" r="6" fill="#ffd700" opacity="0.9"/>
    <circle cx="105" cy="30" r="14" fill="url(#{glow_id})"/>
    
    <!-- Brilhos mágicos -->
    <circle cx="95" cy="45" r="2.5" fill="#ffd700" opacity="0.6"/>
    <circle cx="115" cy="50" r="2" fill="#ffd700" opacity="0.5"/>
    <circle cx="100" cy="60" r="1.8" fill="#ffd700" opacity="0.45"/>
    <circle cx="120" cy="40" r="1.5" fill="#ffd700" opacity="0.4"/>
  </g>
</svg>''',

        "segredos": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#2a235a"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <g fill="#fff">
    <circle cx="100" cy="55" r="1.5" opacity="0.7"/>
    <circle cx="280" cy="35" r="2" opacity="0.65"/>
    <circle cx="480" cy="50" r="1.8" opacity="0.6"/>
    <circle cx="650" cy="45" r="1.5" opacity="0.55"/>
    <circle cx="350" cy="85" r="1.2" opacity="0.5"/>
    <circle cx="520" cy="95" r="1.3" opacity="0.5"/>
  </g>
  
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  
  <!-- Lua -->
  <g transform="translate(260,200)">
    <circle cx="80" cy="80" r="70" fill="url(#{glow_id})"/>
    {_estrela_corpo(80, 80, 1.0, 1.0, "surpreso", uid="p3-lua")}
  </g>
  
  <!-- Fada -->
  <g transform="translate(440,180)">
    <path d="M45 25 Q-5 5 -15 55 Q15 85 45 65 Z" fill="#fce4ec" opacity="0.4" stroke="#fce4ec" stroke-width="1"/>
    <path d="M45 25 Q95 5 105 55 Q75 85 45 65 Z" fill="#fce4ec" opacity="0.4" stroke="#fce4ec" stroke-width="1"/>
    <ellipse cx="45" cy="85" rx="18" ry="38" fill="#fce4ec" opacity="0.8"/>
    <circle cx="45" cy="40" r="20" fill="#ffd9c0"/>
    <circle cx="40" cy="38" r="2.5" fill="#1a1a2e"/>
    <circle cx="50" cy="38" r="2.5" fill="#1a1a2e"/>
    <circle cx="41" cy="37" r="1" fill="#fff"/>
    <circle cx="51" cy="37" r="1" fill="#fff"/>
    <path d="M42 45 Q45 48 48 45" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <ellipse cx="36" cy="43" rx="4" ry="2.5" fill="#ff8a80" opacity="0.4"/>
    <ellipse cx="54" cy="43" rx="4" ry="2.5" fill="#ff8a80" opacity="0.4"/>
    <path d="M26 40 Q22 8 45 16 Q68 8 64 40 Q58 22 45 27 Q32 22 26 40 Z" fill="#ffd700" opacity="0.85"/>
    <line x1="65" y1="55" x2="90" y2="30" stroke="#f5a623" stroke-width="2.5"/>
    <circle cx="90" cy="30" r="5" fill="#ffd700" opacity="0.9"/>
    <circle cx="90" cy="30" r="12" fill="url(#{glow_id})"/>
  </g>
  
  <!-- Símbolos de segredo (coração + estrela) -->
  <g opacity="0.4" fill="#ffd700">
    <path d="M380 280 C375 275 365 275 365 285 C365 295 380 305 380 305 C380 305 395 295 395 285 C395 275 385 275 380 280 Z"/>
    <polygon points="420,270 423,278 432,278 425,284 428,292 420,287 412,292 415,284 408,278 417,278" opacity="0.5"/>
  </g>
  <circle cx="400" cy="310" r="3" fill="#ffd700" opacity="0.3"/>
  <circle cx="410" cy="325" r="2" fill="#ffd700" opacity="0.25"/>
  <circle cx="390" cy="330" r="2.5" fill="#ffd700" opacity="0.28"/>
</svg>''',

        "quarto_crianca": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.35" stop-color="#15123a"/>
      <stop offset="1" stop-color="#1f1b4e"/>
    </linearGradient>
    <linearGradient id="janela-{numero:02d}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a1a5e"/>
      <stop offset="0.7" stop-color="#2a235a"/>
      <stop offset="1" stop-color="#15123a"/>
    </linearGradient>
    <linearGradient id="luz-{numero:02d}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffd700" stop-opacity="0.5"/>
      <stop offset="1" stop-color="#ffd700" stop-opacity="0.15"/>
    </linearGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <g fill="#fff">
    <circle cx="80" cy="50" r="1.5" opacity="0.7"/>
    <circle cx="220" cy="35" r="2" opacity="0.65"/>
    <circle cx="600" cy="45" r="1.8" opacity="0.6"/>
    <circle cx="700" cy="70" r="1.3" opacity="0.5"/>
  </g>
  
  <!-- Casa detalhada -->
  <g>
    <!-- Parede -->
    <rect x="240" y="240" width="320" height="260" rx="6" fill="#2a235a"/>
    <rect x="240" y="240" width="320" height="260" rx="6" fill="#1f1b4e" opacity="0.3"/>
    <!-- Telhado -->
    <polygon points="230,245 400,140 570,245" fill="#15123a"/>
    <polygon points="235,245 400,150 565,245" fill="#0b081a" opacity="0.5"/>
    <!-- Porta -->
    <rect x="375" y="350" width="50" height="80" rx="6" fill="#8b6914"/>
    <rect x="380" y="355" width="40" height="70" rx="4" fill="#a0886b" opacity="0.6"/>
    <circle cx="415" cy="390" r="3" fill="#ffd700"/>
    <!-- Janela 1 -->
    <rect x="280" y="280" width="85" height="75" rx="4" fill="url(#janela-{numero:02d})"/>
    <rect x="280" y="280" width="85" height="75" rx="4" fill="url(#luz-{numero:02d})"/>
    <line x1="322" y1="280" x2="322" y2="355" stroke="#1f1b4e" stroke-width="2.5"/>
    <line x1="280" y1="317" x2="365" y2="317" stroke="#1f1b4e" stroke-width="2.5"/>
    <rect x="275" y="275" width="95" height="85" rx="6" fill="none" stroke="#8b6914" stroke-width="3"/>
    <!-- Janela 2 -->
    <rect x="435" y="280" width="85" height="75" rx="4" fill="url(#janela-{numero:02d})"/>
    <rect x="435" y="280" width="85" height="75" rx="4" fill="url(#luz-{numero:02d})" opacity="0.7"/>
    <line x1="477" y1="280" x2="477" y2="355" stroke="#1f1b4e" stroke-width="2.5"/>
    <line x1="435" y1="317" x2="520" y2="317" stroke="#1f1b4e" stroke-width="2.5"/>
    <rect x="430" y="275" width="95" height="85" rx="6" fill="none" stroke="#8b6914" stroke-width="3"/>
    <!-- Detalhes da parede -->
    <rect x="255" y="255" width="20" height="20" rx="3" fill="#8b6914" opacity="0.4"/>
    <rect x="525" y="255" width="20" height="20" rx="3" fill="#8b6914" opacity="0.4"/>
  </g>
  
  <!-- Chão -->
  <rect x="240" y="500" width="320" height="50" rx="6" fill="#1f1b4e"/>
  <rect x="240" y="500" width="320" height="50" rx="6" fill="#15123a" opacity="0.4"/>
  
  <!-- Pedro na cama -->
  <g transform="translate(300,370)">
    <!-- Cabeceira -->
    <rect x="-5" y="30" width="15" height="80" rx="4" fill="#8b6914"/>
    <!-- Colchão -->
    <rect x="5" y="70" width="160" height="45" rx="8" fill="#a0886b" opacity="0.5"/>
    <!-- Cobertor -->
    <path d="M15 60 Q90 50 175 60 L175 115 L15 115 Z" fill="#69aee6" opacity="0.8"/>
    <path d="M15 60 Q90 50 175 60 L175 80 Q90 70 15 80 Z" fill="#8fc5f0" opacity="0.5"/>
    <!-- Travesseiro -->
    <ellipse cx="45" cy="65" rx="30" ry="15" fill="#fdf8f0" opacity="0.8"/>
    <!-- Pedro -->
    <circle cx="45" cy="55" r="20" fill="#ffd9c0"/>
    <circle cx="40" cy="52" r="3" fill="#1a1a2e"/>
    <circle cx="50" cy="52" r="3" fill="#1a1a2e"/>
    <circle cx="41" cy="51" r="1" fill="#fff"/>
    <circle cx="51" cy="51" r="1" fill="#fff"/>
    <path d="M42 60 Q45 63 48 60" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <ellipse cx="35" cy="58" rx="5" ry="3" fill="#ff8a80" opacity="0.3"/>
    <ellipse cx="55" cy="58" rx="5" ry="3" fill="#ff8a80" opacity="0.3"/>
    <path d="M26 55 Q22 35 45 40 Q68 35 64 55 Q58 42 45 46 Q32 42 26 55 Z" fill="#8b6914"/>
  </g>
  
  <!-- Lua olhando pela janela -->
  <g transform="translate(540,160)">
    <circle cx="30" cy="30" r="14" fill="url(#luz-{numero:02d})"/>
    {_estrela_corpo(30, 30, 0.4, 0.8, "feliz", uid="p4-lua-janela")}
  </g>
</svg>''',

        "conexao": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#1f1b4e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <!-- Lua cheia -->
  <circle cx="650" cy="90" r="52" fill="#ffd700"/>
  <circle cx="640" cy="85" r="47" fill="#0b081a"/>
  <circle cx="645" cy="88" r="42" fill="#ffd700" opacity="0.85"/>
  <circle cx="650" cy="90" r="75" fill="url(#{glow_id})"/>
  
  <g fill="#fff">
    <circle cx="100" cy="55" r="1.5" opacity="0.7"/>
    <circle cx="250" cy="35" r="2" opacity="0.65"/>
    <circle cx="420" cy="50" r="1.8" opacity="0.6"/>
    <circle cx="550" cy="70" r="1.3" opacity="0.5"/>
  </g>
  
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  
  <!-- Lua estrela brilhando -->
  <g transform="translate(270,130)">
    <circle cx="70" cy="70" r="85" fill="url(#{glow_id})"/>
    {_estrela_corpo(70, 70, 1.1, 1.0, "feliz", uid="p5-lua")}
  </g>
  
  <!-- Casa de Pedro -->
  <g transform="translate(380,330)">
    <rect x="0" y="50" width="130" height="110" rx="6" fill="#2a235a"/>
    <polygon points="0,50 65,12 130,50" fill="#15123a"/>
    <rect x="45" y="105" width="40" height="55" rx="4" fill="#8b6914"/>
    <rect x="20" y="70" width="35" height="30" rx="3" fill="#ffd700" opacity="0.4"/>
    <rect x="75" y="70" width="35" height="30" rx="3" fill="#ffd700" opacity="0.35"/>
    <!-- Pedro na janela -->
    <circle cx="37" cy="83" r="10" fill="#ffd9c0"/>
    <circle cx="34" cy="80" r="2" fill="#1a1a2e"/>
    <circle cx="40" cy="80" r="2" fill="#1a1a2e"/>
    <path d="M35 86 Q37 89 39 86" fill="none" stroke="#1a1a2e" stroke-width="1" stroke-linecap="round"/>
    <path d="M22 83 Q20 68 37 72 Q54 68 52 83 Q48 72 37 76 Q26 72 22 83 Z" fill="#8b6914"/>
  </g>
  
  <!-- Feixe de luz -->
  <path d="M340 200 Q390 260 410 360" fill="none" stroke="#ffd700" stroke-width="3" opacity="0.25" stroke-dasharray="8,5"/>
  <circle cx="375" cy="280" r="4" fill="#ffd700" opacity="0.4"/>
  <circle cx="392" cy="310" r="3" fill="#ffd700" opacity="0.35"/>
  <circle cx="405" cy="340" r="3.5" fill="#ffd700" opacity="0.3"/>
  <circle cx="360" cy="250" r="2.5" fill="#ffd700" opacity="0.3"/>
</svg>''',

        "danca_estrelas": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#1f1b4e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  <ellipse cx="200" cy="690" rx="300" ry="130" fill="#15123a"/>
  <ellipse cx="600" cy="680" rx="320" ry="140" fill="#15123a"/>
  
  <!-- Lua no centro -->
  <g transform="translate(320,170)">
    <circle cx="80" cy="80" r="95" fill="url(#{glow_id})"/>
    {_estrela_corpo(80, 80, 1.25, 1.0, "feliz", uid="p6-lua-central")}
  </g>
  
  <!-- Estrelas menores dançando -->
  <g transform="translate(110,140)">
    <circle cx="25" cy="25" r="35" fill="url(#{glow_id})" opacity="0.5"/>
    {_estrela_corpo(25, 25, 0.35, 0.85, "feliz", uid="p6-lua-esq")}
  </g>
  
  <g transform="translate(580,120)">
    <circle cx="25" cy="25" r="35" fill="url(#{glow_id})" opacity="0.5"/>
    {_estrela_corpo(25, 25, 0.32, 0.8, "surpreso", uid="p6-lua-dir")}
  </g>
  
  <g transform="translate(190,290)">
    <circle cx="20" cy="20" r="28" fill="url(#{glow_id})" opacity="0.4"/>
    {_estrela_corpo(20, 20, 0.28, 0.75, "neutro", uid="p6-lua-baixo-esq")}
  </g>
  
  <g transform="translate(540,270)">
    <circle cx="20" cy="20" r="28" fill="url(#{glow_id})" opacity="0.4"/>
    {_estrela_corpo(20, 20, 0.3, 0.7, "feliz", uid="p6-lua-baixo-dir")}
  </g>
  
  <g transform="translate(340,330)">
    <circle cx="18" cy="18" r="24" fill="url(#{glow_id})" opacity="0.35"/>
    {_estrela_corpo(18, 18, 0.25, 0.65, "neutro", uid="p6-lua-centro-baixo")}
  </g>
  
  <!-- Brilhos conectando -->
  <circle cx="200" cy="200" r="3" fill="#ffd700" opacity="0.3"/>
  <circle cx="280" cy="250" r="2.5" fill="#ffd700" opacity="0.25"/>
  <circle cx="500" cy="220" r="3" fill="#ffd700" opacity="0.3"/>
  <circle cx="560" cy="260" r="2.5" fill="#ffd700" opacity="0.25"/>
  <circle cx="400" cy="300" r="2" fill="#ffd700" opacity="0.2"/>
</svg>''',

        "sonho": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.4" stop-color="#15123a"/>
      <stop offset="1" stop-color="#2a235a"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="nuvem-{numero:02d}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fff" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0.04"/>
    </linearGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <g fill="#fff">
    <circle cx="100" cy="50" r="1.5" opacity="0.6"/>
    <circle cx="280" cy="35" r="2" opacity="0.55"/>
    <circle cx="500" cy="45" r="1.8" opacity="0.5"/>
    <circle cx="700" cy="60" r="1.5" opacity="0.45"/>
  </g>
  
  <!-- Nuvem de sonho grande -->
  <ellipse cx="400" cy="300" rx="220" ry="90" fill="url(#nuvem-{numero:02d})"/>
  <ellipse cx="380" cy="285" rx="180" ry="75" fill="url(#nuvem-{numero:02d})"/>
  <ellipse cx="420" cy="315" rx="150" ry="65" fill="url(#nuvem-{numero:02d})"/>
  
  <!-- Pedro sonhando -->
  <g transform="translate(300,310)">
    <!-- Cabeceira -->
    <rect x="-10" y="30" width="15" height="85" rx="4" fill="#8b6914" opacity="0.8"/>
    <!-- Colchão -->
    <rect x="5" y="75" width="185" height="50" rx="8" fill="#a0886b" opacity="0.4"/>
    <!-- Cobertor nuvem -->
    <ellipse cx="95" cy="60" rx="95" ry="35" fill="#e3f2fd" opacity="0.55"/>
    <ellipse cx="75" cy="52" rx="70" ry="28" fill="#fff" opacity="0.45"/>
    <ellipse cx="115" cy="55" rx="60" ry="24" fill="#fff" opacity="0.4"/>
    <!-- Travesseiro -->
    <ellipse cx="45" cy="55" rx="35" ry="18" fill="#fdf8f0" opacity="0.7"/>
    <!-- Pedro dormindo -->
    <circle cx="45" cy="45" r="22" fill="#ffd9c0"/>
    <path d="M35 43 Q38 47 44 43" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M48 43 Q51 47 57 43" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M42 53 Q45 57 50 53" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M24 44 Q20 22 48 28 Q76 22 72 44 Q66 30 48 34 Q30 30 24 44 Z" fill="#8b6914"/>
  </g>
  
  <!-- Lua brilhando -->
  <g transform="translate(340,110)">
    <circle cx="40" cy="40" r="40" fill="url(#{glow_id})"/>
    {_estrela_corpo(40, 40, 0.5, 0.6, "feliz", uid="p7-lua")}
  </g>
  
  <!-- Bolhas de sonho -->
  <circle cx="440" cy="200" r="10" fill="#fff" opacity="0.1"/>
  <circle cx="465" cy="175" r="14" fill="#fff" opacity="0.08"/>
  <circle cx="490" cy="150" r="18" fill="#fff" opacity="0.06"/>
  <circle cx="515" cy="120" r="22" fill="#fff" opacity="0.05"/>
  <circle cx="540" cy="95" r="26" fill="#fff" opacity="0.04"/>
</svg>''',

        "dormindo": f'''<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b081a"/>
      <stop offset="0.5" stop-color="#15123a"/>
      <stop offset="1" stop-color="#1f1b4e"/>
    </linearGradient>
    <radialGradient id="{glow_id}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd700" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#ffd700" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="800" height="600" fill="url(#{grad_id})"/>
  
  <!-- Lua fraca -->
  <circle cx="650" cy="90" r="48" fill="#ffd700" opacity="0.25"/>
  <circle cx="642" cy="86" r="43" fill="#0b081a" opacity="0.85"/>
  <circle cx="646" cy="88" r="38" fill="#ffd700" opacity="0.2"/>
  <circle cx="650" cy="90" r="70" fill="url(#{glow_id})"/>
  
  <g fill="#fff">
    <circle cx="100" cy="55" r="1.2" opacity="0.5"/>
    <circle cx="280" cy="40" r="1.5" opacity="0.45"/>
    <circle cx="450" cy="50" r="1.3" opacity="0.4"/>
    <circle cx="600" cy="35" r="1.5" opacity="0.45"/>
    <circle cx="720" cy="70" r="1" opacity="0.35"/>
  </g>
  
  <ellipse cx="400" cy="660" rx="580" ry="160" fill="#1f1b4e"/>
  <ellipse cx="200" cy="690" rx="300" ry="130" fill="#15123a"/>
  
  <!-- Lua estrela dormindo -->
  <g transform="translate(300,170)">
    <circle cx="70" cy="70" r="65" fill="url(#{glow_id})"/>
    {_estrela_corpo(70, 70, 1.0, 0.85, "sono", uid="p8-lua")}
  </g>
  
  <!-- "z z z" -->
  <text x="420" y="160" font-family="'Quicksand',sans-serif" font-size="30" fill="#ffd700" opacity="0.35" font-weight="600">z</text>
  <text x="455" y="135" font-family="'Quicksand',sans-serif" font-size="22" fill="#ffd700" opacity="0.28" font-weight="600">z</text>
  <text x="485" y="115" font-family="'Quicksand',sans-serif" font-size="16" fill="#ffd700" opacity="0.2" font-weight="600">z</text>
  
  <!-- Pedro dormindo -->
  <g transform="translate(320,370)">
    <rect x="-10" y="30" width="15" height="80" rx="4" fill="#8b6914" opacity="0.8"/>
    <rect x="5" y="72" width="155" height="45" rx="8" fill="#a0886b" opacity="0.4"/>
    <ellipse cx="85" cy="58" rx="80" ry="30" fill="#e3f2fd" opacity="0.4"/>
    <ellipse cx="65" cy="50" rx="55" ry="22" fill="#fff" opacity="0.35"/>
    <circle cx="50" cy="48" r="18" fill="#ffd9c0"/>
    <path d="M40 46 Q43 50 49 46" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M53 46 Q56 50 62 46" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M47 55 Q50 59 55 55" fill="none" stroke="#1a1a2e" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M30 47 Q26 28 50 33 Q74 28 70 47 Q64 34 50 38 Q36 34 30 47 Z" fill="#8b6914"/>
  </g>
</svg>'''
    }

    return cenas.get(cena, cenas["estrela_ceu"])


def montar_livro(historia: dict) -> dict:
    """Monta book.json com SVGs gerados."""
    livro = {
        "titulo": historia["titulo"],
        "subtitulo": historia.get("subtitulo", ""),
        "autor": historia.get("autor", ""),
        "faixa_etaria": historia.get("faixa_etaria", "2 — 6 anos"),
        "lang": historia.get("lang", "pt-BR"),
        "texto_final": historia.get("texto_final", "Fim!"),
        "capa_svg": gerar_svg_capa(historia["titulo"], historia.get("subtitulo", "")),
        "paginas": []
    }

    for pagina in historia["paginas"]:
        svg = gerar_svg_pagina(pagina["numero"], pagina.get("cena", "estrela_ceu"))
        livro["paginas"].append({
            "texto": pagina["texto"],
            "dialogo": pagina.get("dialogo", ""),
            "svg": svg,
            "audio": ""
        })

    return livro


def exportar_json(livro: dict, caminho: str = "book.json") -> str:
    """Exporta livro como JSON."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(livro, f, ensure_ascii=False, indent=2)
    print(f"Livro exportado: {caminho}")
    return caminho


def listar_cenas():
    """Lista cenas disponíveis."""
    return [
        "estrela_ceu", "fada_magica", "segredos", "quarto_crianca",
        "conexao", "danca_estrelas", "sonho", "dormindo"
    ]


if __name__ == "__main__":
    print("=== InfoEngine — Criador de Historias ===")
    print(f"Titulo: {HISTORIA_PADRAO['titulo']}")
    print(f"Paginas: {len(HISTORIA_PADRAO['paginas'])}")
    print(f"Cenas disponiveis: {listar_cenas()}")

    livro = montar_livro(HISTORIA_PADRAO)
    exportar_json(livro, "examples/book.json")
    print("\nPara buildar: python tools/build_livro.py examples/book.json output/livro.html")
