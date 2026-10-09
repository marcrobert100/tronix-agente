# GPU grátis de 32 GB no Kaggle -> modelo de IA no VS Code

**Status: funcionando e verificado.** Túnel no ar, `qwen3-coder:30b` (18 GB) rodando em 2x Tesla T4.

Base do vídeo `youtube.com/watch?v=UH2XvzGkpD0` (Tech2AI), automatizado — e com três correções que o vídeo erra.

## O que foi conferido de verdade

| Item | Resultado |
|---|---|
| GPU via API do Kaggle | **2x Tesla T4, 15360 MiB cada = 30 GB** (o vídeo fala em 32 GB via UI) |
| Cota da conta | 30 h/semana, renova 2026-10-03 |
| Modelo | `qwen3-coder:30b` — 18 GB, carregou e respondeu |
| API local | `http://localhost:11434/api/tags` → 200 |
| Túnel | `https://mobiles-leo-underground-self.trycloudflare.com` |
| OpenAI-compatible | `/v1/models` e `/v1/chat/completions` → 200, resposta real |

## Três erros do vídeo (corrigidos aqui)

1. **Ele manda instalar "zstandard"** (módulo Python). O `install.sh` do Ollama exige o **binário `zstd`**. Sem ele: `ERROR: This version requires zstd for extraction` e o Ollama não instala. O certo é `apt-get install -y zstd`.
2. **`ollama run` numa célula Python** dá erro de sintaxe e, pior, `ollama` não fica disponível. O jeito certo é `ollama pull` + `subprocess.Popen` com caminho absoluto.
3. **A célula do túnel não pode terminar.** Se ela acaba, o Kaggle derruba a VM e a URL morre. Aqui ela entra num laço de guarda e ainda reinicia o `cloudflared` se ele morrer.

## Como usar agora

O túnel já está no ar e a URL está em `tunnel_url.txt`.

### VS Code + Cline

| Campo | Valor |
|---|---|
| API Provider | `OpenAI Compatible` |
| Base URL | `https://mobiles-leo-underground-self.trycloudflare.com/v1` |
| API Key | `ollama` (fictício — o Ollama não checa) |
| Model | `qwen3-coder:30b` |

### Sem GUI, no terminal

```powershell
cd C:\xampp\htdocs\agente\kaggle_ollama
python cliente.py "crie um hello.py"        # teste rápido
.\usar_opencode.bat                         # /models -> kaggle/qwen3-coder:30b
.\usar_qwen.bat                             # Qwen Code
.\usar_aider.bat C:\xampp\htdocs\agente\infoengine
```

### Quando a URL mudar

```powershell
python subir_kernel.py    # recria o kernel, roda tudo e captura a URL nova
```

## Encerrar (importante)

```powershell
python subir_kernel.py --parar
```

Ou o atalho `parar_kernel.bat`. **Derrubar o kernel é o que devolve a cota** — o que segura a sessão é o laço de guarda, e ele que consome as 30 h.

## Como o pacote funciona

| Arquivo | Papel |
|---|---|
| `celula_unica.py` | Script que roda dentro do Kaggle: GPU → zstd → Ollama → modelo → cloudflared → guarda |
| `build_notebook.py` | Gera o `.ipynb` a partir do `.py` (fonte única, com `id` de célula — sem isso o Kaggle não executa) |
| `kaggle_ollama.ipynb` | Notebook pronto para arrastar no Kaggle (caminho manual) |
| `subir_kernel.py` | Sobe o kernel GPU pela API, captura a URL, ou derruba com `--parar` |
| `live_log.py` | Lê o log **ao vivo** (`kernels_logs_stream`) e salva a URL — o `kaggle kernels logs` normal só responde depois que o kernel termina |
| `cliente.py` | Chat/teste do Windows contra o túnel |
| `conectar.bat` | Testa a URL e abre o VS Code |
| `usar_opencode.bat` / `usar_qwen.bat` / `usar_aider.bat` | CLI apontado para o túnel |
| `opencode.json` | Provider `kaggle` (lê `KAGGLE_TUNNEL_URL` do ambiente) |
| `kaggle_auth.bat` | Autorização OAuth do CLI ( só essa parte é manual) |
| `parar_kernel.bat` | Derruba o kernel e devolve a cota |
| `tunnel_url.txt` | URL atual (gerado; não versionar) |

## Lições do caminho (se for refazer)

- **Kernel via API só executa com `id` em toda célula** e `nbformat_minor: 5`. Sem isso ele "roda" sem imprimir nada.
- **Nunca fazer `line.rstrip()` nas linhas de `source`** — tira o `\n` e a célula inteira vira uma linha só. Como o script começa com `#`, virava comentário e passava silenciosamente. Custo: 6 pushes.
- **`kaggle kernels logs` / `output` não funcionam com kernel rodando.** Para log ao vivo use `api.kernels_logs_stream(ref)`.
- Limite do Kaggle: **2 sessões de GPU simultâneas**.
- `kaggle kernels push` deriva o slug do **título**. Se o `id` do metadata não bater com o slug do título: `409 Conflict`.

## Segurança

A URL `trycloudflare.com` é **pública e sem autenticação** — qualquer um com o link usa sua GPU e o modelo. Não compartilhe fora do necessário e encerre a sessão ao terminar. Para uso sério, isso não substitui autenticação.

## Opencode (global)

O provider `kaggle` esta no config **global** (`~/.config/opencode/opencode.json`),
entao `kaggle/qwen3-coder:30b` aparece em **qualquer pasta** do PC:

    opencode models
    opencode run --model kaggle/qwen3-coder:30b "sua tarefa"

Nao precisa copiar `opencode.json` para o projeto, nem exportar variavel de ambiente.

A URL do tunel muda a cada subida. Quem atualiza sozinho e o `subir_kernel.py`:
ao capturar uma URL nova ele reescreve os 3 `opencode.json` (global, deste pacote,
copia do Desktop) e a variavel de usuario `KAGGLE_TUNNEL_URL`.

Se ficar com URL velha e der erro, forcar a sincronizacao:

    python -c "import subir_kernel as s; s.propagar_url(open('tunnel_url.txt').read().strip())"

Depois **reinicie o opencode** (o config so e lido no start).
