# -*- coding: utf-8 -*-
"""
TRONIX MONTANTES — registra manualmente o q vc ve na tela da Blaze (montante
apostado por cor na rodada em andamento) e CORRELAciona com o resultado real.

Nao existe API publica com montantes (verificado: bestblaze /api nao expoe,
playbet.io replica so cor/numero/seed, blaze.com rotas 503+Cloudflare).
Esta ferramenta deixa vc DIGITAR e acumula o historico em blaze_montante.json.

IMPORTANTE (matematica provably-fair): o numero de cada rodada e decidido pelo
hash do server_seed ANTES da rodada abrir. Montante NAO pode influenciar a cor
que sai. Esta tool mostra isso nos proprios dados: se montante tivesse efeito,
a regressao/proporcao apareceria claramente.

Usar:
    python tronix_montantes.py
"""
import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from collections import Counter

BASE = Path(__file__).resolve().parent
ARQ = BASE / "blaze_montante.json"

CORES_COL = {"V": "#e6342a", "P": "#33333d", "B": "#d9d9e0"}
NOME_EX = {"V": "Vermelho", "P": "Preto", "B": "Branco"}


def carregar():
    try:
        d = json.loads(ARQ.read_text(encoding="utf-8"))
        return d["rodadas"] if isinstance(d, dict) else list(d)
    except Exception:
        return []


def salvar(rodadas):
    ARQ.write_text(json.dumps({"rodadas": rodadas[-800:]}, ensure_ascii=False),
                   encoding="utf-8")


def cor_de(num):
    return "B" if num == 0 else ("V" if num <= 7 else "P")


class MontanteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TRONIX MONTANTES — registro por cor")
        self.geometry("560x460")
        self.configure(bg="#0d0d12")
        self.rodadas = carregar()
        self.vars = {c: tk.StringVar() for c in "VPB"}
        self._build()
        self._atualizar_estat()

    # ================================================================ UI
    def _build(self):
        ttk.Label(self, text="MONTA NTE POR COR (o que voce ve na tela da rodada em andamento)",
                  font=("Segoe UI", 11, "bold"), background="#0d0d12",
                  foreground="#e8e8e8").pack(anchor="w", padx=14, pady=(12, 2))

        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=14, pady=6)
        for c in "VPB":
            col = CORES_COL[c]
            inner = tk.Frame(frm, bg="#12121a")
            inner.pack(side="left", expand=True, fill="x", padx=2)
            tk.Label(inner, text=NOME_EX[c], bg="#12121a", fg=col,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=6)
            e = tk.Entry(inner, textvariable=self.vars[c], bg="#0d0d12",
                         fg="#ffffff", relief="flat", font=("Consolas", 12, "bold"),
                         insertbackground="#fff", justify="center")
            e.pack(fill="x", padx=6, pady=(2, 8))

        self.callback_txt = tk.Text(self, height=2, bg="#14141c", fg="#fff",
                                    font=("Consolas", 11), relief="flat")
        self.callback_txt.pack(fill="x", padx=14, pady=(0, 4))
        self.callback_txt.insert("1.0", "Numero que saiu (0-14):")
        self.callback_txt.bind("<Return>", lambda e: self._registrar())

        bts = ttk.Frame(self)
        bts.pack(fill="x", padx=14)
        ttk.Button(bts, text="REGISTRAR RODADA", command=self._registrar).pack(side="left")
        ttk.Button(bts, text="Ultimo: reusar demos", command=self._demo).pack(side="left", padx=6)
        ttk.Button(bts, text="Apagar historico", command=self._limpar).pack(side="left")

        self.stat = tk.Text(self, bg="#0d0d12", fg="#d8ffe8", font=("Consolas", 11),
                            relief="flat", height=18, state="disabled")
        self.stat.pack(fill="both", expand=True, padx=14, pady=(8, 10))

    # ================================================================ logica
    def _txt_num(self):
        t = self.callback_txt.get("1.0", "end").strip().replace(",", " ").replace(";", " ")
        tk_ = self.callback_txt
        if ":" in t:
            t = t.split(":", 1)[1]
        tok = [w for w in t.split() if w.isdigit()]
        return [int(x) for x in tok]

    def _ptr(self):
        # ult rato rasp span: usa doses demo se vazio
        return self.vars["V"].get()

    def _mont(self):
        vals = {}
        for c in "VPB":
            v = self.vars[c].get().strip().replace(".", "").replace(",", ".")
            try:
                vals[c] = float(v)
            except Exception:
                vals[c] = 0.0
        return vals

    def _registrar(self, ev=None):
        nums = self._txt_num()
        if not nums:
            messagebox.showwarning("TRONIX", "Digite o numero que saiu (0-14).")
            return
        m = self._mont()
        if not any(m.values()):
            messagebox.showwarning("TRONIX",
                                   "Digite pelo menos um montante (V/P/B) da rodada.")
            return
        for num in nums:
            alvo = cor_de(num)
            self.rodadas.append({"mont": m, "cor": alvo, "num": num})
        salvar(self.rodadas)
        for c in "VPB":
            self.vars[c].set("")
        self.callback_txt.delete("1.0", "end")
        self.callback_txt.insert("1.0", "Numero que saiu (0-14):")
        self._atualizar_estat()

    def _demo(self):
        m = {"V": 843, "P": 351, "B": 97}
        for c in "VPB":
            self.vars[c].set(str(m[c]))
        self.callback_txt.delete("1.0", "end")
        self.callback_txt.insert("1.0", "Numero que saiu (0-14): 9")

    def _limpar(self):
        self.rodadas = []
        salvar(self.rodadas)
        self._atualizar_estat()

    # ================================================================ stats
    def _atualizar_estat(self):
        L = []
        if not self.rodadas:
            L.append("Sem rodadas registradas ainda.")
            L.append("Preencha os 3 montantes da rodada atual + o numero que saiu,")
            L.append("e confira abaixo se ha qualquer relacao (spoiler: nao ha).")
        else:
            n = len(self.rodadas)
            L.append(f"{n} rodadas registradas (janela {min(n, 800)})")
            L.append("")
            total_m = {c: 0.0 for c in "VPB"}
            saida = {c: 0 for c in "VPB"}
            for r in self.rodadas:
                for c in "VPB":
                    total_m[c] += r["mont"].get(c, 0.0)
                saida[r["cor"]] += 1
            soma = sum(total_m.values()) or 1
            L.append("Montante medio por cor (o que voce veu na tela):")
            for c in "VPB":
                L.append(f"  {NOME_EX[c]:<9} medio R${total_m[c]/n:10,.0f}  "
                         f"({total_m[c]/soma*100:4.1f}% do volume)")
            L.append("")
            L.append("Resultado real (frequencia de saida):")
            for c in "VPB":
                L.append(f"  {NOME_EX[c]:<9} saiu {saida[c]:>3}x  ({saida[c]/n*100:5.1f}%)")
            L.append("")
            # a prova: montante grande numa cor => ela sai mais?
            # split pelo montante dominante de cada rodada vs o que saiu
            domina = Counter()
            acertou_dom = 0
            for r in self.rodadas:
                d = max(r["mont"], key=lambda c: r["mont"].get(c, 0.0))
                domina[d] += 1
                if d == r["cor"]:
                    acertou_dom += 1
            L.append("A cor MAIS APOSTADA coincidiu com a que saiu em:")
            for c in "VPB":
                L.append(f"  {NOME_EX[c]:<9} {acertou_dom and '?' if 0 else ''}"
                         )
            # correlacao correta
            L = L[:len(L)]
            L.append(f"  {acertou_dom}/{n} = {acertou_dom/n*100:.1f}%  (aleatorio seria ~{(1/3)*100:.0f}%)")
            L.append("")
            L.append("EXPLICACAO: numero sai por hash de seed (provably fair),")
            L.append("sorteado ANTES das apostas fecharem. Montante nao muda a cor.")
            L.append("Se tu achar q blefar: acumule 60+ e ve se % sobe de ~33%.")
        self.stat.config(state="normal")
        self.stat.delete("1.0", "end")
        self.stat.insert("1.0", "\n".join(L))
        self.stat.config(state="disabled")


if __name__ == "__main__":
    MontanteApp().mainloop()
