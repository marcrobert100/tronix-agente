# -*- coding: utf-8 -*-
"""
TRONIX PROJECAO — engine de previsao Double com APRENDIZADO ONLINE.
Multi-timeframe Markov + EWMA + vies de transicao + metade de pintura + horario,
combinadas por pesos ADAPTATIVOS aprendidos dos acertos reais (decay exponencial).

A cada resultado novo, sobe o peso das tecnicas que acertaram e abaixa das que
erraram. Confianca calibrada pela frequencia de acerto rolante. <1ms por poll.

Uso:
    from tronix_projecao import PrevisorAprendiz
    p = PrevisorAprendiz.carregar()   # ou PrevisorAprendiz()
    r = p.prever(nums, horas)
    p.aprender(num_saiu)              # feedback apos cada rodada real (LIVE)
    p.salvar()
"""
from collections import Counter
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 0 = BRANCO, 1 = VERMELHO, 2 = PRETO
CORES = {0: 0,
         1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1,
         8: 2, 9: 2, 10: 2, 11: 2, 12: 2, 13: 2, 14: 2}
NOME = {0: "BRANCO", 1: "VERMELHO", 2: "PRETO"}

JANELAS = [15, 30, 60, 120]
DECAY = 0.94           # peso exponencial dos resultados dentro de cada janela
ALPHA = 0.12           # taxa de aprendizado (0.12 = responde rapido ao drift)
CALIBRA = 160          # janela de calibracao da confianca

TECNICAS = ["multi_window", "ewma", "vies_transicao",
            "metade_pintura", "horario", "frio_cedo",
            "segundo_grau"]
ARQ_CEREBRO = BASE / "blaze_cerebro.json"


def cor(n):
    return CORES[n]


class PrevisorAprendiz:
    def __init__(self, pesos=None):
        self._pesos = dict(pesos or {t: 1.0 for t in TECNICAS})
        # (acertos, tentativas) por tecnica — com esquecimento exponencial
        self._ac = {t: 0.0 for t in TECNICAS}
        self._tt = {t: 0.0 for t in TECNICAS}
        self._conf = []            # [[pred, acertou], ...] janela de calibracao
        self._last_probs = {}      # probs ponderadas da ultima previsao
        self._last_preds = {}      # pred por tecnica (p/ re-ponderar)
        self._n = 0

    # ------------------------------------------------------------ persistencia
    def salvar(self, path=None):
        try:
            path = path or ARQ_CEREBRO
            path.write_text(json.dumps({
                "pesos": self._pesos,
                "ac": self._ac,
                "tt": self._tt,
                "conf": self._conf[-CALIBRA * 3:],
                "n": self._n,
            }, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def carregar(cls, path=None):
        p = cls()
        try:
            path = path or ARQ_CEREBRO
            if path.exists():
                d = json.loads(path.read_text(encoding="utf-8"))
                pes = d.get("pesos", {})
                for t in TECNICAS:
                    if t in pes:
                        p._pesos[t] = float(pes[t])
                ac = d.get("ac", {})
                tt = d.get("tt", {})
                for t in TECNICAS:
                    p._ac[t] = float(ac.get(t, 0.0)) if t in ac else 0.0
                    p._tt[t] = float(tt.get(t, 0.0)) if t in tt else 0.0
                p._conf = list(d.get("conf", []))
                p._n = int(d.get("n", 0))
        except Exception:
            pass
        return p

    def reset(self):
        self._pesos = {t: 1.0 for t in TECNICAS}
        self._ac = {t: 0.0 for t in TECNICAS}
        self._tt = {t: 0.0 for t in TECNICAS}
        self._conf = []
        self._last_probs = {}
        self._n = 0
        self.salvar()

    # ------------------------------------------------------- tecnicas internas
    def _transicoes(self, cs, decay=1.0):
        t = {0: {0: 0.0, 1: 0.0, 2: 0.0},
             1: {0: 0.0, 1: 0.0, 2: 0.0},
             2: {0: 0.0, 1: 0.0, 2: 0.0}}
        d = decay
        for i in range(len(cs) - 1, 0, -1):
            t[cs[i - 1]][cs[i]] += d
            d *= decay
        return t

    def _prob_from(self, t, ult):
        tot = sum(t[ult].values())
        if not tot:
            return {0: 1 / 3, 1: 1 / 3, 2: 1 / 3}
        return {b: t[ult][b] / tot for b in t[ult]}

    @staticmethod
    def _best(probs):
        pred = max(probs, key=probs.get)
        return pred, probs

    def _tec_multi_window(self, cs):
        votes = {0: 0.0, 1: 0.0, 2: 0.0}
        for j in JANELAS:
            if len(cs) < j + 1:
                continue
            t = self._transicoes(cs[-j - 1:], DECAY)
            p = self._prob_from(t, cs[-1])
            for b in p:
                votes[b] += p[b]
        tot = sum(votes.values()) or 1
        probs = {b: votes[b] / tot for b in votes}
        return self._best(probs)

    def _tec_ewma(self, cs):
        if len(cs) < 20:
            return 1, {0: 1 / 3, 1: 1 / 3, 2: 1 / 3}
        t = self._transicoes(cs, DECAY)
        return self._best(self._prob_from(t, cs[-1]))

    def _tec_vies_transicao(self, cs):
        if len(cs) < 30:
            return self._tec_multi_window(cs)
        t = self._transicoes(cs, 1.0)   # sem decay: frequencia bruta
        return self._best(self._prob_from(t, cs[-1]))

    def _tec_metade_pintura(self, nums):
        if not nums:
            return 1, {0: 1 / 3, 1: 1 / 3, 2: 1 / 3}
        v = CORES[nums[-1]]
        if v == 0:
            # apos branco a pintura "resetou": favorece a cor anterior dominante
            for x in reversed(nums[:-1]):
                if CORES[x] != 0:
                    v = CORES[x]
                    break
            if v == 0:
                v = 1
        rep = 1
        for x in reversed(nums[:-1]):
            if CORES[x] == v:
                rep += 1
            else:
                break
        alt = 1 if v == 2 else 2
        if rep >= 3:
            probs = {0: 0.18, v: 0.30, alt: 0.52}
        else:
            probs = {0: 0.15, v: 0.55, alt: 0.30}
        return self._best(probs)

    def _tec_horario(self, nums, horas):
        cs = [CORES[n] for n in nums]
        if not horas or len(nums) != len(horas) or len(nums) < 40:
            return self._tec_multi_window(cs)
        h_atual = ""
        try:
            h_atual = (horas[-1] or "")[:2]
        except Exception:
            pass
        if not h_atual:
            return self._tec_multi_window(cs)
        cb = {0: 0, 1: 0, 2: 0}
        n = 0
        for h, c in zip(horas, cs):
            if (h or "")[:2] == h_atual:
                n += 1
                cb[c] += 1
        if n < 2:
            return self._tec_multi_window(cs)
        probs = {b: (cb[b] + 1) / (n + 3) for b in (0, 1, 2)}
        return self._best(probs)

    def _tec_frio_cedo(self, nums):
        cs = [CORES[n] for n in nums]
        if len(cs) < 50 or cs[-1] == 0:
            return self._tec_multi_window(cs)
        v = cs[-1]
        rep = 1
        for x in reversed(cs[:-1]):
            if x == v:
                rep += 1
            else:
                break
        alt = 1 if v == 2 else 2
        if rep >= 6:
            probs = {0: 0.22, v: 0.23, alt: 0.55}
        else:
            probs = {0: 0.15, v: 0.60, alt: 0.25}
        return self._best(probs)

    # ------------------------------------------------------- combinacao
    def _tec_cadeia2(self, cs):
        """Markov de ORDEM 2 — o padrao mais forte em Double: transicoes de
        PAIR (cs[-2], cs[-1]) -> proxima cor, com decay temporal."""
        if len(cs) < 15:
            return self._tec_multi_window(cs)
        par = (cs[-2], cs[-1])
        # t2[par][next] com decay
        t2 = {0: 0.0, 1: 0.0, 2: 0.0}
        d = 1.0
        for i in range(len(cs) - 2, 0, -1):
            if (cs[i - 1], cs[i]) == par:
                t2[cs[i + 1]] += d
                d *= 0.98
        tot = sum(t2.values()) or 1
        # prior uniforme misturado p/ nao colapsar em zero martelo
        probs = {b: (t2[b] + 1.0) / (tot + 3.0) for b in (0, 1, 2)}
        return self._best(probs)

    def _gerar_probs_tecnicas(self, nums, horas):
        cs = [CORES[n] for n in nums]
        out = {
            "multi_window": self._tec_multi_window(cs),
            "ewma": self._tec_ewma(cs),
            "vies_transicao": self._tec_vies_transicao(cs),
            "metade_pintura": self._tec_metade_pintura(nums),
            "horario": self._tec_horario(nums, horas),
            "frio_cedo": self._tec_frio_cedo(nums),
            "segundo_grau": self._tec_cadeia2(cs),
        }
        return out

    def prever(self, nums, horas=None):
        if len(nums) < 20:
            return dict(pred=1, nome="VERMELHO", conf=0.0, score=0.0,
                        metodo="dados_insuficientes", nivel="INS.",
                        acertos={}, pesos=dict(self._pesos),
                        probs={}, tecnicas={}, calibradas={},
                        top_tec="", gap_tecs=0.0)
        cs = [CORES[n] for n in nums]
        tecs = self._gerar_probs_tecnicas(nums, horas)
        soma = {0: 0.0, 1: 0.0, 2: 0.0}
        for nome, (_, probs) in tecs.items():
            w = self._pesos.get(nome, 1.0)
            for b in soma:
                soma[b] += probs[b] * w
        tot = sum(soma.values()) or 1
        probs = {b: soma[b] / tot for b in soma}
        pred = max(probs, key=probs.get)
        self._last_probs = dict(probs)
        self._last_preds = {nome: tc[0] for nome, tc in tecs.items()}

        calib = self._calibrar(probs)
        conf = min(1.0, max(0.0, calib.get(pred, probs[pred])))
        score = min(1.0, probs[pred] * 0.6 + conf * 0.4)
        if score >= 0.70:
            nivel = "FORTE"
        elif score >= 0.55:
            nivel = "MODERADO"
        else:
            nivel = "FRACO"

        # destaca a tecnica de maior peso relativo
        pesos_norm = {k: self._pesos[k] / sum(self._pesos.values())
                      for k in self._pesos}
        top_tec = max(pesos_norm, key=pesos_norm.get)
        # gap entre maior e segunda maior probabilidade
        ordenadas = sorted(probs.values(), reverse=True)
        gap = (ordenadas[0] - ordenadas[1]) if len(ordenadas) > 1 else 0.0

        return dict(
            pred=pred, nome=NOME[pred], conf=conf, score=score, nivel=nivel,
            metodo=f"W-ENSEMBLE {len(tecs)} tecnicas (pesos aprendidos)",
            acertos=dict(self._acuraria()),
            pesos=dict(self._pesos),
            probs={NOME[b]: round(probs[b], 4) for b in probs},
            tecnicas={k: {"pred": v[0], "probs": {NOME[b]: round(v[1][b], 4)
                     for b in v[1]}} for k, v in tecs.items()},
            calibradas=calib,
            top_tec=top_tec, gap_tecs=gap,
        )

    def _calibrar(self, probs):
        if not self._conf:
            return probs
        tent = Counter()
        acert = Counter()
        for pred, ok in self._conf[-CALIBRA:]:
            tent[pred] += 1
            if ok:
                acert[pred] += 1
        out = {}
        for b in (0, 1, 2):
            tn = tent[b]
            if tn >= 5:
                out[b] = acert[b] / tn
            else:
                out[b] = probs[b]
        return out

    def aprender(self, num_saiu):
        """Feedback: num_saiu = numero REAL que saiu. Re-pondera tecnicas."""
        if not self._last_probs:
            return
        alvo = CORES[num_saiu]
        # calibracao
        pred = max(self._last_probs, key=self._last_probs.get)
        self._conf.append([pred, 1 if pred == alvo else 0])
        self._conf = self._conf[-CALIBRA * 3:]

        # esquecimento exponencial + atualizacao de acertos por tecnica
        g = 1 - ALPHA
        for nome in TECNICAS:
            self._ac[nome] = self._ac[nome] * g
            self._tt[nome] = self._tt[nome] * g
            self._tt[nome] += 1.0
            if self._last_preds.get(nome) == alvo:
                self._ac[nome] += 1.0
        self._n += 1

        # re-pondera conforme taxa de acerto acima/abaixo do aleatorio (33%)
        for nome in TECNICAS:
            taxa = self._ac[nome] / self._tt[nome] if self._tt[nome] else 0.34
            excesso = taxa - 0.34
            self._pesos[nome] = max(0.25, min(2.2, 1.0 + excesso * 5))
        self.salvar()

    def _acuraria(self):
        out = {}
        for nome in TECNICAS:
            out[nome] = self._ac[nome] / self._tt[nome] if self._tt[nome] else 0.34
        return out

    def historico_acertos(self, nums, horas=None, janela=100):
        if len(nums) < 30:
            return 0, 0, 0.0, {}
        ac, tt = 0, 0
        for i in range(max(20, len(nums) - janela), len(nums) - 1):
            r = self.prever(nums[:i + 1], horas[:i + 1] if horas else None)
            if r["pred"] == CORES[nums[i + 1]]:
                ac += 1
            tt += 1
        return ac, tt, ac / tt if tt else 0.0, self._acuraria()


# compat v3: previsao simples (carrega o cerebro aprendido)
def prever(nums, horas=None):
    p = PrevisorAprendiz.carregar()
    return p.prever(nums, horas)