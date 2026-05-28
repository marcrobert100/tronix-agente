# Tronix Control - Centro de Comando dos Projetos Tronix

## 1. Descricao

Skill de centro de comando para projetos Tronix. Atua como painel de controle central para executar, monitorar, gerenciar automacoes, scripts, servicos e geracao de conteudo de Midia (imagens e videos).

## 2. Capacidades

### 2.1 Execucao de Scripts
- **Python**: `python <script>.py` com suporte a virtualenv
- **PHP**: `php <script>.php` via CLI ou servidor
- **Node.js**: `node <script>.js`
- **Bash/Shell**: Scripts de automacao geral

### 2.2 Geracao de Midia (Imagens e Videos)

#### Imagens
Suporte a multiplos providers de geracao de imagens via API:
- **Leonardo.ai**: 150 tokens/dia gratis (modelos: leanring-v1-5, dreamshaper-v7)
- **OpenAI DALL-E 3**: Modelo dall-e-3, qualidade standard/hd
- **Replicate (SDXL)**: Stable Diffusion via Replicate API

#### Videos
Integracao com APIs de geracao de video:
- **Runway ML**: Video generativo via Runway API
- **Luma AI**: Geracao de videos via Dream Machine API
- **Replicate (Video)**: Modelos de video como SVD, I2V-Gen-XL

Arquivo principal para imagens: `tronix_media_gen.py`
Arquivo para videos: `tronix_video_gen.py` (a criar)

### 2.3 Monitoramento
- **Logs em tempo real**: `tail -f` em arquivos de log
- **Status de servicos**: Apache, MySQL, Python services
- **Processos**: Lista e monitora processos ativos
- **Portas**: Verifica portas em uso (netstat)

### 2.4 Gerenciamento de Projetos
- Iniciar/parar servicos (Apache, MySQL, etc.)
- Deploy de atualizacoes
- Backup de bancos de dados
- Limpeza de cache

## 3. Comandos de Automacao de Midia

### 3.1 Geracao de Imagens
```
Comando: gerar imagem [prompt]
Acao: Executa tronix_media_gen.py com o prompt informado
Exemplo: gerar imagem uma cidade cyberpunk com neon azul e rosa
```

### 3.2 Geracao de Videos
```
Comando: gerar video [roteiro]
Acao: Executa integracao Runway ou Luma AI via API
Exemplo: gerar video um drone voando sobre uma metropole futurista
```

### 3.3 Utilidades de Midia
```
Comando: baixar midia [url]
Acao: Baixa conteudo para pasta local

Comando: batch gerar [lista_prompts]
Acao: Gera multiplas imagens/videos em sequencia
```

## 4. Estrutura de Diretorios

```
C:\xampp\htdocs\agente\
├── scripts/
│   ├── tronix_media_gen.py   # Gerador de imagens
│   ├── tronix_video_gen.py    # Gerador de videos (a criar)
│   ├── tronix_seguro.py       # Criptografia
│   ├── tronix_sync.py         # Sincronizacao
│   └── tronix_*.py            # Outros scripts
├── tronix_output/             # Midias geradas
├── logs/                      # Arquivos de log
├── .env                       # API keys
└── memoria_tronix.json        # Memoria persistente
```

## 5. Configuracao de APIs

Criar arquivo `.env` na raiz do projeto:

```env
# Leonardo.ai (RECOMENDADO - gratuito)
LEONARDO_API_KEY=seu_token_leonardo

# OpenAI DALL-E 3
OPENAI_API_KEY=seu_token_openai

# Replicate (SDXL + Video)
REPLICATE_API_TOKEN=seu_token_replicate

# Runway ML (Videos)
RUNWAY_API_KEY=seu_token_runway

# Luma AI (Videos)
LUMAAI_API_KEY=seu_token_lumaai
```

Para obter as chaves:
- Leonardo.ai: https://app.leonardo.ai/settings/api-key
- OpenAI: https://platform.openai.com/api-keys
- Replicate: https://replicate.com/account/api-tokens
- Runway: https://account.runwayml.com/
- Luma AI: https://lumalabs.ai/dream-machine

## 6. Exemplos de Uso

### Geracao de Imagem (Leonardo.ai)
```python
from tronix_media_gen import TronixMediaGen
gen = TronixMediaGen()
resultado = gen.gerar_leonardo(
    prompt="cidade cyberpunk, neon, detalhes",
    modelo="leanring-v1-5"
)
if resultado["status"] == "success":
    for url in resultado["urls"]:
        gen.baixar_leonardo(url)
```

### Geracao de Imagem (DALL-E 3)
```python
resultado = gen.gerar_dalle(
    prompt="rob o futuristic no p or do sol",
    tamanho="1024x1024"
)
if resultado["status"] == "success":
    gen.baixar_dalle(resultado['url'])
```

### Geracao de Video (Runway)
```python
from tronix_video_gen import TronixVideoGen
video = TronixVideoGen()
resultado = video.gerar_runway("drone voando sobre a cidade")
```

## 7. Comandos do Sistema

### Execucao
- `run python <script>` — Executa script Python
- `run php <script>` — Executa script PHP
- `run bash <script>` — Executa script Bash

### Monitoramento
- `logs [arquivo]` — Mostra logs
- `status` — Status de servicos
- `processes` — Lista processos
- `ports` — Verifica portas

### Gerenciamento
- `start <servico>` — Inicia servico
- `stop <servico>` — Para servico
- `restart <servico>` — Reinicia servico
- `backup` — Executa backup

## 8. Principios

1. **Sempre confirme antes de executar** — Execucao de scripts e irreversivel
2. **Mostre output em tempo real** — Logs streaming, nao apos termino
3. **Trate erros** — Capture stderr e mostre ao usuario
4. **Timeouts razoaveis** — Scripts longos devem ter timeout configuravel
5. **Verifique API keys** — Confirme que as chaves estao configuradas antes de usar geracao de midia

## 9. Integracao Tronix Core

O Tronix Control se integra com:
- `tronix_core.json` — Identidade e configuracao
- `memoria_tronix.json` — Historico de acoes
- `tronix_seguro.py` — Modulo de criptografia
- `tronix_media_gen.py` — Geracao de imagens
- `tronix_video_gen.py` — Geracao de videos (proximo)
