import json
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
    mp3 = f'mp3/{slug}_estrategia.mp3'
    items.append({'id':slug,'nome':nome,'mp3':mp3})

html = '''<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Estudo em Áudio – GM Chã Preta/AL | Peso 3,0 (84%)</title>
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\">
<link href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css\" rel=\"stylesheet\">
<style>
:root{--bg:#0b1026;--card:#10162c;--primary:#4d7cff;--text:#e5e7eb;--muted:#9aa0c3;--border:rgba(255,255,255,.08);--ok:#22c55e}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
body{background:radial-gradient(1200px 800px at 50% -10%,rgba(77,124,255,.18),transparent),var(--bg);color:var(--text);line-height:1.6}
header{position:sticky;top:0;z-index:10;background:linear-gradient(180deg,rgba(11,16,38,.98),rgba(11,16,38,.9));backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.wrap{max-width:980px;margin:0 auto;padding:1rem}
h1{font-size:clamp(1.05rem,2vw,1.6rem);font-weight:700;letter-spacing:-.01em}
h2{font-size:clamp(.95rem,1.6vw,1.2rem);font-weight:700;margin:1.8rem 0 .8rem}
.sub{color:var(--muted);margin-top:.2rem;font-size:.98rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:.9rem;margin-top:1.2rem}
.card{background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.02));border:1px solid var(--border);border-radius:14px;box-shadow:0 30px 60px -40px rgba(77,124,255,.9);overflow:hidden}
.card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:.8rem;padding:.9rem 1rem 0}
.card-title{font-weight:700;font-size:1.02rem}
.card-badge{font-size:.78rem;color:var(--ok);border:1px solid rgba(34,197,94,.5);background:rgba(34,197,94,.15);border-radius:999px;padding:.15rem .5rem}
.audio-wrap{padding:.6rem 1rem 1rem;display:flex;flex-direction:column;gap:.5rem}
audio{width:100%}
.muted{color:var(--muted);font-size:.9rem}
.footer{border-top:1px solid var(--border);margin-top:2.6rem;padding:1.6rem 0;color:var(--muted);font-size:.9rem}
</style>
</head>
<body>
<header>
  <div class=\"wrap\">
    <h1>Estudo em Áudio – GM Chã Preta/AL</h1>
    <div class=\"sub\">Foco nas 7 disciplinas de <strong>peso 3,0</strong> – juntas representam <strong>84%</strong> da prova. Estratégia: questões de concursos anteriores + banco temático + revisões espaçadas.</div>
  </div>
</header>
<main class=\"wrap\">
  <h2>Disciplinas priorizadas</h2>
  <div class=\"grid\">
''' + '\n'.join([f'''
    <article class=\"card\">
      <div class=\"card-head\">
        <div class=\"card-title\">{item['nome']}</div>
        <span class=\"card-badge\">Peso 3,0 • 12 pts</span>
      </div>
      <div class=\"audio-wrap\">
        <audio controls preload=\"metadata\" src=\"{item['mp3']}\"></audio>
        <div class=\"muted\">Áudio: {item['mp3']}</div>
      </div>
    </article>
''' for item in items]) + '''
  </div>
  <h2>Dica de execução</h2>
  <div class=\"muted\">
    <p>1) Ouça no trânsito/caminhada (revisão passiva). 2) Resolva questões dessas disciplinas cronometrado (simulado). 3) Foque nos erros: revise edital + fichas. 4) Revisões: início, meio, véspera.</p>
    <p>Fontes sugeridas: <strong>QConcursos</strong>, <strong>PCI Concursos</strong>, <strong>Gran Cursos</strong>, <strong>Passei Direto</strong>, <strong>Aprova Concursos</strong> (filtrar por banca FUNVAPI).</p>
  </div>
</main>
<footer class=\"footer wrap\">
  Gerado a partir do PDF: <strong>LIVRO DE ESTUDO GM CHA PRETA AL.pdf</strong>
</footer>
</body>
</html>'''
html_file.write_text(html, encoding='utf-8')
print('HTML gerado:', html_file)
print('Arquivos MP3:', len(list(mp3dir.glob('*.mp3'))))
