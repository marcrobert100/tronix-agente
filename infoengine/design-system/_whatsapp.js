function compartilharWhatsApp(opts) {
  const numero = opts.numero || '5582991856656'
  const mensagem = opts.mensagem || 'Olá! 👋'
  const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensagem)}`
  window.open(url, '_blank')
}

function waBotao(texto, mensagem) {
  return `<button onclick="compartilharWhatsApp({mensagem:'${mensagem.replace(/'/g, "\\'")}'})">${texto}</button>`
}
