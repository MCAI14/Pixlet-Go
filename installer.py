import os
import sys
import threading
import subprocess
import ctypes
import urllib.request
import zipfile
import shutil
import tempfile
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Try to import winreg for Windows Registry access (Desktop path detection)
try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False


REPO_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(REPO_DIR, 'requirements.txt')
QT_BROWSER = os.path.join(REPO_DIR, 'qt_browser.py')


def desktop_path():
    r"""Find the Desktop folder path.
    
    On Windows with OneDrive enabled, the Desktop is typically in OneDrive
    (e.g., C:\Users\<user>\OneDrive\Ambiente de Trabalho on Portuguese systems).
    
    This function tries:
    1. Windows Registry (most reliable for OneDrive redirected folders)
    2. Common folder names on disk
    3. Fallback to home directory
    """
    
    # Try Windows Registry first (most reliable)
    if HAS_WINREG and os.name == 'nt':
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            desktop_path_from_reg, _ = winreg.QueryValueEx(key, 'Desktop')
            winreg.CloseKey(key)
            
            if desktop_path_from_reg and os.path.isdir(desktop_path_from_reg):
                return desktop_path_from_reg
        except Exception:
            pass  # Fall through to folder search
    
    # Fallback: try common folder names
    userprofile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    
    # Try the standard Windows Desktop folder name first (internal)
    desktop_candidate = os.path.join(userprofile, 'Desktop')
    if os.path.isdir(desktop_candidate):
        return desktop_candidate
    
    # Common desktop folder names in different languages (especially with OneDrive)
    desktop_names = [
        'Ambiente de Trabalho',  # Portuguese
        'Área de Trabalho',  # Portuguese variant
        'Bureau',  # French
        'Escritorio',  # Spanish
        'Schreibtisch',  # German
        'Рабочий стол',  # Russian
        '桌面',  # Chinese
    ]
    
    # Try in USERPROFILE
    for desktop_name in desktop_names:
        desktop_path_candidate = os.path.join(userprofile, desktop_name)
        if os.path.isdir(desktop_path_candidate):
            return desktop_path_candidate
    
    # Try in OneDrive if it exists
    onedrive = os.path.join(userprofile, 'OneDrive')
    if os.path.isdir(onedrive):
        for desktop_name in desktop_names:
            desktop_path_candidate = os.path.join(onedrive, desktop_name)
            if os.path.isdir(desktop_path_candidate):
                return desktop_path_candidate
    
    # Final fallback: use USERPROFILE or home
    return userprofile if os.path.isdir(userprofile) else os.path.expanduser('~')


def is_windows_admin() -> bool:
    """Return True if running with Windows admin privileges."""
    if os.name != 'nt':
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    """Relaunch the current script with admin privileges (Windows UAC).
    Returns True if the relaunch was started, False otherwise.
    """
    if os.name != 'nt':
        return False
    python_exe = sys.executable
    script = os.path.abspath(__file__)
    params = f'"{python_exe}" "{script}"'
    try:
        # ShellExecuteW returns an instance handle > 32 on success
        h = ctypes.windll.shell32.ShellExecuteW(None, 'runas', python_exe, f'"{script}"', None, 1)
        return int(h) > 32
    except Exception:
        return False


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Pixlet - Installer')
        self.geometry('700x480')

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text='Instalador do Pixlet Browser', font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        ttk.Label(frm, text='Instala dependências e cria um atalho na sua área de trabalho.').pack(anchor='w', pady=(0,8))

        # Buttons
        btns = ttk.Frame(frm)
        btns.pack(fill='x', pady=6)

        self.install_btn = ttk.Button(btns, text='Instalar dependências', command=self.install_dependencies)
        self.install_btn.pack(side='left')

        self.shortcut_btn = ttk.Button(btns, text='Criar atalho na área de trabalho', command=self.create_shortcut)
        self.shortcut_btn.pack(side='left', padx=8)

        self.run_btn = ttk.Button(btns, text='Executar navegador agora', command=self.run_browser)
        self.run_btn.pack(side='left')

        self.net_btn = ttk.Button(btns, text='Instalar da Internet (GitHub)', command=self.install_from_github_prompt)
        self.net_btn.pack(side='left', padx=8)

        ttk.Button(btns, text='Fechar', command=self.destroy).pack(side='right')

        # Output box
        ttk.Label(frm, text='Saída:').pack(anchor='w', pady=(8,0))
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
        opts.pack(fill='x', pady=(6,0))
        ttk.Label(opts, text='Repo GitHub (owner/repo):').pack(side='left')
        self.repo_entry = ttk.Entry(opts, width=30, textvariable=self.github_default)
        self.repo_entry.pack(side='left', padx=(4,8))
        ttk.Label(opts, text='Pasta de instalação:').pack(side='left')
        self.dest_entry = ttk.Entry(opts, width=40, textvariable=self.install_dir_default)
        self.dest_entry.pack(side='left', padx=(4,8))

    def append_output(self, text: str):
        def _append():
            self.output.configure(state='normal')
            self.output.insert('end', text)
            self.output.see('end')
            self.output.configure(state='disabled')
        self.after(0, _append)

    def _run_subprocess(self, cmd, cwd=None):
        self.append_output(f'> {" ".join(cmd)}\n')
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, text=True)
        except Exception as e:
            self.append_output(f'Falha ao iniciar processo: {e}\n')
            return -1

        for line in proc.stdout:
            self.append_output(line)

        proc.wait()
        self.append_output(f'Processo terminou com código {proc.returncode}\n')
        return proc.returncode

    def install_dependencies(self):
        if not os.path.exists(REQUIREMENTS):
            messagebox.showwarning('Ficheiro não encontrado', f'Não foi encontrado {REQUIREMENTS}')
            return

        # Ensure admin privileges before installing system-wide packages
        if not is_windows_admin():
            # ask the user to restart with elevation
            proceed = messagebox.askyesno('Privilégios necessários',
                                          'A instalação de dependências pode requerer privilégios de administrador. Reiniciar o instalador com privilégios?')
            if proceed:
                started = relaunch_as_admin()
                if started:
                    self.append_output('A reiniciar o instalador com privilégios de administrador...\n')
                    self.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror('Falha', 'Não foi possível reiniciar com privilégios de administrador.')
                    return
            else:
                # user declined elevation
                self.append_output('Instalação cancelada — privilégios não concedidos.\n')
                return

        def worker():
            self.status.config(text='Instalando dependências...')
            self.install_btn.config(state='disabled')
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS]
            code = self._run_subprocess(cmd, cwd=REPO_DIR)
            if code == 0:
                self.append_output('Instalação concluída com sucesso.\n')
                self.status.config(text='Instalação concluída')
            else:
                self.append_output('Erro durante a instalação. Verifique a saída acima.\n')
                self.status.config(text='Erro na instalação')
            self.install_btn.config(state='normal')

        threading.Thread(target=worker, daemon=True).start()

    def install_from_github_prompt(self):
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
                    self.append_output('A reiniciar o instalador com privilégios de administrador...\n')
                    self.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror('Falha', 'Não foi possível reiniciar com privilégios de administrador.')
                    return
            else:
                self.append_output('Instalação GitHub cancelada — privilégios não concedidos.\n')
                return

        threading.Thread(target=self.install_from_github, args=(repo, dest), daemon=True).start()

    def install_from_github(self, owner_repo: str, dest_dir: str, branch: str = 'main'):
        """Download the repository source code zip from GitHub, extract to dest_dir, run pip install -r and create shortcut."""
        self.status.config(text='Baixando do GitHub...')
        self.net_btn.config(state='disabled')
        url = f'https://github.com/{owner_repo}/archive/refs/heads/{branch}.zip'
        self.append_output(f'Download: {url}\n')

        try:
            tmpdir = tempfile.mkdtemp(prefix='pixlet_')
            zip_path = os.path.join(tmpdir, 'repo.zip')
            self.append_output(f'Baixando para {zip_path} ...\n')
            urllib.request.urlretrieve(url, zip_path)
            self.append_output('Download concluído. Extraindo...\n')
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir)

            # Find extracted folder (should be repo_name-branch format, e.g., Pixlet-Go-main)
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
            # copy contents
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
                        self.append_output(f'Atalho criado: {bat_path}\n')
                    except Exception as e:
                        self.append_output(f'Aviso: Não foi possível criar atalho: {e}\n')
                else:
                    self.append_output(f'Aviso: Pasta de atalhos não encontrada, atalho não criado\n')
            else:
                self.append_output(f'Aviso: qt_browser.py não encontrado na instalação\n')

            self.append_output('Instalação a partir do GitHub concluída.\n')
            self.status.config(text='Instalação GitHub concluída')
        except Exception as e:
            self.append_output(f'Erro durante instalação GitHub: {e}\n')
            self.status.config(text='Erro na instalação GitHub')
        finally:
            self.net_btn.config(state='normal')
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                pass

    def create_shortcut(self):
        """Create a shortcut with optional manual fallback dialog."""
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
        """Show a helper dialog with manual shortcut creation instructions."""
        python_exec = sys.executable
        help_win = tk.Toplevel(self)
        help_win.title('Ajuda para Criar Atalho')
        help_win.geometry('600x500')

        frm = ttk.Frame(help_win, padding=12)
        frm.pack(fill='both', expand=True)

        if error:
            ttk.Label(frm, text=f'Erro detectado:', font=('Segoe UI', 10, 'bold'), foreground='red').pack(anchor='w')
            ttk.Label(frm, text=error, wraplength=550, foreground='red').pack(anchor='w', pady=(0, 12))

        ttk.Label(frm, text='Como criar o atalho manualmente:', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(12,0))

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
        txt.pack(fill='both', expand=True, pady=(8,0))
        txt.insert('1.0', instructions_text)
        txt.config(state='disabled')

        # Button to copy instructions to clipboard
        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(instructions_text)
            messagebox.showinfo('Copiar', 'Instruções copiadas para a área de transferência')

        ttk.Button(frm, text='Copiar instruções', command=copy_to_clipboard).pack(pady=(8,0), side='left')
        ttk.Button(frm, text='Fechar', command=help_win.destroy).pack(pady=(8,0), side='right')

    def run_browser(self):
        if not os.path.exists(QT_BROWSER):
            messagebox.showerror('Não encontrado', f'Não foi encontrado {QT_BROWSER}')
            return

        try:
            self.append_output('A executar o navegador...\n')
            subprocess.Popen([sys.executable, QT_BROWSER], cwd=REPO_DIR)
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao executar o navegador: {e}')


def main():
    app = InstallerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
