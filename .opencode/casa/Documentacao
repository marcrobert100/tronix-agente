# 🛵 Delivery Bot WhatsApp

**Desenvolvido por Marco Roberto**  
Bot de WhatsApp completo para delivery e atendimento, com IA, painel admin e fluxos configuráveis.

---

## ✨ O que há de novo (v2.0)

- ✅ **Histórico de conversa por cliente** — a IA lembra o contexto da conversa
- ✅ **Cardápio no contexto da IA** — ela nunca inventa preços
- ✅ **Detecção automática de pedidos** — lista no painel em tempo real
- ✅ **Rate limiting** — evita spam e custo excessivo de IA
- ✅ **Logs persistidos** — todas as conversas salvas em `/logs`
- ✅ **Envio manual de mensagens** pelo painel
- ✅ **Variáveis dinâmicas** nos fluxos (`{empresaNome}`, `{cardapio}`, etc.)
- ✅ **Reconexão automática** do WhatsApp
- ✅ **Chave Groq em `.env`** — mais seguro que config.json
- ✅ **Resposta a mídias** — não fica em silêncio quando recebe foto/áudio
- ✅ **Painel admin dark** — profissional e completo

---

## 🚀 Como usar

### 1. Instale o Node.js
Baixe em [nodejs.org](https://nodejs.org/) → versão LTS

### 2. Inicie
Dê dois cliques em **`INICIAR.bat`**

### 3. Acesse o painel
Abra `http://localhost:3000` no navegador

### 4. Conecte o WhatsApp
Escaneie o QR Code que aparece na aba **WhatsApp**

### 5. Configure sua empresa
Aba **Empresa** → preencha nome, endereço, horário, etc.

### 6. Configure o cardápio
Aba **Cardápio** → edite os itens no formato JSON

### 7. Ative a IA (opcional)
Aba **IA / Groq** → coloque sua chave gratuita de [console.groq.com](https://console.groq.com)

---

## 📁 Estrutura

```
delivery-bot/
├── server.js          # Backend principal
├── config.json        # Configurações (editável pelo painel)
├── .env               # Chave API (criado automaticamente)
├── .env.example       # Modelo do .env
├── package.json
├── INICIAR.bat        # Atalho para Windows
├── logs/              # Logs diários de conversa
└── public/
    ├── index.html     # Painel admin
    ├── css/style.css
    └── js/app.js
```

---

## 🔀 Variáveis nos Fluxos

Nos textos dos fluxos, use estas variáveis que são substituídas automaticamente:

| Variável | Valor |
|---|---|
| `{empresaNome}` | Nome da empresa |
| `{endereco}` | Endereço |
| `{horario}` | Horário de funcionamento |
| `{telefone}` | Telefone |
| `{taxaEntrega}` | Taxa de entrega |
| `{tempoEntrega}` | Tempo estimado |
| `{pedidoMinimo}` | Valor mínimo do pedido |
| `{pagamentos}` | Formas de pagamento |
| `{pixChave}` | Chave Pix |
| `{cardapio}` | Cardápio formatado completo |

---

## 🆘 Problemas comuns

| Problema | Solução |
|---|---|
| Node.js não encontrado | Instale em nodejs.org e reinicie o PC |
| QR Code não aparece | Aguarde 1-2 min. Se não aparecer, clique "Limpar sessão" |
| Bot não responde | Verifique se o WhatsApp está conectado no painel |
| Porta 3000 em uso | Edite `PORT=3001` no arquivo `.env` |

---

**Marco Roberto** · Delivery Bot WhatsApp v2.0
