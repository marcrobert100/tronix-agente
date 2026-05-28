// src/config/state.js
class AppState {
    constructor() {
        this.waClient = null;
        this.waConectado = false;
        this.io = null;
        this.totalMsgs = 0;
        this.autoImprimir = true;
        this.viasImpressao = 1;
        this.agenteAtivo = true;
        this.inicio = Date.now();

        this.historicos = new Map();
        this.rateLimiter = new Map();
        this.estadosPedido = new Map();
        this.pedidosAbertos = new Map();

        this.clientesDB = new Map();
        this.avaliacoesPend = new Map();
        this.cuponsDB = new Map();
        
        this.atendimentoHumano = new Map();
        this.atendHumanoAtivo = false;
        
        this.sessoes = new Map(); // token sessoes auth
    }
}

// Exporta apenas uma única instância (Singleton) para compartilhar a memória global entre modulos
const state = new AppState();
module.exports = state;
