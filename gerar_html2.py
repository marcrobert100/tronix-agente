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

html = '''<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Estudo em Áudio GM Chã Preta/AL – Pergunta & Resposta</title>
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\">
<style>
:root{--bg:#0b1026;--card:#10162c;--text:#e5e7eb;--muted:#9aa0c3;--border:rgba(255,255,255,.08);--ok:#22c55e}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,sans-serif}
body{background:radial-gradient(1200px 800px at 50% -10%,rgba(77,124,255,.18),transparent),var(--bg);color:var(--text);line-height:1.6}
header{position:sticky;top:0;z-index:10;background:linear-gradient(180deg,rgba(11,16,38,.98),rgba(11,16,38,.9));backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.wrap{max-width:980px;margin:0 auto;padding:1rem}
h1{font-size:clamp(1.05rem,2vw,1.6rem);font-weight:700}
.sub{color:var(--muted);margin-top:.2rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:.9rem;margin-top:1.2rem}
.card{background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.02));border:1px solid var(--border);border-radius:14px;overflow:hidden}
.card-head{padding:.9rem 1rem 0;display:flex;justify-content:space-between;align-items:center}
.card-title{font-weight:700}
.badge{color:var(--ok);border:1px solid rgba(34,197,94,.5);background:rgba(34,197,94,.15);border-radius:999px;padding:.15rem .5rem;font-size:.78rem}
.audio{padding:.6rem 1rem;display:flex;flex-direction:column;gap:.4rem}
audio{width:100%}
.small{color:var(--muted);font-size:.88rem}
.footer{border-top:1px solid var(--border);margin-top:2rem;padding:1.2rem 0;color:var(--muted);font-size:.9rem}
</style>
</head>
<body>
<header>
  <div class=\"wrap\">
    <h1>GM Chã Preta/AL – Estudo Pergunta & Resposta (Peso 3,0 – 84%)</h1>
    <div class=\"sub\">Ouça PERGUNTA → RESPOSTA. Ideal pra aprender dirigindo, caminhando ou lavando roupa.</div>
  </div>
</header>
<main class=\"wrap\">
  <div class=\"grid\">
''' + '\n'.join([f'''
    <article class=\"card\">
      <div class=\"card-head\">
        <div class=\"card-title\">{item['nome']}</div>
        <span class=\"badge\">Peso 3,0</span>
      </div>
      <div class=\"audio\">
        <div class=\"small\">1) Estratégia (mapa focado)</div>
        <audio controls preload=\"metadata\" src=\"{item['estrategia']}\"></audio>
        <div class=\"small\">2) Pergunta & Resposta (10 blocos)</div>
        <audio controls preload=\"metadata\" src=\"{item['pq']}\"></audio>
      </div>
    </article>
''' for item in items]) + '''
  </div>
</main>
<footer class=\"footer wrap\">Foque nas 7 disciplinas de peso 3,0. Treine cronometrado + corrija erros.</footer>
</body>
</html>'''
html_file.write_text(html, encoding='utf-8')
print('OK', html_file)
