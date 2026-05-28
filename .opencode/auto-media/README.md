# Auto Media - Automação de Mídia e Navegação Web

Sistema completo para automatizar geração de mídia, postagem em redes sociais e navegação web.

## 🚀 Funcionalidades

### 1. Geração de Imagens Realistas
- **OpenAI DALL-E 3**: Geração de imagens de alta qualidade
- **Stability AI (Stable Diffusion)**: Geração com controle detalhado
- **Tamanhos**: 1024x1024, 1024x1792, 1792x1024
- **Qualidades**: Standard e HD

### 2. Geração de Vídeos
- **Runway ML**: Geração de vídeos com Gen-2
- **Pika Labs**: Geração de vídeos criativos
- **Durações**: 3s, 4s, 5s, 10s

### 3. Postagem Automática em Redes Sociais
- **Twitter/X**: Postagem com mídia
- **Instagram**: Postagem de fotos e vídeos
- **Facebook**: Postagem na página

### 4. Navegação Automatizada
- **Acesso a sites**: Navegação completa com Puppeteer
- **Preenchimento de formulários**: Automatização de inputs
- **Cliques em elementos**: Interação com páginas
- **Captura de screenshots**: Registro visual
- **Extração de dados**: Coleta de informações

## 📦 Instalação

```bash
cd C:\xampp\htdocs\agente\.opencode\auto-media
npm install
```

## ⚙️ Configuração

1. Copie o arquivo `.env.example` para `.env`
2. Configure as chaves de API:

```env
# APIs de Geração
OPENAI_API_KEY=your_openai_api_key_here
STABILITY_API_KEY=your_stability_api_key_here
RUNWAY_API_KEY=your_runway_api_key_here
PIKA_API_KEY=your_pika_api_key_here

# Redes Sociais
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_SECRET=your_twitter_access_secret_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here

# Browser Settings
BROWSER_HEADLESS=true
BROWSER_SLOW_MO=0

# Output Settings
OUTPUT_DIR=./output
TEMP_DIR=./temp
```

## 🎯 Como Usar

### Interface Interativa
```bash
npm start
```

### Comandos Diretos
```bash
# Gerar imagem
npm run image

# Gerar vídeo
npm run video

# Postar em redes sociais
npm run post

# Navegar em sites
npm run browse
```

## 📁 Estrutura do Projeto

```
auto-media/
├── scripts/
│   ├── generate-image.js    # Geração de imagens
│   ├── generate-video.js    # Geração de vídeos
│   ├── post-social.js       # Postagem em redes sociais
│   └── browser-automation.js # Automação de navegador
├── output/                  # Arquivos gerados
├── temp/                    # Arquivos temporários
├── .env                     # Configurações de API
├── package.json
└── README.md
```

## 🎨 Exemplos de Uso

### Gerar Imagem de Produto
```bash
npm run image
# Prompt: "Foto profissional de um smartphone moderno sobre fundo branco, iluminação de estúdio"
```

### Gerar Vídeo Animado
```bash
npm run video
# Prompt: "Câmera lenta de gotas de água caindo em um lago, efeito de ondas"
```

### Postar Automaticamente
```bash
npm run post
# Selecione a plataforma, o arquivo e a legenda
```

### Navegar e Capturar
```bash
npm run browse
# Acesse qualquer site e capture screenshots
```

## 🔧 Tecnologias

- **Node.js**: Runtime environment
- **OpenAI API**: Geração de imagens DALL-E 3
- **Stability AI**: Stable Diffusion XL
- **Puppeteer**: Automação de navegador
- **Twitter API v2**: Postagem no Twitter
- **Instagram Private API**: Postagem no Instagram

## ⚠️ Notas de Segurança

- Nunca commitar o arquivo `.env` com chaves reais
- Use variáveis de ambiente para armazenar credenciais
- Limite o acesso às APIs de terceiros
- Monitore o uso da API para evitar custos excessivos

## 📝 Exemplos de Prompts

### Imagens Realistas
- "Foto profissional de um produto sobre fundo branco"
- "Paisagem de montanhas ao pôr do sol"
- "Retrato de pessoa sorrindo em estúdio"

### Vídeos
- "Câmera lenta de fumaça colorida"
- "Animação de partículas abstratas"
- "Transição de dia para noite"

## 🆘 Suporte

Para problemas ou dúvidas, verifique:
1. As chaves de API estão configuradas corretamente no `.env`
2. As APIs escolhidas estão disponíveis na sua região
3. O formato dos arquivos está correto

---

**Desenvolvido com ❤️ usando OpenCode**
