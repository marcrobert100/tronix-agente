# Guia de Ilustração SVG — InfoEngine

Objetivo: ilustrações que parecem de livro infantil, não "desenhos geométricos". Chave: linguagem de formas, cores, expressões, camadas e detalhes.

## Canvas e Camadas

Usar sempre:

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
```

Cada página, de trás para frente, 4 camadas:

1. **Céu/fundo:** Blocos de cor ou gradiente suave. Sol, lua, nuvens.
2. **Plano de fundo:** Colinas, árvores, casas. Baixa saturação, formas simples.
3. **Chão/meio-ambiente:** Onde o personagem está ou interage.
4. **Personagem e primeiro plano:** Maior, mais vibrante, centro ou terço horizontal.

## Linguagem de Formas: Priorizar Arredondado

Livro infantil não deve ter contornos pontiagudos:

- Corpos: elipses, círculos, retângulos arredondados.
- Se precisar de ponta (espinhos, árvore), manter整体 robusto e arredondado.
- Usar curvas Q/C em vez de linhas retas.
- Nuvens: 3–4 círculos sobrepostos.
- Árvores: copa ondulada e tronco curto e grosso.

## Rosto do Personagem

- Olhos: círculos pretos + círculo branco de destaque.
- Bochechas: dois círculos rosa semi-transparentes.
- Boca: curva Q para alegre ou triste. Surpresa: círculo pequeno.
- Expressão deve combinar com texto. Se texto é tenso, triste ou surpreso, rosto também.

## Paleta de Cores

Manter paleta de 6–9 cores quentes, baixa saturação. Paleta InfoEngine:

- Fundo: `#fdf8f0` creme, `#e3f2fd` azul claro, `#0b081a` azul noite.
- Personagem: `#ff7a5a` coral quente, `#8fbf6b` verde grama, `#f5a623` dourado.
- Detalhes: `#f4766e` coral vivo, `#ffd700` ouro, `#fce4ec` rosa claro.

Cores do personagem devem ser FIXAS. Página 1 corpo `#a8764f`, página 8 também `#a8764f`.

## Consistência de Personagens

Primeira vez que desenhar o protagonista, salvar fragmento SVG. Nas páginas seguintes, copiar e alterar apenas:

- `transform`: posição, escala ou espelhamento.
- Expressão.
- Postura dos braços/pernas.

NÃO repetir `id="hero"` em múltiplas páginas. Usar `class="hero"`.

Se usar gradiente, ID por página: `sky-cover`, `sky-01`, `sky-02`. Todos os SVGs ficam no mesmo DOM, IDs duplicados causam conflito.

## Detalhes

Adicionar 2–3 detalhes por página: grama, folhas caindo, pétalas, estrelas, borboletas, ou sombra oval transparente sob o personagem. Sem sombra, personagem parece flutuar.

## Evitar

- Empilhamento geométrico puro: triângulo + quadrado = casa. Adicionar porta, janela, telhado.
- Texto dentro do SVG. Texto vai na área de conteúdo; ilustração só com onomatopeias.
- Traços finos demais. Usar blocos de cor; traços na mesma cor, mais escuro.
- Cores neon ou preto grande.
- `<script>`, `<foreignObject>`, imagens externas ou links.

## Exemplo de Página

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky-01" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e3f2fd"/>
      <stop offset="1" stop-color="#fdf8f0"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#sky-01)"/>
  <circle cx="680" cy="90" r="46" fill="#f5a623"/>
  <ellipse cx="400" cy="640" rx="520" ry="160" fill="#8fbf6b"/>
  <ellipse cx="320" cy="520" rx="90" ry="14" fill="#000" opacity="0.1"/>
  <g class="hero" transform="translate(320,420)">
    <!-- Personagem: copiar e reutilizar em todas as páginas -->
  </g>
</svg>
```
