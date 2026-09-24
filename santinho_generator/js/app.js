/* Tronix Santinho Generator - App Logic */
const state = {
  modelo: 'classico',
  foto: null,
  lado: 'frente',
  dados: {},
  acessorios: {
    simbolo: 'nenhum',
    moldura_foto: 'quadrada',
    badge: 'nenhum',
    estilo_foto: 'normal',
    selo_je: false,
    vice: '',
    proposta_destaque: '',
    zona_secao: '',
    faixa_cor: true
  }
};

const $ = (id) => document.getElementById(id);
const campos = ['nome', 'cargo', 'partido', 'numero', 'cidade', 'slogan1', 'slogan2', 'whatsapp', 'instagram', 'site', 'coligacao', 'propostas'];

async function init() {
  await carregarModelos();
  carregarCores();
  bindEvents();
  render();
  setStatus('Tronix Santinho Generator carregado · 14 modelos disponiveis');
}

async function carregarModelos() {
  try {
    const resp = await fetch('models.json');
    const data = await resp.json();
    const grid = $('modelos-grid');
    grid.innerHTML = data.modelos.map(m => `
      <div class="modelo-card" data-id="${m.id}" title="${m.descricao}">
        <div class="modelo-preview" style="background:linear-gradient(135deg, ${m.preview_cor}, #1a1a1a)">
          <span class="mp-nome">${m.nome.toUpperCase()}</span>
          <span class="mp-numero">12</span>
        </div>
        <span>${m.nome}</span>
      </div>
    `).join('');
    grid.querySelectorAll('.modelo-card').forEach(card => {
      card.addEventListener('click', () => {
        grid.querySelectorAll('.modelo-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        state.modelo = card.dataset.id;
        render();
      });
    });
    grid.querySelector('[data-id="classico"]').classList.add('active');
  } catch (e) {
    console.error('Erro ao carregar modelos:', e);
  }
}

function carregarCores() {
  const saved = JSON.parse(localStorage.getItem('tronix_santinho_cores') || '{}');
  if (saved.c1) $('cor-primaria').value = saved.c1;
  if (saved.c2) $('cor-secundaria').value = saved.c2;
  if (saved.ct) $('cor-texto').value = saved.ct;
  if (saved.cd) $('cor-destaque').value = saved.cd;
}

function salvarCores() {
  const cores = {
    c1: $('cor-primaria').value,
    c2: $('cor-secundaria').value,
    ct: $('cor-texto').value,
    cd: $('cor-destaque').value
  };
  localStorage.setItem('tronix_santinho_cores', JSON.stringify(cores));
  render();
}

function getDados() {
  const d = {};
  campos.forEach(c => d[c] = $(`f-${c}`).value);
  d.foto = state.foto;
  d.acessorios = { ...state.acessorios };
  return d;
}

function render() {
  const container = $('santinho-container');
  if (state.lado === 'verso') {
    container.innerHTML = TEMPLATES.verso(getDados());
    const qrArea = container.querySelector('#qrcode-area');
    if (qrArea) {
      const d = getDados();
      const link = d.site || (d.instagram ? `https://instagram.com/${d.instagram.replace('@','')}` : `https://wa.me/55${(d.whatsapp||'').replace(/\D/g,'')}`);
      qrArea.innerHTML = '';
      new QRCode(qrArea, { text: link, width: 60, height: 60, colorDark: '#000', colorLight: '#fff' });
    }
  } else {
    const tpl = TEMPLATES[state.modelo];
    if (tpl) {
      let html = tpl(getDados());
      html = aplicarAcessorios(html, getDados());
      container.innerHTML = html;
      container.style.setProperty('--c1', $('cor-primaria').value);
      container.style.setProperty('--c2', $('cor-secundaria').value);
      container.style.setProperty('--ct', $('cor-texto').value);
      container.style.setProperty('--cd', $('cor-destaque').value);
    }
  }
}

function bindEvents() {
  campos.forEach(c => {
    const el = $(`f-${c}`);
    if (el) el.addEventListener('input', render);
  });

  ['cor-primaria', 'cor-secundaria', 'cor-texto', 'cor-destaque'].forEach(id => {
    $(id).addEventListener('input', () => { salvarCores(); render(); });
  });

  const acc = [
    ['acc-simbolo', 'simbolo'],
    ['acc-moldura', 'moldura_foto'],
    ['acc-estilo-foto', 'estilo_foto'],
    ['acc-badge', 'badge'],
    ['acc-selo-je', 'selo_je', true],
    ['acc-faixa-cor', 'faixa_cor', true],
    ['acc-vice', 'vice'],
    ['acc-proposta', 'proposta_destaque'],
    ['acc-zona', 'zona_secao']
  ];
  acc.forEach(([id, key, isCheckbox]) => {
    const el = $(id);
    if (!el) return;
    const evt = isCheckbox ? 'change' : 'input';
    el.addEventListener(evt, () => {
      state.acessorios[key] = isCheckbox ? el.checked : el.value;
      render();
    });
  });

  $('f-foto').addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => { state.foto = ev.target.result; render(); };
    reader.readAsDataURL(file);
  });

  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.lado = tab.dataset.lado;
      render();
    });
  });

  $('btn-pdf-uni').addEventListener('click', () => gerarPDFUnico());
  $('btn-pdf-lote').addEventListener('click', () => gerarLote());
  $('btn-salvar').addEventListener('click', () => salvarCandidato());
  $('btn-carregar').addEventListener('click', () => abrirCarregar());

  const modal = $('modal-carregar');
  const fechar = () => { modal.removeAttribute('hidden'); modal.style.display = 'none'; };
  const abrir = () => { modal.setAttribute('hidden', ''); modal.style.display = 'flex'; };
  $('btn-fechar-modal').addEventListener('click', fechar);
  modal.addEventListener('click', (e) => { if (e.target === modal) fechar(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !modal.hasAttribute('hidden')) fechar(); });

  window._fecharModal = fechar;
  window._abrirModal = abrir;
}

async function gerarPDFUnico() {
  setStatus('Gerando PDF unitario (frente + verso)...', 10);
  const d = getDados();

  const wrap = document.createElement('div');
  wrap.style.cssText = 'position:absolute;left:-99999px;top:0;background:white;padding:20px;display:flex;gap:20px;';
  const frente = document.createElement('div');
  frente.style.cssText = 'width:280px;height:400px;background:white;';
  frente.innerHTML = aplicarAcessorios(TEMPLATES[state.modelo](d), d);
  frente.style.setProperty('--c1', $('cor-primaria').value);
  frente.style.setProperty('--c2', $('cor-secundaria').value);
  const verso = document.createElement('div');
  verso.style.cssText = 'width:280px;height:400px;background:white;';
  verso.innerHTML = TEMPLATES.verso(d);
  wrap.appendChild(frente);
  wrap.appendChild(verso);
  document.body.appendChild(wrap);

  try {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
    setStatus('Renderizando frente...', 30);
    const canvasF = await html2canvas(frente, { scale: 3, backgroundColor: '#ffffff', useCORS: true });
    setStatus('Renderizando verso...', 60);
    const canvasV = await html2canvas(verso, { scale: 3, backgroundColor: '#ffffff', useCORS: true });
    pdf.addImage(canvasF.toDataURL('image/jpeg', 0.95), 'JPEG', 15, 50, 70, 100);
    pdf.addImage(canvasV.toDataURL('image/jpeg', 0.95), 'JPEG', 125, 50, 70, 100);
    setStatus('Salvando PDF...', 90);
    pdf.save(`${$('f-arquivo').value || 'santinho'}_unico.pdf`);
    setStatus('PDF unitario gerado!');
  } catch (e) {
    console.error(e);
    setStatus('Erro: ' + e.message);
  } finally {
    wrap.remove();
    setTimeout(hideLoading, 300);
  }
}

async function gerarLote() {
  const qtd = parseInt($('f-quantidade').value) || 100;
  const copias = parseInt($('f-copias').value) || 9;
  const comVerso = $('f-verso').value === 'sim';
  const totalPaginas = Math.ceil(qtd / copias);

  setStatus(`Renderizando ${qtd} santinhos (${totalPaginas} paginas A4)...`, 0);

  const d = getDados();
  let frenteHTML = TEMPLATES[state.modelo](d);
  frenteHTML = aplicarAcessorios(frenteHTML, d);
  const versoHTML = TEMPLATES.verso(d);

  let cols, rows;
  if (copias === 9) { cols = 3; rows = 3; }
  else if (copias === 6) { cols = 3; rows = 2; }
  else if (copias === 8) { cols = 4; rows = 2; }
  else if (copias === 10) { cols = 5; rows = 2; }
  else { cols = 3; rows = 3; }

  // Criar um santinho ISOLADO para renderizar
  const renderCell = (html, isFront) => {
    const cell = document.createElement('div');
    cell.style.cssText = 'width:70mm;height:100mm;background:white;overflow:hidden;position:relative;';
    cell.innerHTML = html;
    if (isFront) {
      cell.style.setProperty('--c1', $('cor-primaria').value);
      cell.style.setProperty('--c2', $('cor-secundaria').value);
    }
    document.body.appendChild(cell);
    return cell;
  };

  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
  const pageW = 210, pageH = 297;
  const margin = 5, gap = 2;
  const cellW = (pageW - 2 * margin - (cols - 1) * gap) / cols;
  const cellH = (pageH - 2 * margin - (rows - 1) * gap) / rows;
  const xCoords = [], yCoords = [];
  for (let c = 0; c < cols; c++) xCoords.push(margin + c * (cellW + gap));
  for (let r = 0; r < rows; r++) yCoords.push(pageH - margin - cellH - r * (cellH + gap));

  let restante = qtd;
  let pagina = 0;
  let processed = 0;
  const totalTotal = comVerso ? qtd * 2 : qtd;
  while (restante > 0) {
    const naPagina = Math.min(copias, restante);
    for (let i = 0; i < naPagina; i++) {
      const col = i % cols;
      const row = Math.floor(i / cols);
      processed++;
      setStatus(`Renderizando frente ${processed}/${qtd}...`, (processed / totalTotal) * 100);
      const cell = renderCell(frenteHTML, true);
      await new Promise(r => requestAnimationFrame(r));
      const canvas = await html2canvas(cell, { scale: 3, backgroundColor: '#ffffff', useCORS: true, logging: false });
      const imgData = canvas.toDataURL('image/jpeg', 0.92);
      pdf.addImage(imgData, 'JPEG', xCoords[col], yCoords[row], cellW, cellH);
      cell.remove();
    }
    restante -= naPagina;
    pagina++;
    if (restante > 0) pdf.addPage();
  }

  if (comVerso) {
    let restanteV = qtd;
    while (restanteV > 0) {
      const naPagina = Math.min(copias, restanteV);
      for (let i = 0; i < naPagina; i++) {
        const col = i % cols;
        const row = Math.floor(i / cols);
        processed++;
        setStatus(`Renderizando verso ${processed - qtd}/${qtd}...`, (processed / totalTotal) * 100);
        const cell = renderCell(versoHTML, false);
        await new Promise(r => requestAnimationFrame(r));
        const canvas = await html2canvas(cell, { scale: 3, backgroundColor: '#ffffff', useCORS: true, logging: false });
        const imgData = canvas.toDataURL('image/jpeg', 0.92);
        pdf.addImage(imgData, 'JPEG', xCoords[col], yCoords[row], cellW, cellH);
        cell.remove();
      }
      restanteV -= naPagina;
      pdf.addPage();
    }
    pdf.deletePage(pdf.internal.getNumberOfPages());
  }

  setStatus(`Salvando PDF (${qtd} santinhos)...`, 100);
  pdf.save(`${$('f-arquivo').value || 'santinho'}_lote_${qtd}.pdf`);
  setStatus(`Lote OK! ${qtd} santinhos em ${pagina} paginas A4`);
  setTimeout(hideLoading, 500);
}

function salvarCandidato() {
  const d = getDados();
  if (!d.nome) { setStatus('Preencha o nome do candidato'); return; }
  const candidatos = JSON.parse(localStorage.getItem('tronix_santinhos_candidatos') || '[]');
  const id = Date.now();
  candidatos.push({ id, modelo: state.modelo, dados: d, cores: {
    c1: $('cor-primaria').value, c2: $('cor-secundaria').value,
    ct: $('cor-texto').value, cd: $('cor-destaque').value
  }, data: new Date().toISOString() });
  localStorage.setItem('tronix_santinhos_candidatos', JSON.stringify(candidatos));
  setStatus(`Candidato "${d.nome}" salvo! Total: ${candidatos.length}`);
}

function abrirCarregar() {
  const candidatos = JSON.parse(localStorage.getItem('tronix_santinhos_candidatos') || '[]');
  const lista = $('lista-candidatos');
  if (candidatos.length === 0) {
    lista.innerHTML = '<p style="color:var(--text-dim)">Nenhum candidato salvo ainda.</p>';
  } else {
    lista.innerHTML = candidatos.map(c => `
      <div class="candidato-item">
        <div>
          <strong>${escapeHtml(c.dados.nome)}</strong><br>
          <small>${escapeHtml(c.dados.cargo)} - ${escapeHtml(c.dados.numero)} - ${escapeHtml(c.dados.partido)}</small>
        </div>
        <div>
          <button class="btn primary" onclick="carregarCandidato(${c.id})">Carregar</button>
          <button class="btn ghost" onclick="excluirCandidato(${c.id})">X</button>
        </div>
      </div>
    `).join('');
  }
  $('modal-carregar').hidden = false;
  window._abrirModal();
}

window.carregarCandidato = (id) => {
  const candidatos = JSON.parse(localStorage.getItem('tronix_santinhos_candidatos') || '[]');
  const c = candidatos.find(x => x.id === id);
  if (!c) return;
  campos.forEach(campo => {
    const el = $(`f-${campo}`);
    if (el) el.value = c.dados[campo] || '';
  });
  if (c.cores) {
    $('cor-primaria').value = c.cores.c1;
    $('cor-secundaria').value = c.cores.c2;
    $('cor-texto').value = c.cores.ct;
    $('cor-destaque').value = c.cores.cd;
  }
  if (c.dados.foto) state.foto = c.dados.foto;
  document.querySelector(`[data-id="${c.modelo}"]`).click();
  window._fecharModal();
  setStatus(`Candidato "${c.dados.nome}" carregado`);
  render();
};

window.excluirCandidato = (id) => {
  let candidatos = JSON.parse(localStorage.getItem('tronix_santinhos_candidatos') || '[]');
  candidatos = candidatos.filter(x => x.id !== id);
  localStorage.setItem('tronix_santinhos_candidatos', JSON.stringify(candidatos));
  abrirCarregar();
  setStatus('Candidato removido');
};

function setStatus(msg, progress = null) {
  $('status-msg').textContent = msg;
  console.log('[Tronix]', msg);
  const overlay = $('loading-overlay');
  const msgEl = $('loading-msg');
  const fillEl = $('progress-fill');
  if (msg && progress !== null) {
    overlay.removeAttribute('hidden');
    msgEl.textContent = msg;
    fillEl.style.width = progress + '%';
  }
}

function hideLoading() {
  $('loading-overlay').setAttribute('hidden', '');
}

document.addEventListener('DOMContentLoaded', init);
