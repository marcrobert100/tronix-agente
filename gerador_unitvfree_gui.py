#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Códigos de Ativação - UnitvFree 5.2
Formato 11 Dígitos com Validação de Checksum
TRONIX v1.0 - Evolução para Ativador UnitvFree
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import random
import time

class GeradorUnitvFree:
    @staticmethod
    def calcular_dv(base10: str) -> str:
        soma = 0
        peso = 1
        for c in reversed(base10):
            d = int(c)
            v = d * peso
            soma += v
            peso = 3 - peso
        resto = soma % 10
        dv = (10 - resto) % 10
        return str(dv)
    
    @staticmethod
    def gerar_chave() -> str:
        base10 = ''.join(str(random.randint(0, 9)) for _ in range(10))
        return base10 + GeradorUnitvFree.calcular_dv(base10)
    
    @staticmethod
    def validar_chave(chave: str) -> bool:
        chave = chave.strip().replace('-', '').replace(' ', '')
        if len(chave) != 11 or not chave.isdigit():
            return False
        base10 = chave[:-1]
        dv = chave[-1]
        return GeradorUnitvFree.calcular_dv(base10) == dv

class AppUnitvFree(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Códigos de Ativação - UnitvFree 5.2 | TRONIX")
        self.geometry("820x650")
        self.minsize(780, 600)
        self.configure(bg='#0f1026')
        
        self.chaves_geradas = []
        self.qtd_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Pronto. Formato compatível com Ativador UnitvFree 5.2")
        
        self.criar_widgets()
    
    def criar_widgets(self):
        # Header
        header = tk.Frame(self, bg='#1a1d33', height=95)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="ATIVADOR UNITVFREE 5.2 - GERADOR DE CÓDIGOS",
                 font=('Segoe UI', 14, 'bold'), bg='#1a1d33', fg='#ffd700').pack(expand=True, pady=(10, 0))
        tk.Label(header, text="Chaves numéricas de 11 dígitos • Checksum Verificado",
                 font=('Segoe UI', 9), bg='#1a1d33', fg='#9ca3af').pack(pady=(0, 10))
        
        main = tk.Frame(self, bg='#0f1026', padx=40, pady=30)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Painel Gerar
        panel_gerar = tk.LabelFrame(main, text=" Gerar Códigos de Ativação ",
                                    font=('Segoe UI', 11, 'bold'), bg='#0f1026', fg='#06d6a0',
                                    padx=35, pady=30, borderwidth=2, relief=tk.GROOVE)
        panel_gerar.pack(fill=tk.X, pady=(0, 25))
        
        # Quantidade
        qtd_frame = tk.Frame(panel_gerar, bg='#0f1026')
        qtd_frame.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(qtd_frame, text="Quantidade de Códigos:",
                 font=('Segoe UI', 10, 'bold'), bg='#0f1026', fg='#fff').pack(side=tk.LEFT)
        
        spin = ttk.Spinbox(qtd_frame, from_=1, to=500, textvariable=self.qtd_var,
                           width=15, font=('Segoe UI', 11))
        spin.pack(side=tk.LEFT, padx=(20, 15))
        
        tk.Label(qtd_frame, text="(Máx. 500 por geração)",
                 font=('Segoe UI', 9), bg='#0f1026', fg='#9ca3af').pack(side=tk.LEFT)
        
        # Botão Gerar
        btn_gerar = tk.Button(panel_gerar, text="GERAR CÓDIGOS DE ATIVAÇÃO",
                              command=self.gerar,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#06d6a0', fg='#000', relief=tk.FLAT,
                              padx=30, pady=15, cursor='hand2')
        btn_gerar.pack(fill=tk.X)
        
        def e1(e): e.widget.configure(bg='#05c08d')
        def l1(e): e.widget.configure(bg='#06d6a0')
        btn_gerar.bind('<Enter>', e1)
        btn_gerar.bind('<Leave>', l1)
        
        # Painel Resultado
        panel_res = tk.LabelFrame(main, text=" Códigos Gerados (Prontos para Usar) ",
                                  font=('Segoe UI', 11, 'bold'), bg='#0f1026', fg='#ffd700',
                                  padx=35, pady=30, borderwidth=2, relief=tk.GROOVE)
        panel_res.pack(fill=tk.BOTH, expand=True)
        
        # Listbox
        self.listbox = tk.Listbox(panel_res, font=('Consolas', 15, 'bold'),
                                  bg='#1a1d33', fg='#ffd700',
                                  selectbackground='#ffd700', selectforeground='#000',
                                  height=10, relief=tk.FLAT, borderwidth=0)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.listbox.insert(tk.END, "  Nenhum código gerado ainda...")
        
        # Botões
        btn_frame = tk.Frame(panel_res, bg='#0f1026')
        btn_frame.pack(fill=tk.X)
        
        btn_c1 = tk.Button(btn_frame, text="COPIAR SELECIONADO",
                           command=self.copiar_sel,
                           font=('Segoe UI', 9, 'bold'), bg='#3b82f6', fg='#fff',
                           relief=tk.FLAT, padx=15, pady=9, cursor='hand2')
        btn_c1.pack(side=tk.LEFT, padx=(0, 8))
        def e2(e): e.widget.configure(bg='#2563eb')
        def l2(e): e.widget.configure(bg='#3b82f6')
        btn_c1.bind('<Enter>', e2); btn_c1.bind('<Leave>', l2)
        
        btn_c2 = tk.Button(btn_frame, text="COPIAR TODOS",
                           command=self.copiar_todos,
                           font=('Segoe UI', 9, 'bold'), bg='#8b5cf6', fg='#fff',
                           relief=tk.FLAT, padx=15, pady=9, cursor='hand2')
        btn_c2.pack(side=tk.LEFT, padx=(0, 8))
        def e3(e): e.widget.configure(bg='#7c3aed')
        def l3(e): e.widget.configure(bg='#8b5cf6')
        btn_c2.bind('<Enter>', e3); btn_c2.bind('<Leave>', l3)
        
        btn_s = tk.Button(btn_frame, text="SALVAR .TXT",
                          command=self.salvar,
                          font=('Segoe UI', 9, 'bold'), bg='#f59e0b', fg='#000',
                          relief=tk.FLAT, padx=15, pady=9, cursor='hand2')
        btn_s.pack(side=tk.LEFT, padx=(0, 8))
        def e4(e): e.widget.configure(bg='#d97706')
        def l4(e): e.widget.configure(bg='#f59e0b')
        btn_s.bind('<Enter>', e4); btn_s.bind('<Leave>', l4)
        
        btn_v = tk.Button(btn_frame, text="VALIDAR SELECIONADO",
                          command=self.validar_sel,
                          font=('Segoe UI', 9, 'bold'), bg='#06b6d4', fg='#000',
                          relief=tk.FLAT, padx=15, pady=9, cursor='hand2')
        btn_v.pack(side=tk.LEFT, padx=(0, 8))
        def e5(e): e.widget.configure(bg='#0891b2')
        def l5(e): e.widget.configure(bg='#06b6d4')
        btn_v.bind('<Enter>', e5); btn_v.bind('<Leave>', l5)
        
        btn_l = tk.Button(btn_frame, text="LIMPAR",
                          command=self.limpar,
                          font=('Segoe UI', 9, 'bold'), bg='#ef4444', fg='#fff',
                          relief=tk.FLAT, padx=15, pady=9, cursor='hand2')
        btn_l.pack(side=tk.RIGHT)
        def e6(e): e.widget.configure(bg='#dc2626')
        def l6(e): e.widget.configure(bg='#ef4444')
        btn_l.bind('<Enter>', e6); btn_l.bind('<Leave>', l6)
        
        # Status
        status_bar = tk.Frame(self, bg='#1a1d33', height=45)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_var,
                 font=('Segoe UI', 9), bg='#1a1d33', fg='#9ca3af',
                 anchor=tk.W, padx=40).pack(fill=tk.BOTH, expand=True)
    
    def gerar(self):
        try:
            qtd = int(self.qtd_var.get())
            if qtd < 1 or qtd > 500:
                messagebox.showwarning("Aviso", "Quantidade entre 1 e 500")
                return
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade inválida")
            return
        
        self.chaves_geradas.clear()
        self.listbox.delete(0, tk.END)
        
        g = GeradorUnitvFree()
        for i in range(qtd):
            c = g.gerar_chave()
            self.chaves_geradas.append(c)
            self.listbox.insert(tk.END, f"  {c}")
            self.update_idletasks()
            self.status_var.set(f"Gerando... {i+1}/{qtd}")
            time.sleep(0.001)
        
        self.status_var.set(f"{qtd} códigos de ativação gerados com sucesso!")
        messagebox.showinfo("Sucesso",
                           f"{qtd} Códigos de Ativação foram gerados!\n\n"
                           f"Formato: 11 Dígitos Numéricos\n"
                           f"Compatível: Ativador UnitvFree 5.2")
    
    def copiar_sel(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um código")
            return
        c = self.listbox.get(sel[0]).strip()
        self.clipboard_clear()
        self.clipboard_append(c)
        self.status_var.set(f"Copiado: {c}")
    
    def copiar_todos(self):
        if not self.chaves_geradas:
            messagebox.showwarning("Aviso", "Nenhum código gerado")
            return
        self.clipboard_clear()
        self.clipboard_append('\n'.join(self.chaves_geradas))
        self.status_var.set(f"{len(self.chaves_geradas)} códigos copiados")
        messagebox.showinfo("Copiado", "Todos os códigos copiados para área de transferência!")
    
    def salvar(self):
        if not self.chaves_geradas:
            messagebox.showwarning("Aviso", "Nenhum código gerado")
            return
        nome = f"Codigos_Ativacao_UnitvFree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        arq = filedialog.asksaveasfilename(defaultextension='.txt',
                                           filetypes=[('TXT', '*.txt')],
                                           initialfile=nome)
        if arq:
            with open(arq, 'w', encoding='utf-8') as f:
                f.write("ATIVADOR UNITVFREE 5.2 - CÓDIGOS DE ATIVAÇÃO\n")
                f.write("=" * 55 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Quantidade: {len(self.chaves_geradas)} códigos\n")
                f.write("Formato: 11 Dígitos Numéricos (Com Checksum)\n")
                f.write("=" * 55 + "\n\n")
                for i, c in enumerate(self.chaves_geradas, 1):
                    f.write(f"{i:04d}. {c}\n")
                f.write("\n" + "=" * 55 + "\n")
                f.write("Instruções: Cole cada código no Ativador UnitvFree 5.2\n")
            messagebox.showinfo("Salvo", f"Salvo com sucesso!\n\n{arq}")
    
    def validar_sel(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um código")
            return
        c = self.listbox.get(sel[0]).strip()
        ok = GeradorUnitvFree.validar_chave(c)
        if ok:
            messagebox.showinfo("Válido", f"✓ Código VÁLIDO\n\n{c}\n\nChecksum OK")
        else:
            messagebox.showerror("Inválido", f"✗ Código INVÁLIDO\n\n{c}")
    
    def limpar(self):
        self.chaves_geradas.clear()
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "  Nenhum código gerado ainda...")
        self.status_var.set("Pronto. Formato compatível com Ativador UnitvFree 5.2")

if __name__ == '__main__':
    app = AppUnitvFree()
    app.mainloop()
