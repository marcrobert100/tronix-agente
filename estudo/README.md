# Sistema de Estudo para College Entrance Exam

Um sistema completo de estudo com vocabulário, opções de trading e quiz interativo.

## 🚀 Como Usar

### Opção 1: Através do XAMPP (Recomendado)
1. Inicie o XAMPP Control Panel
2. Inicie o Apache
3. Acesse: `http://localhost/agente/estudo/`

### Opção 2: Servidor Python
No terminal, navegue até a pasta `estudo` e execute:
```bash
cd C:\xampp\htdocs\agente\estudo
python -m http.server 8000
```
Acesse: `http://localhost:8000`

### Opção 3: Diretamente no Navegador
Abra o arquivo `index.html` diretamente no seu navegador.

## 📚 Funcionalidades

### 1. Flashcards de Vocabulário
- 20 palavras essenciais para exames de entrada
- Clique no cartão para ver a tradução
- Navegação anterior/próximo

### 2. Opções de Trading
- Explicação de Call e Put Options
- Simulador interativo:
  - Insira o preço da ação
  - Defina o strike price
  - Adicione o premium
  - Veja o resultado (lucro/perda)

### 3. Quiz Interativo
- Perguntas sobre vocabulário e trading
- Feedback imediato (correto/incorreto)
- Pontuação final com porcentagem

## 🎨 Recursos Adicionais
- **Tema Escuro/Claro**: Clique no botão 🌙/☀️ no cabeçalho
- **Cabeçalho Fixo**: Sempre visível ao rolar a página
- **Design Responsivo**: Funciona em desktop e mobile

## 📁 Estrutura de Arquivos
```
estudo/
├── index.html          # Página principal
├── index.php           # Redirecionamento para XAMPP
├── README.md           # Este arquivo
├── css/
│   └── style.css       # Estilos
└── js/
    ├── data.js         # Dados de vocabulário e quiz
    └── main.js         # Lógica JavaScript
```

## 🎯 Dicas de Estudo
1. **Vocabulário**: Revise os flashcards diariamente
2. **Trading**: Use o simulador para entender cenários reais
3. **Quiz**: Faça até acertar 100% das perguntas

## 📞 Suporte
Para problemas ou sugestões, verifique a documentação do Open WebUI.