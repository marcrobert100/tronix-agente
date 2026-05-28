╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 DELIVERY BOT - GUIA DE INSTALAÇÃO                  ║
║     Bot WhatsApp para Delivery e Atendimento               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

📋 REQUISITOS DO SISTEMA
═════════════════════════════════════════════════════════════

  • Windows 10/11 (64 bits)
  • Node.js 18 ou superior (https://nodejs.org/)
  • Google Chrome ou Chromium instalado
  • Conexão com a internet
  • WhatsApp ativo no celular

═════════════════════════════════════════════════════════════


🚀 INSTALAÇÃO RÁPIDA (PASSO A PASSO)
═════════════════════════════════════════════════════════════

  PASSO 1: Instalar Node.js
  ─────────────────────────
  • Acesse: https://nodejs.org/
  • Baixe a versão LTS (recomendada)
  • Execute o instalador e siga as instruções
  • IMPORTANTE: Marque a opção "Add to PATH"


  PASSO 2: Configurar o Bot
  ─────────────────────────
  • Abra o arquivo .env com o Bloco de Notas
  • Preencha as configurações:

    GROQ_API_KEY=sua_chave_aqui
    PORT=3000
    EMPRESA_NOME=Sua Empresa
    EMPRESA_TELEFONE=5511999999999

  • Para obter a GROQ_API_KEY:
    - Acesse: https://console.groq.com
    - Crie uma conta gratuita
    - Vá em API Keys e crie uma nova chave


  PASSO 3: Instalar e Iniciar
  ───────────────────────────
  • Clique duas vezes em INSTALAR.bat
  • Aguarde a instalação das dependências
  • Após instalar, clique em INICIAR.bat
  • O servidor será iniciado na porta 3000


  PASSO 4: Acessar o Painel
  ─────────────────────────
  • Abra o navegador e acesse: http://localhost:3000
  • Login padrão:
    - Usuário: admin
    - Senha: admin123
  • Configure o cardápio no painel
  • Escaneie o QR Code do WhatsApp


═════════════════════════════════════════════════════════════


📁 ESTRUTURA DE ARQUIVOS
═════════════════════════════════════════════════════════════

  delivery-bot/
  ├── INSTALAR.bat          ← Instalador automático
  ├── INICIAR.bat           ← Inicia o servidor
  ├── .env                  ← Configurações (edite este!)
  ├── .env.example          ← Exemplo de configuração
  ├── config.example.json   ← Exemplo de configuração do bot
  ├── config.json           ← Configuração do bot (criado automaticamente)
  ├── package.json          ← Dependências do Node.js
  ├── server.js             ← Servidor principal
  ├── public/               ← Arquivos do painel
  │   ├── index.html        ← Página de login
  │   ├── painel.html       ← Painel de controle
  │   ├── css/              ← Estilos
  │   └── js/               ← Scripts do painel
  └── logs/                 ← Logs e dados
      ├── conversas-*.jsonl ← Histórico de conversas
      ├── vendas.json       ← Registro de vendas
      └── clientes.json     ← Base de clientes

═════════════════════════════════════════════════════════════


⚙️ CONFIGURAÇÕES DO BOT
═════════════════════════════════════════════════════════════

  Arquivo: .env
  ─────────────
  GROQ_API_KEY      = Chave da API Groq (IA)
  PORT              = Porta do servidor (padrão: 3000)
  EMPRESA_NOME      = Nome da empresa
  EMPRESA_TELEFONE  = Telefone com DDD

  Arquivo: config.json (via painel)
  ──────────────────────────────────
  • Cardápio completo
  • Taxa de entrega
  • Tempo de entrega
  • Formas de pagamento
  • Horário de funcionamento
  • Pesquisa de satisfação
  • Fluxos de conversa

═════════════════════════════════════════════════════════════


🎯 FUNCIONALIDADES
═════════════════════════════════════════════════════════════

  ✅ Atendimento automático via WhatsApp
  ✅ Cardápio interativo com categorias
  ✅ Pedido completo (endereço, pagamento, etc.)
  ✅ Pagamento via Pix com comprovante
  ✅ Painel de controle completo
  ✅ Impressão de pedidos
  ✅ Pesquisa de satisfação pós-entrega
  ✅ Áudio via TTS (texto para fala)
  ✅ Reconhecimento de voz (Speech-to-Text)
  ✅ Fluxos de conversa personalizáveis
  ✅ Cupons de desconto
  ✅ Horário de funcionamento

═════════════════════════════════════════════════════════════


🔧 SOLUÇÃO DE PROBLEMAS
═════════════════════════════════════════════════════════════

  Problema: "Node.js não encontrado"
  → Instale o Node.js: https://nodejs.org/
  → Certifique-se de marcar "Add to PATH"
  → Reinicie o terminal após instalar

  Problema: "Erro ao instalar dependências"
  → Verifique sua conexão com a internet
  → Execute: npm install --production
  → Se persistir, delete node_modules e tente novamente

  Problema: "WhatsApp não conecta"
  → Verifique se o Chrome/Chromium está instalado
  → Escaneie o QR Code novamente
  → Verifique se o WhatsApp está ativo no celular

  Problema: "Painel não carrega"
  → Verifique se o servidor está rodando
  → Acesse: http://localhost:3000
  → Verifique se a porta 3000 não está em uso

  Problema: "IA não responde"
  → Verifique se a GROQ_API_KEY está correta
  → Obtenha uma chave em: https://console.groq.com

═════════════════════════════════════════════════════════════


📞 SUPORTE
═════════════════════════════════════════════════════════════

  Desenvolvido por Marco Roberto
  WhatsApp: (XX) XXXXX-XXXX
  Email: suporte@exemplo.com

═════════════════════════════════════════════════════════════


📝 LICENÇA
═════════════════════════════════════════════════════════════

  Este software é de uso exclusivo do cliente adquirente.
  Proibida a reprodução ou distribuição sem autorização.

═════════════════════════════════════════════════════════════
