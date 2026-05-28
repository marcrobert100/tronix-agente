<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard — InfoEngine</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
:root {
  --night-900:#0b081a; --night-800:#15123a; --night-700:#1f1b4e;
  --gold-400:#ffd700; --coral-400:#ff7a5a; --green:#25d366;
  --text-dark:#1a1a2e; --text-soft:#4a3f4a;
  --font-display:'Playfair Display',Georgia,serif;
  --font-body:'Quicksand',sans-serif;
}
body { font-family:var(--font-body); background:linear-gradient(135deg,var(--night-900),var(--night-800)); min-height:100vh; color:#fff; }
.topbar { background:rgba(255,255,255,0.03); backdrop-filter:blur(12px); border-bottom:1px solid rgba(255,255,255,0.06); padding:0.8rem 2rem; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:100; }
.topbar h1 { font-family:var(--font-display); font-size:1.3rem; color:var(--gold-400); }
.topbar .nav { display:flex; gap:0.5rem; }
.topbar .nav a { color:rgba(255,255,255,0.4); text-decoration:none; padding:0.4rem 1rem; border-radius:2rem; font-size:0.85rem; font-weight:600; transition:all 0.3s; }
.topbar .nav a:hover, .topbar .nav a.active { color:#fff; background:rgba(255,255,255,0.06); }
.container { max-width:1200px; margin:0 auto; padding:2rem; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:1rem; margin-bottom:2rem; }
.stat-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:1.2rem; text-align:center; }
.stat-card .num { font-family:var(--font-display); font-weight:900; font-size:2.2rem; color:var(--gold-400); }
.stat-card .lbl { font-size:0.8rem; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:1px; margin-top:0.2rem; }
.section-title { font-family:var(--font-display); font-size:1.4rem; color:var(--gold-400); margin:1.5rem 0 1rem; display:flex; align-items:center; gap:0.5rem; }
.template-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; margin-bottom:2rem; }
.tpl-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:1.2rem; transition:all 0.3s; }
.tpl-card:hover { transform:translateY(-3px); border-color:rgba(255,215,0,0.15); }
.tpl-card h3 { font-family:var(--font-display); font-size:1rem; color:var(--gold-400); margin-bottom:0.3rem; }
.tpl-card p { font-size:0.85rem; color:rgba(255,255,255,0.4); margin-bottom:0.6rem; line-height:1.5; }
.tpl-card .tags { display:flex; gap:0.3rem; flex-wrap:wrap; margin-bottom:0.6rem; }
.tpl-card .tag { padding:0.15rem 0.6rem; border-radius:2rem; font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; }
.tag-infantil { background:rgba(255,215,0,0.12); color:var(--gold-400); }
.tag-infografico { background:rgba(255,122,90,0.12); color:var(--coral-400); }
.tag-pdf { background:rgba(255,122,90,0.1); color:var(--coral-400); }
.tag-whatsapp { background:rgba(37,211,102,0.1); color:var(--green); }
.tpl-card .actions { display:flex; gap:0.4rem; }
.tpl-card .actions a { flex:1; text-align:center; padding:0.3rem 0; border-radius:2rem; font-size:0.7rem; font-weight:600; text-decoration:none; transition:all 0.3s; }
.btn-view { background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.6); }
.btn-view:hover { background:rgba(255,255,255,0.1); color:#fff; }
.btn-wa { background:rgba(37,211,102,0.12); color:var(--green); }
.btn-wa:hover { background:rgba(37,211,102,0.2); }
.row { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:2rem; }
@media (max-width:768px) { .row { grid-template-columns:1fr; } }
.card-form { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:1.5rem; }
.card-form h3 { font-family:var(--font-display); font-size:1.1rem; color:var(--gold-400); margin-bottom:1rem; }
.form-group { margin-bottom:0.8rem; }
.form-group label { display:block; font-size:0.8rem; color:rgba(255,255,255,0.5); margin-bottom:0.3rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; }
.form-group input, .form-group textarea, .form-group select { width:100%; padding:0.6rem 0.8rem; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); border-radius:8px; color:#fff; font-family:var(--font-body); font-size:0.9rem; }
.form-group textarea { min-height:80px; resize:vertical; }
.form-group input:focus, .form-group textarea:focus { outline:none; border-color:var(--gold-400); }
.btn-primary { display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.5rem; background:var(--coral-400); color:#fff; border:none; border-radius:2rem; font-family:var(--font-body); font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.3s; }
.btn-primary:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(255,122,90,0.25); }
.btn-secondary { display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.5rem; background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:2rem; font-family:var(--font-body); font-weight:700; font-size:0.85rem; cursor:pointer; transition:all 0.3s; text-decoration:none; }
.btn-secondary:hover { background:rgba(255,255,255,0.1); color:#fff; }
.pages-list { margin:1rem 0; }
.pg-entry { background:rgba(255,255,255,0.03); border-radius:8px; padding:0.8rem; margin-bottom:0.5rem; border-left:3px solid var(--gold-400); }
.pg-entry .pg-num { font-size:0.75rem; color:rgba(255,255,255,0.3); font-weight:700; text-transform:uppercase; letter-spacing:1px; }
.add-page { display:block; width:100%; padding:0.5rem; text-align:center; background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.1); border-radius:8px; color:rgba(255,255,255,0.3); cursor:pointer; font-family:var(--font-body); font-size:0.85rem; transition:all 0.3s; margin-top:0.5rem; }
.add-page:hover { border-color:var(--gold-400); color:var(--gold-400); }
.toast { position:fixed; bottom:2rem; right:2rem; padding:0.8rem 1.5rem; border-radius:12px; background:rgba(0,0,0,0.8); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.1); color:#fff; font-size:0.85rem; transform:translateY(100px); opacity:0; transition:all 0.5s; z-index:999; }
.toast.show { transform:translateY(0); opacity:1; }
.hidden { display:none; }
.quick-actions { display:flex; gap:0.5rem; flex-wrap:wrap; margin:1rem 0; }
.quick-actions a { flex:1; min-width:120px; text-align:center; padding:0.8rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:12px; text-decoration:none; color:rgba(255,255,255,0.5); font-size:0.85rem; transition:all 0.3s; }
.quick-actions a:hover { border-color:rgba(255,215,0,0.2); color:var(--gold-400); background:rgba(255,215,0,0.03); }
.quick-actions a .icon { font-size:1.5rem; display:block; margin-bottom:0.3rem; }
</style>
</head>
<body>
<div class="topbar">
  <h1>⚡ InfoEngine</h1>
  <div class="nav">
    <a href="#" class="active" onclick="showTab('dashboard')">Dashboard</a>
    <a href="#" onclick="showTab('criar')">Criar</a>
    <a href="#" onclick="showTab('ferramentas')">Ferramentas</a>
    <a href="../index.html">↩ Site</a>
  </div>
</div>

<div class="container">
  <div id="tab-dashboard">
    <div class="stats" id="statsContainer">
      <div class="stat-card"><div class="num" id="statTemplates">-</div><div class="lbl">Templates</div></div>
      <div class="stat-card"><div class="num" id="statInfantil">-</div><div class="lbl">Livros Infantis</div></div>
      <div class="stat-card"><div class="num" id="statInfografico">-</div><div class="lbl">Infográficos</div></div>
      <div class="stat-card"><div class="num" id="statFerramentas">-</div><div class="lbl">Ferramentas</div></div>
    </div>

    <div class="quick-actions">
      <a href="#" onclick="showTab('criar')"><span class="icon">📖</span>Novo Livro</a>
      <a href="#" onclick="showTab('criar')"><span class="icon">📊</span>Novo Infográfico</a>
      <a href="../templates/infografico/vendas.html" target="_blank"><span class="icon">📄</span>Ver Templates</a>
      <a href="https://wa.me/5582991856656" target="_blank"><span class="icon">📱</span>WhatsApp</a>
    </div>

    <h2 class="section-title">📂 Templates</h2>
    <div class="template-grid" id="templateGrid">
      <div class="tpl-card"><p style="text-align:center;color:rgba(255,255,255,0.2);padding:2rem 0;">Carregando...</p></div>
    </div>

    <h2 class="section-title">⚙️ Ferramentas CLI</h2>
    <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;font-family:monospace;font-size:0.85rem;line-height:1.8;color:rgba(255,255,255,0.5);overflow-x:auto;">
      <div style="color:var(--gold-400);margin-bottom:0.5rem;"># Criar história infantil</div>
      <div>python tools/criar_historia.py</div>
      <div style="color:var(--gold-400);margin-top:0.8rem;"># Gerar PDF a partir de HTML</div>
      <div>python tools/gerar_pdf.py templates/infantil/o-dragao-que-aprendeu-a-abracar.html</div>
      <div style="color:var(--gold-400);margin-top:0.8rem;"># Enviar via WhatsApp</div>
      <div>python tools/enviar_whatsapp.py --numero 5582991856656 --mensagem "Olá!"</div>
      <div style="color:var(--gold-400);margin-top:0.8rem;"># Gerar JSON de infográfico</div>
      <div>python tools/gerar_infografico.py --export</div>
    </div>
  </div>

  <div id="tab-criar" class="hidden">
    <div class="row">
      <div class="card-form">
        <h3>📖 Criar Novo Livro Infantil</h3>
        <form id="formLivro" onsubmit="gerarLivro(event)">
          <div class="form-group">
            <label>Título do Livro</label>
            <input type="text" id="livroTitulo" placeholder="Ex: O Dragão que Aprendeu a Abraçar" required>
          </div>
          <div class="form-group">
            <label>Subtítulo</label>
            <input type="text" id="livroSubtitulo" placeholder="Ex: Uma história sobre emoções">
          </div>
          <div class="form-group">
            <label>Autor</label>
            <input type="text" id="livroAutor" value="Marcos Roberto">
          </div>
          <div class="form-group">
            <label>Número de Páginas</label>
            <input type="number" id="livroPaginas" value="8" min="4" max="20">
          </div>
          <div class="form-group" id="paginasContainer">
            <label>Conteúdo das Páginas</label>
            <div class="pages-list" id="pagesList"></div>
          </div>
          <button type="submit" class="btn-primary">✨ Gerar Estrutura JSON</button>
        </form>
      </div>

      <div class="card-form">
        <h3>📊 Criar Novo Infográfico</h3>
        <form id="formInfo" onsubmit="gerarInfo(event)">
          <div class="form-group">
            <label>Título</label>
            <input type="text" id="infoTitulo" placeholder="Ex: Produto Pro Max">
          </div>
          <div class="form-group">
            <label>Subtítulo</label>
            <input type="text" id="infoSubtitulo" placeholder="Ex: A solução completa">
          </div>
          <div class="form-group">
            <label>Número de Benefícios</label>
            <select id="infoBeneficios">
              <option value="3">3</option>
              <option value="4" selected>4</option>
              <option value="6">6</option>
            </select>
          </div>
          <div class="form-group">
            <label>Preço Original</label>
            <input type="text" id="infoPrecoOriginal" placeholder="4.997,00">
          </div>
          <div class="form-group">
            <label>Preço Atual</label>
            <input type="text" id="infoPrecoAtual" placeholder="1.997,00">
          </div>
          <div class="form-group">
            <label>Parcelas</label>
            <input type="number" id="infoParcelas" value="12">
          </div>
          <button type="submit" class="btn-primary">🚀 Gerar Estrutura JSON</button>
        </form>
      </div>
    </div>
    <div id="resultado" class="hidden" style="margin-top:1rem;">
      <h3 class="section-title">✅ Resultado</h3>
      <pre id="resultadoPre" style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;font-family:monospace;font-size:0.85rem;color:rgba(255,255,255,0.6);overflow-x:auto;white-space:pre-wrap;"></pre>
      <button class="btn-secondary" onclick="copiarResultado()" style="margin-top:0.5rem;">📋 Copiar JSON</button>
    </div>
  </div>

  <div id="tab-ferramentas" class="hidden">
    <div class="row">
      <div class="card-form">
        <h3>🔧 Gerar PDF</h3>
        <div class="form-group">
          <label>Template HTML</label>
          <select id="pdfTemplate">
            <option value="templates/infantil/o-sonho-da-estrelinha-lua.html">Estrelinha Lua</option>
            <option value="templates/infantil/o-dragao-que-aprendeu-a-abracar.html">Dragão que Aprendeu a Abraçar</option>
            <option value="templates/infografico/vendas.html">Infográfico Vendas</option>
          </select>
        </div>
        <button class="btn-primary" onclick="window.open(document.getElementById('pdfTemplate').value,'_blank')">📄 Abrir Template</button>
      </div>

      <div class="card-form">
        <h3>📱 Enviar via WhatsApp</h3>
        <div class="form-group">
          <label>Número (com código do país)</label>
          <input type="text" id="waNumero" value="5582991856656">
        </div>
        <div class="form-group">
          <label>Mensagem</label>
          <textarea id="waMensagem" placeholder="Digite sua mensagem...">Olá! 👋 Vi isto no InfoEngine e achei que você gostaria de ver.</textarea>
        </div>
        <button class="btn-primary" onclick="enviarWA()">📱 Abrir WhatsApp</button>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// Templates data
const TEMPLATES = [
  { name:'O Sonho da Estrelinha Lua', path:'templates/infantil/o-sonho-da-estrelinha-lua.html', desc:'Livro infantil ilustrado com 10 páginas SVG', tags:['infantil','pdf','whatsapp'], type:'infantil' },
  { name:'O Dragão que Aprendeu a Abraçar', path:'templates/infantil/o-dragao-que-aprendeu-a-abracar.html', desc:'Livro infantil sobre emoções com narração por voz', tags:['infantil','pdf','whatsapp'], type:'infantil' },
  { name:'Infográfico Profissional', path:'templates/infografico/vendas.html', desc:'Infográfico de vendas com stats, specs e CTA', tags:['infografico','pdf','whatsapp'], type:'infografico' },
  { name:'Social Post', path:'templates/infografico/social-post.html', desc:'Post 1080x1080 para Instagram/LinkedIn', tags:['infografico','whatsapp'], type:'infografico' },
];

function showTab(tab) {
  document.querySelectorAll('[id^="tab-"]').forEach(t => t.classList.add('hidden'));
  document.getElementById('tab-' + tab).classList.remove('hidden');
  document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
  const links = document.querySelectorAll('.nav a');
  const idx = tab === 'dashboard' ? 0 : tab === 'criar' ? 1 : 2;
  if (links[idx]) links[idx].classList.add('active');
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = ' ' + msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

function renderTemplates() {
  const grid = document.getElementById('templateGrid');
  grid.innerHTML = TEMPLATES.map(t => {
    const tagsHtml = t.tags.map(tag => `<span class="tag tag-${tag}">${tag}</span>`).join('');
    return `<div class="tpl-card">
      <h3>${t.name}</h3>
      <p>${t.desc}</p>
      <div class="tags">${tagsHtml}</div>
      <div class="actions">
        <a href="../${t.path}" target="_blank" class="btn-view">👁️ Ver</a>
        <a href="https://wa.me/5582991856656?text=${encodeURIComponent('Olá! Vi este template no InfoEngine: ' + t.name + ' - ' + window.location.origin + '/agente/infoengine/' + t.path)}" target="_blank" class="btn-wa">📱 WhatsApp</a>
      </div>
    </div>`;
  }).join('');
}

function renderStats() {
  const infantil = TEMPLATES.filter(t => t.type === 'infantil').length;
  const infografico = TEMPLATES.filter(t => t.type === 'infografico').length;
  document.getElementById('statTemplates').textContent = TEMPLATES.length;
  document.getElementById('statInfantil').textContent = infantil;
  document.getElementById('statInfografico').textContent = infografico;
  document.getElementById('statFerramentas').textContent = '4';
}

// Livro form - dynamic pages
document.addEventListener('DOMContentLoaded', function() {
  renderTemplates();
  renderStats();
  gerarPaginas();
  document.getElementById('livroPaginas').addEventListener('change', gerarPaginas);
});

function gerarPaginas() {
  const num = parseInt(document.getElementById('livroPaginas').value) || 8;
  const container = document.getElementById('pagesList');
  container.innerHTML = '';
  for (let i = 1; i <= num; i++) {
    const div = document.createElement('div');
    div.className = 'pg-entry';
    div.innerHTML = `<div class="pg-num">PÁGINA ${i}</div>
      <div class="form-group" style="margin:0.3rem 0;">
        <input type="text" class="pg-titulo" placeholder="Título da página ${i}" style="font-size:0.85rem;padding:0.4rem 0.6rem;">
      </div>
      <div class="form-group" style="margin:0;">
        <textarea class="pg-texto" placeholder="Texto da página ${i}..." style="font-size:0.85rem;padding:0.4rem 0.6rem;min-height:50px;"></textarea>
      </div>`;
    container.appendChild(div);
  }
}

function gerarLivro(e) {
  e.preventDefault();
  const titulo = document.getElementById('livroTitulo').value || 'Novo Livro';
  const subtitulo = document.getElementById('livroSubtitulo').value || 'Uma história infantil';
  const autor = document.getElementById('livroAutor').value || 'Marcos Roberto';
  const paginas = [];
  document.querySelectorAll('.pg-entry').forEach((el, i) => {
    const t = el.querySelector('.pg-titulo').value || `Página ${i+1}`;
    const txt = el.querySelector('.pg-texto').value || `Texto da página ${i+1}`;
    paginas.push({ numero: i+1, titulo: t, texto: txt, dialogo: '', ilustracao: 'padrao' });
  });
  const json = { titulo, subtitulo, autor, faixa_etaria: '2 — 6 anos', paginas, gerado_em: new Date().toISOString() };
  mostrarResultado(JSON.stringify(json, null, 2));
  toast('✅ Estrutura do livro gerada! Copie o JSON e use com criar_historia.py');
}

function gerarInfo(e) {
  e.preventDefault();
  const titulo = document.getElementById('infoTitulo').value || 'Produto';
  const subtitle = document.getElementById('infoSubtitulo').value || 'Solução completa';
  const numBenef = parseInt(document.getElementById('infoBeneficios').value) || 4;
  const precoOrig = document.getElementById('infoPrecoOriginal').value || '4.997,00';
  const precoAtual = document.getElementById('infoPrecoAtual').value || '1.997,00';
  const parcelas = document.getElementById('infoParcelas').value || 12;
  const beneficios = [];
  for (let i = 1; i <= numBenef; i++) {
    beneficios.push({ icone: '✨', titulo: `Benefício ${i}`, descricao: `Descrição do benefício ${i}.` });
  }
  const json = {
    titulo, subtitulo: subtitle, estatisticas: [
      { valor: '+50%', rotulo: 'Resultados' },
      { valor: `${parcelas}x`, rotulo: 'Sem Juros' },
      { valor: '7', rotulo: 'Dias' },
      { valor: '+2k', rotulo: 'Clientes' },
    ],
    beneficios,
    preco: { original: parseFloat(precoOrig.replace(/\./g,'').replace(',','.')) || 4997, atual: parseFloat(precoAtual.replace(/\./g,'').replace(',','.')) || 1997, parcelas: parseInt(parcelas), valor_parcela: Math.round((parseFloat(precoAtual.replace(/\./g,'').replace(',','.')) || 1997) / parseInt(parcelas) * 100) / 100 },
    depoimento: { texto: 'Produto excelente! Superou minhas expectativas.', autor: 'Cliente Satisfeito' },
    gerado_em: new Date().toISOString()
  };
  mostrarResultado(JSON.stringify(json, null, 2));
  toast('✅ Estrutura do infográfico gerada! Use com gerar_infografico.py');
}

function mostrarResultado(json) {
  document.getElementById('resultado').classList.remove('hidden');
  document.getElementById('resultadoPre').textContent = json;
  document.getElementById('resultado').scrollIntoView({ behavior:'smooth' });
}

function copiarResultado() {
  const text = document.getElementById('resultadoPre').textContent;
  navigator.clipboard.writeText(text).then(() => toast('📋 JSON copiado!'));
}

function enviarWA() {
  const num = document.getElementById('waNumero').value.replace(/\D/g,'');
  const msg = document.getElementById('waMensagem').value;
  window.open(`https://wa.me/${num}?text=${encodeURIComponent(msg)}`, '_blank');
}
</script>
</body>
</html>
