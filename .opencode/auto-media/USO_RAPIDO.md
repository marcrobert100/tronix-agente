# Guia de Uso Rápido - Auto Media

## 🚀 Início Rápido

### 1. Configurar o Ambiente
```bash
cd C:\xampp\htdocs\agente\.opencode\auto-media
copy .env.example .env
# Edite .env e adicione suas chaves de API
```

### 2. Iniciar o Sistema
```bash
npm start
```

## 🎯 Comandos Principais

### Gerar Imagem
```bash
npm run image
```
**Exemplo de prompt:**
- "Foto profissional de um smartphone moderno sobre fundo branco"
- "Paisagem de montanhas ao pôr do sol"
- "Retrato de pessoa sorrindo em estúdio"

### Gerar Vídeo
```bash
npm run video
```
**Exemplo de prompt:**
- "Câmera lenta de gotas de água caindo em um lago"
- "Animação de partículas abstratas coloridas"

### Postar em Redes Sociais
```bash
npm run post
```
**Suporta:**
- Twitter/X
- Instagram
- Facebook

### Navegar em Sites Automaticamente
```bash
npm run browse
```
**Funcionalidades:**
- Acessar qualquer site
- Capturar screenshots
- Preencher formulários
- Extrair dados

## 📋 Exemplos de Tarefas

### Tarefa 1: Criar e Postar Conteúdo
1. Gerar imagem: `npm run image`
2. Postar no Twitter: `npm run post`
3. Selecionar a imagem gerada e adicionar legenda

### Tarefa 2: Pesquisar e Capturar Dados
1. Navegar para site: `npm run browse`
2. Acessar URL desejada
3. Extrair dados ou capturar screenshot

### Tarefa 3: Automação Completa
Execute o modo "Tarefa Completa" no menu principal para criar fluxos personalizados.

## ⚙️ Configurações Importantes

### APIs Disponíveis
- **OpenAI DALL-E 3**: Geração de imagens (requer API key)
- **Stability AI**: Stable Diffusion (requer API key)
- **Runway ML**: Geração de vídeos (requer API key)
- **Pika Labs**: Geração de vídeos (requer API key)

### Redes Sociais
- **Twitter/X**: Requer API keys do Twitter Developer
- **Instagram**: Requer login e senha
- **Facebook**: Requer Access Token

### Navegador
- `BROWSER_HEADLESS=true` - Executar em segundo plano
- `BROWSER_SLOW_MO=0` - Velocidade da automação (ms)

## 📁 Arquivos Gerados

- **output/** - Imagens, vídeos e dados gerados
- **temp/** - Arquivos temporários

## ⚠️ Limitações e Custos

### Limites de API
- **OpenAI**: Limite de requisições por minuto/hora
- **Stability AI**: Créditos limitados por mês
- **Runway/Pika**: Planos gratuitos limitados

### Custos
- Cada geração de imagem/vídeo tem custo associado
- Monitore o uso para evitar cobranças inesperadas

## 🔧 Solução de Problemas

### Erro: "API key não configurada"
- Verifique o arquivo `.env`
- Adicione as chaves de API necessárias

### Erro: "Dependência não instalada"
- Execute: `npm install`

### Erro: "Não foi possível acessar o site"
- Verifique a URL
- Verifique a conexão com a internet
- Tente modo headless: `BROWSER_HEADLESS=false`

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique o arquivo `.env`
2. Execute `node test.js` para verificar a instalação
3. Consulte a documentação de cada API

---

**Sistema pronto para uso! 🚀**
