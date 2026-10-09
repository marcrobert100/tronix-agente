#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Licenças TRONIX - Interface Gráfica (Tkinter)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
from licenca_tronix import LicencaTronix

class GeradorLicencas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Licenças TRONIX v1.0")
        self.geometry("800x650")
        self.minsize(750, 600)
        
        # Estilo
        self.configure(bg='#1e1e1e')
        
        # Instancia gerador
        self.lic = LicencaTronix()
        
        # Variáveis
        self.cliente_var = tk.StringVar()
        self.dias_var = tk.StringVar(value="365")
        self.chave_gerada_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto para gerar licenças")
        
        self.criar_widgets()
    
    def criar_widgets(self):
        # Título
        title_frame = tk.Frame(self, bg='#2d3748', height=80)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        titulo = tk.Label(
            title_frame, 
            text="SISTEMA DE LICENCIAMENTO TRONIX",
            font=('Segoe UI', 16, 'bold'),
            bg='#2d3748',
            fg='#ffd700'
        )
        titulo.pack(expand=True)
        
        subtitulo = tk.Label(
            title_frame,
            text="Gerador de Códigos de Ativação Legítimos",
            font=('Segoe UI', 10),
            bg='#2d3748',
            fg='#a0aec0'
        )
        subtitulo.pack(pady=(0, 15))
        
        # Frame principal
        main_frame = tk.Frame(self, bg='#1e1e1e', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seção Gerar Licença
        gerar_frame = tk.LabelFrame(
            main_frame,
            text=" Gerar Nova Licença ",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#4fd1c5',
            padx=20,
            pady=20,
            borderwidth=2,
            relief=tk.GROOVE
        )
        gerar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Cliente
        tk.Label(
            gerar_frame,
            text="Nome do Cliente:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_cliente = ttk.Entry(
            gerar_frame,
            textvariable=self.cliente_var,
            font=('Segoe UI', 10)
        )
        self.entry_cliente.pack(fill=tk.X, pady=(0, 15))
        self.entry_cliente.focus()
        
        # Dias de validade
        tk.Label(
            gerar_frame,
            text="Dias de Validade:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        dias_frame = tk.Frame(gerar_frame, bg='#1e1e1e')
        dias_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.entry_dias = ttk.Entry(
            dias_frame,
            textvariable=self.dias_var,
            font=('Segoe UI', 10),
            width=20
        )
        self.entry_dias.pack(side=tk.LEFT, padx=(0, 15))
        
        # Presets de dias
        tk.Button(
            dias_frame,
            text="30 dias",
            command=lambda: self.dias_var.set("30"),
            bg='#4a5568',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            dias_frame,
            text="90 dias",
            command=lambda: self.dias_var.set("90"),
            bg='#4a5568',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            dias_frame,
            text="1 ano (365)",
            command=lambda: self.dias_var.set("365"),
            bg='#4a5568',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            dias_frame,
            text="Permanente (10000)",
            command=lambda: self.dias_var.set("10000"),
            bg='#2b6cb0',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão Gerar
        btn_gerar = tk.Button(
            gerar_frame,
            text="GERAR LICENÇA",
            command=self.gerar_licenca,
            font=('Segoe UI', 11, 'bold'),
            bg='#48bb78',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        btn_gerar.pack(fill=tk.X)
        
        # Efeito hover
        def on_enter(e): e.widget.configure(bg='#38a169')
        def on_leave(e): e.widget.configure(bg='#48bb78')
        btn_gerar.bind('<Enter>', on_enter)
        btn_gerar.bind('<Leave>', on_leave)
        
        # Seção Chave Gerada
        chave_frame = tk.LabelFrame(
            main_frame,
            text=" Chave de Ativação Gerada ",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ffd700',
            padx=20,
            pady=20,
            borderwidth=2,
            relief=tk.GROOVE
        )
        chave_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Textarea para chave
        self.text_chave = tk.Text(
            chave_frame,
            font=('Consolas', 9),
            bg='#2d3748',
            fg='#e2e8f0',
            wrap=tk.WORD,
            height=6,
            padx=15,
            pady=15,
            borderwidth=0
        )
        self.text_chave.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.text_chave.insert(tk.END, "Nenhuma chave gerada ainda...")
        self.text_chave.configure(state=tk.DISABLED)
        
        # Botões de ação
        botoes_frame = tk.Frame(chave_frame, bg='#1e1e1e')
        botoes_frame.pack(fill=tk.X)
        
        btn_copiar = tk.Button(
            botoes_frame,
            text="COPIAR CHAVE",
            command=self.copiar_chave,
            font=('Segoe UI', 9, 'bold'),
            bg='#3182ce',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        btn_copiar.pack(side=tk.LEFT, padx=(0, 10))
        
        def on_enter_c(e): e.widget.configure(bg='#2b6cb0')
        def on_leave_c(e): e.widget.configure(bg='#3182ce')
        btn_copiar.bind('<Enter>', on_enter_c)
        btn_copiar.bind('<Leave>', on_leave_c)
        
        btn_salvar = tk.Button(
            botoes_frame,
            text="SALVAR EM ARQUIVO TXT",
            command=self.salvar_arquivo,
            font=('Segoe UI', 9, 'bold'),
            bg='#805ad5',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        btn_salvar.pack(side=tk.LEFT, padx=(0, 10))
        
        def on_enter_s(e): e.widget.configure(bg='#6b46c1')
        def on_leave_s(e): e.widget.configure(bg='#805ad5')
        btn_salvar.bind('<Enter>', on_enter_s)
        btn_salvar.bind('<Leave>', on_leave_s)
        
        btn_limpar = tk.Button(
            botoes_frame,
            text="LIMPAR",
            command=self.limpar,
            font=('Segoe UI', 9, 'bold'),
            bg='#e53e3e',
            fg='#ffffff',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        btn_limpar.pack(side=tk.RIGHT)
        
        def on_enter_l(e): e.widget.configure(bg='#c53030')
        def on_leave_l(e): e.widget.configure(bg='#e53e3e')
        btn_limpar.bind('<Enter>', on_enter_l)
        btn_limpar.bind('<Leave>', on_leave_l)
        
        # Status bar
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
    
    def gerar_licenca(self):
        cliente = self.cliente_var.get().strip()
        dias_str = self.dias_var.get().strip()
        
        if not cliente:
            messagebox.showwarning("Aviso", "Digite o nome do cliente!")
            self.entry_cliente.focus()
            return
        
        try:
            dias = int(dias_str)
            if dias <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Dias de validade deve ser um número positivo!")
            self.entry_dias.focus()
            return
        
        # Gera chave
        chave = self.lic.gerar_chave(cliente, dias)
        
        # Data de expiração
        from datetime import datetime, timedelta
        data_expira = (datetime.now().date() + timedelta(days=dias)).strftime('%d/%m/%Y')
        
        # Monta informações
        info_completa = f"""SISTEMA DE LICENCIAMENTO TRONIX
{'=' * 60}
CLIENTE: {cliente}
CHAVE DE ATIVAÇÃO:
{chave}
{'=' * 60}
EMITIDA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
VALIDADE: {dias} dias (Expira em {data_expira})
STATUS: VÁLIDA
{'=' * 60}
"""
        
        # Atualiza textarea
        self.text_chave.configure(state=tk.NORMAL)
        self.text_chave.delete(1.0, tk.END)
        self.text_chave.insert(tk.END, info_completa)
        self.text_chave.configure(state=tk.DISABLED)
        
        self.chave_gerada_var.set(chave)
        self.status_var.set(f"Licença gerada com sucesso para {cliente}")
        
        messagebox.showinfo("Sucesso", f"Licença gerada com sucesso!\nCliente: {cliente}")
    
    def copiar_chave(self):
        chave = self.chave_gerada_var.get()
        if not chave:
            messagebox.showwarning("Aviso", "Nenhuma chave para copiar!")
            return
        
        self.clipboard_clear()
        self.clipboard_append(chave)
        self.status_var.set("Chave copiada para a área de transferência!")
        messagebox.showinfo("Copiado", "Chave copiada com sucesso!")
    
    def salvar_arquivo(self):
        chave = self.chave_gerada_var.get()
        cliente = self.cliente_var.get().strip() or "cliente"
        
        if not chave:
            messagebox.showwarning("Aviso", "Nenhuma chave para salvar!")
            return
        
        nome_arquivo = f"licenca_tronix_{cliente.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            initialfile=nome_arquivo,
            title="Salvar Licença"
        )
        
        if arquivo:
            try:
                from datetime import datetime, timedelta
                dias_str = self.dias_var.get().strip()
                dias = int(dias_str) if dias_str else 365
                data_expira = (datetime.now().date() + timedelta(days=dias)).strftime('%d/%m/%Y')
                
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write("SISTEMA DE LICENCIAMENTO TRONIX\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"CLIENTE: {cliente}\n")
                    f.write(f"CHAVE: {chave}\n")
                    f.write(f"EMITIDA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"VALIDADE: {dias} dias (Expira em {data_expira})\n")
                    f.write("=" * 60 + "\n")
                    f.write("\n")
                    f.write("INSTRUÇÕES DE ATIVAÇÃO:\n")
                    f.write("1. Abra o software TRONIX\n")
                    f.write("2. Acesse a tela de Ativação/Licenciamento\n")
                    f.write("3. Cole esta chave no campo 'Código de Ativação'\n")
                    f.write("4. Clique em 'Ativar'\n")
                
                self.status_var.set(f"Licença salva em: {arquivo}")
                messagebox.showinfo("Salvo", f"Licença salva com sucesso!\n\n{arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def limpar(self):
        self.cliente_var.set("")
        self.dias_var.set("365")
        self.chave_gerada_var.set("")
        self.text_chave.configure(state=tk.NORMAL)
        self.text_chave.delete(1.0, tk.END)
        self.text_chave.insert(tk.END, "Nenhuma chave gerada ainda...")
        self.text_chave.configure(state=tk.DISABLED)
        self.status_var.set("Pronto para gerar licenças")
        self.entry_cliente.focus()

def main():
    app = GeradorLicencas()
    app.mainloop()

if __name__ == '__main__':
    main()
