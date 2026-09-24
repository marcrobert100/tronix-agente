# -*- coding: utf-8 -*-
"""
TRONIX BLAZE SIMULATOR v4 - Desktop app
Analise de padroes Double (Blaze), SUPER ALERTA BRANCO (multi-sinal),
previsao, simulador de estrategia. LIVE via BestBlaze (publico, sem login).
Persistencia unica alinhada nums+horas+ids (merge por ID, nunca corrompe).

Como usar:
  python tronix_blaze_simulator.py
"""
import json
import random
import threading
import time as _time
import tkinter as tk
import urllib.request
import urllib.parse
import http.cookiejar
import re
import winsound
from tkinter import ttk, messagebox
from collections import Counter
from pathlib import Path

import tronix_projecao as pj
import analise_blaze as ab

BASE = Path(__file__).resolve().parent
ARQ_DATA = BASE / "blaze_dataset.json"
ARQ_HIST = BASE / "blaze_historico.json"   # legado
ARQ_HORAS = BASE / "blaze_horas.json"      # legado

CORES = {0: "white", 1: "red", 2: "black"}
NOME_COR = {0: "BRANCO", 1: "VERMELHO", 2: "PRETO"}
COR_HEX = {0: "#f5f5f5", 1: "#e6342a", 2: "#1a1a1a"}
COR_HEX2 = {0: "#ffffff", 1: "#ff4d41", 2: "#2e2e3a"}
COR_TXT = {0: "#222222", 1: "#ffffff", 2: "#ffffff"}
COR_BAR = {0: "#c9c9c9", 1: "#e6342a", 2: "#3a3a44"}

BESTBLAZE_URL = "https://www.bestblaze.com.br/"
POLL_MS = 2000

BB_PAT = re.compile(
    r"bb-blaze-tile__box (\w?)rodada'?\"\s*>\s*<span class=\"num\">(\d+)</span>"
    r".*?bb-blaze-tile__time\">([^<]+)<", re.S)


class BestBlaze:
    """Acesso tempo real ao historico Double via POST /jogadasDouble (poll ~2s).
    Sessao urllib + cookie jar + token CSRF, revalidado quando expira."""

    def __init__(self):
        self._jar = None
        self._token = None

    def _sessao(self):
        if self._jar is None:
            self._jar = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        return self._jar

    def _get_token(self):
        op = self._sessao()
        try:
            req = urllib.request.Request(BESTBLAZE_URL, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            html = op.open(req, timeout=25).read().decode("utf-8", errors="replace")
            m = re.search(r"_token'?\s*:\s*'([^']+)'", html)
            if m:
                self._token = m.group(1)
                return True
        except Exception:
            pass
        return False

    def _post(self, ini):
        if not self._token:
            self._get_token()
        if not self._token:
            return []
        op = self._sessao()
        body = urllib.parse.urlencode({"ini": ini, "_token": self._token}).encode()
        req = urllib.request.Request("https://www.bestblaze.com.br/jogadasDouble",
                                     data=body, headers={
                                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                                         "Content-Type": "application/x-www-form-urlencoded",
                                         "X-Requested-With": "XMLHttpRequest",
                                         "Referer": BESTBLAZE_URL})
        try:
            with op.open(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception as e:
            self._token = None
            if "expired" in str(e).lower() or "[Errno" in str(e):
                raise
            return []

    def iniciais(self):
        d = self._post("1")
        if not d:
            raise RuntimeError("BestBlaze: sem resposta inicial")
        rodadas = sorted(d, key=lambda x: int(x["id_rodadas_double"]))
        nums = [int(r["numero"]) for r in rodadas]
        ids = [int(r["id_rodadas_double"]) for r in rodadas]
        horas = [self._hora_str(r) for r in rodadas]
        return nums, ids, horas

    def _hora_str(self, r):
        h = r.get("horario") or ""
        if len(h) == 8 and ":" in h:
            return h
        t = str(r.get("time") or "")
        return t[11:19] if len(t) >= 19 else h

    def novas(self, last_id):
        d = self._post(str(last_id))
        if not d:
            return []
        rodadas = sorted(d, key=lambda x: int(x["id_rodadas_double"]))
        out = []
        for r in rodadas:
            i = int(r["id_rodadas_double"])
            if i > last_id:
                out.append((int(r["numero"]), i, self._hora_str(r)))
        return out


def baixar_bestblaze_antigo():
    req = urllib.request.Request("https://www.bestblaze.com.br/doubleRodadasDia",
                                 headers={"User-Agent":
                                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        html = r.read().decode("utf-8", errors="replace")
    tmp = BB_PAT.findall(html)
    nums = [int(n) for _, n, _ in tmp]
    nums.reverse()
    return nums


def ler_numeros(texto):
    nums = []
    for tok in texto.replace(",", " ").split():
        tok = tok.strip()
        if not tok:
            continue
        try:
            n = int(tok)
            if 0 <= n <= 14:
                nums.append(n)
        except ValueError:
            pass
    return nums


def cor_num(n):
    if n == 0:
        return 0
    return 1 if 1 <= n <= 7 else 2


DEMO = [4, 7, 1, 14, 0, 3, 12, 2, 9, 5, 0, 11, 8, 1, 13, 6, 10, 0, 4, 7, 2, 14, 9, 3, 1, 5, 0, 12, 8, 6, 11]


def simular_estrategia(nums, modo, alvo=14):
    """Simula resultado da estrategia no historico: modo 'seguir' ou 'quebrar'.
    Regra: aposta 1 unidade; se acertar +1; se errar dobra (martingale) ate alvo.
    Retorna (saldo_final, acertos, erros, pico, drawdown)."""
    seq = [cor_num(n) for n in nums]
    saldo, acerto, erro = 0.0, 0, 0
    aposta = 1.0
    pico, dd = 0.0, 0.0
    prev = seq[0]
    for c in seq[1:]:
        if prev == 0:
            prev = c
            continue
        if modo == "seguir":
            previsao = prev
        else:
            previsao = 1 if prev == 2 else 2
        if c == previsao:
            saldo += aposta
            acerto += 1
            aposta = 1.0
        else:
            saldo -= aposta
            erro += 1
            aposta = min(aposta * 2, 2 ** alvo)
        pico = max(pico, saldo)
        dd = max(dd, pico - saldo)
        prev = c
    return saldo, acerto, erro, pico, dd


def analisar(nums, janela=None):
    if not nums:
        return None
    seq = [cor_num(n) for n in nums]
    total_cor = Counter(seq)
    freq_num = Counter(nums)
    recente = seq[-80:]
    r_num = nums[-80:]
    sr = [cor_num(n) for n in r_num]
    sr_counter = Counter(sr)
    seqs = []
    cur, tam = sr[0], 1
    for i in range(1, len(sr)):
        if sr[i] == cur:
            tam += 1
        else:
            seqs.append((cur, tam))
            cur, tam = sr[i], 1
    seqs.append((cur, tam))
    maior = max((s for s in seqs if s[0] != 0), key=lambda s: s[1], default=(0, 0))
    repet = seqs[-1][1] if seqs else 1
    idx0 = [i for i, c in enumerate(sr) if c == 0]
    gaps = [idx0[i + 1] - idx0[i] for i in range(len(idx0) - 1)] if len(idx0) > 1 else []
    idx0t = [i for i, c in enumerate(seq) if c == 0]
    gap_hist = [idx0t[i + 1] - idx0t[i] for i in range(len(idx0t) - 1)] if len(idx0t) > 1 else gaps
    gap_medio = sum(gap_hist) / len(gap_hist) if gap_hist else 0
    t = sum(total_cor.values())
    prob = {c: total_cor[c] / t for c in (0, 1, 2)} if t else {0: 0, 1: 0, 2: 0}
    freq_num_recente = Counter(r_num)
    quentes = [n for n, _ in freq_num_recente.most_common(5)]
    if idx0:
        desde_branco = len(sr) - 1 - idx0[-1]
    else:
        desde_branco = len(sr)
    devendo = gap_medio and desde_branco >= gap_medio * 1.35
    ult = sr[-1]
    sugestao = "AGUARDAR - saiu branco, esperar definir tendencia" if ult == 0 else (
        f"Sequencia {repet}x PRETA. Opcao: seguir preta (1.5x) OU quebrar em vermelha (7x)." if ult == 2
        else f"Sequencia {repet}x VERMELHA. Opcao: seguir vermelha (1.5x) OU quebrar em preta (7x).")
    return dict(seq=seq, recente=r_num, sr=sr, seqs=seqs, maior=maior, repet=repet,
                gaps=gaps, gap_medio=gap_medio, devendo=devendo, desde_branco=desde_branco,
                prob=prob, freq_num=freq_num, total_cor=total_cor, sugestao=sugestao,
                quentes=quentes, freq_num_recente=freq_num_recente)


# ---------------------------------------------------------------- SUPER ALERTA
def _median(lst):
    if not lst:
        return 0
    s = sorted(lst)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def _stdev(lst):
    if len(lst) < 2:
        return 0.0
    m = sum(lst) / len(lst)
    return (sum((x - m) ** 2 for x in lst) / (len(lst) - 1)) ** 0.5


def _freq_branco_hora(horas, cor_seq):
    """Frequencia relativa de branco por hora do dia (janela 60min)."""
    if len(horas) != len(cor_seq) or not horas:
        return 0.5, 0
    ct = Counter()
    cb = Counter()
    for h, c in zip(horas, cor_seq):
        if len(h) >= 5:
            chave = h[:2]  # hora
            ct[chave] += 1
            if c == 0:
                cb[chave] += 1
    hora_atual = _time.strftime("%H")
    if ct.get(hora_atual, 0) >= 3 and ct[hora_atual] > 0:
        return cb[hora_atual] / ct[hora_atual], ct[hora_atual]
    return 0.5, 0


def analisar_branco(nums, horas=None):
    """SUPER sinal de branco. Combina varios indicadores -> score 0..1 + nivel."""
    n = len(nums)
    if n < 20:
        return dict(score=0.0, nivel="NORMAL", sinais=[],
                    atraso=n, gap_medio=15.0, gap_max=0, devendo=False,
                    p_geo=1.0 / 15, p_sobrev=1.0, n_brancos=0,
                    streak=0, mancha_media=0.0, fhora=0.5)
    seq = [cor_num(x) for x in nums]
    idx = [i for i, c in enumerate(seq) if c == 0]
    atraso = n - 1 - idx[-1] if idx else n
    n_brancos = len(idx)
    gaps = [idx[i + 1] - idx[i] for i in range(len(idx) - 1)] if len(idx) > 1 else []
    gm = sum(gaps) / len(gaps) if gaps else 15.0
    gmed = _median(gaps) if gaps else 15.0
    gmax = max(gaps) if gaps else 0
    gstd = _stdev(gaps) if gaps else 0.0

    # 1) Probabilidade geometrica (modelo i.i.d., 1/15) acumulada
    p_base = 1 / 15.0
    p_sobrev = (1 - p_base) ** atraso          # chance de ainda nao ter saido
    s_sobrev = 1.0 - p_sobrev                  # chance acumulada de "já deveria"

    # 2) Atraso vs medio (empirico)
    s_atraso = 0.0
    if gmed > 0:
        s_atraso = max(0.0, (atraso - gmed) / gmed)
        s_atraso = min(1.0, s_atraso)
    # 3) Streak atual da cor dominante (empirico: brancos prefiram depois de mancha)
    streak = 1
    for c in reversed(seq):
        if c == seq[-1] and seq[-1] != 0:
            if c == seq[-1]:
                streak += 1
            else:
                break
        else:
            break
    streak -= 1
    # media de manchas que precedem branco
    manchas = []
    for j in range(len(idx) - 1):
        run = 0
        for k in range(idx[j] + 1, idx[j + 1]):
            run += 1
        manchas.append(run)
    mancha_media = sum(manchas) / len(manchas) if manchas else 8.0
    s_streak = min(1.0, streak / (mancha_media * 1.4)) if streak > 0 and mancha_media > 0 else 0.0

    # 4) Frequencia de branco na hora atual (se horas disponiveis)
    fhora, nfh = _freq_branco_hora(horas, seq)
    # normalizar fhora em relacao a 1/15
    s_hora = max(0.0, min(1.0, (fhora - p_base) / p_base))

    sinais = [
        ("acumulado de sobrevivencia", s_sobrev, 0.42),
        ("atraso vs gap medio", s_atraso, 0.28),
        ("mancha atual pode preceder branco", s_streak, 0.18),
        ("freq. branco na hora atual", s_hora if nfh >= 3 else 0.0, 0.12),
    ]
    score = sum(v * w for _, v, w in sinais)
    devendo = atraso >= gmed * 1.35
    if devendo:
        score = max(score, 0.55)
    if score >= 0.85:
        nivel = "BRANCO IMINENTE"
    elif score >= 0.70:
        nivel = "CRITICO"
    elif score >= 0.55:
        nivel = "ATENCAO"
    else:
        nivel = "NORMAL"
    return dict(score=score, nivel=nivel, sinais=sinais, atraso=atraso,
                gap_medio=gm, gap_max=gmax, devendo=devendo,
                p_geo=p_base, p_sobrev=p_sobrev, n_brancos=n_brancos,
                streak=streak, mancha_media=mancha_media, fhora=fhora)


class BlazeSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TRONIX BLAZE v4 - SUPER ALERTA BRANCO")
        self.geometry("1280x880")
        self.configure(bg="#0d0d12")
        self.nums, self.horas, self.ids = self._carregar_dataset()
        if not self.nums:
            self.nums = list(DEMO)
            self.horas = []
            self.ids = []
        self.live_on = False
        self.som_on = True
        self._ultimo_num = self.nums[-1] if self.nums else None
        self.janela_opcao = tk.StringVar(value="80")
        self.pred_cor = None
        self.pred_pct = 0.0
        self.pred_motivo = ""
        self.pred_score = 0.0
        self.pred_visivel = True
        self._flash_job = None
        self._last_pred = None
        self._hits = 0
        self._tries = 0
        self._beep_vivo = False
        self._warn_cor = None
        self._warn_frame = None
        self._warn_label = None
        self._warn_sub = None
        self._warn_visivel = True
        self._warn_flash_job = None
        self._warn_level = ""
        self.cerebro = pj.PrevisorAprendiz.carregar()
        self._build()
        self.atualizar()
        self._flasher()
        self._warn_flasher()
        self.after(600, self.toggle_live)

    # ----------------------------------------------------------- persistencia
    def _carregar_dataset(self):
        if ARQ_DATA.exists():
            try:
                d = json.loads(ARQ_DATA.read_text(encoding="utf-8"))
                nums = list(d.get("nums", []))
                horas = list(d.get("horas", []))
                ids = list(d.get("ids", []))
                return nums, horas, ids
            except Exception:
                pass
        # legado
        nums = []
        horas = []
        if ARQ_HIST.exists():
            try:
                nums = list(json.loads(ARQ_HIST.read_text(encoding="utf-8")))
            except Exception:
                nums = []
        if ARQ_HORAS.exists():
            try:
                horas = list(json.loads(ARQ_HORAS.read_text(encoding="utf-8")))
            except Exception:
                horas = []
        if horas and len(horas) != len(nums):
            horas = horas[:len(nums)]
        ids = []
        # legado corrompido (nums<20 sem ids): descartar, LIVE recaptura
        if len(nums) < 20:
            return [], [], []
        return nums, horas, ids

    def _salvar_dataset(self):
        try:
            n = list(self.nums[-2000:])
            hn = len(n)
            h = list(self.horas[-2000:])[-hn:]
            i = list(self.ids[-2000:])[-hn:]
            # garantir alinhamento estrito nums/horas/ids
            if len(h) != hn:
                h = ["11:00:00"] * hn
            if len(i) != hn:
                i = list(range(-hn, 0))
            ARQ_DATA.write_text(json.dumps(
                {"nums": n, "horas": h, "ids": i}, ensure_ascii=False), encoding="utf-8")
            # legado tambem (compat)
            ARQ_HIST.write_text(json.dumps(n), encoding="utf-8")
            (BASE / "blaze_horas.json").write_text(
                json.dumps(h, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _beep(self, modo):
        if not self.som_on:
            return
        try:
            if modo == "novo":
                winsound.Beep(900, 50)
            elif modo == "branco_saiu":
                winsound.Beep(700, 220)
                winsound.Beep(950, 220)
            elif modo == "branco_atencao":
                winsound.Beep(660, 140)
            elif modo == "branco_critico":
                winsound.Beep(780, 200)
                winsound.Beep(520, 200)
            elif modo == "branco_iminente":
                winsound.Beep(880, 160)
                winsound.Beep(1160, 160)
                winsound.Beep(880, 160)
                winsound.Beep(1160, 240)
        except Exception:
            pass

    # ---------------------------------------------------------------- LIVE
    def toggle_live(self):
        if self.live_on:
            self.live_on = False
            self.btn_live.config(text="AO VIVO (BestBlaze)")
            self.status.config(text="LIVE desativado.")
            return
        self.live_on = True
        self.btn_live.config(text="AO VIVO ... ON")
        self.bb = BestBlaze()
        self._last_id = 0
        threading.Thread(target=self._live_loop, daemon=True).start()

    def _live_loop(self):
        try:
            nums, ids, horas = self.bb.iniciais()
            hist = list(self.nums)
            hhist = list(self.horas)
            ihist = list(self.ids)
            # merge por ID (robusto, nunca duplica nem corrompe)
            if ihist:
                ult_id = ihist[-1]
                novos = [(ids[j], nums[j], horas[j])
                         for j in range(len(ids)) if ids[j] > ult_id]
                final = hist + [x[1] for x in novos]
                fhoras = hhist + [x[2] for x in novos]
                fids = ihist + [x[0] for x in novos]
            else:
                final, fids, fhoras = nums, ids, horas
            self.after(0, lambda f=final, h=fhoras, i=fids: self._set_nums(f, h, i))
            self._last_id = fids[-1] if fids else 0
        except Exception as e:
            self.after(0, lambda: self.status.config(
                text=f"LIVE erro init: {str(e)[:80]}"))
        while self.live_on:
            _time.sleep(POLL_MS / 1000)
            if not self.live_on:
                return
            try:
                novas = self.bb.novas(self._last_id)
                if novas:
                    novas.sort(key=lambda x: x[1])
                    self._last_id = novas[-1][1]
                    nums = [x[0] for x in novas]
                    ids = [x[1] for x in novas]
                    horas = [x[2] for x in novas]
                    self.after(0, lambda n=nums, i=ids, h=horas:
                               self._aplicar_live_batch(n, i, h))
            except Exception:
                try:
                    self.bb._token = None
                    nums, ids, horas = self.bb.iniciais()
                    self._last_id = ids[-1]
                except Exception:
                    pass

    def _set_nums(self, nums, horas, ids):
        self.nums = nums
        self.horas = horas
        self.ids = ids
        self._ultimo_num = self.nums[-1] if self.nums else None
        self._salvar_dataset()
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", " ".join(map(str, self.nums[-120:])))
        self.txt.see("end")
        self.status.config(text=f"[LIVE BestBlaze] {len(self.nums)} rodadas sincronizadas "
                               f"(tempo real, poll {POLL_MS // 1000}s)")
        self.atualizar()

    def _aplicar_live_batch(self, novos, ids, horas):
        if not novos:
            return
        pred_antes = self.pred_cor
        for i, n in enumerate(novos):
            self.nums.append(n)
            if i < len(ids):
                self.ids.append(ids[i])
            if i < len(horas):
                self.horas.append(horas[i])
            if pred_antes is not None:
                self._tries += 1
                if pred_antes == cor_num(n):
                    self._hits += 1
                self.cerebro.aprender(n)  # feedback: aprende com o resultado
            if n == 0:
                self._beep("branco_saiu")
        self._ultimo_num = self.nums[-1]
        self._salvar_dataset()
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", " ".join(map(str, self.nums[-120:])))
        self.txt.see("end")
        nova_txt = (f"[LIVE BestBlaze] {len(self.nums)} rodadas | "
                    f"ultimo: {NOME_COR[cor_num(self.nums[-1])]} #{self.nums[-1]}"
                    f" | +{len(novos)} novas")
        w = self._ultimo_analise_branco()
        if w and w["nivel"] in ("CRITICO", "BRANCO IMINENTE"):
            nova_txt += f" | *{w['nivel']}* score={w['score']*100:.0f}%"
            if w["nivel"] == "CRITICO":
                self._beep("branco_critico")
            else:
                self._beep("branco_iminente")
        elif w and w["nivel"] == "ATENCAO":
            self._beep("branco_atencao")
        self.status.config(text=nova_txt)
        self.atualizar()

    def _ultimo_analise_branco(self):
        if len(self.nums) < 20:
            return None
        return analisar_branco(self.nums, self.horas)

    def _alerta_deveria(self):
        a = analisar(self.nums)
        return bool(a and a["devendo"])

    # --------------------------------------------------------------- UI
    def _build(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("T.Label", background="#0d0d12", foreground="#e8e8e8", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#0d0d12", foreground="#e6342a", font=("Segoe UI", 16, "bold"))
        style.configure("Big.TLabel", background="#0d0d12", foreground="#ffffff", font=("Segoe UI", 12))
        style.configure("TFrame", background="#0d0d12")
        style.configure("Card.TFrame", background="#181820")
        style.configure("TButton", font=("Segoe UI", 10))

        top = ttk.Frame(self)
        top.pack(fill="x", padx=16, pady=(14, 6))
        ttk.Label(top, text="TRONIX BLAZE v4", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text="SUPER ALERTA BRANCO | previsao | padroes | estrategia | LIVE",
                  style="T.Label").pack(side="left", padx=12)
        self._som_var = tk.BooleanVar(value=self.som_on)
        ttk.Checkbutton(top, text="Som", variable=self._som_var,
                        command=self._toggle_som).pack(side="right")

        entrada = ttk.Frame(self)
        entrada.pack(fill="x", padx=16, pady=4)
        ttk.Label(entrada, text="Resultados (numeros 0-14 separados por espaco ou virgula):",
                  style="Big.TLabel").pack(anchor="w")
        self.txt = tk.Text(entrada, height=2, bg="#14141c", fg="#ffffff", insertbackground="#fff",
                           font=("Consolas", 12), relief="flat")
        self.txt.pack(fill="x", pady=(4, 6))
        self.txt.insert("1.0", " ".join(map(str, self.nums[-120:])))
        btns = ttk.Frame(entrada)
        btns.pack(fill="x")
        ttk.Button(btns, text="CARREGAR RESULTADOS", command=self.carregar).pack(side="left")
        ttk.Button(btns, text="Demo", command=self.add_demo).pack(side="left", padx=6)
        ttk.Button(btns, text="Limpar", command=self.limpar).pack(side="left")
        self.btn_live = ttk.Button(btns, text="AO VIVO (BestBlaze)", command=self.toggle_live)
        self.btn_live.pack(side="left", padx=6)
        ttk.Label(btns, text="Janela:", style="T.Label").pack(side="left", padx=(16, 2))
        for val in ("40", "80", "200", "tudo"):
            ttk.Radiobutton(btns, text=val, value=val, variable=self.janela_opcao,
                            command=lambda: self.atualizar()).pack(side="left")
        ttk.Label(btns, text=f"ultimo: {self.ult_resumo()}", style="T.Label").pack(side="right")

        # SUPER ALERTA BRANCO (pisca forte quando nivel sobe)
        self._warn_frame = tk.Frame(self, bg="#2a1a10", height=52)
        self._warn_frame.pack(fill="x", padx=16, pady=(2, 0))
        self._warn_frame.pack_propagate(False)
        self._warn_label = tk.Label(self._warn_frame,
                                    text="BRANCO: monitorando...",
                                    bg="#2a1a10", fg="#ffd700",
                                    font=("Segoe UI", 20, "bold"))
        self._warn_label.pack(anchor="w", padx=14, pady=(2, 0))
        self._warn_sub = tk.Label(self._warn_frame,
                                  text="gap medio - - | a atraso - | score -",
                                  bg="#2a1a10", fg="#c8a870",
                                  font=("Segoe UI", 10))
        self._warn_sub.pack(anchor="w", padx=16)

        self.pred_frame = tk.Frame(self, bg="#12121a", height=56)
        self.pred_frame.pack(fill="x", padx=16, pady=(2, 0))
        self.pred_frame.pack_propagate(False)
        self.pred_label = tk.Label(self.pred_frame, text="PROXIMO SORTEIO: --",
                                   bg="#12121a", fg="#5a5a66",
                                   font=("Segoe UI", 22, "bold"))
        self.pred_label.pack(anchor="w", padx=14, pady=(4, 0))
        self.pred_sub = tk.Label(self.pred_frame, text="sem dados",
                                 bg="#12121a", fg="#7a7a86",
                                 font=("Segoe UI", 10))
        self.pred_sub.pack(anchor="w", padx=16)

        self.grafico = tk.Canvas(self, bg="#101018", highlightthickness=0, height=120)
        self.grafico.pack(fill="x", padx=16, pady=(4, 0))
        self.grafico.bind("<Configure>", lambda e: self.atualizar())

        self.cards = ttk.Frame(self)
        self.cards.pack(fill="both", expand=True, padx=16, pady=6)
        self.stat_var = {}

        self.status = ttk.Label(self, text="", style="Big.TLabel")
        self.status.pack(anchor="w", padx=16, pady=(0, 8))

    def _toggle_som(self):
        self.som_on = not self.som_on

    def ult_resumo(self):
        if not self.nums:
            return "sem resultados"
        return f"{NOME_COR[cor_num(self.nums[-1])]} #{self.nums[-1]}"

    def carregar(self):
        nums = ler_numeros(self.txt.get("1.0", "end"))
        if not nums:
            messagebox.showwarning("TRONIX", "Nenhum numero valido (0-14) encontrado.")
            return
        self.nums = nums
        self.horas = []
        self.ids = []
        self._ultimo_num = nums[-1]
        self._salvar_dataset()
        self.atualizar()

    def add_demo(self):
        novo = []
        for _ in range(40):
            r = random.random()
            novo.append(random.randint(1, 14) if r > 0.05 else 0)
        self.nums = self.nums + novo
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", " ".join(map(str, self.nums)))
        self._salvar_dataset()
        self.atualizar()

    def limpar(self):
        self.nums = []
        self.horas = []
        self.ids = []
        self.txt.delete("1.0", "end")
        self.atualizar()

    def card(self, parent, titulo, texto_linhas, cor_titulo="#e6342a"):
        f = ttk.Frame(parent, style="Card.TFrame")
        ttk.Label(f, text=titulo, style="Big.TLabel", foreground=cor_titulo).pack(anchor="w", padx=10, pady=(8, 2))
        for l in texto_linhas:
            ttk.Label(f, text=l, style="T.Label", wraplength=380, justify="left").pack(anchor="w", padx=10)
        return f

    def _desenhar_grafico(self, recente, a):
        self.grafico.delete("all")
        w = self.grafico.winfo_width()
        h = self.grafico.winfo_height()
        if w < 40:
            return
        fr = a["freq_num_recente"] if a else Counter(recente)
        nb = 15
        bw = (w - 20) / nb
        maxc = max(fr.values()) if fr else 1
        for n in range(15):
            c = fr.get(n, 0)
            bh = (h - 30) * c / maxc
            x0 = 10 + n * bw
            colr = COR_BAR[cor_num(n)]
            self.grafico.create_rectangle(x0, h - 12 - bh, x0 + bw - 3, h - 12,
                                          fill=colr, outline="")
            self.grafico.create_text(x0 + bw / 2 - 1, h - 6, text=str(n),
                                     fill="#9a9aa5", font=("Segoe UI", 8))
            self.grafico.create_text(x0 + bw / 2 - 1, h - 16 - bh, text=str(c),
                                     fill="#d0d0da", font=("Segoe UI", 8, "bold"))
        if a and a["quentes"]:
            quentes = set(a["quentes"])
            for n in quentes:
                x0 = 10 + n * bw
                self.grafico.create_line(x0, h - 14, x0 + bw - 3, h - 14,
                                         fill="#ffd700", width=3)
        self.grafico.create_text(w - 8, 10, text="numeros quentes = ouro",
                                 fill="#ffd700", anchor="ne", font=("Segoe UI", 8))

    def _calibra_txt(self):
        """Taxa real de acerto das previsoes confiantes (calibracao)."""
        conf = self.cerebro._conf
        if not conf:
            return "ainda aprendendo"
        calib = self.cerebro._calibrar({0: 0.34, 1: 0.33, 2: 0.33})
        return "/".join(f"{NOME_COR[c]} {v*100:.0f}%" for c, v in calib.items())

    def _calcular_previsao(self, a):
        """Previsao via cerebro aprendido (W-ENSEMBLE) + sinal de branco dominante."""
        if len(self.nums) < 20:
            self.pred_cor = None
            self.pred_pct = 0.0
            self.pred_motivo = "dados insuficientes (<20)"
            self.pred_score = 0.0
            return
        try:
            horas = self.horas if len(self.horas) == len(self.nums) else None
            r = self.cerebro.prever(self.nums, horas)
        except Exception as e:
            self.pred_cor = None
            self.pred_motivo = f"erro: {str(e)[:40]}"
            self.pred_score = 0.0
            return
        w = analisar_branco(self.nums, self.horas)
        probs = r["probs"]
        if w["score"] >= 0.70:
            # branco domina a previsao quando sinal muito alto
            self.pred_cor = 0
            self.pred_pct = w["score"] * 100
            self.pred_score = w["score"]
            self.pred_motivo = (f"{w['nivel']} | BRANCO domina ensemble\n"
                                f"sinal sobrevivencia {w['sinais'][0][1]*100:.0f}% | "
                                f"atraso {w['atraso']} (medio {w['gap_medio']:.0f}) | "
                                f"pesos aprendidos: {self._str_pesos()}")
        else:
            self.pred_cor = r["pred"]
            self.pred_pct = r["conf"] * 100
            self.pred_score = r["score"]
            self.pred_motivo = (f"{r['nivel']} | {r['metodo']} | pega {r['top_tec']}\n"
                                f"VERMELHO {probs.get('VERMELHO',0)*100:.0f}%  "
                                f"PRETO {probs.get('PRETO',0)*100:.0f}%  "
                                f"BRANCO {probs.get('BRANCO',0)*100:.0f}% | "
                                f"gap {r['gap_tecs']*100:.1f}pp | pesos: {self._str_pesos()}")
        self.pred_label.config(text=f"PROXIMO: {NOME_COR[self.pred_cor]}  {self.pred_pct:.0f}%")
        self.pred_sub.config(text=self.pred_motivo)

    def _str_pesos(self):
        ps = self.cerebro._pesos
        top = sorted(ps.items(), key=lambda x: -x[1])[:2]
        return " / ".join(f"{t}={v:.2f}" for t, v in top)

    def _flasher(self):
        if self._flash_job:
            try:
                self.after_cancel(self._flash_job)
            except Exception:
                pass
        self.pred_visivel = not self.pred_visivel
        try:
            if self.pred_cor is not None:
                conf = self.pred_score
                rate = max(220, 450 - int(conf * 400))
                if self.pred_visivel:
                    hexc = COR_HEX2.get(self.pred_cor, COR_HEX[self.pred_cor])
                    txtc = COR_TXT[self.pred_cor]
                else:
                    hexc = "#0e0e14"
                    txtc = "#4a4a55"
                self.pred_frame.configure(bg=hexc)
                self.pred_label.configure(bg=hexc, fg=txtc)
                self.pred_sub.configure(bg=hexc, fg=txtc)
                self._flash_job = self.after(rate, self._flasher)
            else:
                self.pred_frame.configure(bg="#12121a")
                self.pred_label.configure(bg="#12121a", fg="#5a5a66")
                self.pred_sub.configure(bg="#12121a", fg="#7a7a86")
                self._flash_job = self.after(450, self._flasher)
        except Exception:
            try:
                self._flash_job = self.after(450, self._flasher)
            except Exception:
                pass

    def _warn_flasher(self):
        if self._warn_flash_job:
            try:
                self.after_cancel(self._warn_flash_job)
            except Exception:
                pass
        try:
            w = analisar_branco(self.nums, self.horas)
            nivel = w["nivel"]
            score = w["score"]
            atraso = w["atraso"]
            gm = w["gap_medio"]
            self._warn_level = nivel
            self._warn_visivel = not self._warn_visivel
            if nivel == "NORMAL":
                bg_a, bg_b, fg = "#2a1a10", "#2a1a10", "#ffd700"
                txt = (f"BRANCO: vigiando (score {score*100:.0f}% | "
                       f"atraso {atraso} | gap medio {gm:.0f} | "
                       f"{w['n_brancos']}x no historico)")
                rate = 600
            elif nivel == "ATENCAO":
                bg_a, bg_b, fg = "#3a2508", "#1c1204", "#ffb020"
                txt = (f"BRANCO: ATENCAO {score*100:.0f}% | "
                       f"atraso {atraso} rodadas (medio {gm:.0f})")
                rate = 340
            elif nivel == "CRITICO":
                bg_a, bg_b, fg = "#5a1c08", "#250a03", "#ff7043"
                txt = (f"BRANCO: CRITICO {score*100:.0f}% | "
                       f"DEVENDO | atraso {atraso} (medio {gm:.0f})")
                rate = 240
            else:
                self._beep_vivo = True
                bg_a, bg_b, fg = "#8a1507", "#1a0300", "#ff4d2e"
                txt = (f"!!! BRANCO IMINENTE {score*100:.0f}% !!! | "
                       f"atraso {atraso} rodadas PAGA 14x")
                rate = 140
            bg = bg_a if self._warn_visivel else bg_b
            self._warn_frame.configure(bg=bg)
            self._warn_label.configure(bg=bg, fg=fg)
            self._warn_sub.configure(bg=bg, fg=fg)
            self._warn_label.config(text=txt)
            self._warn_sub.config(text=" | ".join(
                f"{nome}: {v*100:.0f}%" for nome, v, _ in w["sinais"]))
            self._warn_flash_job = self.after(rate, self._warn_flasher)
        except Exception:
            try:
                self._warn_flash_job = self.after(600, self._warn_flasher)
            except Exception:
                pass

    def atualizar(self):
        for w in self.cards.winfo_children():
            w.destroy()
        if not self.nums:
            self.status.config(text="Sem dados. Cole resultados, adicione demo ou ligue o LIVE.")
            return
        opc = self.janela_opcao.get()
        data = self.nums if opc == "tudo" else self.nums[-int(opc):]
        a = analisar(data)
        if not a:
            return
        self._calcular_previsao(a)
        fr = a["freq_num_recente"]
        total = sum(a["total_cor"].values())
        fq = a["total_cor"]
        p_vm = fq.get(1, 0) / total * 100 if total else 0
        p_pt = fq.get(2, 0) / total * 100 if total else 0
        p_br = fq.get(0, 0) / total * 100 if total else 0

        self._desenhar_grafico(a["recente"], a)

        grid = ttk.Frame(self.cards)
        grid.pack(fill="both", expand=True)
        for c in range(3):
            grid.columnconfigure(c, weight=1)

        bola_f = ttk.Frame(grid)
        bola_f.grid(row=0, column=0, columnspan=3, sticky="we", pady=(0, 8))
        inner = tk.Frame(bola_f, bg="#0d0d12")
        inner.pack(fill="x")
        for n in a["recente"][-40:]:
            c = cor_num(n)
            bola = tk.Label(inner, text=str(n), width=3, height=1, bg=COR_HEX[c], fg=COR_TXT[c],
                            font=("Segoe UI", 10, "bold"), relief="flat")
            bola.pack(side="left", padx=2, pady=2)
        tk.Label(inner, text="ultimos", bg="#0d0d12", fg="#8a8a95", font=("Segoe UI", 9)).pack(side="right")
        bg_ult = COR_HEX[cor_num(a["recente"][-1])]
        tk.Label(inner, text=f"#{a['recente'][-1]}", bg="#0d0d12", fg=bg_ult,
                 font=("Segoe UI", 15, "bold")).pack(side="right", padx=8)

        linhas_freq = [
            f"VERMELHO: {fq.get(1,0)}x  ({p_vm:.1f}%)",
            f"PRETO:     {fq.get(2,0)}x  ({p_pt:.1f}%)",
            f"BRANCO:   {fq.get(0,0)}x  ({p_br:.1f}%)",
            "",
            "Numeros mais repetidos (janela): "
            + ", ".join(f"#{n}({fr[n]})" for n in a["quentes"]),
            "",
            "Frios (zeros na janela): "
            + ", ".join(f"#{n}" for n in range(15) if fr.get(n, 0) == 0)[:80]
            or "nenhum",
        ]
        fc = self.card(grid, "FREQUENCIA", linhas_freq)
        fc.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        maior = a["maior"]
        ult_cor = a['sr'][-1]
        ant_cor = a['sr'][-2] if len(a['sr']) > 1 else ult_cor
        linhas_seq = [
            f"Sequencia atual: {NOME_COR[ult_cor]}  ({a['repet']}x seguidas)",
            f"Maior nessa janela: {NOME_COR[maior[0]]} com {maior[1]}x",
            f"Antes dela: {NOME_COR[ant_cor]}",
        ]
        seq_recentes = [(NOME_COR[c], t) for c, t in a["seqs"][-14:]]
        linhas_seq += [f"{c}: {t}x" for c, t in reversed(seq_recentes)]
        sc = self.card(grid, "SEQUENCIAS", linhas_seq, "#4fc3f7")
        sc.grid(row=1, column=1, sticky="nsew", padx=3)

        saldo_s, ac_s, er_s, _, _ = simular_estrategia(a["recente"], "seguir")
        saldo_q, ac_q, er_q, _, _ = simular_estrategia(a["recente"], "quebrar")
        linhas_prev = [
            f"Ultimo: {NOME_COR[a['sr'][-1]]} #{a['recente'][-1]}",
            f"Odds prox -> vermelho {p_vm:.1f}% | preto {p_pt:.1f}% | branco {p_br:.1f}%",
            "",
            ">> " + a["sugestao"],
            "",
            f"Estrategia SEGUIR (janela): +{saldo_s:.0f}u ({ac_s} ac / {er_s} er)",
            f"Estrategia QUEBRAR (janela): {saldo_q:+.0f}u ({ac_q} ac / {er_q} er)",
            "",
            "Jogo de azar. Nenhuma estrategia garante lucro.",
        ]
        pc = self.card(grid, "PREVISAO + ESTRATEGIA", linhas_prev, "#ffd700")
        pc.grid(row=1, column=2, sticky="nsew", padx=(6, 0))

        w = analisar_branco(self.nums, self.horas)
        linhas_br = [
            f"Nivel: {w['nivel']} (score {w['score']*100:.0f}%)",
            f"Ultimo branco ha {w['atraso']} rodadas | gap medio {w['gap_medio']:.1f} "
            f"(max {w['gap_max']})",
            f"Brancos no historico: {w['n_brancos']}x | P(geo) {w['p_geo']*100:.1f}% | "
            f"P(sobrevivencia) {w['p_sobrev']*100:.1f}%",
            f"Mancha atual: {w['streak']}x (media antes de branco {w['mancha_media']:.0f})",
        ]
        for nome, v, p in w["sinais"]:
            linhas_br.append(f"  sinal {nome}: {v*100:.1f}% (peso {p*100:.0f}%)")
        bc = self.card(grid, "SUPER ALERTA BRANCO (PAGA 14x)", linhas_br, "#ffb020")
        bc.grid(row=2, column=0, sticky="nsew", padx=(0, 6), pady=(8, 0))

        s = a["sr"]
        linhas_des = [
            f"Vermelho -> Preto: {sum(1 for i in range(1,len(s)) if s[i-1]==1 and s[i]==2)} quebras",
            f"Preto -> Vermelho: {sum(1 for i in range(1,len(s)) if s[i-1]==2 and s[i]==1)} quebras",
            f"Mancha vermelha (2+): {sum(1 for c,t in a['seqs'] if c==1 and t>=2)}x",
            f"Mancha preta (2+): {sum(1 for c,t in a['seqs'] if c==2 and t>=2)}x",
        ]
        dc = self.card(grid, "QUEBRAS DE PADRAO", linhas_des)
        dc.grid(row=2, column=1, sticky="nsew", padx=3, pady=(8, 0))

        linhas_est = [
            f"Total na janela: {len(a['sr'])}",
            f"Salvo localmente: {len(self.nums)} rodadas",
            f"Tendencia: {NOME_COR[a['sr'][-1]]}" if a["sr"][-1] != 0
            else "Tendencia: indefinida apos branco",
        ]
        if self._tries:
            pct_acc = self._hits / self._tries * 100
            linhas_est.append(f"Acuracia da previsao (live): {self._hits}/{self._tries} = {pct_acc:.0f}%")
        ec = self.card(grid, "STATUS", linhas_est)
        ec.grid(row=2, column=2, sticky="nsew", padx=(6, 0), pady=(8, 0))

        cerebro = self.cerebro
        acur = cerebro._acuraria()
        pesos = cerebro._pesos
        linhas_cbr = [
            f"Ensemble {len(pesos)} tecnicas, pesos APRENDIDOS dos acertos live:",
        ]
        for t in pj.TECNICAS:
            linhas_cbr.append(
                f"  {t}: acur {acur[t]*100:.0f}% | peso {pesos[t]:.2f}")
        linhas_cbr.append(
            f"  feedbacks: {len(cerebro._conf)} | "
            f"acerto real confianca: {self._calibra_txt()}")
        cb = self.card(grid, "CEREBRO APRENDIZADO (feedback live)", linhas_cbr, "#00e5a0")
        cb.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=0, pady=(8, 0))

        linhas_prof = self._analise_profunda()
        ac = self.card(grid, "ANALISE PROFUNDA (aleatoriedade + soma horarios/numeros)", linhas_prof, "#c678dd")
        ac.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=0, pady=(8, 0))

        self.status.config(
            text=f"{len(self.nums)} rodadas salvas | janela {opc} | "
                 f"ultimo: {NOME_COR[cor_num(self.nums[-1])]} #{self.nums[-1]}"
                 + (f" | *{w['nivel']}*" if w["nivel"] != "NORMAL" else ""))

    def _analise_profunda(self):
        try:
            horas = self.horas if len(self.horas) == len(self.nums) else None
            res = ab.resumo_completo(self.nums, horas)
        except Exception as e:
            return [f"erro analise: {str(e)[:60]}"]
        if not res:
            return ["dados insuficientes (min 15 rodadas)"]
        L = []
        z = res["zipf"]
        L.append(f"Distribuicao da janela ({z['n']} jogos): chi2={z['chi']:.1f} p={z['p']:.3f} -> "
                 + ("ALEATORIA (sem vies)" if z['p'] > 0.05 else "desvio detectado"))
        L.append(f"Quentes: {' '.join(map(str, z['quentes']))} | Frios: {' '.join(map(str, z['frios']))}")
        m = res["momentum"]
        L.append(f"Streak atual: {NOME_COR[m['atual_cor']]}x{m['atual_tam']} | recordes V={m['best'][1]} P={m['best'][2]} B={m['best'][0]}")
        w = res["white"]
        L.append(f"Branco: {w['n_brancos']}x | gap medio {w['gap_medio']:.1f} | max {w['gap_max']} | atraso {w['atraso']}")
        f = res["freq_num"]
        L.append(f"Cor dominante por soma de numeros: {f['NOME_dom']} {f['p_dom']*100:.0f}%")
        mk = res["markov"]
        L.append(f"Markov 1a ordem (projecao mais provavel): {mk['base']} {mk['p_proj']*100:.1f}%")
        tec = res.get("tecnicas")
        if tec:
            L.append(f"Baseline (cor mais frequente): {tec['baseline_cor']} {tec['baseline']*100:.1f}%")
            for nome in ("horario_soma_par", "horario_mod3", "soma3_numeros",
                         "num_minuto", "num_hora", "espelho", "metade_pintura"):
                if nome in tec:
                    d = tec[nome] - tec["baseline"]
                    tag = ">base" if d > 0 else "<=base"
                    L.append(f"Tecnica {nome}: {tec[nome]*100:.1f}% (diff {d*100:+.1f}pp {tag})")
            v = ab.tecnica_vencedora(tec)
            if v:
                L.append(f"Melhor projecao: {v[0][1]} {v[0][0]*100:.1f}% vs baseline {tec['baseline']*100:.1f}%")
        else:
            L.append("Historico sem horarios: ligue LIVE ou recarregue para capturar soma de horarios.")
        return L


if __name__ == "__main__":
    app = BlazeSimulator()
    app.mainloop()