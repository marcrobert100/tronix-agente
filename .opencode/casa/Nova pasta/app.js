/**
 * DeliveryBot — Frontend v7
 * Marco Roberto — Reescrito do zero, sem patches
 */

// ── AUTH ──
let TK = sessionStorage.getItem("dbtk") || new URLSearchParams(location.search).get("token") || "";
if (TK) sessionStorage.setItem("dbtk", TK);

async function api(method, url, body) {
  const o = { method, headers: { "Content-Type":"application/json","x-token":TK } };
  if (body !== undefined) o.body = JSON.stringify(body);
  try {
    const r = await fetch(url, o);
    if (r.status === 401) { sessionStorage.removeItem("dbtk"); location.href="/"; return {ok:false}; }
    return r.json();
  } catch(e) { console.error("[api]",e); return {ok:false}; }
}

// ── BOOT ──
window.addEventListener("DOMContentLoaded", async () => {
  if (!TK) { location.href="/"; return; }
  const r = await api("GET","/api/auth/check");
  if (!r.ok) { sessionStorage.removeItem("dbtk"); location.href="/"; return; }
  initSocket();
  loadConfig();
  pollStatus();
});

// ── LOGOUT ──
document.getElementById("btn-logout").addEventListener("click", async () => {
  await api("POST","/api/logout");
  sessionStorage.removeItem("dbtk");
  if (socket) socket.disconnect();
  location.href="/";
});

// ── NAVEGAÇÃO ──
const NAV_TITLES = {
  dashboard:"Dashboard", whatsapp:"WhatsApp", pedidos:"Pedidos",
  cardapio:"Cardápio", fluxos:"Fluxos", ia:"IA / Groq", empresa:"Empresa",
  statuswa:"Status WhatsApp", promocoes:"Promoções", relatorios:"Relatórios",
  logs:"Logs", enviar:"Enviar Mensagem", aparencia:"🎨 Aparência", suporte:"Licença & Suporte"
};

document.querySelectorAll(".nb").forEach(b => {
  b.addEventListener("click", () => {
    const tab = b.dataset.tab;
    document.querySelectorAll(".nb").forEach(x => x.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    const sec = document.getElementById("tab-"+tab);
    if (sec) sec.classList.add("active");
    document.getElementById("tb-title").textContent = NAV_TITLES[tab] || tab;
    if (tab==="logs") loadLogs();
    if (["fluxos","ia","empresa"].includes(tab)) loadConfig();
    if (tab==="cardapio") { loadCardapio(); loadAcomps(); }
    if (tab==="statuswa") loadStatusWA();
    if (tab==="promocoes") loadPromocoes();
    if (tab==="relatorios") loadRelatorios();
    if (tab==="suporte") initSuporteLock();
    if (tab==="aparencia") loadSkinGrid();
    closeSB();
  });
});

document.getElementById("mtog").addEventListener("click", () => document.getElementById("sb").classList.toggle("open"));
function closeSB() { document.getElementById("sb").classList.remove("open"); }

// ── SOCKET ──
let socket = null;
let autoImprimir = true;
let _vias = 1;

function initSocket() {
  socket = io({ auth: { token: TK } });
  socket.on("connect_error", () => { sessionStorage.removeItem("dbtk"); location.href="/"; });

  socket.on("status", ({ conectado, mensagem }) => {
    setEl("sd","className","sd "+(conectado?"on":"off"));
    setEl("sbft","textContent",conectado?"Conectado":"Desconectado");
    setEl("wd","className","wd "+(conectado?"on":""));
    setEl("wtxt","textContent",conectado?"Conectado":"Desconectado");
    const b = document.getElementById("sb-banner");
    if (b) { b.className="sbanner "+(conectado?"on":""); document.getElementById("sb-txt").textContent=mensagem; }
  });

  socket.on("qr", d => {
    const ql=get("ql"), qi=get("qr-img");
    if (!d||d==="loading") { show(ql); hide(qi); }
    else { hide(ql); qi.src=d; show(qi); }
  });

  socket.on("msg", d => addFeed(d));
  socket.on("pedidos", ps => renderPedidos(ps));

  socket.on("novo_pedido", p => {
    // NÃO adicionar card aqui — o evento "pedidos" já faz isso via renderPedidos
    // Apenas: bip, flash e impressão
    bipAlto();
    setTimeout(() => flash(p.numero), 500);
    if (autoImprimir) mostrarPrint(p, true);
    else mostrarPrint(p, false);
  });

  socket.on("log", d => addLog(d, true));
  socket.on("licenca", d => updateLic(d));
  socket.on("cardapio_atualizado", () => { if (tabAtiva()==="cardapio") loadCardapio(); });
  socket.on("status_wa_config", d => { _statusWA = Array.isArray(d)?d:[]; if(tabAtiva()==="statuswa") renderStatusWA(); });
  socket.on("status_wa_publicado", d => addLogWA(`✅ Publicado às ${d.horario}: "${(d.item?.texto||"").slice(0,40)}"`));
  socket.on("pedindo_agora", d => atualizarPedindoAgora(d.total||0));
  // ── MELHORIA 5: Alerta de reclamação ──
  socket.on("alerta_reclamacao", d => {
    bipAlto();
    const feed = get("feed-d");
    if (feed) {
      const div = document.createElement("div");
      div.style.cssText = "padding:10px 12px;border-left:3px solid var(--rd);background:rgba(255,51,81,.08);border-radius:6px;margin-bottom:4px";
      div.innerHTML = `<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
        <span>⚠️</span>
        <span style="font-size:.76rem;font-weight:700;color:var(--rd)">RECLAMAÇÃO — ${esc(d.numero||"")}</span>
        <span style="font-size:.7rem;color:var(--mu);margin-left:auto">${new Date(d.ts).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}</span>
      </div>
      <div style="font-size:.78rem;color:var(--mu2);padding-left:22px">${esc(d.mensagem||"")}</div>`;
      feed.prepend(div);
    }
    // Toast visível em qualquer aba
    const t = document.createElement("div");
    t.style.cssText = "position:fixed;top:16px;right:16px;z-index:9999;background:var(--rd);color:#fff;padding:12px 18px;border-radius:10px;font-size:.86rem;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,.4);animation:up .3s ease";
    t.innerHTML = `⚠️ Reclamação de ${esc(d.numero||"")}`;
    document.body.appendChild(t);
    setTimeout(()=>t.remove(), 6000);
  });

  socket.on("avaliacao", d => {
    const e2 = "⭐".repeat(d.nota||0);
    addFeed({ numero:d.numero, mensagem:`${e2} Avaliação: ${d.nota}/5`, tipo:"entrada" });
  });
  socket.on("loja_status", d => {
    const badge=get("loja-badge"), btn=get("btn-loja");
    if (!badge||!btn) return;
    if (d.fechado){ badge.textContent="FECHADA"; badge.className="abadge off"; btn.textContent="🔓 Abrir loja"; btn.className="btn btg btsm btn-w"; }
    else { badge.textContent="ABERTA"; badge.className="abadge on"; btn.textContent="🔒 Fechar loja"; btn.className="btn btd btsm btn-w"; }
  });

  socket.on("auto_imprimir", d => {
    autoImprimir = d.ativo;
    const t = get("tog-print"); if(t) t.checked=d.ativo;
  });
  socket.on("vias_impressao", d => {
    _vias = d.vias||1;
    document.querySelectorAll(".via-btn").forEach(b=>b.classList.toggle("active-via",parseInt(b.dataset.via)===_vias));
  });
  socket.on("agente_status", d => {
    const btn=get("btn-agente"), badge=get("agente-badge");
    if (btn) { btn.textContent=d.ativo?"⏸️ Pausar":"▶️ Retomar"; btn.className="btn "+(d.ativo?"btd":"btg")+" btsm btn-w"; }
    if (badge) { badge.textContent=d.ativo?"ATIVO":"PAUSADO"; badge.className="abadge "+(d.ativo?"on":"off"); }
  });

  // ── ATENDIMENTO HUMANO — sockets dentro do initSocket ──
  socket.on("atend_humano_status", d => {
    const tog=get("tog-atend"); if(tog)tog.checked=!!d.ativo;
    atualizarBadgeAtend(!!d.ativo);
    const nbd=get("nbd-atend"); if(nbd)nbd.style.display=d.total>0?"inline":"none";
  });

  socket.on("novo_atendimento", d => {
    const nbd=get("nbd-atend");
    if(nbd){ nbd.textContent="!"; nbd.style.display="inline"; }
    bipAlto();
    if(typeof loadAtendLista==="function") loadAtendLista();
    // Abrir automaticamente o chat se estiver na aba atendimento
    if(tabAtiva()==="atendimento") {
      if(typeof abrirChat==="function") abrirChat(d.numero);
    }
    // Toast vermelho em qualquer aba
    const t=document.createElement("div");
    t.style.cssText="position:fixed;top:16px;right:16px;z-index:9999;background:var(--rd);color:#fff;padding:14px 20px;border-radius:12px;font-size:.9rem;font-weight:700;box-shadow:0 8px 24px rgba(0,0,0,.5);cursor:pointer";
    t.innerHTML="👤 " + esc(d.numero) + " quer atendente!<br><small style='font-weight:400;opacity:.85'>Clique para abrir o chat</small>";
    t.onclick=()=>{ document.querySelector('[data-tab="atendimento"]')?.click(); t.remove(); };
    document.body.appendChild(t);
    setTimeout(()=>t.remove(), 10000);
  });

  socket.on("atendimento_msg", d => {
    if(_atendNumeroAtivo===d.numero) renderMsgsAtend(d.numero);
    if(typeof loadAtendLista==="function") loadAtendLista();
  });

  socket.on("atendimento_encerrado", d => {
    if(_atendNumeroAtivo===d.numero){
      _atendNumeroAtivo=null;
      const box=get("atend-chat-box"); if(box) box.style.display="none";
    }
    if(typeof loadAtendLista==="function") loadAtendLista();
  });
}

// ── HELPERS DOM ──
function get(id) { return document.getElementById(id); }
function setEl(id,p,v) { const e=get(id); if(e) e[p]=v; }
function show(e) { if(e) e.style.display=""; }
function hide(e) { if(e) e.style.display="none"; }
function tabAtiva() { const a=document.querySelector(".tab.active"); return a?.id?.replace("tab-",""); }
function esc(s) { return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
function fmtT(ts) { return new Date(ts).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}); }
function fmtFull(ts) { if(!ts)return"—"; return new Date(ts).toLocaleString("pt-BR",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"}); }
function upStr(s) { if(s<60)return s+"s"; if(s<3600)return Math.floor(s/60)+"m"; return Math.floor(s/3600)+"h"+Math.floor((s%3600)/60)+"m"; }
function toast(id,msg,ok) {
  const e=get(id); if(!e)return;
  e.textContent=msg; e.className="toast "+(ok?"ok":"er");
  clearTimeout(e._t); e._t=setTimeout(()=>e.className="toast",4000);
}

// ── BIP ──
function bipAlto() {
  try {
    const play=()=>{
      const ctx=new(window.AudioContext||window.webkitAudioContext)();
      const n=(f,t,d)=>{const o=ctx.createOscillator(),g=ctx.createGain();o.type="square";o.connect(g);g.connect(ctx.destination);o.frequency.value=f;g.gain.setValueAtTime(0,ctx.currentTime+t);g.gain.linearRampToValueAtTime(1,ctx.currentTime+t+.01);g.gain.linearRampToValueAtTime(0,ctx.currentTime+t+d-.02);o.start(ctx.currentTime+t);o.stop(ctx.currentTime+t+d);};
      n(1046,.00,.15);n(1318,.17,.15);n(1568,.34,.22);
    };
    play();setTimeout(play,700);setTimeout(play,1400);
  } catch(_){}
}

// ── PISCAR CARD 10S ──
function flash(numero) {
  const num=(numero||"").replace(/[^a-zA-Z0-9]/g,"_");
  document.querySelectorAll(`[id^="pc-"]`).forEach(e=>{
    if(e.id.includes(num.slice(0,10))){ e.classList.add("flash"); setTimeout(()=>e.classList.remove("flash"),10000); }
  });
  const nb=document.querySelector('[data-tab="pedidos"]');
  if(nb){const orig=nb.style.background;nb.style.background="var(--rd)";setTimeout(()=>nb.style.background=orig,10000);}
}

// ── FEED ──
const _feed=[];
function addFeed(d){
  d._ts = Date.now();
  _feed.unshift(d); if(_feed.length>60)_feed.pop();
  const f=get("feed-d"); if(!f)return;
  f.innerHTML=_feed.slice(0,30).map(m=>{
    const icone = m.tipo==="saida" ? "🤖" : m.tipo==="avaliacao" ? "⭐" : "👤";
    const cor   = m.tipo==="saida"
      ? "border-left:3px solid var(--ac)"
      : m.tipo==="avaliacao"
        ? "border-left:3px solid var(--am)"
        : "border-left:3px solid var(--bl)";
    const num = (m.numero||"").replace("@c.us","").replace(/(\d{2})(\d{2})(\d{4,5})(\d{4})/,"$1 $2 $3-$4");
    const hora = m._ts ? new Date(m._ts).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}) : "";
    return `<div class="fi ${m.tipo}" style="padding:8px 10px;${cor};margin-bottom:4px;border-radius:6px">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
        <span style="font-size:.9rem">${icone}</span>
        <span style="font-size:.76rem;font-weight:600;color:var(--tx)">${esc(num||"—")}</span>
        <span style="font-size:.7rem;color:var(--mu);margin-left:auto">${hora}</span>
      </div>
      <div class="fm" style="font-size:.78rem;color:var(--mu2);padding-left:22px">${esc((m.mensagem||"").slice(0,120))}</div>
    </div>`;
  }).join("");
}

// ── PEDIDOS ──
function mkCardPedido(p) {
    const num=(p.numero||"").replace("@c.us","");
    const pid="pc-"+num.replace(/[^a-z0-9]/gi,"_");
    const maps=p.mapsUrl?`<a href="${p.mapsUrl}" target="_blank" class="btn btb btsm" style="margin-bottom:3px">🗺️ Mapa</a>`:"";
    const comp=p.complemento?`<div>🏠 ${esc(p.complemento)}</div>`:"";
    const ref=p.referencia?`<div>📌 ${esc(p.referencia)}</div>`:"";
    const tel=p.telefone?`<div>📞 ${esc(p.telefone)}</div>`:"";
    const troco=p.troco?`<div>💰 Troco R$${esc(p.troco)}</div>`:"";
    const obs=p.observacao?`<div>📝 ${esc(p.observacao)}</div>`:"";
    const end=p.mapsUrl?`📍 <span style="color:var(--bl)">GPS</span>`:`📍 ${esc(p.endereco||"—")}`;
    const pj=JSON.stringify(p).replace(/"/g,"&quot;");
    return `<div class="pc" id="${pid}"><span class="pc-tag">NOVO</span>
      <div class="pm">
        <div class="pnum">#${esc(p.numPedido||"—")}</div>
        <div class="pn">📱 ${num}</div>
        <div class="pt">🕐 ${fmtFull(p.confirmado||p.inicio)}</div>
        <div class="pa">${maps}<button class="btn btd btsm" onclick='doPrint(JSON.parse(this.dataset.p))' data-p="${pj}">🖨️</button><button class="btn btg btsm" onclick="entregar('${esc(p.numero)}')">✅ Entregue</button></div>
      </div>
      <div class="pb"><div class="pi">🛒 ${esc(p.itens||"—")}</div><div class="pd">${end}${comp}${ref}${tel}${obs}${troco}<div>💳 ${esc(p.pagamento||"—")}</div></div></div>
    </div>`;
}

function renderPedidos(ps) {
  const nbd=get("nbd");
  nbd.textContent=ps.length; nbd.className="nbd"+(ps.length>0?" show":"");
  setEl("sv-p","textContent",ps.length);

  const mk = p => mkCardPedido(p);

  const html=ps.length?ps.map(mk).join(""):'<div class="fe">Nenhum pedido em aberto.</div>';
  setEl("lista-ped","innerHTML",html);
  const dp=get("dash-p");
  if(dp)dp.innerHTML=ps.length?ps.slice(0,3).map(mk).join(""):'<div class="fe">Nenhum pedido.</div>';
}
window.entregar=async num=>{ await api("POST",`/api/pedidos/${encodeURIComponent(num)}/entregar`); };

// Controles pedidos
get("tog-print").addEventListener("change",function(){ api("POST","/api/auto-imprimir",{ativo:this.checked}); autoImprimir=this.checked; });
document.querySelectorAll(".via-btn").forEach(b=>b.addEventListener("click",function(){
  _vias=parseInt(this.dataset.via);
  api("POST","/api/vias-impressao",{vias:_vias});
  document.querySelectorAll(".via-btn").forEach(x=>x.classList.remove("active-via"));
  this.classList.add("active-via");
}));
get("btn-agente").addEventListener("click",async function(){
  const fechar=this.textContent.includes("Pausar");
  await api("POST","/api/agente/fechar",{fechar});
});

// ── LOJA FECHADA ──
async function loadLojaStatus() {
  const r = await api("GET","/api/loja/status");
  if (!r) return;
  const badge=get("loja-badge"), btn=get("btn-loja");
  if (!badge||!btn) return;
  if (r.fechado) {
    badge.textContent="FECHADA"; badge.className="abadge off";
    btn.textContent="🔓 Abrir loja"; btn.className="btn btg btsm btn-w";
  } else {
    badge.textContent="ABERTA"; badge.className="abadge on";
    btn.textContent="🔒 Fechar loja"; btn.className="btn btd btsm btn-w";
  }
}
get("btn-loja")?.addEventListener("click", async () => {
  const r = await api("GET","/api/loja/status");
  const novoFechado = !r?.fechado;
  let msgCustom = null;
  if (novoFechado) msgCustom = prompt("Mensagem personalizada (Enter para padrão):");
  const res = await api("POST","/api/loja/fechar",{ fechado:novoFechado, msgCustom });
  if (res?.ok) loadLojaStatus();
});

// ── IMPRESSÃO ──
let _printData=null,_printTimer=null;

function mostrarPrint(p,auto){
  _printData=p;
  const num=(p.numero||"").replace("@c.us","");
  get("pr-np").textContent="#"+(p.numPedido||"—");
  get("pr-n").textContent=num;
  get("pr-i").textContent=p.itens||"—";
  get("pr-p").textContent=p.pagamento||"—";
  get("pr-h").textContent=fmtT(p.confirmado||Date.now());
  get("pr-e").textContent=p.mapsUrl?"📍 Pin GPS":(p.endereco||"—");
  const cr=get("pr-comp-row"); if(p.complemento){get("pr-c").textContent=p.complemento;cr.style.display="flex";}else cr.style.display="none";
  const tr=get("pr-tel-row"); if(p.telefone){get("pr-tel").textContent=p.telefone;tr.style.display="flex";}else tr.style.display="none";
  const mr=get("pr-maps-row"),ml=get("pr-m"); if(p.mapsUrl){ml.href=p.mapsUrl;mr.style.display="flex";}else mr.style.display="none";
  const trocor=get("pr-troco-row"); if(p.troco){get("pr-troco").textContent="R$ "+p.troco;trocor.style.display="flex";}else trocor.style.display="none";
  get("pov").classList.add("show");
  clearInterval(_printTimer);
  if(auto){
    let c=3; const el=get("pcount"); el.textContent=c; el.className="pcount";
    _printTimer=setInterval(()=>{c--;el.textContent=c;if(c<=0){el.className="pcount go";clearInterval(_printTimer);setTimeout(()=>doPrint(p),200);}},1000);
  } else { get("pcount").textContent="—"; }
}

get("btn-imp").addEventListener("click",()=>{clearInterval(_printTimer);doPrint(_printData);});
get("btn-fch").addEventListener("click",()=>{clearInterval(_printTimer);get("pov").classList.remove("show");});

function doPrint(p){
  get("pov").classList.remove("show");
  const empresa=get("e-nome")?.value||"Delivery";
  const num=(p.numero||"").replace("@c.us","");
  const hora=fmtT(p.confirmado||Date.now());
  const end=p.mapsUrl?"PIN GPS":(p.endereco||"—");
  const comp=p.complemento?`<div class="r"><span class="l">🏠</span><span class="v">${esc(p.complemento)}</span></div>`:"";
  const tel=p.telefone?`<div class="r"><span class="l">📞</span><span class="v">${esc(p.telefone)}</span></div>`:"";
  const maps=p.mapsUrl?`<div class="r"><span class="l">🗺️</span><span class="v" style="color:#1155cc;font-size:10px;word-break:break-all">${p.mapsUrl}</span></div>`:"";
  const troco=p.troco?`<div class="r"><span class="l">💰 Troco</span><span class="v">R$ ${esc(p.troco)}</span></div>`:"";

  const via=n=>`<div style="${n>1?"page-break-before:always;padding-top:7px;border-top:2px dashed #333;":""}">
    <h1>🛵 ${esc(empresa)}</h1>
    <div class="s">PEDIDO #<strong>${p.numPedido||"—"}</strong> • ${hora} • VIA ${n}/${_vias}</div>
    <div class="r"><span class="l">📱</span><span class="v">${esc(num)}</span></div>
    <div class="r"><span class="l">🛒</span><span class="v">${esc(p.itens||"—")}</span></div>
    <div class="r"><span class="l">📍</span><span class="v">${esc(end)}</span></div>
    ${comp}${tel}${maps}
    <div class="r"><span class="l">💳</span><span class="v">${esc(p.pagamento||"—")}</span></div>
    ${troco}
    <div class="f">DeliveryBot — Marco Roberto</div>
  </div>`;

  const html=`<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;font-size:13px;padding:9px;width:300px;color:#111}h1{font-size:14px;font-weight:bold;text-align:center;border-bottom:2px solid #111;padding-bottom:5px;margin-bottom:4px}.s{text-align:center;font-size:11px;color:#555;margin-bottom:9px}.r{display:flex;justify-content:space-between;gap:7px;padding:4px 0;border-bottom:1px dashed #ccc;align-items:flex-start}.r:last-child{border:none}.l{color:#555;font-size:11px;flex-shrink:0;min-width:62px}.v{font-weight:bold;font-size:12px;text-align:right;word-break:break-word}.f{margin-top:9px;text-align:center;font-size:10px;color:#888;border-top:1px dashed #ccc;padding-top:6px}@media print{@page{size:80mm auto;margin:0}body{padding:3px;width:80mm}}</style></head><body>${Array.from({length:_vias},(_,i)=>via(i+1)).join("")}</body></html>`;

  const w=window.open("","_blank","width=360,height=580,left=80,top=40");
  if(w){w.document.write(html);w.document.close();w.focus();setTimeout(()=>{w.print();w.close();},600);}
}

// ── POLL STATUS ──
function atualizarPedindoAgora(n) {
  const el  = document.getElementById("sv-pa");
  const dot = document.getElementById("sv-pa-pulse");
  if (el) {
    el.textContent = n;
    el.style.color = n > 0 ? "var(--ac)" : "var(--mu)";
  }
  if (dot) dot.style.display = n > 0 ? "block" : "none";
}

async function pollStatus(){
  try{
    const d=await api("GET","/api/status");
    if(!d||!d.conectado&&d.conectado!==false)return;
    setEl("sv-m","textContent",d.mensagens||0);
    setEl("sv-s","textContent",d.sessoes||0);
    setEl("sv-u","textContent",upStr(d.uptime||0));
    atualizarPedindoAgora(d.pedindoAgora||0);
    if(d.licenca) updateLic(d.licenca);
    autoImprimir=d.autoImprimir??true;
    _vias=d.viasImpressao||1;
    const tp=get("tog-print"); if(tp)tp.checked=autoImprimir;
    document.querySelectorAll(".via-btn").forEach(b=>b.classList.toggle("active-via",parseInt(b.dataset.via)===_vias));
    const gs=get("groq-status");
    if(gs){gs.textContent=d.groqConfigurada?"✅ Chave Groq configurada e ativa":"⚠️ Chave Groq não configurada";gs.style.color=d.groqConfigurada?"var(--gr)":"var(--am)";}
  }catch(_){}
  setTimeout(pollStatus,15000);
}

// ── WA BOTÕES ──
get("btn-qr").addEventListener("click",()=>api("POST","/api/wa/restart"));
get("btn-limpar").addEventListener("click",()=>{if(confirm("Limpar sessão e gerar novo QR?"))api("POST","/api/wa/restart?limpar=1");});
get("btn-desc").addEventListener("click",()=>{if(confirm("Desconectar WhatsApp?"))api("POST","/api/wa/disconnect");});

// ── CONFIG ──
async function loadConfig(){
  const c=await api("GET","/api/config"); if(!c)return;
  const ef=get("ed-flx"); if(ef)ef.value=JSON.stringify(c.fluxos||[],null,2);
  const ti=get("tog-ia"); if(ti)ti.checked=!!c.useAI;
  const ep=get("ed-prompt"); if(ep)ep.value=c.promptSistema||"";
  const sm=get("sel-mdl"); if(sm)sm.value=c.model||"llama-3.1-8b-instant";
  const MAP={"e-nome":"empresaNome","e-end":"empresaEndereco","e-tel":"empresaTelefone","e-taxa":"taxaEntrega","e-tempo":"tempoEntrega","e-min":"pedidoMinimo","e-pag":"pagamentos","e-pix":"pixChave"};
  for(const[id,k]of Object.entries(MAP)){const e=get(id);if(e)e.value=c[k]||"";}
  // Renderizar grade de horários
  renderGradeHorario(c.horarios || horariosDoTexto(c.horarioFuncionamento||""));
}

// Salvar chave Groq
get("btn-sv-key").addEventListener("click",async()=>{
  const key=get("inp-key").value.trim();
  if(!key){toast("t-key","❌ Digite a chave antes de salvar.",false);return;}
  if(!key.startsWith("gsk_")){toast("t-key","❌ Chave inválida — deve começar com gsk_",false);return;}
  const r=await api("POST","/api/groq-key",{key});
  if(r.ok){toast("t-key","✅ Chave salva com sucesso!",true);get("inp-key").value="";get("groq-status").textContent="✅ Chave Groq configurada";get("groq-status").style.color="var(--gr)";}
  else toast("t-key","❌ "+(r.erro||"Erro."),false);
});

get("btn-sv-ia").addEventListener("click",async()=>{
  const r=await api("POST","/api/config",{useAI:get("tog-ia").checked,model:get("sel-mdl").value});
  toast("t-ia",r.ok?"✅ Salvo!":"❌ Erro.",r.ok);
});
get("btn-sv-prompt").addEventListener("click",async()=>{
  const r=await api("POST","/api/config",{promptSistema:get("ed-prompt").value,model:get("sel-mdl").value});
  toast("t-prompt",r.ok?"✅ Prompt salvo!":"❌ Erro.",r.ok);
});
get("btn-sv-flx").addEventListener("click",async()=>{
  try{const v=JSON.parse(get("ed-flx").value);const r=await api("POST","/api/config",{fluxos:v});toast("t-flx",r.ok?"✅ Fluxos salvos!":"❌ Erro.",r.ok);}
  catch(_){toast("t-flx","❌ JSON inválido.",false);}
});
// ── GRADE DE HORÁRIOS ──
const DIAS_LABEL = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"];
const DIAS_IDX   = [0,1,2,3,4,5,6];

// Converter texto "Seg a Sex: 11h às 23h | Sab e Dom: 11h às 00h" → array horarios
function horariosDoTexto(txt) {
  if (!txt) return defaultHorarios();
  const diasMap = {dom:0,seg:1,ter:2,qua:3,qui:4,sex:5,sab:6,sáb:6};
  const segs = txt.toLowerCase().split(/[|;]/);
  const result = [];
  for (const seg of segs) {
    const horMatch = seg.match(/(\d{1,2})(?:h|:00)?\s*(?:às|as|-)\s*(\d{1,2})(?:h|:00)?/);
    if (!horMatch) continue;
    const abre  = String(parseInt(horMatch[1])).padStart(2,"0")+":00";
    const hFech = parseInt(horMatch[2]);
    const fecha = hFech===0?"00:00":String(hFech).padStart(2,"0")+":00";
    const diasSeg = new Set();
    const rangeM = seg.match(/([a-záàâãéêíóôõúç]+)\s+a\s+([a-záàâãéêíóôõúç]+)/);
    if (rangeM) {
      const d1=diasMap[rangeM[1].trim()],d2=diasMap[rangeM[2].trim()];
      if(d1!==undefined&&d2!==undefined){
        if(d2>=d1){for(let i=d1;i<=d2;i++)diasSeg.add(i);}
        else{for(let i=d1;i<7;i++)diasSeg.add(i);for(let i=0;i<=d2;i++)diasSeg.add(i);}
      }
    }
    for(const[k,v] of Object.entries(diasMap)){if(seg.includes(k))diasSeg.add(v);}
    if(diasSeg.size>0) result.push({dias:[...diasSeg].sort(),abre,fecha,ativo:true});
  }
  return result.length ? result : defaultHorarios();
}

function defaultHorarios() {
  return [
    { dias:[1,2,3,4,5], abre:"11:00", fecha:"23:00", ativo:true },
    { dias:[6,0],        abre:"11:00", fecha:"00:00", ativo:true }
  ];
}

// Converter array horarios → texto legível
function horariosParaTexto(horarios) {
  return horarios.filter(h=>h.ativo&&h.dias&&h.dias.length).map(h => {
    // Remover dias duplicados e ordenar
    const diasUnicos = [...new Set(h.dias)].sort((a,b)=>a-b);
    const dias = diasUnicos.map(d=>DIAS_LABEL[d]).join(", ");
    // Formatar hora (04:00 → 04h, 11:00 → 11h, 11:30 → 11:30h)
    const fmtHora = t => {
      if (!t) return "?";
      const [hh, mm] = t.split(":");
      return mm && mm !== "00" ? `${hh}:${mm}h` : `${hh}h`;
    };
    return `${dias}: ${fmtHora(h.abre)} às ${fmtHora(h.fecha)}`;
  }).join(" | ");
}

let _horarios = defaultHorarios();

function renderGradeHorario(horarios) {
  _horarios = horarios && horarios.length ? JSON.parse(JSON.stringify(horarios)) : defaultHorarios();
  const el = get("grade-horario");
  if (!el) return;
  el.innerHTML = _horarios.map((h,i) => {
    const diasBtns = DIAS_IDX.map(d => {
      const ativo = h.dias.includes(d);
      return `<button type="button" onclick="toggleDia(${i},${d})" id="dia-${i}-${d}"
        style="width:36px;height:36px;border-radius:50%;font-size:.74rem;font-weight:700;cursor:pointer;
        border:2px solid ${ativo?"var(--ac)":"var(--brd)"};
        background:${ativo?"var(--ac)":"var(--bg3)"};
        color:${ativo?"#fff":"var(--mu)"};transition:all .15s">${DIAS_LABEL[d]}</button>`;
    }).join("");
    return `<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px;background:var(--bg3);border-radius:9px;border:1px solid var(--brd)">
      <label class="tog" title="Ativar/desativar este horário">
        <input type="checkbox" ${h.ativo?"checked":""} onchange="_horarios[${i}].ativo=this.checked;atualizarHorTexto()"/>
        <span class="tsl"></span>
      </label>
      <div style="display:flex;gap:4px;flex-wrap:wrap">${diasBtns}</div>
      <div style="display:flex;align-items:center;gap:6px;margin-left:auto">
        <span style="font-size:.78rem;color:var(--mu)">Abre:</span>
        <input type="time" value="${h.abre||"11:00"}" class="inp" style="width:100px;padding:4px 8px;font-size:.84rem"
          onchange="_horarios[${i}].abre=this.value;atualizarHorTexto()"/>
        <span style="font-size:.78rem;color:var(--mu)">Fecha:</span>
        <input type="time" value="${h.fecha==="00:00"?"00:00":h.fecha||"23:00"}" class="inp" style="width:100px;padding:4px 8px;font-size:.84rem"
          onchange="_horarios[${i}].fecha=this.value;atualizarHorTexto()"/>
        <button type="button" onclick="removerHorario(${i})" title="Remover"
          style="background:none;border:none;cursor:pointer;color:var(--rd);font-size:1.1rem;padding:2px 6px">🗑️</button>
      </div>
    </div>`;
  }).join("") + `
  <button type="button" onclick="adicionarHorario()"
    style="padding:8px 16px;border-radius:8px;border:2px dashed var(--brd);background:none;color:var(--mu);cursor:pointer;font-size:.82rem;width:100%;transition:all .15s"
    onmouseover="this.style.borderColor='var(--ac)';this.style.color='var(--ac)'"
    onmouseout="this.style.borderColor='var(--brd)';this.style.color='var(--mu)'">
    ➕ Adicionar outro horário
  </button>`;
  atualizarHorTexto();
}

window.toggleDia = function(hIdx, dia) {
  const h = _horarios[hIdx];
  if (!h) return;
  // Garantir sem duplicatas
  h.dias = [...new Set(h.dias)];
  const pos = h.dias.indexOf(dia);
  if (pos >= 0) h.dias.splice(pos,1); else h.dias.push(dia);
  h.dias = [...new Set(h.dias)].sort((a,b)=>a-b);
  const btn = get(`dia-${hIdx}-${dia}`);
  if (btn) {
    const ativo = h.dias.includes(dia);
    btn.style.background  = ativo?"var(--ac)":"var(--bg3)";
    btn.style.borderColor = ativo?"var(--ac)":"var(--brd)";
    btn.style.color       = ativo?"#fff":"var(--mu)";
  }
  atualizarHorTexto();
};

window.removerHorario = function(i) {
  _horarios.splice(i,1);
  renderGradeHorario(_horarios);
};

window.adicionarHorario = function() {
  // Descobrir quais dias ainda não estão cobertos
  const diasUsados = new Set(_horarios.flatMap(h=>h.dias));
  const diasLivres = DIAS_IDX.filter(d=>!diasUsados.has(d));
  _horarios.push({ dias: diasLivres.length ? diasLivres : [], abre:"11:00", fecha:"23:00", ativo:true });
  renderGradeHorario(_horarios);
};

function atualizarHorTexto() {
  const txt = horariosParaTexto(_horarios);
  const inp = get("e-hor");
  if (inp) inp.value = txt;
}

get("btn-sv-emp").addEventListener("click",async()=>{
  atualizarHorTexto();
  const r=await api("POST","/api/config",{
    empresaNome:get("e-nome").value,
    empresaEndereco:get("e-end").value,
    empresaTelefone:get("e-tel").value,
    horarioFuncionamento:get("e-hor").value,
    horarios: _horarios,
    taxaEntrega:get("e-taxa").value,
    tempoEntrega:get("e-tempo").value,
    pedidoMinimo:get("e-min").value,
    pagamentos:get("e-pag").value,
    pixChave:get("e-pix").value
  });
  toast("t-emp",r.ok?"✅ Horários salvos!":"❌ Erro.",r.ok);
});

// ── CARDÁPIO ──
let _card=[];

// ── CLIENTES ──
async function loadClientes() {
  const lista = await api("GET","/api/clientes");
  const el = get("clientes-lista");
  if (!el) return;
  if (!lista||!lista.length) { el.innerHTML='<div class="fe">Nenhum cliente ainda.</div>'; return; }
  el.innerHTML = lista.map(cli => {
    const ult = cli.ultimoPedido||{};
    const data = ult.data ? new Date(ult.data).toLocaleDateString("pt-BR") : "—";
    const aval = cli.ultimaAvaliacao ? "⭐".repeat(cli.ultimaAvaliacao) : "—";
    return `<div class="pc" style="margin-bottom:8px">
      <div class="pm">
        <div class="pnum">📱 ${esc(cli.numero||"")}</div>
        <div class="pt">📦 ${cli.totalPedidos||1} pedido(s) · Último: ${data} ${aval}</div>
      </div>
      <div class="pb"><div class="pi">🛒 ${esc(ult.itens||"—")}</div>
      <div class="pd"><div>💳 ${esc(ult.pagamento||"—")}</div><div>📍 ${esc(ult.endereco||"—")}</div></div></div>
    </div>`;
  }).join("");
}

// ── ACOMPANHAMENTOS ──
let _acomps = [];

async function loadAcomps() {
  const cfg = await api("GET","/api/config");
  _acomps = Array.isArray(cfg?.acompanhamentos) ? [...cfg.acompanhamentos] : [];
  renderAcomps();
}

function renderAcomps() {
  const el = document.getElementById("acomp-lista");
  if (!el) return;
  if (!_acomps.length) {
    el.innerHTML = '<div class="fe" style="font-size:.8rem">Nenhum acompanhamento cadastrado.</div>';
    return;
  }
  el.innerHTML = _acomps.map((a, i) =>
    `<div style="display:flex;align-items:center;gap:5px;background:var(--bg3);border:1px solid var(--brd);border-radius:20px;padding:5px 12px;font-size:.82rem">
      <span>${esc(a)}</span>
      <button onclick="removerAcomp(${i})" style="background:none;border:none;cursor:pointer;color:var(--rd);font-size:.9rem;padding:0 0 0 4px">❌</button>
    </div>`
  ).join("");
}

window.removerAcomp = function(i) {
  _acomps.splice(i, 1);
  renderAcomps();
};

document.getElementById("btn-add-acomp")?.addEventListener("click", () => {
  const inp = document.getElementById("acomp-novo");
  const val = (inp?.value || "").trim();
  if (!val) return;
  // Suporta múltiplos separados por vírgula
  const novos = val.split(",").map(v => v.trim()).filter(v => v && !_acomps.includes(v));
  _acomps.push(...novos);
  renderAcomps();
  if (inp) inp.value = "";
});

document.getElementById("acomp-novo")?.addEventListener("keydown", e => {
  if (e.key === "Enter") document.getElementById("btn-add-acomp")?.click();
});

document.getElementById("btn-sv-acomp")?.addEventListener("click", async () => {
  const r = await api("POST", "/api/config", { acompanhamentos: _acomps });
  toast("t-acomp", r?.ok ? `✅ ${_acomps.length} acompanhamento(s) salvo(s)!` : "❌ Erro ao salvar.", !!r?.ok);
});

async function loadCardapio(){
  const c=await api("GET","/api/config"); if(!c)return;
  _card=c.cardapio||[];
  renderCard();
  // Carregar regra meio a meio
  const mam = await api("GET","/api/meio-a-meio");
  if (mam && mam.rule) {
    const r = document.getElementById("rule-"+mam.rule);
    if (r) r.checked = true;
    // Highlight label ativo
    document.querySelectorAll("#label-maior,#label-media").forEach(l => {
      l.style.borderColor = l.id === "label-"+mam.rule ? "var(--ac)" : "var(--brd)";
    });
  }
  // Atualizar select do modal
  const sel=get("mi-cat"); if(sel)sel.innerHTML=_card.map(c=>`<option value="${esc(c.categoria)}">${esc(c.categoria)}</option>`).join("");
}

function renderCard(){
  const w=get("cardapio-admin"); if(!w)return;
  if(!_card.length){w.innerHTML='<div class="fe">Nenhum grupo. Clique em <strong>➕ Grupo</strong>.</div>';return;}
  const ativos=_card.flatMap(c=>(c.itens||[]).filter(i=>!i.pausado)).length;
  const paus=_card.flatMap(c=>(c.itens||[]).filter(i=>i.pausado)).length;
  w.innerHTML=`<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
    <div style="padding:5px 11px;background:rgba(27,204,111,.08);border:1px solid rgba(27,204,111,.2);border-radius:7px;font-size:.76rem;color:var(--gr)">✅ ${ativos} disponíveis</div>
    ${paus?`<div style="padding:5px 11px;background:rgba(255,51,81,.08);border:1px solid rgba(255,51,81,.2);border-radius:7px;font-size:.76rem;color:var(--rd)">⏸️ ${paus} pausados</div>`:""}
  </div>`+
  _card.map((cat,ci)=>{
    const total=(cat.itens||[]).length;
    const pdias=(cat.itens||[]).filter(i=>i.pausado).length;
    const body=(cat.itens||[]).map(item=>`
      <div class="ir ${item.pausado?"pausado":""}" style="display:flex;align-items:center">
        ${item.imagem
          ? `<div style="width:62px;height:62px;min-width:62px;border-radius:8px;overflow:hidden;margin-right:10px;border:1px solid var(--brd);flex-shrink:0"><img src="${item.imagem}" style="width:100%;height:100%;object-fit:cover" title="${esc(item.nome)}"/></div>`
          : `<div style="width:62px;height:62px;min-width:62px;border-radius:8px;background:var(--bg3);display:flex;align-items:center;justify-content:center;margin-right:10px;border:1px dashed var(--brd);flex-shrink:0;font-size:1.4rem">🍽️</div>`
        }
        <div class="ii" style="flex:1">
          <div class="in">${esc(item.nome)}${item.pausado?` <span style="font-size:.68rem;background:var(--rd);color:#fff;padding:1px 5px;border-radius:3px">PAUSADO</span>`:""}</div>
          <div class="ip">${esc(item.preco)}</div>
          ${item.descricao?`<div class="id2">${esc(item.descricao)}</div>`:""}
          ${item.tamanhos?`<div style="font-size:.7rem;color:var(--mu2)">📐 ${esc(item.tamanhos)}</div>`:""}
          ${item.maxAcomp?`<div style="font-size:.7rem;color:var(--pu)">🧩 ${item.maxAcomp} acomp.</div>`:""}
          ${item.imagem?`<div style="font-size:.68rem;color:#1bcc6f;margin-top:2px">📸 Com foto</div>`:""}
        </div>
        <div class="ia">
          <button class="btn ${item.pausado?"btg":"btam"} btsm" onclick="togglePausa('${esc(cat.categoria)}','${esc(item.nome)}',${!item.pausado})">${item.pausado?"▶️":"⏸️"}</button>
          <button class="btn bto btsm" onclick="editarItem('${esc(cat.categoria)}','${esc(item.nome)}')">✏️</button>
          <button class="btn btd btsm" onclick="excluirItem('${esc(cat.categoria)}','${esc(item.nome)}')">🗑️</button>
        </div>
      </div>`).join("");
    return `<div class="cg">
      <div class="cg-hd" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none'">
        <div><div class="cg-name">${esc(cat.categoria)}</div><div class="cg-cnt">${total} produto${total!==1?"s":""} ${pdias?`• <span style="color:var(--rd)">${pdias} pausado${pdias!==1?"s":""}</span>`:""}</div></div>
        <div class="brow"><button class="btn btd btsm" onclick="event.stopPropagation();excluirCat('${esc(cat.categoria)}')">🗑️</button></div>
      </div>
      <div class="cg-body">${total===0?'<div class="fe" style="padding:10px">Sem produtos.</div>':body}</div>
    </div>`;
  }).join("");
}

// Modal categoria
get("btn-nova-cat").addEventListener("click",()=>{ get("mc-ico").value=""; get("mc-nome").value=""; get("modal-cat").classList.add("show"); setTimeout(()=>get("mc-nome").focus(),100); });
get("btn-cc").addEventListener("click",()=>get("modal-cat").classList.remove("show"));
get("btn-oc").addEventListener("click",async()=>{
  const nome=get("mc-nome").value.trim(), ico=get("mc-ico").value.trim();
  if(!nome){toast("t-cat","❌ Digite o nome.",false);return;}
  const r=await api("POST","/api/cardapio/categoria",{nome,icone:ico});
  if(r.ok){get("modal-cat").classList.remove("show");_card=r.cardapio||_card;renderCard();const sel=get("mi-cat");if(sel)sel.innerHTML=_card.map(c=>`<option value="${esc(c.categoria)}">${esc(c.categoria)}</option>`).join("");}
  else toast("t-cat","❌ "+(r.erro||"Erro."),false);
});

// Modal item
get("btn-novo-item").addEventListener("click",()=>{
  get("mi-title").textContent="➕ Novo Produto";
  get("mi-cat-orig").value=""; get("mi-nome-orig").value="";
  get("mi-nome").value=""; get("mi-desc").value=""; get("mi-preco").value=""; get("mi-tam").value=""; if(get("mi-acomp"))get("mi-acomp").value="0";
  // Limpar imagem
  _miImgBase64 = "";
  if(get("mi-img-thumb")){get("mi-img-thumb").style.display="none";get("mi-img-thumb").src="";}
  if(get("mi-img-placeholder"))get("mi-img-placeholder").style.display="";
  if(get("mi-img-remove"))get("mi-img-remove").style.display="none";
  get("mi-cat").innerHTML=_card.map(c=>`<option value="${esc(c.categoria)}">${esc(c.categoria)}</option>`).join("");
  get("modal-item").classList.add("show"); setTimeout(()=>get("mi-nome").focus(),100);
});

// Upload de imagem do produto
let _miImgBase64 = "";
if(get("mi-img-input")){
  get("mi-img-input").addEventListener("change", function(){
    const file = this.files[0];
    if(!file) return;
    if(file.size > 2.5*1024*1024){ alert("Imagem muito grande! Máximo 2MB."); return; }
    const reader = new FileReader();
    reader.onload = e => {
      _miImgBase64 = e.target.result; // data:image/...;base64,...
      const thumb = get("mi-img-thumb");
      const ph = get("mi-img-placeholder");
      const rm = get("mi-img-remove");
      if(thumb){ thumb.src = _miImgBase64; thumb.style.display="block"; }
      if(ph) ph.style.display = "none";
      if(rm) rm.style.display = "inline-block";
    };
    reader.readAsDataURL(file);
  });
}
window.removerImagemItem = () => {
  _miImgBase64 = "";
  const thumb = get("mi-img-thumb"); const ph = get("mi-img-placeholder"); const rm = get("mi-img-remove");
  if(thumb){ thumb.src=""; thumb.style.display="none"; }
  if(ph) ph.style.display = "";
  if(rm) rm.style.display = "none";
  if(get("mi-img-input")) get("mi-img-input").value = "";
};

get("btn-ci").addEventListener("click",()=>get("modal-item").classList.remove("show"));
get("btn-oi").addEventListener("click",async()=>{
  const catOrig=get("mi-cat-orig").value, nomeOrig=get("mi-nome-orig").value;
  const cat=get("mi-cat").value, nome=get("mi-nome").value.trim();
  const desc=get("mi-desc").value.trim(), preco=get("mi-preco").value.trim(), tam=get("mi-tam").value.trim();
  const maxAcomp=parseInt(get("mi-acomp")?.value||"0")||0;
  if(!nome||!preco){toast("t-item","❌ Nome e preço obrigatórios.",false);return;}
  // Incluir imagem no payload (pode ser "" para remover ou base64 nova)
  const payload = {categoria:cat,nome,descricao:desc,preco,tamanhos:tam,maxAcomp,imagem:_miImgBase64};
  const r=nomeOrig
    ?await api("PUT","/api/cardapio/item",{...payload,nomeOriginal:nomeOrig})
    :await api("POST","/api/cardapio/item",payload);
  if(r.ok){get("modal-item").classList.remove("show");_card=r.cardapio||_card;renderCard();}
  else toast("t-item","❌ "+(r.erro||"Erro."),false);
});
window.editarItem=(cat,nome)=>{
  const item=_card.find(c=>c.categoria===cat)?.itens?.find(i=>i.nome===nome); if(!item)return;
  get("mi-title").textContent="✏️ Editar Produto";
  get("mi-cat-orig").value=cat; get("mi-nome-orig").value=nome;
  get("mi-cat").innerHTML=_card.map(c=>`<option value="${esc(c.categoria)}">${esc(c.categoria)}</option>`).join("");
  get("mi-cat").value=cat; get("mi-nome").value=item.nome; get("mi-desc").value=item.descricao||""; get("mi-preco").value=item.preco; get("mi-tam").value=item.tamanhos||"";
  if(get("mi-acomp")) get("mi-acomp").value=item.maxAcomp||0;
  // Carregar imagem existente
  _miImgBase64 = item.imagem || "";
  const thumb = get("mi-img-thumb"); const ph = get("mi-img-placeholder"); const rm = get("mi-img-remove");
  if(item.imagem && thumb){ thumb.src=item.imagem; thumb.style.display="block"; if(ph)ph.style.display="none"; if(rm)rm.style.display="inline-block"; }
  else { if(thumb){thumb.src="";thumb.style.display="none";} if(ph)ph.style.display=""; if(rm)rm.style.display="none"; }
  get("modal-item").classList.add("show");
};
window.excluirItem=async(cat,nome)=>{if(!confirm(`Excluir "${nome}"?`))return;const r=await api("DELETE","/api/cardapio/item",{categoria:cat,nome});if(r.ok)loadCardapio();};
// Regra meio a meio
document.querySelectorAll('input[name="meioameio"]').forEach(r => {
  r.addEventListener("change", function() {
    document.querySelectorAll("#label-maior,#label-media").forEach(l => {
      l.style.borderColor = l.id === "label-"+this.value ? "var(--ac)" : "var(--brd)";
    });
  });
});
get("btn-sv-mam")?.addEventListener("click", async () => {
  const sel = document.querySelector('input[name="meioameio"]:checked');
  if (!sel) { toast("t-mam","❌ Selecione uma opção.",false); return; }
  const r = await api("POST","/api/meio-a-meio",{ rule: sel.value });
  toast("t-mam", r.ok
    ? `✅ Regra salva: ${sel.value==="maior"?"cobra o maior valor":"cobra a média"}!`
    : "❌ Erro ao salvar.", r.ok);
});

window.excluirCat=async cat=>{if(!confirm(`Excluir grupo "${cat}" e todos os produtos?`))return;const r=await api("DELETE","/api/cardapio/categoria",{categoria:cat});if(r.ok)loadCardapio();};
window.togglePausa=async(cat,nome,pausado)=>{await api("POST","/api/produto/pausar",{categoria:cat,nome,pausado});loadCardapio();};

// ── STATUS WA ──
let _statusWA=[];
const DIAS=["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"];
const TMPLS=[
  // ── ABERTURA / FUNCIONAMENTO ──
  {e:"🔥",t:"🔥 Estamos ABERTOS!\n\n{empresaNome} pronto para atender você!\n⏱️ Entrega: {tempoEntrega}\n📱 Peça agora pelo WhatsApp!"},
  {e:"🌅",t:"🌅 Bom dia! ☀️\n\n{empresaNome} acabou de abrir!\nVenha tomar café com a gente 😋\n⏰ Horário: {horario}\n📱 Pedidos pelo WhatsApp!"},
  {e:"☀️",t:"☀️ Bom dia, família!\n\nComeçando mais um dia com muita energia e sabor! 🍽️\n\n{empresaNome} aberto e esperando seu pedido!\n🛵 Taxa: {taxaEntrega}"},
  {e:"🌙",t:"🌙 Boa noite!\n\nAinda estamos de portas abertas pra você! 🍕\n{empresaNome} — delivery quentinho até mais tarde.\n⏰ {horario}"},
  {e:"🌆",t:"🌆 Boa tarde!\n\nTá com fome? Nós resolvemos! 😋\n{empresaNome} no seu endereço em {tempoEntrega}.\n📱 Chama no WhatsApp e faz seu pedido!"},

  // ── PROMOÇÕES ──
  {e:"🎯",t:"🎯 OFERTA DO DIA!\n\n{promocoes}\n\n⏰ Só hoje! Corre que acaba!\n{empresaNome} 📱"},
  {e:"💥",t:"💥 PROMOÇÃO IMPERDÍVEL!\n\n{promocoes}\n\nPeça agora e aproveite!\n🛵 {empresaNome}"},
  {e:"🔖",t:"🔖 Economize hoje!\n\n{empresaNome} com preços especiais:\n\n{promocoes}\n\n📱 Peça pelo WhatsApp!"},

  // ── FINAL DE SEMANA ──
  {e:"🎉",t:"🎉 Final de semana chegou!\n\nNada melhor do que um delivery gostoso pra relaxar! 🛵\n\n{empresaNome} entrega na sua porta.\n📱 Peça agora!"},
  {e:"🍻",t:"🍻 Sábado é dia de curtir!\n\nE curtir fica melhor com a comida do {empresaNome}! 😄\n\n🛵 Entrega em {tempoEntrega}\nTaxa: {taxaEntrega}"},
  {e:"🌴",t:"🌴 Domingo de descanso merece comida boa!\n\n{empresaNome} entrega no seu sofá. 🛋️\n⏱️ Tempo médio: {tempoEntrega}\n📱 Chama no WhatsApp!"},

  // ── ENGAJAMENTO ──
  {e:"❤️",t:"❤️ Obrigado pela preferência!\n\nVocês são incríveis! {empresaNome} agradece cada pedido e se dedica ao máximo pra vocês! 🙏\n\nNos vemos no próximo pedido! 🛵"},
  {e:"⭐",t:"⭐ Sua opinião é muito importante!\n\nSe você gostou do nosso atendimento, compartilha com os amigos! 😊\n\n{empresaNome} — qualidade e sabor em cada entrega! 🍽️"},
  {e:"📣",t:"📣 Novidades chegando!\n\nFica de olho no nosso WhatsApp! Em breve novos pratos e promoções especiais no {empresaNome}! 🤩\n\n📱 Salva nosso número!"},

  // ── CLIMA / SITUAÇÃO ──
  {e:"🌧️",t:"🌧️ Dia de chuva?\n\nFica em casa que a gente leva até você! ☂️\n\n{empresaNome} — delivery quentinho pra aquecer o seu dia!\n🛵 Entrega: {tempoEntrega}"},
  {e:"🌞",t:"🌞 Que sol gostoso!\n\nDia perfeito pra pedir uma comidinha especial! 😋\n\n{empresaNome} entrega rapidinho: {tempoEntrega}\n📱 Chama no WhatsApp!"},
  {e:"🏠",t:"🏠 Sem sair de casa!\n\nO {empresaNome} leva até a sua porta com todo o cuidado e sabor que você merece! 💛\n\n🛵 Taxa de entrega: {taxaEntrega}\n⏱️ Tempo: {tempoEntrega}"},

  // ── ENCERRAMENTO ──
  {e:"😴",t:"😴 Quase encerrando!\n\nÚltima chamada pro pedido de hoje!\n{empresaNome} fecha em breve.\n\n⏰ {horario}\n📱 Corre e faz seu pedido!"},
  {e:"🙏",t:"🙏 Obrigado por hoje!\n\nFoi um prazer atender vocês! Amanhã estaremos de volta com muito mais sabor! 😊\n\n{empresaNome}\n⏰ {horario}"},
  {e:"🛵",t:"🛵 {empresaNome}\n\nSabor e qualidade na sua porta!\n⏱️ Entrega em {tempoEntrega}\n💳 Pagamentos: {pagamentos}\n📱 Peça agora pelo WhatsApp!"},
];

async function loadStatusWA(){
  const r=await api("GET","/api/status-wa");
  _statusWA=Array.isArray(r)?r:[];
  renderStatusWA(); renderTmpls();
}

function renderStatusWA(){
  const w=get("lista-sw"); if(!w)return;
  if(!_statusWA.length){w.innerHTML='<div class="fe">Nenhum status. Clique em <strong>➕ Novo</strong> ou use um template.</div>';return;}
  w.innerHTML=_statusWA.map((s,i)=>{
    const dias=DIAS.map((d,di)=>`<button class="dia ${(s.dias||[0,1,2,3,4,5,6]).includes(di)?"on":""}" onclick="_statusWA[${i}].dias=toggleDia(_statusWA[${i}].dias||[],${di});renderStatusWA()">${d}</button>`).join("");
    const nums=(s.numeros||[]).join(", ");
    return `<div class="sw-card ${s.ativo?"":"inativo"}">
      <!-- Cabeçalho: ativo + horário + dias + excluir -->
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
        <label class="tog" title="${s.ativo?"Ativo":"Inativo"}"><input type="checkbox" ${s.ativo?"checked":""} onchange="_statusWA[${i}].ativo=this.checked;renderStatusWA()"/><span class="tsl"></span></label>
        <input type="time" class="inp" style="width:90px;padding:5px 8px;font-size:.84rem" value="${esc(s.horario||"08:00")}" oninput="_statusWA[${i}].horario=this.value" title="Horário de publicação"/>
        <span style="font-size:.72rem;color:var(--mu)">Dias:</span>
        <div class="dias">${dias}</div>
        <button class="btn btd btsm" style="margin-left:auto" onclick="_statusWA.splice(${i},1);renderStatusWA()" title="Excluir">🗑️</button>
      </div>

      <!-- Texto do status -->
      <div class="fg" style="margin-bottom:6px">
        <label style="display:block;font-size:.71rem;color:var(--mu);font-weight:500;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Texto do status (máx 139 chars)</label>
        <textarea class="inp" rows="3" maxlength="139" style="resize:none;font-size:.82rem" placeholder="Ex: 🔥 Estamos abertos! Peça agora..." oninput="_statusWA[${i}].texto=this.value;get('pr${i}').textContent=this.value;get('cnt${i}').textContent=this.value.length+'/139'">${esc(s.texto||"")}</textarea>
        <div style="font-size:.68rem;color:var(--mu);text-align:right;margin-top:2px" id="cnt${i}">${(s.texto||"").length}/139</div>
      </div>

      <!-- Pré-visualização -->
      <div class="sw-prev" id="pr${i}" style="margin-bottom:10px">${esc(s.texto||"")}</div>

      <!-- Como funciona -->
      <div style="padding:8px 12px;background:rgba(61,149,255,.07);border:1px solid rgba(61,149,255,.2);border-radius:8px;margin-bottom:10px;font-size:.78rem;color:var(--mu2)">
        📢 <strong style="color:var(--tx)">O que acontece ao publicar:</strong><br/>
        <span>① Posta no <strong style="color:var(--gr)">Status/Stories</strong> do WhatsApp (visível 24h para todos os contatos)</span><br/>
        <span>② Envia <strong>mensagem direta</strong> para números abaixo (opcional)</span>
      </div>

      <!-- Números extras -->
      <div class="fg" style="margin-bottom:8px">
        <label style="display:block;font-size:.71rem;color:var(--mu);font-weight:500;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">
          📱 Números extras — mensagem direta (opcional)
        </label>
        <input class="inp" style="font-size:.82rem" placeholder="Ex: 5582991856656, 5511999990002"
          value="${esc(nums)}"
          oninput="_statusWA[${i}].numeros=this.value.split(',').map(n=>n.trim()).filter(Boolean)"
          title="DDI+DDD+número, só dígitos, separados por vírgula"/>
        <div style="font-size:.7rem;color:var(--mu);margin-top:3px">
          DDI+DDD sem espaços. Ex: <strong>5582991856656</strong> &nbsp;•&nbsp; Deixe vazio para postar só no Status.
        </div>
      </div>

      <!-- Ação -->
      <button class="btn btg btsm" onclick="pubAgora('${esc(s.id||String(i))}')">▶️ Publicar agora</button>
    </div>`;
  }).join("");
}

function renderTmpls(){
  const w=get("lista-tmpl"); if(!w)return;
  w.innerHTML=TMPLS.map((t,i)=>`<button class="btn bto tmpl btn-w" onclick="addTmpl(${i})">${t.e} ${esc(t.t.slice(0,44))}...</button>`).join("");
}

function toggleDia(dias,di){ const a=[...(dias||[])]; const idx=a.indexOf(di); if(idx>=0)a.splice(idx,1);else a.push(di); return a; }
window.addTmpl=i=>{ _statusWA.push({id:"sw_"+Date.now(),texto:TMPLS[i].t,horario:"08:00",dias:[0,1,2,3,4,5,6],ativo:true,numeros:[]}); renderStatusWA(); get("lista-sw").lastElementChild?.scrollIntoView({behavior:"smooth"}); };
window.pubAgora=async id=>{ const r=await api("POST","/api/status-wa/publicar-agora",{id}); toast("t-sw",r.ok?"✅ Publicado agora!":"❌ "+(r.erro||"Erro."),r.ok); if(r.ok)addLogWA("▶️ Manual: "+(_statusWA.find(s=>s.id===id)||{}).texto?.slice(0,40)); };
function addLogWA(msg){ const w=get("sw-log"); if(!w)return; const emp=w.querySelector(".fe"); if(emp)emp.remove(); const d=document.createElement("div"); d.className="sw-log-item"; d.textContent=fmtT(Date.now())+" "+msg; w.prepend(d); }

get("btn-add-sw").addEventListener("click",()=>{ _statusWA.push({id:"sw_"+Date.now(),texto:"",horario:"08:00",dias:[0,1,2,3,4,5,6],ativo:true,numeros:[]}); renderStatusWA(); get("lista-sw").lastElementChild?.scrollIntoView({behavior:"smooth"}); });
get("btn-sv-sw").addEventListener("click",async()=>{ const r=await api("POST","/api/status-wa",{statusWA:_statusWA}); toast("t-sw",r.ok?"✅ Agendamentos salvos!":"❌ Erro.",r.ok); });

// ── PROMOÇÕES ──
let _promos=[];

async function loadPromocoes(){
  const r=await api("GET","/api/promocoes");
  _promos=Array.isArray(r)?r:[];
  renderPromos();
}

function renderPromos() { renderPromosCard(); } // compatibilidade

function atualizarBadgePromo(ativo) {
  const b = get("promo-geral-badge"); if(!b) return;
  b.textContent = ativo ? "✅ Ativo" : "Desativado";
  b.style.background = ativo ? "rgba(34,197,94,.15)" : "var(--bg3)";
  b.style.color = ativo ? "var(--gr)" : "var(--mu)";
}

function renderPromosCard() {
  const w = get("lista-promos-card"); if(!w) return;
  if(!_promos.length){ w.innerHTML='<div class="fe">Nenhuma promoção. Clique em ➕ Nova Promoção.</div>'; return; }
  w.innerHTML = _promos.map((p,i) => `
    <div style="background:var(--bg2);border:1px solid var(--brd);border-radius:12px;overflow:hidden;position:relative">
      ${p.imagem
        ? `<img src="${p.imagem}" style="width:100%;height:140px;object-fit:cover"/>`
        : `<div style="width:100%;height:140px;background:var(--bg3);display:flex;align-items:center;justify-content:center;color:var(--mu);font-size:.8rem">📷 Sem imagem</div>`}
      <div style="position:absolute;top:8px;right:8px">
        <label class="tog" title="${p.ativo?'Desativar':'Ativar'}">
          <input type="checkbox" ${p.ativo?"checked":""} onchange="_promos[${i}].ativo=this.checked;salvarPromos()"/>
          <span class="tsl"></span>
        </label>
      </div>
      <div style="padding:10px 12px">
        <div style="font-weight:700;font-size:.86rem;color:var(--tx)">${esc(p.nome||"Sem nome")}</div>
        ${p.descricao?`<div style="font-size:.74rem;color:var(--mu);margin-top:2px">${esc(p.descricao)}</div>`:""}
        <div style="display:flex;align-items:center;gap:8px;margin-top:6px">
          ${p.precoOriginal?`<span style="font-size:.74rem;color:var(--mu);text-decoration:line-through">R$ ${esc(p.precoOriginal)}</span>`:""}
          ${p.precoPromo?`<span style="font-weight:700;color:var(--ac)">R$ ${esc(p.precoPromo)}</span>`:""}
          ${p.desconto?`<span style="font-size:.72rem;background:rgba(255,79,31,.15);color:var(--ac);padding:2px 6px;border-radius:10px">${esc(p.desconto)}</span>`:""}
        </div>
        <div style="display:flex;gap:6px;margin-top:8px">
          <button class="btn bto btsm" style="flex:1" onclick="editarPromo(${i})">✏️ Editar</button>
          <button class="btn btd btsm" onclick="excluirPromo(${i})">🗑️</button>
        </div>
      </div>
    </div>`).join("");
}

async function salvarPromos() {
  await api("POST","/api/promocoes",{promocoes:_promos});
}

window.editarPromo = function(i) {
  const p = _promos[i];
  get("mp-id").value = i;
  get("mp-nome").value = p.nome||"";
  get("mp-desc").value = p.descricao||"";
  get("mp-preco-orig").value = p.precoOriginal||"";
  get("mp-preco-promo").value = p.precoPromo||"";
  get("mp-desconto").value = p.desconto||"";
  get("mp-ativo").checked = p.ativo!==false;
  _mpImgBase64 = p.imagem||null;
  const thumb=get("mp-img-thumb"), ph=get("mp-img-placeholder");
  if(_mpImgBase64){thumb.src=_mpImgBase64;thumb.style.display="block";if(ph)ph.style.display="none";}
  else{thumb.style.display="none";if(ph)ph.style.display="block";}
  get("mp-title").textContent = "✏️ Editar Promoção";
  get("modal-promo").classList.add("show");
};

window.excluirPromo = async function(i) {
  if(!confirm("Excluir esta promoção?")) return;
  _promos.splice(i,1);
  await salvarPromos();
  renderPromosCard();
};

// Abrir modal nova promoção
get("btn-nova-promo")?.addEventListener("click", () => {
  get("mp-id").value="";
  get("mp-nome").value=""; get("mp-desc").value=""; get("mp-preco-orig").value="";
  get("mp-preco-promo").value=""; get("mp-desconto").value="";
  get("mp-ativo").checked=true; _mpImgBase64=null;
  const thumb=get("mp-img-thumb"),ph=get("mp-img-placeholder");
  if(thumb)thumb.style.display="none"; if(ph)ph.style.display="block";
  get("mp-title").textContent="🔥 Nova Promoção";
  get("modal-promo")?.classList.add("show");
});
get("btn-cancelar-promo")?.addEventListener("click",()=>get("modal-promo")?.classList.remove("show"));

// Preview de imagem
get("mp-img-input")?.addEventListener("change", function() {
  const file=this.files[0]; if(!file) return;
  if(file.size>2*1024*1024){alert("Imagem muito grande! Máximo 2MB.");return;}
  const r=new FileReader();
  r.onload=e=>{
    _mpImgBase64=e.target.result;
    const thumb=get("mp-img-thumb"),ph=get("mp-img-placeholder");
    if(thumb){thumb.src=_mpImgBase64;thumb.style.display="block";}
    if(ph)ph.style.display="none";
  };
  r.readAsDataURL(file);
});

// Salvar promoção
get("btn-salvar-promo")?.addEventListener("click", async () => {
  const nome=get("mp-nome")?.value.trim();
  if(!nome){toast("t-mp","❌ Nome obrigatório.",false);return;}
  const idx=get("mp-id")?.value;
  const promo={
    id: idx!=="" ? (_promos[idx]?.id||Date.now()+"") : Date.now()+"",
    nome, descricao:get("mp-desc")?.value.trim(),
    precoOriginal:get("mp-preco-orig")?.value.trim(),
    precoPromo:get("mp-preco-promo")?.value.trim(),
    desconto:get("mp-desconto")?.value.trim(),
    ativo:get("mp-ativo")?.checked!==false,
    imagem:_mpImgBase64||null
  };
  if(idx!=="") _promos[idx]=promo; else _promos.push(promo);
  const r=await api("POST","/api/promocoes",{promocoes:_promos});
  if(r?.ok){get("modal-promo")?.classList.remove("show");renderPromosCard();toast("t-promo","✅ Promoção salva!",true);}
  else toast("t-mp","❌ Erro ao salvar.",false);
});

// Toggle geral
get("tog-promo-geral")?.addEventListener("change", async function() {
  const r=await api("POST","/api/promocoes/toggle-geral",{ativo:this.checked});
  if(r?.ok) atualizarBadgePromo(this.checked);
});

// ── RELATÓRIOS ──
async function loadRelatorios(){
  const r=await api("GET","/api/relatorios"); if(!r?.hoje)return;
  setEl("rel-hoje","textContent",r.hoje.qtd);
  setEl("rel-total","textContent",r.geral.totalPedidos);
  setEl("rel-top","textContent",(r.geral.ranking[0]?.nome||"—").slice(0,14));
  // Faturamento do dia
  const fat = r.hoje.faturamento || 0;
  const fatEl = get("rel-fat");
  if (fatEl) fatEl.textContent = "R$ " + fat.toFixed(2).replace(".",",");

  // Pedidos hoje
  const ph=get("rel-pedidos");
  if(ph){
    if(!r.hoje.pedidos.length){ph.innerHTML='<div class="fe">Sem pedidos hoje.</div>';}
    else ph.innerHTML=r.hoje.pedidos.map(p=>`<div class="li2 saida" style="margin-bottom:3px"><div style="display:flex;justify-content:space-between"><span class="lt">${esc(p.hora||"")}</span><span style="font-family:var(--fh);font-weight:700;font-size:.86rem;color:var(--ac)">#${esc(p.numPedido||"—")}</span><span style="font-size:.73rem;color:var(--mu2)">${esc(p.pagamento||"")}</span></div><div class="lm">${esc(p.itens||"—")}</div><div style="font-size:.7rem;color:var(--mu)">${esc((p.telefone||p.numero||"").replace("@c.us",""))}</div></div>`).join("");
  }

  // Top itens
  const rank=get("rel-rank");
  if(rank){
    if(!r.geral.ranking.length)rank.innerHTML='<div class="fe">Sem dados.</div>';
    else rank.innerHTML=r.geral.ranking.map((it,i)=>`<div class="rank-item"><div class="rank-num">${i===0?"🥇":i===1?"🥈":i===2?"🥉":"#"+(i+1)}</div><div class="rank-nome">${esc(it.nome)}</div><div class="rank-qtd">${it.qtd}x</div></div>`).join("");
  }

  // Histórico
  const hist=get("rel-hist");
  if(hist){
    const dias=r.geral.porDia;
    if(!dias.length)hist.innerHTML='<div class="fe">Sem histórico.</div>';
    else{ const mx=Math.max(...dias.map(d=>d.qtd),1); hist.innerHTML=dias.map(d=>{ const pct=Math.round(d.qtd/mx*100); const df=new Date(d.data+"T12:00").toLocaleDateString("pt-BR",{day:"2-digit",month:"2-digit"}); const pag=Object.entries(d.pagamentos||{}).map(([k,v])=>k+":"+v).join(" | "); return `<div class="hist-row"><div class="hist-data">${df}</div><div class="hist-qtd">${d.qtd}</div><div class="hist-bar"><div class="hist-fill" style="width:${pct}%"></div></div><div class="hist-pag">${pag}</div></div>`; }).join(""); }
  }
}
get("btn-atrel")?.addEventListener("click",loadRelatorios);

// ── LOGS ──
async function loadLogs(){
  const logs=await api("GET","/api/logs");
  const f=get("log-feed");
  if(!Array.isArray(logs)||!logs.length){f.innerHTML='<div class="fe">Sem logs hoje.</div>';return;}
  f.innerHTML=""; logs.forEach(l=>addLog(l,false));
}
function addLog(l,prep){
  const f=get("log-feed"); const emp=f.querySelector(".fe"); if(emp)emp.remove();
  const tipo=l.tipo||"entrada", num=(l.de||l.para||"—").replace("@c.us","");
  const d=document.createElement("div"); d.className="li2 "+tipo;
  d.innerHTML=`<span class="lt">${fmtFull(l.ts)}</span> <span class="lde">[${tipo==="entrada"?"↙ ":"↗ "}${esc(num)}]</span><div class="lm">${esc(l.mensagem||"")}</div>`;
  prep?f.prepend(d):f.appendChild(d);
}
get("btn-atlog").addEventListener("click",loadLogs);

// ── ENVIAR ──
get("btn-env").addEventListener("click",async()=>{
  const n=get("env-n").value.trim(), m=get("env-m").value.trim();
  if(!n||!m){toast("t-env","❌ Preencha número e mensagem.",false);return;}
  const r=await api("POST","/api/enviar",{numero:n,mensagem:m});
  toast("t-env",r.ok?"✅ Enviada!":"❌ "+(r.erro||"Erro."),r.ok);
  if(r.ok)get("env-m").value="";
});

// ── LICENÇA ──
async function loadLic2(){
  const r=await api("GET","/api/licenca"); if(!r.validade&&!r.comerciante)return;
  updateLic(r);
  const ni=get("lic-nome-inp"),vi=get("lic-val-inp"),ti=get("tog-lic");
  if(ni)ni.value=r.comerciante||"";
  if(vi&&r.validade)vi.value=r.validade.slice(0,10);
  if(ti)ti.checked=!!r.ativa;
}
function updateLic(d){
  const dias=d.diasRestantes??0, ok=d.valida??false, nome=d.comerciante||"—";
  const cls=ok?(dias<=7?"warn":"ok"):"bad";
  const ld=get("ld"); if(ld){ld.className="ld "+cls;setEl("ln","textContent",nome);setEl("ldi","textContent",ok?dias+" dias restantes":"Licença expirada!");}
  const big=get("lic-big"); if(big){big.textContent=ok?dias+"":"✕";big.className="lic-num "+cls;setEl("lic-lbl","textContent",ok?"dias restantes":"Expirada ou inativa");setEl("lic-com","textContent",nome);}
}
get("btn-sv-lic")?.addEventListener("click",async()=>{
  const r=await api("POST","/api/licenca",{comerciante:get("lic-nome-inp").value.trim(),validade:get("lic-val-inp").value,ativa:get("tog-lic").checked});
  toast("t-lic",r.ok?"✅ Licença salva!":"❌ Erro.",r.ok);
  if(r.ok)loadLic2();
});

// ── SENHA SUPORTE ──
const SUP_PASS="251234";
let supUnlocked=false;
function initSuporteLock(){
  if(supUnlocked){showSup();loadLic2();return;}
  get("sup-lock").style.display="block";
  get("sup-content").style.display="none";
  setTimeout(()=>get("sup-user")?.focus(),200);
}
function showSup(){get("sup-lock").style.display="none";get("sup-content").style.display="block";}
get("btn-sup-unlock").addEventListener("click",()=>{
  const supUser = (get("sup-user")?.value||"").trim().toLowerCase();
  const supSenha = get("sup-senha").value;
  if(supUser==="suporte" && supSenha===SUP_PASS){
    supUnlocked=true; showSup(); loadLic2();
  } else {
    toast("t-sup-lock","❌ Usuário ou senha incorretos.",false);
    if(get("sup-senha")) { get("sup-senha").value=""; get("sup-senha").focus(); }
  }
});
get("sup-senha").addEventListener("keydown",e=>{if(e.key==="Enter")get("btn-sup-unlock").click();});

// ── ATENDIMENTO HUMANO ──
let _atendNumeroAtivo = null;

async function loadAtendConfig() {
  const r = await api("GET","/api/atendimento-humano/status");
  if (!r) return;
  const tog = document.getElementById("tog-atend");
  if (tog) tog.checked = !!r.ativo;
  atualizarBadgeAtend(!!r.ativo);
}

function atualizarBadgeAtend(ativo) {
  const badge = document.getElementById("atend-badge");
  if (!badge) return;
  badge.textContent = ativo ? "✅ Ativo" : "Desativado";
  badge.style.background = ativo ? "rgba(34,197,94,.15)" : "var(--bg3)";
  badge.style.color = ativo ? "var(--gr)" : "var(--mu)";
}

document.getElementById("tog-atend")?.addEventListener("change", async function() {
  await api("POST","/api/atendimento-humano/toggle",{ ativo: this.checked });
  atualizarBadgeAtend(this.checked);
});

document.getElementById("btn-sv-atend")?.addEventListener("click", async () => {
  const num = (document.getElementById("inp-num-atend")?.value||"").replace(/\D/g,"");
  const r = await api("POST","/api/config",{ numeroAtendente: num });
  toast("t-atend", r?.ok ? "✅ Salvo!" : "❌ Erro.", !!r?.ok);
});

async function loadAtendLista() {
  const lista = await api("GET","/api/atendimento-humano");
  const el = document.getElementById("atend-lista");
  if (!el) return;
  if (!lista?.length) { el.innerHTML='<div class="fe">Nenhum atendimento ativo.</div>'; return; }
  el.innerHTML = lista.map(a => `<div onclick="abrirChat('${esc(a.numero)}')" style="cursor:pointer;padding:10px 12px;background:var(--bg3);border-radius:8px;border:2px solid ${_atendNumeroAtivo===a.numero?'var(--ac)':'var(--brd)'};margin-bottom:6px;display:flex;align-items:center;gap:10px">
    <span style="font-size:1.1rem">💬</span>
    <div style="flex:1"><div style="font-weight:700;font-size:.84rem;color:var(--tx)">📱 ${esc(a.numero)}</div>
    <div style="font-size:.74rem;color:var(--mu)">${esc(a.motivo||"")} · ${a.msgs?.length||0} msg(s)</div></div>
    <span style="font-size:.7rem;color:var(--mu)">${a.inicio?new Date(a.inicio).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):""}</span>
  </div>`).join("");
}

window.abrirChat = async function(numero) {
  _atendNumeroAtivo = numero;
  document.getElementById("atend-chat-num").textContent = numero;
  document.getElementById("atend-chat-box").style.display = "block";
  await renderMsgsAtend(numero);
  loadAtendLista();
};

async function renderMsgsAtend(numero) {
  const lista = await api("GET","/api/atendimento-humano");
  const a = (lista||[]).find(x=>x.numero===numero);
  const el = document.getElementById("atend-msgs");
  if (!el) return;
  if (!a?.msgs?.length) { el.innerHTML='<div class="fe">Sem mensagens.</div>'; return; }
  el.innerHTML = a.msgs.map(m => {
    const lado = m.de==="atendente";
    return `<div style="display:flex;justify-content:${lado?'flex-end':'flex-start'}"><div style="max-width:80%;padding:8px 12px;border-radius:12px;background:${lado?'var(--ac)':'var(--bg4)'};color:${lado?'#fff':'var(--tx)'};font-size:.82rem"><div style="font-size:.68rem;opacity:.7;margin-bottom:3px">${m.de==="atendente"?"Você":"Cliente"}</div>${esc(m.texto||"")}</div></div>`;
  }).join("");
  el.scrollTop = el.scrollHeight;
}

document.getElementById("btn-enviar-atend")?.addEventListener("click", async () => {
  if (!_atendNumeroAtivo) return;
  const inp = document.getElementById("atend-resposta");
  const msg = (inp?.value||"").trim();
  if (!msg) return;
  const r = await api("POST","/api/atendimento-humano/responder",{ numero:_atendNumeroAtivo, mensagem:msg });
  if (r?.ok) { if(inp) inp.value=""; renderMsgsAtend(_atendNumeroAtivo); }
});

document.getElementById("atend-resposta")?.addEventListener("keydown", e => {
  if (e.key==="Enter"&&!e.shiftKey){e.preventDefault();document.getElementById("btn-enviar-atend")?.click();}
});

document.getElementById("btn-encerrar-atend")?.addEventListener("click", async () => {
  if (!_atendNumeroAtivo||!confirm("Encerrar e devolver ao bot?")) return;
  const r = await api("POST","/api/atendimento-humano/encerrar",{ numero:_atendNumeroAtivo });
  if (r?.ok) { _atendNumeroAtivo=null; document.getElementById("atend-chat-box").style.display="none"; loadAtendLista(); }
});

document.getElementById("btn-refresh-atend")?.addEventListener("click", loadAtendLista);



// ── SKINS / APARÊNCIA ──
const SKINS = [
  { id:"carbon",  nome:"🌑 Carbon",  desc:"Escuro clássico",     bg:"#090b10", ac:"#ff4f1f" },
  { id:"ocean",   nome:"🌊 Ocean",   desc:"Azul profundo",       bg:"#03080f", ac:"#0ea5e9" },
  { id:"emerald", nome:"💚 Emerald", desc:"Verde esmeralda",     bg:"#020c09", ac:"#10b981" },
  { id:"violet",  nome:"💜 Violet",  desc:"Roxo misterioso",     bg:"#07030f", ac:"#7c3aed" },
  { id:"rose",    nome:"🌹 Rose",    desc:"Rosa intenso",        bg:"#0f030a", ac:"#f43f5e" },
  { id:"amber",   nome:"🔥 Amber",   desc:"Âmbar vibrante",      bg:"#0f0a02", ac:"#f59e0b" },
  { id:"steel",   nome:"🔩 Steel",   desc:"Cinza profissional",  bg:"#060709", ac:"#64748b" },
  { id:"light",   nome:"☀️ Light",   desc:"Tema claro",          bg:"#f0f2f7", ac:"#3d6aff" },
  { id:"neon",    nome:"⚡ Neon",    desc:"Verde neon",          bg:"#030508", ac:"#00ffcc" },
  { id:"crimson", nome:"🔴 Crimson", desc:"Vermelho forte",      bg:"#0a0202", ac:"#dc2626" },
];
function applySkin(id) {
  document.documentElement.setAttribute("data-skin", id);
  localStorage.setItem("dbSkin", id);
}
function loadSkinGrid() {
  const grid = document.getElementById("skin-grid");
  if (!grid) return;
  const atual = localStorage.getItem("dbSkin") || "carbon";
  grid.innerHTML = "";
  SKINS.forEach(s => {
    const ativo = s.id === atual;
    const div = document.createElement("div");
    div.style.cssText = "cursor:pointer;border-radius:12px;overflow:hidden;border:3px solid "+(ativo?s.ac:"var(--brd)")+";transition:all .2s;position:relative";
    div.onclick = () => { applySkin(s.id); loadSkinGrid(); toast("t-skin","✅ Tema "+s.nome+" aplicado!",true); };
    div.innerHTML =
      "<div style='height:56px;background:"+s.bg+";display:flex;align-items:center;justify-content:center;gap:6px'>"+
        "<div style='width:22px;height:22px;border-radius:50%;background:"+s.ac+"'></div>"+
        "<div style='width:14px;height:14px;border-radius:50%;background:"+s.ac+";opacity:.45'></div>"+
      "</div>"+
      "<div style='padding:8px 10px;background:var(--bg2)'>"+
        "<div style='font-weight:700;font-size:.82rem;color:var(--tx)'>"+s.nome+"</div>"+
        "<div style='font-size:.72rem;color:var(--mu);margin-top:1px'>"+s.desc+"</div>"+
      "</div>"+
      (ativo?"<div style='position:absolute;top:5px;right:5px;background:"+s.ac+";border-radius:50%;width:18px;height:18px;display:flex;align-items:center;justify-content:center;font-size:.7rem;color:#fff'>✓</div>":"");
    grid.appendChild(div);
  });
}
(function(){ applySkin(localStorage.getItem("dbSkin") || "carbon"); })();
