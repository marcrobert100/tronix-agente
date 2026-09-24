# Tronix Santinho Generator

> Gerador profissional de santinhos políticos em quantidade.
> 20 modelos visuais · 15+ acessórios · 300 DPI · Grade A4 para gráfica · Frente e verso · QR Code

**Equipe envolvida:** Tronix-DEV + Tronix-MEDIA + Tronix-SUPER + Tronix-DB + Tronix-ROTEIRISTA + Tronix-DIRETOR

---

## Recursos

- **20 modelos visuais** em CSS + engine Python
- **15+ acessórios configuráveis** sobrepostos em qualquer modelo
- **Editor visual** com preview ao vivo e personalização de cores
- **Geração em lote** (1 a 10.000 santinhos) com grid A4 automático
- **Frente e verso** com propostas, contato e QR Code
- **300 DPI** (qualidade gráfica profissional)
- **4 layouts A4** (6, 8, 9 ou 10 santinhos por folha)
- **Persistência SQLite** de candidatos e gerações
- **CLI** para automação
- **One-click** via `iniciar_santinho.bat`

## Como usar

### 1. Interface visual (recomendado)

```cmd
cd C:\xampp\htdocs\agente\santinho_generator
iniciar_santinho.bat
```

Abre no navegador: `http://localhost/agente/santinho_generator/`

Preencha os dados, escolha o modelo, clique em **Gerar Lote** → PDF pronto para gráfica.

### 2. Linha de comando (CLI)

```bash
# Unitário
python santinho.py --nome "Maria Silva" --numero "40123" --cargo "Vereadora" --quantidade 100

# Em lote (vários candidatos)
python gerar_lote.py --input exemplos_candidatos.json --quantidade 1000

# Listar modelos
python santinho.py --listar

# Apenas inicializar banco
python santinho.py --init-db
```

### 3. API JSON

Formato `exemplos_candidatos.json`:

```json
[
  {
    "nome": "Maria Silva",
    "cargo": "Vereadora",
    "partido": "UNIÃO",
    "numero": "40123",
    "cidade": "Viçosa - AL",
    "slogan1": "Juntos pela nossa gente",
    "whatsapp": "(82) 99999-1111",
    "instagram": "@mariasantos",
    "propostas": "Saúde\nEducação\nEmprego",
    "modelo": "classico"
  }
]
```

## Modelos disponíveis (20)

| # | ID | Nome | Categoria |
|---|----|------|-----------|
| 1 | `classico` | Clássico | tradicional |
| 2 | `moderno_minimalista` | Moderno Minimalista | moderno |
| 3 | `premium_executivo` | Premium Executivo | premium |
| 4 | `colorido_partidario` | Colorido Partidário | colorido |
| 5 | `jovem_dinamico` | Jovem Dinâmico | jovem |
| 6 | `tradicao_brasileiro` | Tradição Brasileiro | tradicional |
| 7 | `agro_forte` | Agro Forte | regional |
| 8 | `sindical_trabalhador` | Sindical Trabalhador | popular |
| 9 | `empresarial_pro` | Empresarial Pro | premium |
| 10 | `fotografico_impacto` | Fotográfico Impacto | moderno |
| 11 | `minimalista_horizontal` | Minimalista Horizontal | moderno |
| 12 | `cristao_familia` | Cristão Família | regional |
| 13 | `tecnologico_inovador` | Tecnológico Inovador | moderno |
| 14 | `esporte_juventude` | Esporte Juventude | jovem |
| 15 | `diagonal_dinamico` | Diagonal Dinâmico | moderno |
| 16 | `retro_vintage` | Retro Vintage | vintage |
| 17 | `gradient_suave` | Gradient Suave | moderno |
| 18 | `black_gold_luxo` | Black Gold Luxo | premium |
| 19 | `tropical_verao` | Tropical Verão | colorido |
| 20 | `civico_municipal` | Cívico Municipal | institucional |

## Acessórios (15+)

### Símbolos de fundo
- Nenhum, Cruz, Estrela, Coração, Bandeira, Raio, Mão, Família, Pomba

### Molduras da foto
- Quadrada, Redonda, Losango, Hexagonal, Escudo

### Estilos da foto
- Normal, Preto e Branco, Sépia, Duotone

### Badges (tags)
- Nenhum, ♀ Mulher, ★ Juventude, ↻ Renovação, ✓ Experiência, Educação, Saúde, Segurança, Agro, Cristão, Trabalhador, NOVO

### Extras (toggles)
- Selo "Justiça Eleitoral"
- Vice (nome)
- Proposta destaque (caixa colorida)
- Zona / Seção
- Faixa de cor inferior

## Estrutura

```
santinho_generator/
├── index.html              # Interface visual
├── css/styles.css          # 14 templates + dark mode
├── js/
│   ├── app.js              # Lógica + geração PDF (html2pdf)
│   └── templates.js        # 14 templates de renderização
├── models.json             # Catálogo de modelos
├── santinho.py             # Engine Python 300 DPI
├── gerar_lote.py           # Geração multi-candidato
├── exemplos_candidatos.json
├── iniciar_santinho.bat    # One-click
├── README.md
├── outputs/                # PDFs gerados
├── assets/fotos/           # Fotos dos candidatos
└── santinho.db             # SQLite (candidatos + gerações)
```

## Banco de dados (SQLite)

```sql
-- Tabela de candidatos
CREATE TABLE candidatos (
  id, nome, cargo, partido, numero, cidade,
  slogan1, slogan2, whatsapp, instagram, site,
  coligacao, propostas, foto_path, modelo, created_at
);

-- Tabela de gerações
CREATE TABLE geracoes (
  id, candidato_id, quantidade, copias_por_pagina,
  com_verso, arquivo_saida, created_at
);
```

## Integração com o ecossistema Tronix

- **Memória persistente:** cada geração registra em `memoria_tronix.json` (agente: `Tronix-SANTINHO`)
- **Dashboard:** cards de gerações em `dashboard.php` (em breve)
- **CrewAI:** pode ser invocado pelo agente `Tronix-MEDIA` para gerar material de campanha
- **Output Padronizado:** PDFs de 70x100mm prontos para gráfica (papel couchê 250g)

## Requisitos

- Python 3.10+
- `pip install pillow reportlab`
- Navegador moderno (Chrome/Edge/Firefox) para a interface visual

## Próximos passos

- [ ] Adicionar upload de logo do partido
- [ ] Integração direta com gráficas via API
- [ ] Mais modelos (vereador preto, prefeito diagonal, etc)
- [ ] Verso com tabela de propostas estilizada por modelo
- [ ] Exportar PNG unitário (para Instagram/WhatsApp)
- [ ] Gerador de adesivo de carro combinando
