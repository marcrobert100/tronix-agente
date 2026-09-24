/* Tronix Santinho Generator - Templates Rendering */
const TEMPLATES = {
  classico: (d) => `
    <div class="santinho tpl-classico">
      <div class="faixa-top">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : '<span style="color:#aaa;font-size:10px">FOTO</span>'}</div>
      <div class="cargo">Candidato a</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
      <div class="cidade">${escapeHtml(d.cidade)}</div>
    </div>`,

  moderno_minimalista: (d) => `
    <div class="santinho tpl-moderno_minimalista">
      <div class="linha-top"></div>
      <div class="numero-tag">${escapeHtml(d.numero)}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cargo)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
      <div class="cidade">${escapeHtml(d.cidade)}</div>
    </div>`,

  premium_executivo: (d) => `
    <div class="santinho tpl-premium_executivo">
      <div class="linha-ouro"></div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cargo)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero-box">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
      <div class="linha-ouro"></div>
    </div>`,

  colorido_partidario: (d) => `
    <div class="santinho tpl-colorido_partidario">
      <div class="header">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  jovem_dinamico: (d) => `
    <div class="santinho tpl-jovem_dinamico">
      <span class="badge">${escapeHtml(d.cargo)}</span>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  tradicao_brasileiro: (d) => `
    <div class="santinho tpl-tradicao_brasileiro">
      <div class="faixa"></div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cargo)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero-box"><span class="numero">${escapeHtml(d.numero)}</span></div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  agro_forte: (d) => `
    <div class="santinho tpl-agro_forte">
      <div class="header">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  sindical_trabalhador: (d) => `
    <div class="santinho tpl-sindical_trabalhador">
      <div class="faixa-top">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="estrelas">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  empresarial_pro: (d) => `
    <div class="santinho tpl-empresarial_pro">
      <div class="header">
        <span class="partido-mini">${escapeHtml(d.partido)}</span>
        <span class="numero-mini">${escapeHtml(d.numero)}</span>
      </div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cargo)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="slogan">"${escapeHtml(d.slogan1 || '')}"</div>
    </div>`,

  fotografico_impacto: (d) => `
    <div class="santinho tpl-fotografico_impacto">
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : '<div style="background:#333;width:100%;height:100%"></div>'}</div>
      <div class="overlay">
        <div class="numero">${escapeHtml(d.numero)}</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
      </div>
    </div>`,

  minimalista_horizontal: (d) => `
    <div class="santinho tpl-minimalista_horizontal">
      <div class="linha-preta">
        <span class="partido-tipo">${escapeHtml(d.partido)}</span>
        <span class="numero-tipo">${escapeHtml(d.numero)}</span>
      </div>
      <div class="content">
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
        <div class="numero-grande">${escapeHtml(d.numero)}</div>
        <div class="cidade">${escapeHtml(d.cidade)}</div>
      </div>
    </div>`,

  cristao_familia: (d) => `
    <div class="santinho tpl-cristao_familia">
      <div class="topo">
        <div class="simbolo">&#10013;</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
      </div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="lema">"${escapeHtml(d.slogan1 || 'Deus, familia e trabalho')}"</div>
      <div class="numero-box"><span class="numero">${escapeHtml(d.numero)}</span></div>
    </div>`,

  tecnologico_inovador: (d) => `
    <div class="santinho tpl-tecnologico_inovador">
      <div class="content">
        <div class="linha-tech"></div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
        <div class="linha-tech"></div>
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
        <div class="numero">${escapeHtml(d.numero)}</div>
        <div class="partido">${escapeHtml(d.partido)}</div>
      </div>
    </div>`,

  esporte_juventude: (d) => `
    <div class="santinho tpl-esporte_juventude">
      <div class="header">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  diagonal_dinamico: (d) => `
    <div class="santinho tpl-diagonal_dinamico">
      <div class="content">
        <div class="partido">${escapeHtml(d.partido)}</div>
        <div class="numero">${escapeHtml(d.numero)}</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)} - ${escapeHtml(d.cidade)}</div>
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      </div>
    </div>`,

  retro_vintage: (d) => `
    <div class="santinho tpl-retro_vintage">
      <div class="content">
        <div class="top-bar">
          <span class="partido">${escapeHtml(d.partido)}</span>
          <span class="numero">${escapeHtml(d.numero)}</span>
        </div>
        <div class="estrelas">&#10038; &#10038; &#10038;</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
        <div class="numero-grande">${escapeHtml(d.numero)}</div>
        <div class="cidade">${escapeHtml(d.cidade)}</div>
      </div>
    </div>`,

  gradient_suave: (d) => `
    <div class="santinho tpl-gradient_suave">
      <div class="header-blur">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero-wrap"><span class="numero-pill">${escapeHtml(d.numero)}</span></div>
      <div class="partido">${escapeHtml(d.partido)}</div>
    </div>`,

  black_gold_luxo: (d) => `
    <div class="santinho tpl-black_gold_luxo">
      <div class="content">
        <div class="simbolo-topo">&#10070;</div>
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
        <div class="linha-ouro"></div>
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
        <div class="numero-box"><span class="numero">${escapeHtml(d.numero)}</span></div>
        <div class="partido">${escapeHtml(d.partido)}</div>
      </div>
    </div>`,

  tropical_verao: (d) => `
    <div class="santinho tpl-tropical_verao">
      <div class="header">${escapeHtml(d.cargo.toUpperCase())}</div>
      <div class="nome">${escapeHtml(d.nome)}</div>
      <div class="cargo">${escapeHtml(d.cidade)}</div>
      <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
      <div class="numero">${escapeHtml(d.numero)}</div>
      <div class="partido">${escapeHtml(d.partido)}</div>
      <div class="palmeira">&#127796;</div>
    </div>`,

  civico_municipal: (d) => `
    <div class="santinho tpl-civico_municipal">
      <div class="header">
        <div class="simbolo">&#10070;</div>
        <div class="titulo">${escapeHtml(d.cidade)}</div>
      </div>
      <div class="body">
        <div class="nome">${escapeHtml(d.nome)}</div>
        <div class="cargo">${escapeHtml(d.cargo)}</div>
        <div class="foto-area">${d.foto ? `<img src="${d.foto}">` : ''}</div>
        <div class="numero-box"><span class="numero">${escapeHtml(d.numero)}</span></div>
        <div class="partido">${escapeHtml(d.partido)}</div>
      </div>
      <div class="footer-strip">${escapeHtml(d.coligacao || 'UNIÃO PELA CIDADE')}</div>
    </div>`,

  verso: (d) => {
    const propostas = (d.propostas || '').split('\n').filter(p => p.trim()).slice(0, 6);
    return `
    <div class="santinho-verso">
      <div class="v-header">${escapeHtml(d.cargo.toUpperCase())} - ${escapeHtml(d.cidade)}</div>
      <div class="v-nome">${escapeHtml(d.nome)}</div>
      <div class="v-cargo">Numero ${escapeHtml(d.numero)} - ${escapeHtml(d.partido)}</div>
      <div class="v-section">Minhas Propostas</div>
      <ul class="v-propostas">
        ${propostas.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
      </ul>
      <div class="v-contato">
        ${d.whatsapp ? `WhatsApp: ${escapeHtml(d.whatsapp)}` : ''}
        ${d.instagram ? ` · ${escapeHtml(d.instagram)}` : ''}
        ${d.site ? ` · ${escapeHtml(d.site)}` : ''}
      </div>
      <div class="v-coligacao">${escapeHtml(d.coligacao || '')}</div>
      <div class="v-qr" id="qrcode-area"></div>
    </div>`;
  }
};

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* ============== ACESSORIOS (camada sobreposta) ============== */
const SIMBOLOS = {
  nenhum: '',
  cruz: '✝',
  estrela: '★',
  coracao: '♥',
  bandeira: '⚑',
  raio: '⚡',
  mao: '✋',
  familia: '👨‍👩‍👧',
  pomba: '🕊'
};

const MOLDURAS = {
  quadrada: '',
  redonda: 'acc-foto-redonda',
  losango: 'acc-foto-losango',
  hexagonal: 'acc-foto-hexagonal',
  escudo: 'acc-foto-escudo'
};

const ESTILOS_FOTO = {
  normal: '',
  pb: 'acc-foto-pb',
  sepia: 'acc-foto-sepia',
  duotone: 'acc-foto-duotone'
};

const BADGES = {
  nenhum: '',
  mulher: '♀ MULHER',
  jovem: '★ JOVEM',
  renovacao: '↻ RENOVAÇÃO',
  experiencia: '✓ EXPERIÊNCIA',
  educacao: '📚 EDUCAÇÃO',
  saude: '✚ SAÚDE',
  seguranca: '🛡 SEGURANÇA',
  agro: '🌱 AGRO',
  religioso: '✝ CRISTÃO',
  trabalhador: '⚒ TRABALHADOR',
  novo: '★ NOVO'
};

function aplicarAcessorios(frontHTML, d) {
  if (!d) return frontHTML;
  const acc = d.acessorios || {};
  const inj = [];

  if (acc.selo_je) {
    inj.push(`<div class="acc-selo-je">JUSTIÇA ELEITORAL</div>`);
  }
  if (acc.vice) {
    inj.push(`<div class="acc-vice">VICE: ${escapeHtml(acc.vice)}</div>`);
  }
  if (acc.badge && BADGES[acc.badge]) {
    inj.push(`<div class="acc-badge">${BADGES[acc.badge]}</div>`);
  }
  if (acc.simbolo && SIMBOLOS[acc.simbolo]) {
    inj.push(`<div class="acc-simbolo">${SIMBOLOS[acc.simbolo]}</div>`);
  }
  if (acc.proposta_destaque) {
    inj.push(`<div class="acc-proposta-destaque">★ ${escapeHtml(acc.proposta_destaque)}</div>`);
  }
  if (acc.zona_secao) {
    inj.push(`<div class="acc-zona-secao">ZONA ${escapeHtml(acc.zona_secao)}</div>`);
  }
  if (acc.faixa_cor) {
    inj.push(`<div class="acc-faixa-cor"></div>`);
  }

  let html = frontHTML;
  if (inj.length) {
    html = html.replace(/<div class="santinho([^"]*)">/, `<div class="santinho$1">${inj.join('')}`);
  }

  if (acc.moldura_foto && MOLDURAS[acc.moldura_foto]) {
    const cls = MOLDURAS[acc.moldura_foto];
    html = html.replace(/class="foto-area"/g, `class="foto-area ${cls}"`);
  }
  if (acc.estilo_foto && ESTILOS_FOTO[acc.estilo_foto]) {
    const cls = ESTILOS_FOTO[acc.estilo_foto];
    html = html.replace(/class="foto-area([^"]*)"/g, `class="foto-area$1 ${cls}"`);
  }

  return html;
}
