# -*- coding: utf-8 -*-
"""
TRONIX ANALISE BLAZE — analise profunda Double
Testa aleatoriedade, metodos de projecao (soma de horarios e numeros),
cadeia Markov 1a ordem, frequencia modal, e mede precisao real na janela.

Nao ha garantia de previsao — Double e provably fair (random). Tudo aqui
quantifica o quanto cada tecnica supera (ou nao) o baseline de 46.67%.
"""
from collections import Counter
import math

BRANCO = 0
VERMELHO = 1
PRETO = 2
NOME = {0: "BRANCO", 1: "VERMELHO", 2: "PRETO"}
NUMPC = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1,
         8: 2, 9: 2, 10: 2, 11: 2, 12: 2, 13: 2, 14: 2}


def cor(n):
    return NUMPC[n]


def soma_digitos(x):
    s = 0
    for c in str(x):
        if c.isdigit():
            s += int(c)
    return s


def chi2_obs_esp(obs):
    """Qui-quadrado para distribuicao uniforme das 15 frequencias."""
    n = sum(obs)
    if n == 0:
        return 0.0, 0.0
    esp = n / len(obs)
    chi = sum((o - esp) ** 2 / esp for o in obs)
    df = len(obs) - 1
    return chi, df


def p_chi2(chi, df):
    """P-value aproximado de qui-quadrado (regra do limite central, df>10 ok)."""
    if df <= 0:
        return 1.0
    z = math.sqrt(2 * chi) - math.sqrt(2 * df - 1)
    return 0.5 * math.erfc(z / math.sqrt(2))


def zipf_stats(nums, janela=200):
    """Distribuicao dos numeros (quentes/frios) + chi2 na janela."""
    w = nums[-janela:]
    cn = Counter(w)
    esp = len(w) / 15
    chi = sum((cn.get(i, 0) - esp) ** 2 / esp for i in range(15))
    quentes = [i for i, _ in cn.most_common(4)]
    frios = [i for i in range(15) if cn.get(i, 0) <= esp * 0.6]
    return dict(freq=dict(cn), quentes=quentes, frios=frios, chi=chi,
                p=p_chi2(chi, 14), n=len(w))


def segs_momento(nums):
    """Analise de sequencias de cores: streaks atuais e historicas."""
    cs = [cor(n) for n in nums]
    atual = []
    ult = cs[-1]
    for c in reversed(cs):
        if c == ult:
            atual.append(c)
        else:
            break
    # maiores streaks historicas
    best = {0: 0, 1: 0, 2: 0}
    run, prev = 0, None
    for c in cs:
        if c == prev:
            run += 1
        else:
            run = 1
            prev = c
        best[c] = max(best[c], run)
    # breaks de streak: depois de streak >=3, qual cor sai em seguida?
    breaks = {}
    run = 0
    for i in range(1, len(cs)):
        if cs[i] == cs[i - 1]:
            run += 1
        else:
            if run >= 2:
                k = (cs[i - 1], run)
                breaks.setdefault(k, []).append(cs[i])
            run = 0
    return dict(atual_cor=ult, atual_tam=len(atual), best=best, breaks_depois_streaks=breaks)


def tecnicas(nums, horarios):
    """Testa tecnicas de projecao. horarios: lista de HH:MM:SS (mesmo len de nums).
    Retorna acuracia de cada tecnica vs baseline, na 2a metade (holdout)."""
    n = len(nums)
    if n < 40 or len(horarios) != n:
        return None
    metade = n // 2
    cs = [cor(x) for x in nums]
    # baseline: sempre apostar na cor mais frequente da 1a metade
    base_cor = Counter(cs[:metade]).most_common(1)[0][0]

    def h_dig(h):
        hh, mm, ss = h.split(":")
        return int(hh), int(mm), int(ss)

    res = {}
    for i in range(metade, n - 1):
        alvo = cs[i + 1]
        hh, mm, ss = h_dig(horarios[i])
        # tecnica 1: soma dos digitos do horario -> par=vermelho, impar=preto
        s = soma_digitos(int(hh)) + soma_digitos(int(mm)) + soma_digitos(int(ss))
        t1 = VERMELHO if s % 2 == 0 else PRETO
        # tecnica 2: horas+minutos -> mod cor (0=B, 1=V, 2=P)
        t2 = (int(hh) * 60 + int(mm) + int(ss)) % 3
        # tecnica 3: soma dos 3 numeros anteriores mod 3
        t3 = sum(nums[i - 2:i + 1]) % 3
        # tecnica 4: numero anterior somado ao digito do minuto mod 3
        t4 = (nums[i] + int(mm)) % 3
        # tecnica 5: numero anterior + hora mod 3
        t5 = (nums[i] + int(hh)) % 3
        # tecnica 6: reverso do numero (espelho 14-n)
        t6 = 14 - nums[i]
        # tecnica 7: numero central da casa (5-9 tendem cor?) - cor do numero deletivo
        t7 = VERMELHO if nums[i] <= 7 else PRETO
        for nome, pred in (("horario_soma_par", t1), ("horario_mod3", t2),
                           ("soma3_numeros", t3), ("num_minuto", t4),
                           ("num_hora", t5), ("espelho", t6), ("metade_pintura", t7)):
            r = res.setdefault(nome, [0, 0])
            r[1] += 1
            r[0] += 1 if pred == alvo else 0

    total = n - 1 - metade
    base_ac = sum(1 for i in range(metade, n - 1) if cs[i + 1] == base_cor)
    out = {"baseline_cor": NOME[base_cor], "baseline": base_ac / total}
    for nome, (ac, tot) in res.items():
        out[nome] = ac / tot
    # significancia: usa intervalo de Wilson p/ comparar com baseline
    return out


def markov(nums, janela=200):
    """Cadeia de Markov 1a ordem sobre cores + projecao pela mais provavel."""
    w = nums[-janela:]
    cs = [cor(x) for x in w]
    trans = {0: {0: 0, 1: 0, 2: 0}, 1: {0: 0, 1: 0, 2: 0}, 2: {0: 0, 1: 0, 2: 0}}
    for i in range(len(cs) - 1):
        trans[cs[i]][cs[i + 1]] += 1
    prob_cond = {}
    for a in trans:
        tot = sum(trans[a].values())
        prob_cond[a] = {b: trans[a][b] / tot for b in trans[a]} if tot else {0: 0, 1: 0, 2: 0}
    ultima = cs[-1] if cs else VERMELHO
    proj = max(prob_cond[ultima], key=prob_cond[ultima].get)
    return dict(proj=proj, p_proj=prob_cond[ultima][proj],
                cond=prob_cond, base=NOME[proj])


def frequencia_numeros(nums, janela=200):
    """Os numeros mais quentes determinam a cor dominante? metricas simples."""
    w = nums[-janela:]
    cn = Counter(w)
    cor_soma = {0: 0, 1: 0, 2: 0}
    for num, k in cn.items():
        cor_soma[cor(num)] += k
    dom = max(cor_soma, key=cor_soma.get)
    return dict(cor_soma=cor_soma, dom=dom, p_dom=cor_soma[dom] / sum(cor_soma.values()),
                NOME_dom=NOME[dom])


def white_gap(nums):
    """Gaps entre brancos + historico de horarios de saida do branco."""
    idx = [i for i, n in enumerate(nums) if n == 0]
    gaps = [idx[i + 1] - idx[i] for i in range(len(idx) - 1)]
    return dict(gaps=gaps, n_brancos=len(idx),
                gap_medio=sum(gaps) / len(gaps) if gaps else 0,
                gap_max=max(gaps) if gaps else 0,
                atraso=(len(nums) - 1 - idx[-1]) if idx else len(nums))


def resumo_completo(nums, horarios=None):
    """Agrega todas as metricas numa string + dict."""
    if len(nums) < 15:
        return None
    out = {}
    out["nums_total"] = len(nums)
    out["zipf"] = zipf_stats(nums)
    out["momentum"] = segs_momento(nums)
    out["white"] = white_gap(nums)
    out["freq_num"] = frequencia_numeros(nums)
    out["markov"] = markov(nums)
    if horarios:
        out["tecnicas"] = tecnicas(nums, horarios)

    # texto humano
    L = []
    z = out["zipf"]
    L.append(f"Numeros na janela: {z['n']}")
    L.append(f"Quentes: {' '.join(str(x) for x in z['quentes'])}   Frios: {' '.join(str(x) for x in z['frios'])}")
    L.append(f"Chi-quadrado uniforme: {z['chi']:.1f} (p={z['p']:.3f}) -> {'compativel com aleatorio' if z['p'] > 0.05 else 'desvio do aleatorio'}")
    m = out["momentum"]
    L.append(f"Streak atual: {NOME[m['atual_cor']]}x{m['atual_tam']} | maiores historicamente: V={m['best'][1]} P={m['best'][2]} B={m['best'][0]}")
    w = out["white"]
    L.append(f"Brancos: {w['n_brancos']} | gap medio {w['gap_medio']:.1f} | max {w['gap_max']} | atraso atual {w['atraso']}")
    f = out["freq_num"]
    L.append(f"Cor dominante por soma de numeros: {f['NOME_dom']} ({f['p_dom']*100:.0f}%)")
    mk = out["markov"]
    L.append(f"Markov 1a ordem (projecao mais provavel): {mk['base']} em {mk['p_proj']*100:.1f}%")
    out["texto"] = "\n".join(L)
    return out


def wilson(p, n, z=1.96):
    """Intervalo de confianca Wilson p/ proporcao."""
    if n == 0:
        return 0, 0
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    e = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - e), min(1, c + e)


def tecnica_vencedora(tec):
    """Compara tecnicas vs baseline com Wilson; retorna ranking."""
    if not tec:
        return []
    rank = []
    for k, v in tec.items():
        if k in ("baseline_cor", "baseline"):
            continue
        n = 200  # holdout aproximado
        lo, hi = wilson(v, 120)
        rank.append((v, k, lo, hi, tec["baseline"], k))
    rank.sort(reverse=True)
    return rank