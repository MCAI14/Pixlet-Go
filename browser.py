"""
Navegador Python com interface Tkinter e renderização HTML
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import urllib.request
import urllib.error
from html.parser import HTMLParser
import re
from typing import List


class SimpleHTMLRenderer(HTMLParser):
    """Parser simples para renderizar HTML em Tkinter"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.text_parts = []
        self.skip_script = False
        self.skip_style = False
        self.in_button = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.skip_script = True
        elif tag == 'style':
            self.skip_style = True
        elif tag in ['p', 'div', 'section', 'article', 'main']:
            if self.text_parts and self.text_parts[-1] != '\n':
                self.text_parts.append('\n')
        elif tag == 'h1':
            self.text_parts.append('\n' + '═'*60 + '\n')
        elif tag == 'h2':
            self.text_parts.append('\n' + '─'*60 + '\n')
        elif tag == 'h3':
            self.text_parts.append('\n► ')
        elif tag == 'h4':
            self.text_parts.append('\n  ▸ ')
        elif tag == 'br':
            self.text_parts.append('\n')
        elif tag == 'hr':
            self.text_parts.append('\n' + '═'*60 + '\n')
        elif tag == 'a':
            self.text_parts.append('[')
        elif tag in ['b', 'strong']:
            self.text_parts.append('█')
        elif tag in ['i', 'em']:
            self.text_parts.append('▸')
        elif tag == 'li':
            self.text_parts.append('\n  • ')
        elif tag == 'ul':
            self.text_parts.append('\n')
        elif tag == 'ol':
            self.text_parts.append('\n')
        elif tag == 'button':
            self.in_button = True
            self.text_parts.append('[BTN: ')
        elif tag == 'img':
            alt = dict(attrs).get('alt', 'imagem')
            self.text_parts.append(f' [IMG: {alt}] ')
        elif tag == 'input':
            input_type = dict(attrs).get('type', 'text')
            placeholder = dict(attrs).get('placeholder', '')
            if placeholder:
                self.text_parts.append(f'[{input_type.upper()}: {placeholder}]')
            else:
                self.text_parts.append(f'[{input_type.upper()}]')
        elif tag == 'select':
            self.text_parts.append('[DROPDOWN]')
        elif tag == 'textarea':
            self.text_parts.append('[TEXTAREA]')
        elif tag == 'span':
            pass  # Não adiciona quebra para span
            
    def handle_endtag(self, tag):
        if tag == 'script':
            self.skip_script = False
        elif tag == 'style':
            self.skip_style = False
        elif tag == 'h1':
            self.text_parts.append('\n' + '═'*60 + '\n')
        elif tag == 'h2':
            self.text_parts.append('\n' + '─'*60 + '\n')
        elif tag in ['h3', 'h4']:
            self.text_parts.append('\n')
        elif tag in ['p', 'div', 'section', 'article', 'main']:
            if self.text_parts and self.text_parts[-1] != '\n':
                self.text_parts.append('\n')
        elif tag == 'a':
            self.text_parts.append(']')
        elif tag in ['b', 'strong']:
            self.text_parts.append('█')
        elif tag in ['i', 'em']:
            self.text_parts.append('▸')
        elif tag == 'button':
            self.in_button = False
            self.text_parts.append(']')
        elif tag in ['ul', 'ol']:
            self.text_parts.append('\n')
            
    def handle_data(self, data):
        if self.skip_script or self.skip_style:
            return
            
        text = data.strip()
        if text:
            # Limpar espaços múltiplos
            text = ' '.join(text.split())
            self.text_parts.append(text + ' ')
            
    def handle_entityref(self, name):
        if self.skip_script or self.skip_style:
            return
            
        entities = {
            'nbsp': ' ',
            'lt': '<',
            'gt': '>',
            'amp': '&',
            'quot': '"',
            'apos': "'",
        }
        self.text_parts.append(entities.get(name, '&' + name + ';'))
        
    def get_text(self):
        text = ''.join(self.text_parts)
        # Limpar múltiplas quebras de linha
        text = re.sub(r'\n\n\n+', '\n\n', text)
        # Remove espaços extras no início das linhas
        lines = text.split('\n')
        text = '\n'.join(line.strip() if line.strip() else '' for line in lines)
        return text.strip()


class SimpleBrowser:
    """Navegador simples com interface Tkinter"""

    def __init__(self, root):
        self.root = root
        self.root.title("Pixlet Browser")
        self.root.geometry("1200x800")
        
        self.history = []
        self.history_index = -1
        self.current_url = ""
        self.current_html = ""
        
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface gráfica"""
        
        # Barra de ferramentas
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Botão voltar
        ttk.Button(toolbar, text="← Voltar", command=self.go_back).pack(side=tk.LEFT, padx=2)
        
        # Botão avançar
        ttk.Button(toolbar, text="Avançar →", command=self.go_forward).pack(side=tk.LEFT, padx=2)
        
        # Botão recarregar
        ttk.Button(toolbar, text="⟲ Recarregar", command=self.reload).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Campo de URL
        ttk.Label(toolbar, text="URL:").pack(side=tk.LEFT, padx=2)
        self.url_entry = ttk.Entry(toolbar)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.bind("<Return>", lambda e: self.navigate())
        
        # Botão navegar
        ttk.Button(toolbar, text="Ir", command=self.navigate).pack(side=tk.LEFT, padx=2)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba 1: Renderização
        render_frame = ttk.Frame(self.notebook)
        self.notebook.add(render_frame, text="🌐 Renderizado")
        
        # Área de informações
        info_frame = ttk.LabelFrame(render_frame, text="Informações da Página", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="URL atual:").pack(anchor=tk.W)
        self.current_url_label = ttk.Label(info_frame, text="", wraplength=1100, foreground="green", font=("Arial", 9))
        self.current_url_label.pack(anchor=tk.W, padx=20)
        
        # Área de conteúdo renderizado
        ttk.Label(render_frame, text="Conteúdo da Página:").pack(anchor=tk.W, padx=5)
        
        self.render_text = scrolledtext.ScrolledText(
            render_frame, height=30, width=150, wrap=tk.WORD, font=("Arial", 10)
        )
        self.render_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.render_text.config(state=tk.DISABLED)
        
        # Aba 2: HTML bruto
        html_frame = ttk.Frame(self.notebook)
        self.notebook.add(html_frame, text="📝 HTML Bruto")
        
        ttk.Label(html_frame, text="Código HTML completo:").pack(anchor=tk.W, padx=5, pady=2)
        
        self.html_text = scrolledtext.ScrolledText(
            html_frame, height=30, width=150, wrap=tk.WORD, font=("Courier", 9)
        )
        self.html_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.html_text.config(state=tk.DISABLED)
        
        # Aba 3: Ferramentas
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="🛠️ Ferramentas")
        
        ttk.Label(tools_frame, text="Ferramentas do Navegador", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Button(
            tools_frame, 
            text="💾 Salvar HTML", 
            command=self.save_html
        ).pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Button(
            tools_frame, 
            text="🔎 Pesquisar texto", 
            command=self.show_search_dialog
        ).pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Button(
            tools_frame, 
            text="📊 Estatísticas da página", 
            command=self.show_stats
        ).pack(pady=5, padx=5, fill=tk.X)
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def navigate(self):
        """Navega para a URL digitada"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL")
            return
        
        if not url.startswith("http"):
            url = "https://" + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        self.status_var.set("Carregando...")
        self.root.update()
        threading.Thread(target=self._fetch_url, args=(url,), daemon=True).start()

    def _fetch_url(self, url: str):
        """Busca conteúdo da URL em uma thread"""
        try:
            # Adicionar ao histórico
            if self.history_index + 1 < len(self.history):
                self.history = self.history[:self.history_index + 1]
            self.history.append(url)
            self.history_index += 1
            
            # Fazer requisição
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
                # Renderizar HTML
                parser = SimpleHTMLRenderer()
                parser.feed(html_content)
                rendered_text = parser.get_text()
                
                # Atualizar UI
                self.current_url = url
                self.current_html = html_content
                self.current_url_label.config(text=url)
                
                # Mostrar HTML bruto
                self.html_text.config(state=tk.NORMAL)
                self.html_text.delete(1.0, tk.END)
                self.html_text.insert(1.0, html_content)
                self.html_text.config(state=tk.DISABLED)
                
                # Mostrar renderizado
                self.render_text.config(state=tk.NORMAL)
                self.render_text.delete(1.0, tk.END)
                self.render_text.insert(1.0, rendered_text)
                self.render_text.config(state=tk.DISABLED)
                
                self.status_var.set(f"✓ Carregado: {url}")
                
        except urllib.error.URLError as e:
            messagebox.showerror("Erro", f"Erro ao acessar URL: {e}")
            self.status_var.set("Erro ao carregar")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")
            self.status_var.set("Erro ao carregar")

    def go_back(self):
        """Volta à página anterior"""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.navigate()
        else:
            messagebox.showinfo("Aviso", "Não há página anterior")

    def go_forward(self):
        """Avança para a próxima página"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.navigate()
        else:
            messagebox.showinfo("Aviso", "Não há próxima página")

    def reload(self):
        """Recarrega a página"""
        if self.current_url:
            self.navigate()
        else:
            messagebox.showwarning("Aviso", "Navegue para um site primeiro")

    def save_html(self):
        """Salva o HTML da página"""
        if not self.current_html:
            messagebox.showwarning("Aviso", "Navegue para um site primeiro")
            return
        
        try:
            filename = "pagina.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.current_html)
            messagebox.showinfo("Sucesso", f"HTML salvo: {filename}")
            self.status_var.set(f"✓ HTML salvo: {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def show_search_dialog(self):
        """Mostra diálogo para pesquisar texto na página"""
        if not self.current_html:
            messagebox.showwarning("Aviso", "Navegue para um site primeiro")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Pesquisar")
        dialog.geometry("400x150")
        
        ttk.Label(dialog, text="Texto a pesquisar:").pack(padx=10, pady=5)
        
        search_entry = ttk.Entry(dialog)
        search_entry.pack(fill=tk.X, padx=10, pady=5)
        search_entry.focus()
        
        def search():
            text = search_entry.get().strip().lower()
            if not text:
                messagebox.showwarning("Aviso", "Digite um texto para pesquisar")
                return
            
            html_lower = self.current_html.lower()
            count = html_lower.count(text)
            
            if count > 0:
                messagebox.showinfo("Resultado", f"'{text}' encontrado {count} vez(es)")
            else:
                messagebox.showinfo("Resultado", f"'{text}' não encontrado")
            
            dialog.destroy()
        
        ttk.Button(dialog, text="Pesquisar", command=search).pack(pady=10)

    def show_stats(self):
        """Mostra estatísticas da página"""
        if not self.current_html:
            messagebox.showwarning("Aviso", "Navegue para um site primeiro")
            return
        
        stats = {
            "Tamanho do HTML": f"{len(self.current_html):,} caracteres",
            "Número de tags": len(re.findall(r'<[^>]+>', self.current_html)),
            "Número de links": len(re.findall(r'href=[\'"]([^\'"]+)[\'"]', self.current_html)),
            "Número de imagens": len(re.findall(r'<img[^>]*>', self.current_html)),
            "Número de parágrafos": self.current_html.count('<p'),
            "Número de divs": self.current_html.count('<div'),
        }
        
        stats_text = "Estatísticas da Página:\n\n" + "\n".join(f"{k}: {v}" for k, v in stats.items())
        messagebox.showinfo("Estatísticas", stats_text)

    def _execute_js_async(self, code: str):
        try:
            result = self.loop.run_until_complete(self.page.evaluate(code))
            messagebox.showinfo("Resultado JavaScript", f"Resultado: {result}")
            self.status_var.set(f"✓ JavaScript executado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar: {e}")


def main():
    """Inicia a aplicação"""
    root = tk.Tk()
    app = SimpleBrowser(root)
    root.mainloop()


if __name__ == "__main__":
    main()
