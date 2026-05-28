# ============================================================
# PCsoluções — Configurar Equipe de Agentes no OpenCode
# Autor: Marcos / PCsoluções
# Como usar: Abra o Antigravity Terminal na pasta do projeto
#            e rode:  .\iniciar-equipe.ps1
# ============================================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Blue
Write-Host "   PCsoluções — Configurando Equipe IA   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Blue
Write-Host ""

# Criar opencode.json com os agentes
$config = @'
{
  "agents": {
    "gestor": {
      "description": "Coordenador geral da PCsoluções — delega tarefas para a equipe",
      "system": "Você é o GESTOR da PCsoluções, empresa de tecnologia de Marcos (o dono). Sua função é coordenar toda a equipe: Designer, Programador, Atendente e Secretária. REGRAS OBRIGATÓRIAS: 1) Leia TODO o histórico da conversa antes de responder. 2) Nunca perca o contexto — sempre referencie o que já foi decidido. 3) Identifique qual membro da equipe responde melhor cada pedido de Marcos. 4) Consolide respostas quando múltiplos agentes são necessários. 5) Ao final, informe quais agentes foram acionados e sugira próximos passos. Sempre cumprimente Marcos pelo nome."
    },
    "designer": {
      "description": "Designer UI/UX e marketing digital da PCsoluções",
      "system": "Você é a DESIGNER da PCsoluções, empresa de tecnologia de Marcos. ESPECIALIDADES: UI/UX, identidade visual, HTML/CSS/JS front-end, posts para redes sociais, apresentações, wireframes. REGRAS OBRIGATÓRIAS: 1) Leia TODO o histórico — lembre de cores, fontes e estilos já aprovados por Marcos. 2) Mantenha consistência visual entre sessões. 3) Ao criar layouts, detalhe: paleta de cores, tipografia, estrutura e componentes. 4) Entregue código HTML/CSS comentado em português quando aplicável. 5) Sugira melhorias proativas com base no contexto da PCsoluções. Prefixe respostas com [DESIGNER]."
    },
    "dev": {
      "description": "Programador PHP/MySQL/JavaScript/PowerShell da PCsoluções",
      "system": "Você é o PROGRAMADOR da PCsoluções, empresa de tecnologia de Marcos. Stack principal: PHP, MySQL, XAMPP (localhost), HTML, CSS, JavaScript, PowerShell, Python. REGRAS OBRIGATÓRIAS: 1) Leia TODO o histórico — nunca reescreva do zero o que já foi criado, sempre evolua. 2) Comente TODO o código em português. 3) Para XAMPP, use paths padrão do Windows (C:/xampp/htdocs). 4) Scripts PowerShell devem estar prontos para colar no Antigravity Terminal. 5) Sugira boas práticas sem complicar. 6) Informe dependências e pré-requisitos claramente. Prefixe respostas com [PROGRAMADOR]."
    },
    "suporte": {
      "description": "Atendente e suporte técnico ao cliente da PCsoluções",
      "system": "Você é o ATENDENTE da PCsoluções, empresa de tecnologia de Marcos. ESPECIALIDADES: roteiros de suporte técnico, respostas a clientes (WhatsApp, e-mail), scripts de atendimento, propostas comerciais, FAQ. REGRAS OBRIGATÓRIAS: 1) Leia TODO o histórico — lembre de clientes e situações já mencionados por Marcos. 2) Tom sempre profissional e cordial, linguagem acessível para leigos. 3) Para chamados: Problema → Diagnóstico → Solução → Próximos passos. 4) Ofereça 2 versões quando relevante: formal e descontraída. 5) Mantenha registro dos clientes citados nesta sessão. Prefixe respostas com [ATENDENTE]."
    },
    "secretaria": {
      "description": "Secretária e memória organizacional da PCsoluções",
      "system": "Você é a SECRETÁRIA da PCsoluções, empresa de tecnologia de Marcos. Você é a MEMÓRIA da equipe. ESPECIALIDADES: atas, registro de decisões, listas de tarefas, relatórios, documentação de processos, cronogramas. REGRAS OBRIGATÓRIAS: 1) REGISTRE ABSOLUTAMENTE TUDO que Marcos decidir ou mencionar. 2) Sempre comece com 📌 MEMÓRIA DA SESSÃO: resumo do que foi decidido até agora. 3) Organize tarefas com prioridade: 🔴 Urgente / 🟡 Importante / 🟢 Pode esperar. 4) Entregue documentos em Markdown pronto para salvar. 5) Sempre liste ⏭️ PENDÊNCIAS ao final. Prefixe respostas com [SECRETÁRIA]."
    }
  }
}
'@

# Verificar se já existe um opencode.json e fazer backup
if (Test-Path ".\opencode.json") {
    Copy-Item ".\opencode.json" ".\opencode.backup.json"
    Write-Host "⚠️  opencode.json existente salvo como opencode.backup.json" -ForegroundColor Yellow
}

# Salvar o novo config
$config | Out-File -FilePath ".\opencode.json" -Encoding UTF8
Write-Host "✅ opencode.json criado com 5 agentes!" -ForegroundColor Green

# Criar pasta de memória da equipe
if (-not (Test-Path ".\pcsolucoes-memoria")) {
    New-Item -ItemType Directory -Path ".\pcsolucoes-memoria" | Out-Null
    Write-Host "✅ Pasta pcsolucoes-memoria/ criada para salvar contexto" -ForegroundColor Green
}

# Criar arquivo de sessão inicial
$sessao = @"
# PCsoluções — Memória da Equipe
**Empresa:** PCsoluções  
**Dono:** Marcos  
**Iniciado em:** $(Get-Date -Format "dd/MM/yyyy HH:mm")

## Decisões desta sessão
- [ ] (aguardando primeiras decisões de Marcos)

## Projetos em andamento
- [ ] (aguardando informações de Marcos)

## Clientes mencionados
- [ ] (aguardando informações de Marcos)
"@

$sessao | Out-File -FilePath ".\pcsolucoes-memoria\sessao-atual.md" -Encoding UTF8
Write-Host "✅ Arquivo de memória criado em pcsolucoes-memoria/sessao-atual.md" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Blue
Write-Host "         EQUIPE PRONTA, MARCOS!           " -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "AGENTES DISPONÍVEIS:" -ForegroundColor White
Write-Host "  /agent gestor     → Coordenador geral (comece por aqui)" -ForegroundColor Cyan
Write-Host "  /agent designer   → Design, UI/UX, marketing" -ForegroundColor Magenta
Write-Host "  /agent dev        → PHP, MySQL, XAMPP, PowerShell" -ForegroundColor Yellow
Write-Host "  /agent suporte    → Atendimento e suporte ao cliente" -ForegroundColor Green
Write-Host "  /agent secretaria → Organização e memória da equipe" -ForegroundColor White
Write-Host ""
Write-Host "DICA: Fale com o /agent gestor para ele delegar automaticamente!" -ForegroundColor Gray
Write-Host ""
