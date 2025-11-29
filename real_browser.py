"""
Navegador Real em Python - Similar ao Chrome
Usa PyWebView para renderizar páginas HTML de verdade
"""

import webview
import threading


class BrowserAPI:
    """API para controlar o navegador"""
    
    def __init__(self):
        self.current_url = "https://www.pixlet.netlify.app/"
        
    def navigate(self, url):
        """Navega para uma URL"""
        if not url.startswith("http"):
            url = "https://" + url
        self.current_url = url
        # Tenta atualizar o iframe no HTML da UI
        try:
            self.window.evaluate_js(f"document.getElementById('browser-frame').src = '{url}';")
        except Exception:
            # Fallback: carrega a URL na janela principal
            try:
                self.window.load_url(url)
            except Exception:
                pass
        
    def go_back(self):
        """Volta à página anterior"""
        self.window.evaluate_js("window.history.back()")
        
    def go_forward(self):
        """Avança para a próxima página"""
        try:
            # tenta usar o histórico do iframe (pode falhar por CORS)
            self.window.evaluate_js("var f=document.getElementById('browser-frame'); try{f.contentWindow.history.forward();}catch(e){ };")
        except Exception:
            pass
        
    def reload(self):
        """Recarrega a página"""
        try:
            self.window.evaluate_js("var f=document.getElementById('browser-frame'); try{f.contentWindow.location.reload();}catch(e){ window.location.reload(); };")
        except Exception:
            pass


def main():
    """Inicia o navegador"""
    api = BrowserAPI()
    
    # Criar janela do navegador
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pixlet Browser</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            .toolbar {
                display: flex;
                gap: 10px;
                padding: 10px;
                background: #f5f5f5;
                border-bottom: 1px solid #ddd;
                align-items: center;
            }
            .toolbar button {
                padding: 8px 12px;
                border: 1px solid #ccc;
                background: white;
                cursor: pointer;
                border-radius: 4px;
                font-size: 14px;
            }
            .toolbar button:hover {
                background: #e0e0e0;
            }
            .url-bar {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            #browser-frame {
                width: 100%;
                height: calc(100vh - 60px);
                border: none;
            }
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button onclick="goBack()">← Voltar</button>
            <button onclick="goForward()">Avançar →</button>
            <button onclick="reload()">⟲ Recarregar</button>
            <input type="text" class="url-bar" id="urlInput" placeholder="Digite a URL aqui..." value="https://pixlet.netlify.app/">
            <button onclick="navigate()">Ir</button>
        </div>
        <iframe id="browser-frame"></iframe>
        
        <script>
            function navigate() {
                const url = document.getElementById('urlInput').value;
                pywebview.api.navigate(url).then(() => {
                    location.href = url;
                });
            }
            
            function goBack() {
                pywebview.api.go_back();
            }
            
            function goForward() {
                pywebview.api.go_forward();
            }
            
            function reload() {
                pywebview.api.reload();
            }
            
            document.getElementById('urlInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') navigate();
            });
            
            // Carregar Google ao iniciar
            window.location.href = 'https://pixlet.netlify.app/';
        </script>
    </body>
    </html>
    """
    
    # Criar a janela com a interface (toolbar + iframe) como HTML
    api.window = webview.create_window(
        'Pixlet Browser',
        html,
        js_api=api,
        width=1200,
        height=800,
        resizable=True
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
