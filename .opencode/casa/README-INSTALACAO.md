# 🚀 Guia de Instalação - Delivery Bot v6

## Requisitos do Sistema

| Recurso | Mínimo | Recomendado |
|---------|--------|------------|
| Windows | Windows 10 | Windows 11 |
| RAM | 4 GB | 8 GB |
| Disco | 10 GB | 20 GB |
| Internet | 10 Mbps | 50 Mbps |

---

## Instalação Rápida

### 1. Instale o Node.js
Baixe em: https://nodejs.org (versão LTS)

### 2. Clone ou baixe o projeto
Copie a pasta `casa` para seu computador

### 3. Execute o instalador
```powershell
cd C:\casa
instalar.bat
```

### 4. Configure
Edite `config.json` com suas informações:
- `groqApiKey`: Sua chave API (começa com gsk_)
- `empresaNome`: Nome da sua delivery
- `empresaEndereco`: Endereço
- `empresaTelefone`: WhatsApp
- `pixChave`: Chave Pix para pagamentos

### 5. Inicie
```powershell
npm start
```

### 6. Conecte o WhatsApp
- Escaneie o QR Code que aparecer
- Pronto!

---

## Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `npm start` | Iniciar o bot |
| `npm run dev` | Iniciar com reload automático |
| Ctrl+C | Parar o bot |

---

## Problemas Comuns

### "Node.js não encontrado"
- Reinicie o computador após instalar o Node.js
- Ou adicione ao PATH do Windows

### "Groq API inválida"
- Obtain uma chave gratuita em: https://console.groq.com
- A chave deve começar com `gsk_`

### WhatsApp desconecta
- Mantenha o navegador aberto
- Não faça logout do WhatsApp Web

---

## Estrutura de Arquivos

```
casa/
├── server.js          # Código principal
├── config.json        # Configurações
├── package.json      # Dependências
├── instalar.bat      # Instalador automático
├── .env              # Variáveis de ambiente
├── .wwebjs_auth/     # Cache do WhatsApp
├── logs/             # Histórico de vendas
├── public/           # Arquivos do painel
└── node_modules/     # Dependências
```

---

## Licença
Desenvolvido por Marco Roberto
