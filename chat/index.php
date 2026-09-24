<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tronix AI - Gallery PC</title>
    <!-- Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <!-- Icones -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    
    <!-- Markdown e HighlightJS Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/monokai-sublime.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    
    <style>
        :root {
            --bg-color: #0b0c10;
            --panel-bg: rgba(31, 40, 51, 0.65);
            --cyan: #66fcf1;
            --cyan-dim: #45a29e;
            --gray: #c5c6c7;
            --gold: #FFD700;
            --red: #FF3B30;
            --text-color: #ffffff;
        }

        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at top right, rgba(102, 252, 241, 0.15), transparent 50%),
                              radial-gradient(circle at bottom left, rgba(255, 59, 48, 0.08), transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-app {
            width: 100%;
            max-width: 950px;
            height: 92vh;
            background: var(--panel-bg);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(102, 252, 241, 0.2);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
            overflow: hidden;
            position: relative;
        }

        /* HEADER */
        .header {
            padding: 20px 25px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.3);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 10;
        }

        .header h1 {
            margin: 0;
            font-size: 1.3rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: 0.5px;
        }

        .header h1 span {
            color: var(--cyan);
            text-transform: uppercase;
            text-shadow: 0 0 12px rgba(102, 252, 241, 0.5);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background-color: var(--cyan);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--cyan);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(102, 252, 241, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(102, 252, 241, 0); }
            100% { box-shadow: 0 0 0 0 rgba(102, 252, 241, 0); }
        }

        /* CHAT BOX */
        .chat-window {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            scroll-behavior: smooth;
        }

        /* SCROLLBAR */
        .chat-window::-webkit-scrollbar { width: 8px; }
        .chat-window::-webkit-scrollbar-track { background: transparent; }
        .chat-window::-webkit-scrollbar-thumb { background: rgba(102, 252, 241, 0.2); border-radius: 4px; }
        .chat-window::-webkit-scrollbar-thumb:hover { background: rgba(102, 252, 241, 0.4); }

        .message-wrapper {
            display: flex;
            gap: 12px;
            max-width: 90%;
            animation: fadeIn 0.4s ease-out forwards;
        }

        .wrapper-tronix {
            align-self: flex-start;
        }

        .wrapper-user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            font-size: 1.1rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }

        .avatar-tronix {
            background: linear-gradient(135deg, #112F2C, #0F635D);
            color: var(--cyan);
            border: 1px solid rgba(102, 252, 241, 0.4);
        }

        .avatar-user {
            background: linear-gradient(135deg, #332B00, #8A7300);
            color: var(--gold);
            border: 1px solid rgba(255, 215, 0, 0.4);
        }

        .message {
            padding: 16px 22px;
            border-radius: 16px;
            line-height: 1.6;
            font-size: 0.98rem;
            word-wrap: break-word;
        }

        .msg-user {
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.2);
            color: #fff;
            border-top-right-radius: 4px;
        }

        .msg-tronix {
            background: rgba(102, 252, 241, 0.06);
            border: 1px solid rgba(102, 252, 241, 0.15);
            color: var(--gray);
            border-top-left-radius: 4px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* TYPING INDICATOR */
        .typing {
            display: none;
            padding: 18px 22px;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            color: var(--cyan);
            font-style: italic;
            font-size: 0.9rem;
            border-top-left-radius: 4px;
            letter-spacing: 0.5px;
            border: 1px dashed rgba(102, 252, 241, 0.2);
        }

        .dots span {
            animation: typingDots 1.4s infinite;
            opacity: 0;
            font-size: 1.2rem;
            line-height: 0;
            padding: 0 1px;
        }
        .dots span:nth-child(2) { animation-delay: 0.2s; }
        .dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typingDots {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }

        /* INPUT AREA */
        .input-area {
            display: flex;
            padding: 20px 25px;
            background: rgba(0,0,0,0.4);
            border-top: 1px solid rgba(255,255,255,0.05);
            gap: 15px;
            align-items: center;
        }

        .input-area textarea {
            flex: 1;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 18px;
            padding: 16px 20px;
            color: white;
            font-size: 1rem;
            font-family: inherit;
            outline: none;
            transition: all 0.3s;
            resize: none;
            height: 24px;
            line-height: 1.4;
        }

        .input-area textarea:focus {
            background: rgba(0,0,0,0.6);
            border-color: var(--cyan);
            box-shadow: 0 0 12px rgba(102, 252, 241, 0.15);
        }

        .input-area button {
            background: linear-gradient(135deg, #45a29e, var(--cyan));
            color: #000;
            border: none;
            border-radius: 50%;
            width: 55px;
            height: 55px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s;
            flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(102, 252, 241, 0.3);
        }

        .input-area button:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 20px rgba(102, 252, 241, 0.6);
        }

        /* MARKDOWN STYLES */
        .msg-tronix p { margin-top: 0; margin-bottom: 12px; }
        .msg-tronix p:last-child { margin-bottom: 0; }
        
        .msg-tronix a { color: var(--cyan); text-decoration: underline; text-underline-offset: 4px; }
        .msg-tronix strong { color: #fff; font-weight: 600; }
        .msg-tronix h1, .msg-tronix h2, .msg-tronix h3 { margin-top: 0; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }

        .msg-tronix blockquote {
            border-left: 3px solid var(--gold);
            margin: 10px 0;
            padding: 10px 15px;
            background: rgba(255, 215, 0, 0.05);
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }

        /* CODE BLOCKS */
        .msg-tronix code {
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.5);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--cyan);
        }

        .msg-tronix pre {
            background: #1e1e1e !important;
            padding: 15px;
            border-radius: 10px;
            overflow-x: auto;
            border: 1px solid rgba(255,255,255,0.1);
            margin: 15px 0;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        
        .msg-tronix pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }

    </style>
</head>
<body>

    <div class="chat-app">
        <div class="header">
            <h1><div class="status-dot"></div> <span>TRONIX</span> Inteligência Central</h1>
            <div style="color: var(--cyan-dim); font-size: 0.85rem; font-weight: 600;"><i class="fas fa-microchip"></i> PCsoluções - Viçosa</div>
        </div>

        <div class="chat-window" id="chat">
            
            <div class="message-wrapper wrapper-tronix">
                <div class="avatar avatar-tronix"><i class="fas fa-robot"></i></div>
                <div class="message msg-tronix markdown-body">
                    ### Olá, Marcos! ⚡<br>
                    Meu sistema foi completamente aprimorado. 
                    <br><br>
                    As novas capacidades (Skills) foram ativadas e integradas diretamente no meu painel de processamento. Experimente digitar comandos como:
                    - **"Qual o meu saldo do Kie?"**
                    - **"Verifique a memória e o status"**
                    - **"Informações sobre o Major / Abatedouro"**
                </div>
            </div>

            <!-- Typing Template -->
            <div class="message-wrapper wrapper-tronix" id="typingBlock" style="display: none;">
                <div class="avatar avatar-tronix"><i class="fas fa-robot"></i></div>
                <div class="typing" id="typingIndicator">Processando na rede neural<span class="dots"><span>.</span><span>.</span><span>.</span></span></div>
            </div>

        </div>

        <div class="input-area">
            <textarea id="userInput" placeholder="Envie sua mensagem ou instrução..."></textarea>
            <button id="sendBtn"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>

    <script>
        // Configurações do MarkedJS (Markdown)
        marked.setOptions({
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-',
            breaks: true,
            gfm: true
        });

        const sendBtn = document.getElementById('sendBtn');
        const userInput = document.getElementById('userInput');
        const chatWindow = document.getElementById('chat');
        const typingBlock = document.getElementById('typingBlock');

        // Allow pressing Enter to send (Shift+Enter for newline)
        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });

        // Auto-resize textarea
        userInput.addEventListener('input', function() {
            this.style.height = '24px';
            this.style.height = (this.scrollHeight - 32) + 'px';
            if (this.value === '') this.style.height = '24px';
        });

        sendBtn.addEventListener('click', send);

        function createDiv(isUser, text, isHTML = false) {
            const wrapper = document.createElement('div');
            wrapper.className = `message-wrapper ${isUser ? 'wrapper-user' : 'wrapper-tronix'}`;
            
            const avatar = document.createElement('div');
            avatar.className = `avatar ${isUser ? 'avatar-user' : 'avatar-tronix'}`;
            avatar.innerHTML = isUser ? '<i class="fas fa-user-astronaut"></i>' : '<i class="fas fa-robot"></i>';

            const div = document.createElement('div');
            div.className = `message ${isUser ? 'msg-user' : 'msg-tronix'}`;
            
            if (isHTML) { 
                div.innerHTML = text; 
            } else { 
                div.textContent = text; 
            }
            
            wrapper.appendChild(avatar);
            wrapper.appendChild(div);
            
            chatWindow.insertBefore(wrapper, typingBlock);
            scrollToBottom();
        }

        function scrollToBottom() {
            chatWindow.scrollTop = chatWindow.scrollHeight + 100;
        }

        async function send() {
            const text = userInput.value.trim();
            if (!text) return;

            // Render User
            createDiv(true, text, false);
            
            // Reposition and format Textarea
            userInput.value = '';
            userInput.style.height = '24px';
            userInput.focus();

            // Show Typing
            typingBlock.style.display = 'flex';
            scrollToBottom();

            try {
                const req = await fetch('api.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const res = await req.json();

                // Hide typing
                typingBlock.style.display = 'none';

                if (res.status === 'success') {
                    // Transforma o Markdown retornado pelo PHP/Llama em HTML!
                    const htmlContent = marked.parse(res.reply);
                    createDiv(false, htmlContent, true);
                } else {
                    createDiv(false, `<span style="color: var(--red);"><i class="fas fa-exclamation-triangle"></i> Erro:</span> ${res.reply}`, true);
                }
            } catch (err) {
                typingBlock.style.display = 'none';
                createDiv(false, `<span style="color: var(--red);"><i class="fas fa-exclamation-triangle"></i> Falha Bridge:</span> ${err.message}`, true);
            }
        }
    </script>
</body>
</html>
