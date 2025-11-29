"""
Script para testar o navegador com carregamento de sites
"""

import tkinter as tk
from browser import SimpleBrowser
import time
import threading


def load_site(app, url):
    """Carrega um site no navegador"""
    time.sleep(1)  # Aguardar a UI estar pronta
    app.url_entry.delete(0, tk.END)
    app.url_entry.insert(0, url)
    app.navigate()


def main():
    """Inicia o navegador com um site pré-carregado"""
    root = tk.Tk()
    app = SimpleBrowser(root)
    
    # Carregar Google em uma thread
    threading.Thread(
        target=load_site, 
        args=(app, "https://www.google.com"),
        daemon=True
    ).start()
    
    root.mainloop()


if __name__ == "__main__":
    main()
