# Objetivo
Refatorar a aplicação `Delivery Bot WhatsApp` (diretório `casa`), atualmente concentrada em um único arquivo de 210KB (`server.js`), separando-a no padrão de arquitetura **MVC (Model-View-Controller) / Service Layers**, garantindo facilidade de expansão no futuro.

> [!IMPORTANT]
> **Condição Crítica:** Respeitando a diretriz imposta, o arquivo `server.js` original **NÃO SERÁ APAGADO NEM ALTERADO**. O refatoramento construirá uma infraestrutura paralela (`server_v2.js`) para que ambas as versões existam simultaneamente até que você aprove 100% o novo motor. Todo o banco de dados (que engloba arquivos json) e variáveis permanecerão idênticos.

## User Review Required
Por favor, revise atentamente as camadas abaixo. O projeto dividirá as regras de Express (App Web), Inteligência Artificial (Groq), Conexão WhatsApp Web e a **nova engine de Síntese de Voz (TTS)** em módulos específicos na pasta `src/`. Confirme se o isolamento proposto na estrutura atende sua visão de arquitetura.

## Proposed Changes

### 1. Estrutura de Pastas e Configurações Base
A nova espinha dorsal será criada dentro de um novo subdiretório `src/`.

#### [NEW] [package.json (novo script)](file:///c:/xampp/htdocs/agente/.opencode/casa/package.json)
Vamos adicionar `"start:v2": "node src/server_v2.js"` aos scripts para que você possa iniciar o modelo refatorado em paralelo, sem quebrar o `"start": "node server.js"`.

#### [NEW] [server_v2.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/server_v2.js)
Este será o novo entrypoint do servidor. Sua única função será inicializar módulos limpos de Socket, DB, WhatsApp e o App Express.

---

### 2. Camada de Configuração & Estado (Data)
Arquivos que gerenciarão a leitura e persistência em arquivos físicos e estados em memória (Maps).

#### [NEW] [state.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/config/state.js)
Exportará todas as variáveis globais (ex: `sessoes`, `clientesDB`, `cuponsDB`, `rateLimiter`, `pedidosAbertos`, `waConectado`).

#### [NEW] [dbConfig.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/config/dbConfig.js)
Moveremos as funções `loadConfig`, `saveConfig`, `loadClientes`, `saveClientes`, etc., reduzindo brutalmente o escopo do arquivo principal.

---

### 3. Camada de Serviços (Core Logic)
Os motores independentes. 

#### [NEW] [groqService.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/services/groqService.js)
Hospedará exclusivamente o `initGroq()`, envio de mensagens para IA e a validação de tokens `gsk_`.

#### [NEW] [voiceService.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/services/voiceService.js)
Levará a função assíncrona robusta `transcreverAudioGroq(bufferAudio)` que lida com o Whisper e a manipulação de Buffers/Stream de Node.
**[NOVA FUNCIONALIDADE]** Ganhará também o motor de Sintetização de Voz (TTS). Ele receberá a resposta em texto gerada pelo Chatbot e a converterá em um buffer de tempo real gerando um arquivo de áudio (`.ogg`).

#### [NEW] [whatsappService.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/services/whatsappService.js)
Instanciação do `Client` e `LocalAuth`, emissões de Socket.io ("qr", "ready").
**[NOVA FUNCIONALIDADE]** Em vez de usar apenas `.sendMessage(chatId, texto)`, ele usará a classe estrutural `MessageMedia.fromFilePath()` ou `fromBuffer()`, passando a tag `sendAudioAsVoice: true` para que o WhatsApp do cliente ache que o bot gravou um áudio no microfone na hora.

---

### 4. Application Flow (Controllers & Routes)
O coração da API para seu Painel Admin.

#### [NEW] [authMiddleware.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/middlewares/authMiddleware.js)
Funções `gerarToken()`, `authOk(req)` e `guard(req, res, next)`.

#### [NEW] [api.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/routes/api.js)
O mapa das rotas Express (`app.post('/api/login')`, `app.put('/api/cardapio/item')`, `app.get('/api/status')`).

#### [NEW] [menuController.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/controllers/menuController.js)
A lógica executada em solicitações de cardápio, removendo esses blocos de linha soltos na raiz.

#### [NEW] [settingsController.js](file:///c:/xampp/htdocs/agente/.opencode/casa/src/controllers/settingsController.js)
Lógicas para alteração da API Key, Relatórios de Vendas, e Cupons.

## Open Questions
- **Porta do Servidor de Testes:** Você quer que o novo `server_v2.js` pegue uma porta diferente de `3000` (ex: `3001` ou `8080`) no desenvolvimento para que você possa rodar os DOIS servidores ao mesmo tempo para fins de teste e comparação?
- **Motor de Voz (TTS):** Para que o robô crie "sua própria voz" (responda em áudio), nós precisamos de um motor. Se eu usar a tecnologia local/embarcada gratuita, existem opções como `Google-TTS` ou Bibliotecas Edge. Se quisermos que o robô tenha uma voz incrivelmente natural humana e que respira, teremos que bater na API de voz da **OpenAI (TTS-1)** ou **ElevenLabs**. Você tem chaves deles ou devo arquitetar para ele utilizar a voz nativa embarcada 100% gratuita?

## Verification Plan
### Automated Tests
1. Não há bateria de testes automatizados estrita (Jest/Mocha), logo a verificação será via runtime de loggings.
2. Iniciar o Painel usando a v2 (`npm run start:v2`), testar chamadas básicas do Painel (Login e carregar Cupons) via browser.
3. Mandar mensagem simuladora na própria classe Service para garantir que a IA (Groq) responde idêntico no novo arquivo.

### Manual Verification
O User tentará utilizar as chamadas usuais no Front-End já existente (`index.html`) mudando a porta de alvo temporária ou via Proxy reverso enquanto analisa logs. O arquivo anterior `server.js` mantém estado inoperante seguro como backup zero stress.
