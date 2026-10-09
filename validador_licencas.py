#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Licenças TRONIX - Interface Gráfica (Tkinter)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from licenca_tronix import LicencaTronix
from datetime import datetime

class ValidadorLicencas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Validador de Licenças TRONIX v1.0")
        self.geometry("750x550")
        self.minsize(700, 500)
        
        self.configure(bg='#1e1e1e')
        self.lic = LicencaTronix()
        
        self.chave_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Cole uma chave para validar")
        
        self.criar_widgets()
    
    def criar_widgets(self):
        # Título
        title_frame = tk.Frame(self, bg='#2d3748', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        titulo = tk.Label(
            title_frame,
            text="VALIDADOR DE LICENÇAS TRONIX",
            font=('Segoe UI', 16, 'bold'),
            bg='#2d3748',
            fg='#ffd700'
        )
        titulo.pack(expand=True)
        
        subtitulo = tk.Label(
            title_frame,
            text="Verificar validade de códigos de ativação",
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#a0aec0'
        )
        subtitulo.pack(pady=(0, 15))
        
        # Main
        main_frame = tk.Frame(self, bg='#1e1e1e', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame validar
        validar_frame = tk.LabelFrame(
            main_frame,
            text=" Validar Licença ",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#4fd1c5',
            padx=20,
            pady=20,
            borderwidth=2,
            relief=tk.GROOVE
        )
        validar_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            validar_frame,
            text="Chave de Licença:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_chave = ttk.Entry(
            validar_frame,
            textvariable=self.chave_var,
            font=('Consolas', 9)
        )
        self.entry_chave.pack(fill=tk.X, pady=(0, 15))
        self.entry_chave.focus()
        
        btn_validar = tk.Button(
            validar_frame,
            text="VALIDAR CHAVE",
            command=self.validar,
            font=('Segoe UI', 11, 'bold'),
            bg='#3182ce',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        btn_validar.pack(fill=tk.X)
        
        def on_enter(e): e.widget.configure(bg='#2b6cb0')
        def on_leave(e): e.widget.configure(bg='#3182ce')
        btn_validar.bind('<Enter>', on_enter)
        btn_validar.bind('<Leave>', on_leave)
        
        # Resultado
        resultado_frame = tk.LabelFrame(
            main_frame,
            text=" Resultado da Validação ",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ffd700',
            padx=20,
            pady=20,
            borderwidth=2,
            relief=tk.GROOVE
        )
        resultado_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_resultado = scrolledtext.ScrolledText(
            resultado_frame,
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#e2e8f0',
            wrap=tk.WORD,
            padx=20,
            pady=20,
            borderwidth=0
        )
        self.text_resultado.pack(fill=tk.BOTH, expand=True)
        self.text_resultado.insert(tk.END, "Aguardando validação...")
        self.text_resultado.configure(state=tk.DISABLED)
        
        # Status
        status_frame = tk.Frame(self, bg='#2d3748', height=40)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg='#2d3748',
            fg='#a0aec0',
            anchor=tk.W,
            padx=20
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)
    
    def validar(self):
        chave = self.chave_var.get().strip()
        if not chave:
            messagebox.showwarning("Aviso", "Digite uma chave para validar!")
            return
        
        valida, dados = self.lic.validar_chave(chave)
        
        self.text_resultado.configure(state=tk.NORMAL)
        self.text_resultado.delete(1.0, tk.END)
        
        if valida:
            self.text_resultado.insert(tk.END, "✓ LICENÇA VÁLIDA\n\n")
            self.text_resultado.insert(tk.END, f"Cliente: {dados.get('cliente', 'N/A')}\n")
            self.text_resultado.insert(tk.END, f"Emitida: {dados.get('emitida', 'N/A')}\n")
            self.text_resultado.insert(tk.END, f"Expira em: {dados.get('expira', 'N/A')}\n")
            self.text_resultado.insert(tk.END, f"Dias restantes: {dados.get('dias_restantes', 'N/A')}\n")
            self.text_resultado.insert(tk.END, f"Versão: {dados.get('versao', 'N/A')}\n\n")
            self.text_resultado.insert(tk.END, "Status: ATIVA E VÁLIDA")
            self.status_var.set("Licença válida")
            self.text_resultado.tag_add('valida', '1.0', '1.10')
            self.text_resultado.tag_config('valida', foreground='#48bb78', font=('Segoe UI', 11, 'bold'))
        else:
            self.text_resultado.insert(tk.END, "✗ LICENÇA INVÁLIDA\n\n")
            self.text_resultado.insert(tk.END, f"Motivo: {dados.get('erro', 'Erro desconhecido')}\n")
            if 'expirou_em' in dados:
                self.text_resultado.insert(tk.END, f"Expirou em: {dados.get('expirou_em')}\n")
            self.status_var.set("Licença inválida")
            self.text_resultado.tag_add('invalida', '1.0', '1.12')
            self.text_resultado.tag_config('invalida', foreground='#f56565', font=('Segoe UI', 11, 'bold'))
        
        self.text_resultado.configure(state=tk.DISABLED)

def main():
    app = ValidadorLicencas()
    app.mainloop()

if __name__ == '__main__':
    main()
