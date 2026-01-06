"""
Pixlet-Go Installer
Instalador GUI para gerenciar dependências, criar atalhos e instalar do GitHub.
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


def relaunch_as_admin():
    """Relança o script com privilégios de administrador."""
    try:
        import ctypes
        ctypes.windll.shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=' '.join(sys.argv))
        return True
    except Exception:
        return False


def desktop_path():
    """Retorna o caminho da Área de Trabalho do utilizador."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Pixlet-Go Installer')
        self.geometry('900x700')
        self.resizable(True, True)

        # Main frame
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)

        # Title
        ttk.Label(frm, text='Pixlet-Go Browser Installer', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))

        # Buttons frame
        btns = ttk.Frame(frm)
        btns.pack(fill='x', pady=(0, 12))

        self.install_btn = ttk.Button(btns, text='Instalar dependências (pip)', command=self.install_dependencies)
        self.install_btn.pack(side='left', padx=8)

        self.shortcut_btn = ttk.Button(btns, text='Criar atalho na Área de Trabalho', command=self.create_shortcut)
        self.shortcut_btn.pack(side='left', padx=8)

        self.icon_btn = ttk.Button(btns, text='Gerar ícone', command=self.generate_icon)
        self.icon_btn.pack(side='left', padx=8)

        self.run_btn = ttk.Button(btns, text='Executar navegador agora', command=self.run_browser)
        self.run_btn.pack(side='left', padx=8)

        self.net_btn = ttk.Button(btns, text='Instalar da Internet (GitHub)', command=self.install_from_github_prompt)
        self.net_btn.pack(side='left', padx=8)

        ttk.Button(btns, text='Fechar', command=self.destroy).pack(side='right')

        # Output box
        ttk.Label(frm, text='Saída:').pack(anchor='w', pady=(8, 0))
        self.output = scrolledtext.ScrolledText(frm, height=20)
        self.output.pack(fill='both', expand=True)
        self.output.configure(state='disabled')

        # Status bar
        self.status = ttk.Label(self, text='Pronto', relief='sunken', anchor='w')
        self.status.pack(fill='x', side='bottom')

        # GitHub install defaults
        self.github_default = tk.StringVar(value='MCAI14/Pixlet-Go')
        self.install_dir_default = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Pixlet-Browser'))

        opts = ttk.Frame(frm)
        opts.pack(fill='x', pady=(6, 0))
        ttk.Label(opts, text='Repo GitHub (owner/repo):').pack(side='left')
        self.repo_entry = ttk.Entry(opts, width=30, textvariable=self.github_default)
        self.repo_entry.pack(side='left', padx=(4, 8))
        ttk.Label(opts, text='Pasta de instalação:').pack(side='left')
        self.dest_entry = ttk.Entry(opts, width=40, textvariable=self.install_dir_default)
        self.dest_entry.pack(side='left', padx=(4, 8))

    def append_output(self, text: str):
        """Adiciona texto à caixa de saída de forma thread-safe."""
        def _append():
            self.output.config(state='normal')
            self.output.insert('end', text)
            self.output.see('end')
            self.output.config(state='disabled')
        
        self.after(0, _append)

    def _run_subprocess(self, cmd, cwd=None):
        """Executa um comando de subprocess e captura a saída."""
        self.append_output(f'> {" ".join(cmd)}\n')
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
        except Exception as e:
            self.append_output(f'Erro ao iniciar o processo: {e}\n')
            return 1

        for line in proc.stdout:
            self.append_output(line)

        proc.wait()
        self.append_output(f'Processo terminou com código {proc.returncode}\n')
        return proc.returncode

    def install_dependencies(self):
        """Instala as dependências do ficheiro requirements.txt."""
        if not os.path.exists(REQUIREMENTS):
            messagebox.showwarning('Ficheiro não encontrado', f'Não foi encontrado {REQUIREMENTS}')
            return

        # Ensure admin privileges before installing system-wide packages
        if not is_windows_admin():
            proceed = messagebox.askyesno('Privilégios necessários',
                                          'A instalação de dependências pode requerer privilégios de administrador. Reiniciar o instalador com privilégios?')
            if proceed:
                if relaunch_as_admin():
                    self.destroy()
                    return
            else:
                self.append_output('Instalação cancelada — privilégios não concedidos.\n')
                return

        def worker():
            self.status.config(text='Instalando dependências...')
            self.install_btn.config(state='disabled')
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS]
            code = self._run_subprocess(cmd, cwd=REPO_DIR)
            if code == 0:
                self.append_output('✓ Dependências instaladas com sucesso!\n')
                self.status.config(text='Dependências instaladas')
            else:
                self.append_output('✗ Erro na instalação de dependências.\n')
                self.status.config(text='Erro na instalação')
            self.install_btn.config(state='normal')

        threading.Thread(target=worker, daemon=True).start()

    def install_from_github_prompt(self):
        """Pede confirmação do utilizador para instalar a partir do GitHub."""
        repo = self.repo_entry.get().strip()
        dest = self.dest_entry.get().strip()
        if not repo:
            messagebox.showwarning('Repo inválido', 'Introduza o repositório no formato owner/repo')
            return
        if not dest:
            messagebox.showwarning('Pasta inválida', 'Introduza a pasta de instalação')
            return

        if os.path.exists(dest) and os.listdir(dest):
            if not messagebox.askyesno('Confirmar', f'A pasta {dest} não está vazia — prosseguir e SOBREPOR?'):
                return

        # Ensure admin privileges before installing to system locations
        if not is_windows_admin():
            proceed = messagebox.askyesno('Privilégios necessários',
                                          'A instalação a partir do GitHub pode requerer privilégios de administrador. Reiniciar o instalador com privilégios?')
            if proceed:
                started = relaunch_as_admin()
                if started:
                    self.destroy()
                    return
                else:
                    messagebox.showerror('Erro', 'Não foi possível relançar com privilégios')
            else:
                self.append_output('Instalação GitHub cancelada — privilégios não concedidos.\n')
                return

        threading.Thread(target=self.install_from_github, args=(repo, dest), daemon=True).start()

    def install_from_github(self, owner_repo: str, dest_dir: str, branch: str = 'main'):
        """Descarrega o repositório do GitHub, extrai e instala dependências."""
        self.status.config(text='Baixando do GitHub...')
        self.net_btn.config(state='disabled')
        url = f'https://github.com/{owner_repo}/archive/refs/heads/{branch}.zip'
        self.append_output(f'Download: {url}\n')

        tmpdir = None
        try:
            tmpdir = tempfile.mkdtemp(prefix='pixlet_')
            zip_path = os.path.join(tmpdir, 'repo.zip')
            self.append_output(f'Baixando para {zip_path} ...\n')
            urllib.request.urlretrieve(url, zip_path)
            self.append_output('Download concluído. Extraindo...\n')
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir)

            # Find extracted folder (should be repo_name-branch format)
            extracted_dirs = [d for d in os.listdir(tmpdir) if os.path.isdir(os.path.join(tmpdir, d)) and d != '__MACOSX']
            if not extracted_dirs:
                raise RuntimeError('Não foi possível localizar a raíz do repositório extraído')
            repo_root = os.path.join(tmpdir, extracted_dirs[0])
            self.append_output(f'Pasta extraída: {extracted_dirs[0]}\n')

            # Prepare destination
            if os.path.exists(dest_dir):
                try:
                    shutil.rmtree(dest_dir)
                except Exception:
                    pass
            os.makedirs(dest_dir, exist_ok=True)
            self.append_output(f'Copiando ficheiros para {dest_dir} ...\n')
            
            # Copy contents
            for item in os.listdir(repo_root):
                s = os.path.join(repo_root, item)
                d = os.path.join(dest_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            self.append_output('Ficheiros copiados. Instalando dependências...\n')
            req = os.path.join(dest_dir, 'requirements.txt')
            if os.path.exists(req):
                code = self._run_subprocess([sys.executable, '-m', 'pip', 'install', '-r', req], cwd=dest_dir)
                if code != 0:
                    self.append_output('Erro na instalação de dependências. Ver saída.\n')
            else:
                self.append_output('requirements.txt não encontrado no repositório extraído.\n')

            # Create shortcut to the installed qt_browser.py if present
            installed_qt = os.path.join(dest_dir, 'qt_browser.py')
            if os.path.exists(installed_qt):
                desk = desktop_path()
                if desk and os.path.isdir(desk):
                    bat_path = os.path.join(desk, 'Pixlet-Browser.bat')
                    content = f'@echo off\ncd /d "{dest_dir}"\n"{sys.executable}" "{installed_qt}" %*\npause\n'
                    try:
                        with open(bat_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.append_output(f'✓ Atalho criado: {bat_path}\n')
                    except Exception as e:
                        self.append_output(f'✗ Erro ao criar atalho: {e}\n')
                else:
                    self.append_output(f'Aviso: Pasta de atalhos não encontrada, atalho não criado\n')
            else:
                self.append_output(f'Aviso: qt_browser.py não encontrado na instalação\n')

            self.append_output('✓ Instalação a partir do GitHub concluída.\n')
            self.status.config(text='Instalação GitHub concluída')
            messagebox.showinfo('Sucesso', f'Instalação concluída em {dest_dir}')
        except Exception as e:
            self.append_output(f'✗ Erro durante instalação GitHub: {e}\n')
            self.status.config(text='Erro na instalação GitHub')
            messagebox.showerror('Erro', f'Erro na instalação: {e}')
        finally:
            self.net_btn.config(state='normal')
            if tmpdir and os.path.exists(tmpdir):
                try:
                    shutil.rmtree(tmpdir)
                except Exception:
                    pass

    def create_shortcut(self):
        """Cria um atalho na Área de Trabalho para executar o navegador."""
        desk = desktop_path()
        
        # Verify we have a valid directory
        if not os.path.isdir(desk):
            self.append_output(f'Pasta de área de trabalho não encontrada: {desk}\n')
            self._show_shortcut_help_dialog(desk)
            return

        python_exec = sys.executable
        bat_path = os.path.join(desk, 'Pixlet-Browser.bat')
        content = f'@echo off\ncd /d "{REPO_DIR}"\n"{python_exec}" "{QT_BROWSER}" %*\npause\n'
        
        # Try to create the shortcut
        try:
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.append_output(f'✓ Atalho criado com sucesso: {bat_path}\n')
            messagebox.showinfo('Sucesso', f'Atalho criado em:\n{bat_path}\n\nProcure "Pixlet-Browser.bat" na sua Área de Trabalho.')
        except Exception as e:
            self.append_output(f'✗ Erro ao criar atalho: {e}\n')
            self._show_shortcut_help_dialog(desk, error=str(e))

    def _show_shortcut_help_dialog(self, desk_path, error=None):
        """Mostra um diálogo com instruções para criar atalho manualmente."""
        python_exec = sys.executable
        help_win = tk.Toplevel(self)
        help_win.title('Ajuda para Criar Atalho')
        help_win.geometry('600x500')

        frm = ttk.Frame(help_win, padding=12)
        frm.pack(fill='both', expand=True)

        if error:
            ttk.Label(frm, text=f'Erro detectado:', font=('Segoe UI', 10, 'bold'), foreground='red').pack(anchor='w')
            ttk.Label(frm, text=error, wraplength=550, foreground='red').pack(anchor='w', pady=(0, 12))

        ttk.Label(frm, text='Como criar o atalho manualmente:', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(12, 0))

        instructions_text = f"""
1. LOCALIZAÇÃO DA ÁREA DE TRABALHO DETECTADA:
   {desk_path}

2. OPÇÃO A - Criar um arquivo .bat (recomendado):
   
   a) Clique com botão DIREITO na Área de Trabalho
   b) Selecione "Novo" → "Documento de Texto"
   c) Cole o seguinte:
   
      @echo off
      cd /d "{REPO_DIR}"
      "{python_exec}" "{QT_BROWSER}" %*
      pause
   
   d) Guarde como "Pixlet-Browser.bat" (com extensão .bat)
   e) Dê um duplo clique para testar

3. OPÇÃO B - Criar um atalho (.lnk):
   
   a) Clique com botão DIREITO na Área de Trabalho
   b) Selecione "Novo" → "Atalho"
   c) Introduza:
      {python_exec} "{QT_BROWSER}"
   d) Dê o nome "Pixlet Browser"
   e) Clique "Concluir"

4. TESTAR:
   - Procure o atalho na Área de Trabalho
   - Dê um duplo clique
   - A janela do navegador deve abrir-se

Se nenhuma das opções funcionar, abra uma janela de Comando e execute:
   python "{QT_BROWSER}"
"""

        txt = scrolledtext.ScrolledText(frm, height=18, width=70)
        txt.pack(fill='both', expand=True, pady=(8, 0))
        txt.insert('1.0', instructions_text)
        txt.config(state='disabled')

        # Button to copy instructions to clipboard
        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(instructions_text)
            messagebox.showinfo('Copiar', 'Instruções copiadas para a área de transferência')

        ttk.Button(frm, text='Copiar instruções', command=copy_to_clipboard).pack(pady=(8, 0), side='left')
        ttk.Button(frm, text='Fechar', command=help_win.destroy).pack(pady=(8, 0), side='right')

    def generate_icon(self):
        """Placeholder para geração de ícone."""
        self.append_output('Funcionalidade de geração de ícone ainda não implementada.\n')
        messagebox.showinfo('Info', 'Esta funcionalidade será implementada em breve.')

    def run_browser(self):
        """Executa o navegador diretamente."""
        if not os.path.exists(QT_BROWSER):
            messagebox.showerror('Erro', f'Ficheiro não encontrado: {QT_BROWSER}')
            return

        def worker():
            self.status.config(text='Executando navegador...')
            self.append_output(f'Iniciando {QT_BROWSER}...\n')
            try:
                subprocess.Popen([sys.executable, QT_BROWSER])
                self.append_output('Navegador iniciado com sucesso.\n')
            except Exception as e:
                self.append_output(f'Erro ao iniciar navegador: {e}\n')
            self.status.config(text='Pronto')

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = InstallerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
