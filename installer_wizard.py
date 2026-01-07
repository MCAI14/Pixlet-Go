"""
Pixlet-Go Installer Wizard
Instalador multi-página estilo wizard para gerenciar dependências, criar atalhos e instalar do GitHub.
"""

import os
import sys
import json
import subprocess
import threading
import tempfile
import zipfile
import shutil
import urllib.request
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk, scrolledtext

# Constantes
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
QT_BROWSER = os.path.join(REPO_DIR, 'qt_browser.py')
REQUIREMENTS = os.path.join(REPO_DIR, 'requirements.txt')


def is_windows_admin():
    """Verifica se o script está sendo executado com privilégios de administrador no Windows."""
    try:
        import ctypes
        return ctypes.windll.shell.IsUserAnAdmin()
    except Exception:
        return False


def desktop_path():
    """Retorna o caminho da Área de Trabalho do utilizador."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')


class WizardPage(ttk.Frame):
    """Página base para o wizard."""
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)

    def next_page(self):
        """Retorna a próxima página (None se for última)."""
        return None

    def prev_page(self):
        """Retorna a página anterior (None se for primeira)."""
        return None


class WelcomePage(WizardPage):
    def __init__(self, parent, wizard):
        super().__init__(parent)
        self.wizard = wizard
        
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill='both', expand=True)
        
        ttk.Label(frm, text='🎉 Bem-vindo ao Pixlet-Go', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(frm, text='Assistente de Instalação', font=('Segoe UI', 12)).pack(anchor='w', pady=(0, 20))
        
        info = ttk.Frame(frm)
        info.pack(fill='both', expand=True)
        
        ttk.Label(info, text='Este assistente ajudará você a:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        ttk.Label(info, text='✓ Instalar dependências Python (pip)', wraplength=400).pack(anchor='w', padx=20)
        ttk.Label(info, text='✓ Criar atalhos na Área de Trabalho', wraplength=400).pack(anchor='w', padx=20)
        ttk.Label(info, text='✓ Executar o navegador Pixlet', wraplength=400).pack(anchor='w', padx=20)
        ttk.Label(info, text='✓ Instalar a partir do GitHub (opcional)', wraplength=400).pack(anchor='w', padx=20)
        
        ttk.Label(info, text='', wraplength=400).pack(anchor='w')  # Espaço
        
        # Status de admin
        if is_windows_admin():
            ttk.Label(info, text='✓ Executando como administrador', font=('Segoe UI', 10), foreground='green').pack(anchor='w')
        else:
            ttk.Label(info, text='⚠️ Sem privilégios de administrador', font=('Segoe UI', 10), foreground='orange').pack(anchor='w')
            ttk.Label(info, text='Algumas funções podem estar limitadas', wraplength=400).pack(anchor='w', padx=20)


class InstallDepsPage(WizardPage):
    def __init__(self, parent, wizard):
        super().__init__(parent)
        self.wizard = wizard
        
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill='both', expand=True)
        
        ttk.Label(frm, text='📦 Instalar Dependências', font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))
        
        info = ttk.Label(frm, text='Instalar pacotes Python necessários (PySide6, etc)', wraplength=400)
        info.pack(anchor='w', pady=(0, 20))
        
        # Output box
        ttk.Label(frm, text='Saída:').pack(anchor='w', pady=(8, 0))
        self.output = scrolledtext.ScrolledText(frm, height=12, width=60)
        self.output.pack(fill='both', expand=True, pady=(0, 12))
        self.output.configure(state='disabled')
        
        # Botão instalar
        btn_frm = ttk.Frame(frm)
        btn_frm.pack(fill='x', pady=(0, 0))
        
        self.install_btn = ttk.Button(btn_frm, text='Instalar Agora', command=self.install_dependencies)
        self.install_btn.pack(side='left', padx=4)
        
        self.status_label = ttk.Label(btn_frm, text='Aguardando...', foreground='gray')
        self.status_label.pack(side='left', padx=12)
    
    def append_output(self, text):
        """Adiciona texto à caixa de saída."""
        def _append():
            self.output.config(state='normal')
            self.output.insert('end', text)
            self.output.see('end')
            self.output.config(state='disabled')
        self.after(0, _append)
    
    def install_dependencies(self):
        """Instala dependências."""
        if not os.path.exists(REQUIREMENTS):
            messagebox.showwarning('Erro', f'Ficheiro não encontrado: {REQUIREMENTS}')
            return
        
        if not is_windows_admin():
            messagebox.showwarning('Privilégios', 'Abra o instalador como administrador para instalar dependências.')
            return
        
        def worker():
            self.install_btn.config(state='disabled')
            self.status_label.config(text='Instalando...', foreground='blue')
            
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS]
            self.append_output(f'> {" ".join(cmd)}\n')
            
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=REPO_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                for line in proc.stdout:
                    self.append_output(line)
                proc.wait()
                
                if proc.returncode == 0:
                    self.append_output('\n✓ Dependências instaladas com sucesso!\n')
                    self.status_label.config(text='Concluído', foreground='green')
                else:
                    self.append_output(f'\n✗ Erro (código {proc.returncode})\n')
                    self.status_label.config(text='Erro', foreground='red')
            except Exception as e:
                self.append_output(f'\n✗ Erro: {e}\n')
                self.status_label.config(text='Erro', foreground='red')
            finally:
                self.install_btn.config(state='normal')
        
        threading.Thread(target=worker, daemon=True).start()


class ShortcutPage(WizardPage):
    def __init__(self, parent, wizard):
        super().__init__(parent)
        self.wizard = wizard
        
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill='both', expand=True)
        
        ttk.Label(frm, text='⭐ Criar Atalho', font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(frm, text='Criar um atalho na Área de Trabalho para executar o navegador', wraplength=400).pack(anchor='w', pady=(0, 20))
        
        # Output
        ttk.Label(frm, text='Saída:').pack(anchor='w', pady=(8, 0))
        self.output = scrolledtext.ScrolledText(frm, height=12, width=60)
        self.output.pack(fill='both', expand=True, pady=(0, 12))
        self.output.configure(state='disabled')
        
        # Botão
        btn_frm = ttk.Frame(frm)
        btn_frm.pack(fill='x', pady=(0, 0))
        
        self.create_btn = ttk.Button(btn_frm, text='Criar Atalho', command=self.create_shortcut)
        self.create_btn.pack(side='left', padx=4)
        
        self.status_label = ttk.Label(btn_frm, text='Aguardando...', foreground='gray')
        self.status_label.pack(side='left', padx=12)
    
    def append_output(self, text):
        def _append():
            self.output.config(state='normal')
            self.output.insert('end', text)
            self.output.see('end')
            self.output.config(state='disabled')
        self.after(0, _append)
    
    def create_shortcut(self):
        """Cria atalho na Área de Trabalho."""
        desk = desktop_path()
        
        if not os.path.isdir(desk):
            self.append_output(f'✗ Pasta de Área de Trabalho não encontrada: {desk}\n')
            return
        
        python_exec = sys.executable
        bat_path = os.path.join(desk, 'Pixlet-Browser.bat')
        content = f'@echo off\ncd /d "{REPO_DIR}"\n"{python_exec}" "{QT_BROWSER}" %*\npause\n'
        
        try:
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.append_output(f'✓ Atalho criado: {bat_path}\n')
            self.status_label.config(text='Concluído', foreground='green')
        except Exception as e:
            self.append_output(f'✗ Erro: {e}\n')
            self.status_label.config(text='Erro', foreground='red')


class RunBrowserPage(WizardPage):
    def __init__(self, parent, wizard):
        super().__init__(parent)
        self.wizard = wizard
        
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill='both', expand=True)
        
        ttk.Label(frm, text='🌐 Executar Navegador', font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(frm, text='Inicia o navegador Pixlet Browser', wraplength=400).pack(anchor='w', pady=(0, 20))
        
        self.output = scrolledtext.ScrolledText(frm, height=12, width=60)
        self.output.pack(fill='both', expand=True, pady=(0, 12))
        self.output.configure(state='disabled')
        
        btn_frm = ttk.Frame(frm)
        btn_frm.pack(fill='x', pady=(0, 0))
        
        self.run_btn = ttk.Button(btn_frm, text='Executar Agora', command=self.run_browser)
        self.run_btn.pack(side='left', padx=4)
        
        self.status_label = ttk.Label(btn_frm, text='Aguardando...', foreground='gray')
        self.status_label.pack(side='left', padx=12)
    
    def append_output(self, text):
        def _append():
            self.output.config(state='normal')
            self.output.insert('end', text)
            self.output.see('end')
            self.output.config(state='disabled')
        self.after(0, _append)
    
    def run_browser(self):
        if not os.path.exists(QT_BROWSER):
            self.append_output(f'✗ Ficheiro não encontrado: {QT_BROWSER}\n')
            return
        
        def worker():
            self.run_btn.config(state='disabled')
            self.status_label.config(text='Iniciando...', foreground='blue')
            self.append_output(f'Iniciando {QT_BROWSER}...\n')
            
            try:
                subprocess.Popen([sys.executable, QT_BROWSER])
                self.append_output('✓ Navegador iniciado com sucesso\n')
                self.status_label.config(text='Iniciado', foreground='green')
            except Exception as e:
                self.append_output(f'✗ Erro: {e}\n')
                self.status_label.config(text='Erro', foreground='red')
            finally:
                self.run_btn.config(state='normal')
        
        threading.Thread(target=worker, daemon=True).start()


class InstallerWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Pixlet-Go Installer Wizard')
        self.geometry('700x600')
        self.resizable(True, True)
        
        # Páginas
        self.pages = [
            WelcomePage,
            InstallDepsPage,
            ShortcutPage,
            RunBrowserPage,
        ]
        self.current_page_index = 0
        self.current_page = None
        
        # Container principal
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Barra de navegação inferior
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill='x', side='bottom', padx=12, pady=12)
        
        self.prev_btn = ttk.Button(nav_frame, text='← Anterior', command=self.prev_page)
        self.prev_btn.pack(side='left', padx=4)
        
        self.page_label = ttk.Label(nav_frame, text='1/4')
        self.page_label.pack(side='left', padx=12, expand=True)
        
        self.next_btn = ttk.Button(nav_frame, text='Próximo →', command=self.next_page)
        self.next_btn.pack(side='left', padx=4)
        
        self.close_btn = ttk.Button(nav_frame, text='Fechar', command=self.destroy)
        self.close_btn.pack(side='right', padx=4)
        
        # Mostrar primeira página
        self.show_page()
    
    def show_page(self):
        """Mostra a página atual."""
        if self.current_page:
            self.current_page.destroy()
        
        page_class = self.pages[self.current_page_index]
        self.current_page = page_class(self.container, self)
        self.current_page.grid(row=0, column=0, sticky='nsew')
        
        # Atualizar rótulo
        self.page_label.config(text=f'{self.current_page_index + 1}/{len(self.pages)}')
        
        # Desativar botões se necessário
        self.prev_btn.config(state='normal' if self.current_page_index > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page_index < len(self.pages) - 1 else 'disabled')
    
    def next_page(self):
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self.show_page()
    
    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.show_page()


def main():
    app = InstallerWizard()
    app.mainloop()


if __name__ == '__main__':
    main()
