# Delivery Bot WhatsApp - Evolucao

## 📦 Instalador Completo

Este instalador permite instalar o Delivery Bot WhatsApp em qualquer computador com Windows, incluindo máquinas recém-formatadas.

## 🚀 Como Usar

### Instalação Rápida

1. **Execute o instalador**: Clique duas vezes em `instalar_bot.bat`
2. **Aguarde**: O script irá:
   - Criar a estrutura de pastas
   - Verificar se Node.js está instalado
   - Copiar todos os arquivos do bot
   - Instalar as dependências automaticamente
   - Criar atalhos no desktop

3. **Inicie o bot**: Clique no atalho "Iniciar Bot" no desktop

### Acessando o Painel

1. Abra o navegador (Chrome, Firefox, Edge)
2. Digite: `http://localhost:3000`
3. Faça login com:
   - **Usuário**: `cliente`
   - **Senha**: `123456`

### Conectando o WhatsApp

1. No painel, vá em "WhatsApp" > "Conectar"
2. Escaneie o QR Code com seu WhatsApp
3. Aguarde a confirmação de conexão

## 📁 Estrutura de Pastas

```
Desktop/
└── evolucao/
    ├── instalar_bot.bat          # Script de instalação
    ├── README.md                 # Este arquivo
    └── bot/                      # Pasta do bot (gerada automaticamente)
        ├── server.js             # Servidor principal
        ├── package.json          # Dependências
        ├── config.json           # Configurações
        ├── logs/                 # Logs e dados
        ├── public/               # Arquivos web
        ├── src/                  # Código fonte
        └── Scripts/              # Scripts de inicialização
```

## ⚙️ Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11
- **Node.js**: Versão 16 ou superior (instalado automaticamente se não existir)
- **Memória RAM**: Mínimo 4GB (recomendado 8GB)
- **Espaço em disco**: Aproximadamente 500MB

## 🔧 Comandos Úteis

### Iniciar o Bot
```batch
%USERPROFILE%\Desktop\evolucao\bot\Scripts\INICIAR.bat
```

### Reiniciar o Bot
- Feche a janela do CMD
- Execute novamente `INICIAR.bat`

### Limpar Sessão do WhatsApp
1. No painel, vá em "WhatsApp" > "Limpar Sessão"
2. Ou delete a pasta `.wwebjs_auth` dentro da pasta do bot

## 📝 Configurações Iniciais

Após a primeira execução, configure o bot:

1. **Dados da Loja**: Nome, endereço, horário, telefone
2. **Taxa de Entrega**: Valor da taxa de entrega
3. **Cardápio**: Adicione categorias e produtos
4. **IA (Opcional)**: Configure a chave Groq para atendimento inteligente
5. **TTS (Opcional)**: Configure ElevenLabs para voz

## 🔄 Atualização

Para atualizar o bot:

1. Pare o bot (feche a janela do CMD)
2. Copie os novos arquivos para `%USERPROFILE%\Desktop\evolucao\bot\`
3. Abra o CMD na pasta do bot e execute:
   ```batch
   npm install
   ```
4. Inicie novamente com `INICIAR.bat`

## 🆘 Suporte

- **Documentação**: Consulte os arquivos de ajuda no painel
- **Logs**: Verifique a pasta `logs/` para diagnosticar problemas
- **Reinício**: Se o bot travar, feche e reabra a janela do CMD

## ⚠️ Notas Importantes

- **Não delete** a pasta `.wwebjs_auth` a menos que queira reconectar o WhatsApp
- **Backup**: Faça backup regular da pasta `logs/` para preservar dados
- **Internet**: O bot requer conexão constante com a internet
- **WhatsApp**: Use apenas uma sessão por vez para evitar bloqueios

## 📋 Checklist de Instalação

- [ ] Node.js instalado (verificado automaticamente)
- [ ] Pasta `evolucao` criada no desktop
- [ ] Arquivos do bot copiados
- [ ] Dependências instaladas
- [ ] Atalhos criados no desktop
- [ ] README gerado

---

**Bot desenvolvido por Marco Roberto**
*Delivery Bot WhatsApp v6.0*