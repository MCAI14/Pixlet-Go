#!/usr/bin/env python3
"""
Create GitHub release for Pixlet-Go v0.2.0
"""
import os
import json
import subprocess
from urllib.request import Request, urlopen
from urllib.error import URLError

REPO_OWNER = "MCAI14"
REPO_NAME = "Pixlet-Go"
TAG_NAME = "v0.2.0"
RELEASE_NAME = "v0.2.0 - Icon Support & OneDrive Support"
RELEASE_BODY = """## Pixlet Browser v0.2.0

### Novas Funcionalidades / New Features

✨ **Suporte para Ícone SVG / SVG Icon Support**
- Converter SVG para ICO usando Pillow + cairosvg ou ImageMagick
- Aplicar ícone personalizado aos atalhos (.lnk)
- Botão "Gerar ícone" no installer

✨ **Melhor Suporte para OneDrive**
- Detectar corretamente a Área de Trabalho em sistemas com OneDrive ativado
- Usar Windows Registry para encontrar o caminho correto
- Fallback automático para múltiplos idiomas (português, inglês, francês, espanhol, etc.)

✨ **Criação Melhorada de Atalhos**
- Criar atalhos `.lnk` (melhor que `.bat`) com ícone
- Suporte via win32com (Python) ou VBScript (padrão Windows)
- Fallback automático se um método falhar

✨ **Instruções em Português**
- Ficheiro `CRIAR_ATALHO.txt` com instruções passo-a-passo para criar manualmente
- Diálogo visual de ajuda no installer

### Ficheiros Adicionados / Added Files

- `create_icon.py` - Script para converter SVG em ícone
- `create_shortcut.vbs` - Script VBScript para criar atalhos
- `Pixlet.svg` - Ícone original em formato SVG
- `CRIAR_ATALHO.txt` - Instruções em português

### Melhorias / Improvements

- Melhor tratamento de erros em imports opcionais
- Suporte robusto para múltiplas línguas e configurações do Windows
- Código mais modular e testável

### Requisitos Opcionais / Optional Requirements

Para gerar ícones a partir do SVG, instale:
```bash
pip install pillow cairosvg
```

Ou use ImageMagick/Inkscape (já disponível em muitos sistemas).

---

**Compatível com:** Windows 7+, Python 3.9+, PySide6

**Criado com:** Python, Tkinter, Qt WebEngine

### Changelog

- [x] Desktop path detection com suporte a OneDrive
- [x] Conversão de SVG para ICO
- [x] Criação de atalhos com ícone personalizado
- [x] Tratamento de erros robusto
- [x] Instruções em português

---

Para mais informações, visite: https://github.com/MCAI14/Pixlet-Go
"""

def create_release():
    """Create a GitHub release using the API."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("ERRO: Variável GITHUB_TOKEN não definida")
        print("Configure com o seu token do GitHub")
        return False
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    data = {
        "tag_name": TAG_NAME,
        "target_commitish": "main",
        "name": RELEASE_NAME,
        "body": RELEASE_BODY,
        "draft": False,
        "prerelease": False
    }
    
    req = Request(url, 
                  data=json.dumps(data).encode('utf-8'),
                  headers={
                      'Authorization': f'token {token}',
                      'Accept': 'application/vnd.github.v3+json',
                      'Content-Type': 'application/json'
                  },
                  method='POST')
    
    try:
        print(f"Criando release {TAG_NAME}...")
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Release criada com sucesso!")
            print(f"  URL: {result['html_url']}")
            print(f"  Tag: {result['tag_name']}")
            print(f"  Nome: {result['name']}")
            return True
    except URLError as e:
        print(f"✗ Erro ao criar release: {e}")
        if hasattr(e, 'read'):
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"  Detalhes: {error_data}")
        return False

if __name__ == '__main__':
    success = create_release()
    exit(0 if success else 1)
