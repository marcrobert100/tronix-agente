#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Licenças TRONIX - Formato 11 Dígitos (GUI)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from licenca_tronix_11dig_v2 import Licenca11Digitos

class Validador11Dig(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Validador de Licenças - 11 Dígitos TRONIX")
        self.geometry("700x550")
        self.minsize(650, 500)
        self.configure(bg='#0f1026')
        
        self.lic = Licenca11Digitos()
        self.chave_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Cole uma chave de 11 dígitos para validar")
        
        self.criar_widgets()
    
    def criar_widgets(self):
        title_frame = tk.Frame(self, bg='#1a1d33', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="VALIDADOR - LICENÇAS 11 DÍGITOS",
                 font=('Segoe UI', 14, 'bold'), bg='#1a1d33', fg='#ffd700').pack(expand=True)
        tk.Label(title_frame, text="Verificar checksum e formato numérico",
                 font=('Segoe UI', 9), bg='#1a1d33', fg='#9ca3af').pack(pady=(0,15))
        
        main = tk.Frame(self, bg='#0f1026', padx=40, pady=30)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Validar
        val_frame = tk.LabelFrame(main, text=" VALIDAR CHAVE ",
                                  font=('Segoe UI', 10, 'bold'), bg='#0f1026', fg='#06d6a0',
                                  padx=30, pady=25, borderwidth=2, relief=tk.GROOVE)
        val_frame.pack(fill=tk.X, pady=(0,25))
        
        tk.Label(val_frame, text="Chave de 11 Dígitos:",
                 font=('Segoe UI', 9, 'bold'), bg='#0f1026', fg='#fff').pack(anchor=tk.W, pady=(0,6))
        
        ttk.Entry(val_frame, textvariable=self.chave_var,
                  font=('Consolas', 14, 'bold')).pack(fill=tk.X, pady=(0,20))
        
        btn = tk.Button(val_frame, text="VALIDAR CHAVE",
                        command=self.validar,
                        font=('Segoe UI', 10, 'bold'),
                        bg='#3b82f6', fg='#fff', relief=tk.FLAT,
                        padx=25, pady=12, cursor='hand2')
        btn.pack(fill=tk.X)
        def e(e): e.widget.configure(bg='#2563eb')
        def l(e): e.widget.configure(bg='#3b82f6')
        btn.bind('<Enter>', e); btn.bind('<Leave>', l)
        
        # Resultado
        res_frame = tk.LabelFrame(main, text=" RESULTADO ",
                                  font=('Segoe UI', 10, 'bold'), bg='#0f1026', fg='#ffd700',
                                  padx=30, pady=25, borderwidth=2, relief=tk.GROOVE)
        res_frame.pack(fill=tk.BOTH, expand=True)
        
        self.texto = scrolledtext.ScrolledText(
            res_frame,
            font=('Segoe UI', 10),
            bg='#1a1d33',
            fg='#e5e7eb',
            wrap=tk.WORD,
            padx=25,
            pady=25,
            borderwidth=0,
            relief=tk.FLAT
        )
        self.texto.pack(fill=tk.BOTH, expand=True)
        self.texto.insert(tk.END, "Aguardando validação...")
        self.texto.configure(state=tk.DISABLED)
        
        # Status
        st = tk.Frame(self, bg='#1a1d33', height=40)
        st.pack(fill=tk.X); st.pack_propagate(False)
        tk.Label(st, textvariable=self.status_var,
                 font=('Segoe UI', 9), bg='#1a1d33', fg='#9ca3af',
                 anchor=tk.W, padx=30).pack(fill=tk.BOTH, expand=True)
    
    def validar(self):
        chave = self.chave_var.get()
        ok, dados = self.lic.validar_chave(chave)
        
        self.texto.configure(state=tk.NORMAL)
        self.texto.delete(1.0, tk.END)
        
        if ok:
            self.texto.insert(tk.END, "✓ CHAVE VÁLIDA\n")
            self.texto.insert(tk.END, "=" * 40 + "\n\n")
            self.texto.insert(tk.END, f"Chave: {dados['chave']}\n")
            self.texto.insert(tk.END, f"Formato: {dados['formato']}\n")
            self.texto.insert(tk.END, f"Checksum: OK\n\n")
            self.texto.insert(tk.END, "Status: VÁLIDA PARA ATIVAÇÃO\n")
            self.status_var.set("✓ Chave válida")
        else:
            self.texto.insert(tk.END, "✗ CHAVE INVÁLIDA\n")
            self.texto.insert(tk.END, "=" * 40 + "\n\n")
            self.texto.insert(tk.END, f"Chave: {chave}\n")
            self.texto.insert(tk.END, f"Motivo: {dados['erro']}\n\n")
            self.texto.insert(tk.END, "Status: REJEITADA\n")
            self.status_var.set("✗ Chave inválida")
        
        self.texto.configure(state=tk.DISABLED)

if __name__ == '__main__':
    app = Validador11Dig()
    app.mainloop()
