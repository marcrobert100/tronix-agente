# TRONIX AI — Control HUD (estrutura JARVIS-Mark)

Assistente de voz em tempo real com controle total do computador, baseado na estrutura
**MARK XLVIII** (Gemini Live API) do vídeo "I Gave JARVIS Full Control of My Computer".
Portado e nacionalizado para o ecossistema TRONIX do Marcos Roberto (PCsoluções, Viçosa-AL).

- Voz bidirecional em tempo real (Gemini Live API, pt-BR)
- HUD visual PyQt6 com waveform, log, botão de interrupção, câmera e painel de conteúdo
- **19 módulos de ações**: abertura de apps, browser, arquivos, código, tela/câmera, sistema,
  reminders, clima, voos, YouTube, WhatsApp/Telegram, jogos, desktop, pesquisa web
- Memória persistente `memory/long_term.json`
- Painel de controle remoto (celular) via dashboard FastAPI na porta 8000
- **Integração TRONIX**: ferramentas `tronix_*` (status, agentes, scripts, executar, memória)
  consumindo o API Gateway localhost:8081 e o banco `tronix.db`

## Estrutura

```
tronix_jarvis/
├── main.py              # Loop core — sessão Gemini Live, dispatch de ferramentas
├── ui.py                # HUD PyQt6 — waveform, log, interrupt, câmera
├── setup.py             # Instala dependências + Playwright + chave do .env
├── actions/             # 19 módulos de ferramentas
├── core/                # prompt.txt (persona TRONIX), tts/stt/llm_client, installer
├── memory/              # memória persistente por sessão
├── dashboard/           # painel remoto (celular) + servidor
└── config/              # api_keys.json (chave Gemini, nome, voz, modelo)
```

## Instalação

```powershell
cd C:\xampp\htdocs\agente\tronix_jarvis
python setup.py        # pip install -r requirements.txt + playwright install
python main.py         # inicia o HUD
```

- Sem chave no `.env`: o HUD abre um wizard no primeiro run pedindo a Gemini API Key.
- Chave grátis: https://aistudio.google.com/apikey

## Configuração (`config/api_keys.json`)

| Campo | Significado | Padrão |
|-------|-------------|--------|
| `gemini_api_key` | Chave Gemini Live | do `.env` |
| `assistant_name` | Nome do assistente | TRONIX |
| `user_name` | Nome do usuário | Marcos |
| `voice` | Voz (Kore, Charon, Puck...) | Kore |
| `language` | Idioma | pt-BR |
| `live_model` | Modelo Live | gemini-3.1-flash-live-preview |
| `os_system` | windows / mac / linux | auto |

## Dependências

`sounddevice` `google-genai` `PyQt6` `playwright` `pyautogui` `pycaw` `pywinauto`
`mss` `opencv-python` `psutil` `pillow` `duckduckgo-search` `youtube-transcript-api`
`fastapi` `uvicorn` `cryptography` `qrcode` etc. — listadas em `requirements.txt`.

## Notas

- Projeto original: MARK XLVIII by FatihMakes (Gemini Live API, open source).
- `config/api_keys.json` contém segredo — não versionar.
- Para fallback de voz offline usar LM Studio: configurar `llm_provider` em `core/llm_client.py`.