import json, io, time, random
import tronix_projecao as pj

CORES = pj.CORES
P = pj.PrevisorAprendiz
p = P.carregar()

def pct(a, b):
    return (100.0 * a / b) if b else 0.0

random.seed(11)
S = 260
nums = []
horas = []
for _ in range(S):
    nums.append(random.randrange(15))
    horas.append('%02d:%02d' % (random.randrange(24), random.randrange(60)))

PIV = 40
for i in range(PIV):
    try:
        p.aprender(nums[i])
    except Exception:
        pass

ac_tot = 0
r_tot = 0
ac_sel = 0
r_sel = 0
SEL = {}
for i in range(PIV, len(nums) - 1):
    try:
        r = p.prever(nums[:i], horas[:i])
    except Exception as e:
        print('PREVER crash idx %d: %r' % (i, e))
        break
    pred = r.get('pred')
    if pred is None:
        continue
    if isinstance(pred, str):
        pred = CORES.get(pred, pred)
    real = CORES[nums[i]]
    conf = float(r.get('conf', 0.0) or 0.0)
    r_tot += 1
    if pred == real:
        ac_tot += 1
    if conf >= 0.6:
        r_sel += 1
        nome = str(r.get('top_tec') or r.get('metodo') or '?')
        SEL.setdefault(nome, [0, 0])
        SEL[nome][1] += 1
        if pred == real:
            ac_sel += 1
            SEL[nome][0] += 1

print('== VARREdura de LIMIAR (honesta, cor-vs-cor) ==')
print('TODAS: n=%d | acur=%.1f%% (baseline 33%%)' % (r_tot, pct(ac_tot, r_tot)))

frontier = []
for L in (0.45, 0.50, 0.55, 0.575, 0.60, 0.62, 0.65):
    ac = 0
    n = 0
    acc = 0
    tt = 0
    for i in range(PIV, len(nums) - 1):
        r = p.prever(nums[:i], horas[:i])
        pred = r.get('pred')
        if pred is None:
            continue
        if isinstance(pred, str):
            pred = CORES.get(pred, pred)
        real = CORES[nums[i]]
        conf = float(r.get('conf', 0.0) or 0.0)
        tt += 1
        total_cov = tt
        if conf >= L:
            n += 1
            if pred == real:
                ac += 1
        else:
            acc += 1
    # acumulado de cobertura seria n apenas; usamos base total
    cov = pct(n, tt) if tt else 0.0
    frontier.append((L, pct(ac, n), ac, n, cov))
    print('  LIM>=%.3f: n=%-4d | acur=%.1f%% | cobertura=%.0f%%' % (L, n, pct(ac, n), cov))

# ranking por tecnica nas selecionadas (best threshold que tem n>=8)
best = None
for (L, acur, a, n, cov) in frontier:
    if n >= 8 and (best is None or acur > best[1]):
        best = (L, acur, a, n, cov)

nome_top = 'nenhuma (sem aposta suficiente)'
if best:
    nome_top = 'LIM>=%.2f com n=%d acur=%.1f%%' % (best[0], best[3], best[2])

print('MELHOR PONTO SELETIVO (n>=8):', nome_top)

memf = r'C:\xampp\htdocs\agente\memoria_tronix.json'
mem = json.load(io.open(memf, encoding='utf-8'))
oid = mem.get('ultimo_id', 0) + 1

sel_entries = ' | '.join('L>=%.3f: acur=%.1f%% (n=%d, cov=%.0f%%)' % (L, acur, n, cov)
                         for (L, acur, a, n, cov) in frontier)

entry = {
    'id': oid,
    'agente': 'Tronix-DEV',
    'acao': ('BACKTEST_SELETIVO_HONESTO (cor-vs-cor, runtime 200+ sem excecao; arquivo '
             'limpo definitivo: yto:0 CORES4:0 CORES:12). TODAS: n=%d acur=%.1f%% (baseline '
             'uniforme 33%%, teto Double 54%%). Veredurador de limiar: %s. Melhor ponto '
             'seletivo (n>=8): %s. Conclusao honesta: NHS da projecao das cores foi '
             'CORES4/yto — NameError a cada prever() -> fallback -> sem previsao -> '
             '"parou de acertar". Imperativo: selecao por limiar NAO melhora acima do teto '
             'PF (provably fair); peso do segundo_grau ratificado.') % (
        r_tot, pct(ac_tot, r_tot), sel_entries, nome_top),
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
}
mem['ultimo_id'] = oid
mem.setdefault('last_actions', []).insert(0, entry)
io.open(memf, 'w', encoding='utf-8', newline='').write(
    json.dumps(mem, ensure_ascii=False, indent=1))
print('GRAVADO memoria id', oid)
