# Video Creation

Criação de vídeos e animações para demonstrações de sistemas.

## Quando usar
- Quando solicitado "criar vídeo", "animação", "demo em vídeo"
- Converter imagens em vídeo
- Criar animações de fluxos de sistema
- Materiais de apresentação

## Ferramentas

### FFmpeg
Converter sequências de imagens em vídeo .mp4

```bash
# Instalar FFmpeg (Windows)
# Baixar em https://ffmpeg.org/download.html

# Converter imagens em vídeo (30 FPS)
ffmpeg -framerate 30 -i img_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Converter pasta de imagens
ffmpeg -framerate 30 -pattern_type glob -i "*.png" -c:v libx264 output.mp4

# Vídeo com áudio
ffmpeg -framerate 30 -i img_%04d.png -i audio.mp3 -shortest output.mp4

# GIF para MP4
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p output.mp4

# Concatenar vídeos
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Ajustar duração (slow motion)
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output_slow.mp4
```

### Manim (Python)
Animações matemáticas e explicativas

```python
# Instalação
pip install manim

# Configuração (manim.cfg)
[CLI]
quality = high_quality
frame_rate = 60

[output]
media_dir = "./media"

# Exemplo básico - Cena de animação
from manim import *

class IntroScene(Scene):
    def construct(self):
        # Título
        title = Text("Sistema de Delivery", font_size=48)
        self.play(Write(title))
        self.wait()

        # Transição
        self.play(FadeOut(title))

        # Fluxo do sistema
        arrow = Arrow(LEFT, RIGHT)
        client = Text("Cliente")
        sistema = Text("Sistema")

        self.play(
            Write(client),
            Write(arrow),
            Write(sistema)
        )
        self.wait()

# Renderizar
manim -pql scene.py IntroScene  # Preview rápido
manim -qh scene.py IntroScene    # Alta qualidade
```

## Fluxo de Trabalho

### 1. Planejar o Vídeo
- Defina história/roteiro
- Liste cenas necessárias
- Estime duração

### 2. Criar Assets
- Screenshots do sistema
- Gráficos/diagramas
- Sequências de imagens

### 3. Produzir Vídeo
- Use FFmpeg para compilar imagens
- Use Manim para animações
- Adicione áudio/trilha

### 4. Pós-Produção
- Ajustar timing
- Adicionar transições
- Compilar final

## Exemplos de Uso

### Demo Sistema Delivery
1. Capturar screenshots de cada tela
2. Criar sequência: login → catálogo → carrinho → checkout → sucesso
3. Compilar com FFmpeg
4. Adicionar narração ou música

### Animação de Fluxo
```python
from manim import *

class FluxoSistema(Scene):
    def construct(self):
        # Elementos
        usuario = Circle(color=BLUE, radius=0.5).shift(LEFT * 3)
        sistema = Square(color=GREEN, side_length=1).shift(RIGHT * 3)
        banco = Triangle(color=RED, height=1).shift(DOWN * 2)

        labels = VGroup(
            Text("Usuário").next_to(usuario, UP),
            Text("Sistema").next_to(sistema, UP),
            Text("Banco").next_to(banco, UP)
        )

        # Animação
        self.play(Create(usuario), Create(labels[0]))
        self.play(Create(sistema), Create(labels[1]))
        self.play(Create(banco), Create(labels[2]))

        # Setas de fluxo
        arrow1 = Arrow(usuario, sistema, buff=0.1)
        arrow2 = Arrow(sistema, banco, buff=0.1)

        self.play(GrowArrow(arrow1))
        self.play(GrowArrow(arrow2))
        self.wait()
```

## Comandos Úteis

```bash
# Renderizar Manim
manim -pql arquivo.py SceneName    # Preview
manim -qh arquivo.py SceneName     # Alta qualidade
manim -qk arquivo.py SceneName     # 4K

# FFmpeg - Informações
ffmpeg -i video.mp4                # Ver detalhes
ffmpeg -i video.mp4 -vn -ar 44100 -ac 2 audio.mp3  # Extrair áudio

# FFmpeg - Conversão
ffmpeg -i input.avi output.mp4
ffmpeg -i input.mov -c:v libx264 output.mp4
```

## Scripts Automáticos

### Gerador de Vídeo para Pizzaria
Script Python que compila imagens em vídeo automaticamente:

```bash
# Executar
python scripts/gerador_demo_pizzaria.py
```

### Capturador de Screenshots
Captura automaticamente páginas web para criar demos:

```bash
# Com Playwright
python scripts/capturador_screenshots.py

# Instalar dependências
pip install playwright
playwright install chromium
```

### Fluxo Automático Completo
```python
from capturador_screenshots import capturar_demo_pizzaria
from gerador_demo_pizzaria import gerar_video_demo
import asyncio

async def criar_demo_completo(url: str):
    # 1. Capturar screenshots
    await capturar_demo_pizzaria(url, "./screenshots")

    # 2. Gerar vídeo
    gerar_video_demo(
        titulo="Demo Sistema Pizzaria",
        imagens=[
            "screenshots/01_login.png",
            "screenshots/02_cardapio.png",
            "screenshots/03_pizza_detalhes.png",
            "screenshots/04_carrinho.png",
            "screenshots/05_checkout.png",
            "screenshots/06_sucesso.png",
        ],
        output="demo_pizzaria.mp4"
    )

# Executar
asyncio.run(criar_demo_completo("http://localhost:3000"))
```

## Output Esperado
```
## Video Creation

### Cena: Demo Login
- Duração: 5s
- Assets: login_screen.png, success_screen.png
- Transição: fade (0.5s)

### Cena: Fluxo Pedido
- Duração: 10s
- Animação: Manim com setas
- Áudio: background.mp3

### Arquivo Final
- output/demo_sistema.mp4
- Resolução: 1920x1080
- FPS: 30
```