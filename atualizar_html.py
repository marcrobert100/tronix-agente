from pathlib import Path

out = Path(r'C:\Users\CHCONTE RECPÇÃO\Desktop\estudo_audio_gm_cha_preta_al')
mp3dir = out / 'mp3'
html_file = out / 'index.html'

disciplinas = [
  ('direito_constitucional','Noções de Direito Constitucional'),
  ('direito_administrativo','Noções de Direito Administrativo'),
  ('direito_penal','Noções de Direito Penal'),
  ('direito_processual_penal','Noções de Direito Processual Penal'),
  ('direitos_humanos','Noções de Direitos Humanos'),
  ('legislacao_penal_extravagante','Legislação Penal Extravagante'),
  ('legislacao_geral_gm','Legislação Geral da Guarda Municipal'),
]

items = []
for slug,nome in disciplinas:
    items.append({
        'nome':nome,
        'estrategia':f'mp3/{slug}_estrategia.mp3',
        'pq':f'mp3/{slug}_pq_resposta.mp3'
    })

# blocos extras
extras = sorted([f'mp3/{p.name}' for p in mp3dir.glob('pq_concursos_bloco_*.mp3')])

html = '''<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>GM Chã Preta/AL – Estudo Pergunta & Resposta (Amplo)</title>
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\">
<style>
:root{--bg:#0b1026;--card:#10162c;--text:#e5e7eb;--muted:#9aa0c3;--border:rgba(255,255,255,.08);--ok:#22c55e;--primary:#4d7cff}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,sans-serif}
body{background:radial-gradient(1200px 800px at 50% -10%,rgba(77,124,255,.18),transparent),var(--bg);color:var(--text);line-height:1.65}
header{position:sticky;top:0;z-index:10;background:linear-gradient(180deg,rgba(11,16,38,.98),rgba(11,16,38,.9));backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.wrap{max-width:1040px;margin:0 auto;padding:1rem}
h1{font-size:clamp(1.05rem,2vw,1.55rem);font-weight:700}
h2{margin:1.8rem 0 .6rem;font-size:clamp(1rem,1.6vw,1.25rem)}
.sub{color:var(--muted);margin-top:.25rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:.9rem;margin-top:1rem}
.card{background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.02));border:1px solid var(--border);border-radius:14px;overflow:hidden}
.card-head{padding:.9rem 1rem .2rem;display:flex;justify-content:space-between;align-items:flex-start;gap:.8rem}
.card-title{font-weight:700}
.badge{color:var(--ok);border:1px solid rgba(34,197,94,.5);background:rgba(34,197,94,.15);border-radius:999px;padding:.15rem .5rem;font-size:.78rem;white-space:nowrap}
.audio{padding:.6rem 1rem 1rem;display:flex;flex-direction:column;gap:.55rem}
.label{color:var(--muted);font-size:.9rem}
audio{width:100%}
.box{margin-top:1.2rem;padding:1rem 1rem .8rem;border:1px solid var(--border);border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.02))}
ul{padding-left:1.2rem;color:var(--muted)}
li{margin:.25rem 0}
.footer{border-top:1px solid var(--border);margin-top:2rem;padding:1.2rem 0;color:var(--muted);font-size:.92rem}
</style>
</head>
<body>
<header>
  <div class=\"wrap\">
    <h1>GM Chã Preta/AL – Estudo Ampliado: Pergunta → Resposta</h1>
    <div class=\"sub\">Foco 100% nas 7 disciplinas de <strong>peso 3,0 (84%)</strong>. Ideal para aprender ouvindo e passar no concurso.</div>
  </div>
</header>
<main class=\"wrap\">
  <h2>1) Disciplinas (Estratégia + Pergunta & Resposta – 10 blocos por matéria)</h2>
  <div class=\"grid\">
''' + '\n'.join([f'''
    <article class=\"card\">
      <div class=\"card-head\">
        <div class=\"card-title\">{item['nome']}</div>
        <span class=\"badge\">Peso 3,0 • 12 pts</span>
      </div>
      <div class=\"audio\">
        <div class=\"label\">Estratégia de estudo (prioritário)</div>
        <audio controls preload=\"metadata\" src=\"{item['estrategia']}\"></audio>
        <div class=\"label\">Pergunta & Resposta – Modo Aprendizado</div>
        <audio controls preload=\"metadata\" src=\"{item['pq']}\"></audio>
      </div>
    </article>
''' for item in items]) + '''
  </div>
''' + (('''
  <h2>2) Banco de Questões (extraído do livro)</h2>
  <div class=\"box\">
''' + '\n'.join([f'''
    <div style=\"margin:.4rem 0 .8rem\">
      <div class=\"label\">{Path(x).name.replace('_',' ').replace('.mp3','')}</div>
      <audio controls preload=\"metadata\" src=\"{x}\"></audio>
    </div>
''' for x in extras]) + '''
  </div>
''') if extras else '') + '''
  <h2>Como usar (método mais eficaz)</h2>
  <div class=\"box\">
    <ul>
      <li><strong>Pergunta → Pausa → Resposta</strong>: ouça pergunta, pense a resposta (5–10 seg), depois ouça a resposta.</li>
      <li><strong>Repetição espaçada</strong>: repita matéria em 1, 3, 7, 14 dias. Foque nas 7 de peso 3,0.</li>
      <li><strong>Aprendizado ativo</strong>: fale a resposta em voz alta antes de ouvir.</li>
      <li><strong>Treino cronometrado</strong>: resolva questões reais (QConcursos/PCI) + corrija erros.</li>
      <li><strong>Ouvindo no dia a dia</strong>: trânsito, caminhada, tarefas – aproveita tempo morto.</li>
    </ul>
  </div>
</main>
<footer class=\"footer wrap\">
  Base: <strong>LIVRO DE ESTUDO GM CHA PRETA AL.pdf</strong> • Foco: 84% da prova • Arquivos .mp3 offline
</footer>
</body>
</html>'''
html_file.write_text(html, encoding='utf-8')
print('ATUALIZADO', html_file)
