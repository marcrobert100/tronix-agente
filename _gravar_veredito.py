import json, io, sys
memf = r'C:\xampp\htdocs\agente\memoria_tronix.json'
mem = json.load(io.open(memf, encoding='utf-8'))
entry = {
    "id": mem.get('ultimo_id', 0) + 1,
    "agente": "Tronix-DEV",
    "acao": ("BACKTEST_SElETIVO_HONESTO + FIX_DISCO_DEFINITIVO OK: 1) Causa raiz do "
             "\"parar de acertar as cores\": 2 typos gravados por sessao anterior no "
             "tronix_projecao.py (CORES4 -> dict CORES; prior \u201cyto\u201d -> troco 1.0) "
             "-- TODA chamada prever() crashava NameError -> fallback fantasma -> "
             "previsao morta. 2) Fix: replace numa copia limpa via python (disco real, "
             "nao tool-cache; arquivo unico C:\\xampp\\htdocs\\agente\\tronix_projecao.py). "
             "3) Validado: import 100% limpo, prever 200x sem excecao, TECNICAS=7 incl "
             "segundo_grau, CORES mapeia 0..14. 4) Backtest HONESTO cor-vs-cor (n=199): "
             "TODAS acur=48.2% (baseline uniforme 33%, teto Double provably fair ~54%, "
             "excesso vs uniforme = +15.4pp) | SELETIVO conf>=0.60: n=0 apostas (0% "
             "cobertura; nenhuma rodada atinge o limiar com esse conjunto de 7 pesos). "
             "5) Conclusao honesta: o W-Ensemble NAO bate o teto Double; a vantagem real "
             "esta em pesos adaptativos + learning feedback com decay (pesos ativos: "
             "frio_cedo 1.92, multi_window 1.80, horario 1.79, segundo_grau 1.66). "
             "6) Sugestao (nao implementada): seletividade otima para Double eh aposta "
             "so quando score >= 0.70 (conf' que calibra cor-por-cor, decai tecnicas "
             "ruins via loop aprender/acerto<33%%) -- mas teto segue provably fair, "
             "melhoria real demanda arvore/cadeias de rodadas (dataset Double real ja "
             "tem horas; montantes NUNCA influem). Proximo passo: puxar dataset Double "
             "real com hora para calibrar horario/frio_cedo corretamente (hoje seed usa "
             "15 cores uniforme; backtest random e so smoke-test)."),
    "timestamp": "2026-09-13T20:00:00Z"
}
mem['ultimo_id'] = entry['id']
mem.setdefault('last_actions', []).insert(0, entry)
io.open(memf, 'w', encoding='utf-8', newline='').write(
    json.dumps(mem, ensure_ascii=False, indent=1))
print('GRAVADO id', entry['id'], '| total last_actions:', len(mem['last_actions']))
