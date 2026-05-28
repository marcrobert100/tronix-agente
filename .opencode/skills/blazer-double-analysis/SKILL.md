# Blazer Double Analysis

Análise de padrões e tendências do jogo Blazer Double (cores: White, Red, Black).

## Quando usar
- Quando solicitado "analisar Blazer Double", "padrões do jogo", "estatísticas Blazer"
- Receber histórico de cores e processar
- Detectar padrões de entrada e alertar

## Visão Geral do Jogo

### Cores
- **White** (Branco) - 0 (menor frequência, ~13%)
- **Red** (Vermelho) - 1 a 7 (maior frequência, ~44%)
- **Black** (Preto) - 8 a 14 (frequência média, ~43%)

### Dados de Entrada
O agente aceita:
- Array de cores: `['W', 'R', 'B']` ou `['White', 'Red', 'Black']`
- Histórico em arquivo JSON
- Entrada via terminal

## Análises Realizadas

### 1. Estatísticas Básicas
- Frequência de cada cor
- Percentuais
- Média de repetições consecutivas

### 2. Análise de Padrões
- Sequências mais comuns (RRR, BBB, etc)
- Padrões alternados (R-B-R, W-R-B)
- Comprimento máximo de sequências

### 3. Probabilidade
- Probabilidade condicional (dado último resultado)
- Tendência atual
- Probabilidade de mudança

### 4. Alertas de Padrão
- Configurável via arquivo de configuração
- Notificação quando padrão detectado

## Arquivos do Projeto

```
blazer-double-analysis/
├── analyzer.py          # Script principal Python
├── config.json          # Configurações de alertas
├── history.json         # Histórico de resultados
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## Uso

### Python (Recomendado)
```bash
# Instalação
pip install -r requirements.txt

# Executar análise
python analyzer.py --history W,R,R,B,R,W,R,B,B,R

# Modo interativo
python analyzer.py --interactive

# Monitor em tempo real
python analyzer.py --monitor

# Adicionar resultado e analisar
python analyzer.py --add R
```

### Node.js
```bash
# Instalação
npm install

# Executar
node analyzer.js --history W,R,R,B,R,W,R,B,B,R
```

## Configuração de Alertas

Edite `config.json` para configurar alertas:

```json
{
  "alerts": {
    "max_streak": 5,
    "pattern_alerts": [
      {"pattern": "W,R,R", "message": "Atenção: Padrão White-Red-Red detectado"},
      {"pattern": "R,R,R,R", "message": "Alerta: 4 Reds consecutivos!"},
      {"pattern": "B,B,W", "message": "Sequência Black-Black-White"}
    ],
    "probability_threshold": 0.7
  },
  "notification": {
    "terminal": true,
    "log_file": "alerts.log",
    "sound": false
  }
}
```

## Output示例

```
===========================================
     BLAZER DOUBLE ANALYZER v1.0
===========================================

📊 ESTATÍSTICAS (últimos 20 jogos)

| Cor    | Quantidade | Percentual |
|--------|------------|------------|
| White  |     3      |   15.0%    |
| Red    |     9      |   45.0%    |
| Black  |     8      |   40.0%    |

📈 ANÁLISE DE PADRÕES

Sequências mais comuns:
  - R,R: 4x (20%)
  - B,B: 3x (15%)
  - R,B: 3x (15%)

Maior sequência atual:
  - Red: 3x consecutivas

🎯 PROBABILIDADES

Último resultado: Red
  - P(White) = 15.6%
  - P(Red)   = 43.2%
  - P(Black) = 41.2%

⚠️ ALERTAS

  [ATIVO] 3 Reds consecutivos - tendência de continuação
  [INFO]  Probabilidade de mudança: 56.8%

===========================================
```

## Integração com Tronix

Para usar com o agente:
1. Execute o analyzer com os dados
2. Cole a saída no chat
3. O agente interpretará e explicará os padrões

## Aviso Legal

Este ferramenta é apenas para análise estatística.
Jogos de azar envolvem risco. Use com responsabilidade.