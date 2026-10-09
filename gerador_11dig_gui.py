#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Licenças TRONIX - Formato 11 Dígitos (GUI)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from licenca_tronix_11dig import Licenca11Digitos

class Gerador11Dig(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Licenças TRONIX - 11 Dígitos v1.0")
        self.geometry("750x600")
        self.minsize(700, 550)
        self.configure(bg='#0f1026')
        
        self.lic = Licenca11Digitos()
        self.cliente_var = tk.StringVar()
        self.qtd_var = tk.StringVar(value="1")
        self.chave_var = tk.StringVar()
        self.status_var = tk.StringVar(value="PRONTO - Gerador compatível com formato 11 dígitos")
        
        self.criar_widgets()
    
    def criar_widgets(self):
        # Título
        title_frame = tk.Frame(self, bg='#1a1d33', height=90)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="TRONIX - GERADOR DE LICENÇAS 11 DÍGITOS",
            font=('Segoe UI', 14, 'bold'),
            bg='#1a1d33',
            fg='#ffd700'
        ).pack(expand=True)
        
        tk.Label(
            title_frame,
            text="Formato numérico • Checksum validado • Compatível com padrão UnitvFree",
            font=('Segoe UI', 9),
            bg='#1a1d33',
            fg='#9ca3af'
        ).pack(pady=(0, 15))
        
        main = tk.Frame(self, bg='#0f1026', padx=40, pady=30)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Frame gerar
        gerar_frame = tk.LabelFrame(
            main,
            text=" GERAR CHAVES ",
            font=('Segoe UI', 10, 'bold'),
            bg='#0f1026',
            fg='#06d6a0',
            padx=30,
            pady=25,
            borderwidth=2,
            relief=tk.GROOVE
        )
        gerar_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Cliente
        tk.Label(
            gerar_frame,
            text="Nome/Identificador do Cliente:",
            font=('Segoe UI', 9, 'bold'),
            bg='#0f1026',
            fg='#ffffff'
        ).pack(anchor=tk.W, pady=(0, 6))
        
        ttk.Entry(
            gerar_frame,
            textvariable=self.cliente_var,
            font=('Segoe UI', 10)
        ).pack(fill=tk.X, pady=(0, 20))
        
        # Quantidade
        qtd_frame = tk.Frame(gerar_frame, bg='#0f1026')
        qtd_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            qtd_frame,
            text="Quantidade:",
            font=('Segoe UI', 9, 'bold'),
            bg='#0f1026',
            fg='#ffffff'
        ).pack(side=tk.LEFT)
        
        ttk.Spinbox(
            qtd_frame,
            from_=1,
            to=100,
            textvariable=self.qtd_var,
            width=10,
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT, padx=(15, 15))
        
        tk.Label(
            qtd_frame,
            text="(1 - 100 chaves)",
            font=('Segoe UI', 9),
            bg='#0f1026',
            fg='#9ca3af'
        ).pack(side=tk.LEFT)
        
        # Botão gerar
        btn_gerar = tk.Button(
            gerar_frame,
            text="GERAR CHAVE(S) DE 11 DÍGITOS",
            command=self.gerar,
            font=('Segoe UI', 10, 'bold'),
            bg='#06d6a0',
            fg='#000000',
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        btn_gerar.pack(fill=tk.X)
        
        def on_enter(e): e.widget.configure(bg='#05c08d')
        def on_leave(e): e.widget.configure(bg='#06d6a0')
        btn_gerar.bind('<Enter>', on_enter)
        btn_gerar.bind('<Leave>', on_leave)
        
        # Frame resultado
        res_frame = tk.LabelFrame(
            main,
            text=" CHAVES GERADAS ",
            font=('Segoe UI', 10, 'bold'),
            bg='#0f1026',
            fg='#ffd700',
            padx=30,
            pady=25,
            borderwidth=2,
            relief=tk.GROOVE
        )
        res_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de chaves
        self.listbox = tk.Listbox(
            res_frame,
            font=('Consolas', 16, 'bold'),
            bg='#1a1d33',
            fg='#ffd700',
            selectbackground='#ffd700',
            selectforeground='#000000',
            height=8,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.listbox.insert(tk.END, "Nenhuma chave gerada ainda...")
        
        # Botões
        btns_frame = tk.Frame(res_frame, bg='#0f1026')
        btns_frame.pack(fill=tk.X)
        
        btn_copiar = tk.Button(
            btns_frame,
            text="COPIAR SELECIONADA",
            command=self.copiar_selecionada,
            font=('Segoe UI', 9, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor='hand2'
        )
        btn_copiar.pack(side=tk.LEFT, padx=(0, 10))
        
        def ec(e): e.widget.configure(bg='#2563eb')
        def lc(e): e.widget.configure(bg='#3b82f6')
        btn_copiar.bind('<Enter>', ec)
        btn_copiar.bind('<Leave>', lc)
        
        btn_copiar_todas = tk.Button(
            btns_frame,
            text="COPIAR TODAS",
            command=self.copiar_todas,
            font=('Segoe UI', 9, 'bold'),
            bg='#8b5cf6',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor='hand2'
        )
        btn_copiar_todas.pack(side=tk.LEFT, padx=(0, 10))
        
        def ect(e): e.widget.configure(bg='#7c3aed')
        def lct(e): e.widget.configure(bg='#8b5cf6')
        btn_copiar_todas.bind('<Enter>', ect)
        btn_copiar_todas.bind('<Leave>', lct)
        
        btn_salvar = tk.Button(
            btns_frame,
            text="SALVAR EM .TXT",
            command=self.salvar,
            font=('Segoe UI', 9, 'bold'),
            bg='#f59e0b',
            fg='#000000',
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor='hand2'
        )
        btn_salvar.pack(side=tk.LEFT, padx=(0, 10))
        
        def es(e): e.widget.configure(bg='#d97706')
        def ls(e): e.widget.configure(bg='#f59e0b')
        btn_salvar.bind('<Enter>', es)
        btn_salvar.bind('<Leave>', ls)
        
        btn_limpar = tk.Button(
            btns_frame,
            text="LIMPAR",
            command=self.limpar,
            font=('Segoe UI', 9, 'bold'),
            bg='#ef4444',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor='hand2'
        )
        btn_limpar.pack(side=tk.RIGHT)
        
        def el(e): e.widget.configure(bg='#dc2626')
        def ll(e): e.widget.configure(bg='#ef4444')
        btn_limpar.bind('<Enter>', el)
        btn_limpar.bind('<Leave>', ll)
        
        # Status
        status_frame = tk.Frame(self, bg='#1a1d33', height=40)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg='#1a1d33',
            fg='#9ca3af',
            anchor=tk.W,
            padx=30
        ).pack(fill=tk.BOTH, expand=True)
        
        self.chaves_geradas = []
    
    def gerar(self):
        try:
            qtd = int(self.qtd_var.get())
            if qtd < 1 or qtd > 100:
                messagebox.showwarning("Aviso", "Quantidade deve ser entre 1 e 100")
                return
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade inválida")
            return
        
        cliente = self.cliente_var.get().strip() or "TRONIX"
        self.chaves_geradas = self.lic.gerar_multiplas(qtd, cliente)
        
        self.listbox.delete(0, tk.END)
        for i, c in enumerate(self.chaves_geradas, 1):
            self.listbox.insert(tk.END, f"{c}")
        
        self.status_var.set(f"{qtd} chave(s) gerada(s) com sucesso")
        messagebox.showinfo("Sucesso", f"{qtd} chave(s) de 11 dígitos geradas!")
    
    def copiar_selecionada(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma chave")
            return
        chave = self.listbox.get(sel[0]).strip()
        self.clipboard_clear()
        self.clipboard_append(chave)
        self.status_var.set(f"Copiado: {chave}")
    
    def copiar_todas(self):
        if not self.chaves_geradas:
            messagebox.showwarning("Aviso", "Nenhuma chave gerada")
            return
        texto = '\n'.join(self.chaves_geradas)
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.status_var.set(f"{len(self.chaves_geradas)} chaves copiadas")
        messagebox.showinfo("Copiado", "Todas as chaves copiadas!")
    
    def salvar(self):
        if not self.chaves_geradas:
            messagebox.showwarning("Aviso", "Nenhuma chave gerada")
            return
        
        nome = f"licencas_11dig_tronix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("TXT", "*.txt")],
            initialfile=nome
        )
        
        if arquivo:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("TRONIX - GERADOR DE LICENÇAS 11 DÍGITOS\n")
                f.write("=" * 50 + "\n")
                f.write(f"GERADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"QUANTIDADE: {len(self.chaves_geradas)}\n")
                f.write("=" * 50 + "\n\n")
                for i, c in enumerate(self.chaves_geradas, 1):
                    f.write(f"{i:03d}. {c}\n")
                f.write("\n" + "=" * 50 + "\n")
            
            messagebox.showinfo("Salvo", f"Salvo em:\n{arquivo}")
    
    def limpar(self):
        self.chaves_geradas.clear()
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "Nenhuma chave gerada ainda...")
        self.status_var.set("PRONTO - Gerador compatível com formato 11 dígitos")

if __name__ == '__main__':
    app = Gerador11Dig()
    app.mainloop()
