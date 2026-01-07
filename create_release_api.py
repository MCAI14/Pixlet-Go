#!/usr/bin/env python3
"""
GitHub Release API Setup Guide e Script de Automação

Este script demonstra como usar a GitHub REST API v3 para criar releases
automaticamente sem precisar de UI web ou GitHub CLI.
"""

import os
import json
import subprocess
from typing import Optional

# ============================================================================
# PASSO 1: GERAR GITHUB TOKEN PESSOAL
# ============================================================================
"""
Para usar a API do GitHub, precisa de um token pessoal:

1. Aceda a https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Dê um nome: "Pixlet-Go Release Automation"
4. Selecione permissões:
   - [x] repo (acesso completo ao repositório)
   - [x] workflow (para criar releases)
5. Clique em "Generate token"
6. COPIE o token (aparece uma única vez!) e guarde num local seguro

Exemplo de token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""

# ============================================================================
# PASSO 2: GUARDAR O TOKEN COM SEGURANÇA
# ============================================================================
"""
Opção A: Variável de Ambiente (recomendado)
  
  Windows (PowerShell):
    $env:GITHUB_TOKEN = "seu-token-aqui"
  
  Windows (CMD):
    set GITHUB_TOKEN=seu-token-aqui
  
  Linux/Mac:
    export GITHUB_TOKEN="seu-token-aqui"

Opção B: Ficheiro .env (não commitar!)
  
  Crie .env na raiz do projeto:
    GITHUB_TOKEN=seu-token-aqui
  
  Adicione .env ao .gitignore
"""

# ============================================================================
# PASSO 3: USAR A API COM PYTHON (requests)
# ============================================================================

def create_release_via_api(
    owner: str,
    repo: str,
    tag_name: str,
    release_name: str,
    body: str,
    prerelease: bool = False,
    draft: bool = False,
    token: Optional[str] = None
) -> dict:
    """
    Cria uma release no GitHub usando a REST API.
    
    Args:
        owner: Proprietário do repositório (ex: "MCAI14")
        repo: Nome do repositório (ex: "Pixlet-Go")
        tag_name: Tag git (ex: "v2.0.1-pre")
        release_name: Nome descritivo (ex: "v2.0.1 Pre-Release")
        body: Descrição (em Markdown)
        prerelease: Se é pré-release (True/False)
        draft: Se é rascunho (True/False)
        token: GitHub token (ou ler de GITHUB_TOKEN env var)
    
    Returns:
        dict: Resposta JSON da API
    
    Exemplo:
        create_release_via_api(
            owner="MCAI14",
            repo="Pixlet-Go",
            tag_name="v2.0.1-pre",
            release_name="v2.0.1 Pre-Release",
            body="Este é um pré-release para testes...",
            prerelease=True,
            token=os.getenv("GITHUB_TOKEN")
        )
    """
    
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        raise ValueError("GITHUB_TOKEN não configurado. Veja as instruções acima.")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tag_name": tag_name,
        "name": release_name,
        "body": body,
        "draft": draft,
        "prerelease": prerelease
    }
    
    # Usar curl (alternativa se requests não estiver instalado)
    import subprocess
    import json
    
    cmd = [
        "curl",
        "-X", "POST",
        "-H", f"Authorization: token {token}",
        "-H", "Accept: application/vnd.github.v3+json",
        "-d", json.dumps(payload),
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Erro: {result.stderr}")
    
    return json.loads(result.stdout)


# ============================================================================
# PASSO 4: EXEMPLO DE USO
# ============================================================================

def main():
    """Exemplo: Criar release v2.0.1-pre"""
    
    # Ler ficheiro RELEASE_NOTES
    notes_file = "RELEASE_NOTES_v2.0.1-pre.md"
    if not os.path.exists(notes_file):
        print(f"Erro: {notes_file} não encontrado")
        return
    
    with open(notes_file, 'r', encoding='utf-8') as f:
        release_notes = f.read()
    
    try:
        response = create_release_via_api(
            owner="MCAI14",
            repo="Pixlet-Go",
            tag_name="v2.0.1-pre",
            release_name="v2.0.1 Pre-Release",
            body=release_notes,
            prerelease=True,
            draft=False,
            token=os.getenv("GITHUB_TOKEN")
        )
        
        print("✓ Release criada com sucesso!")
        print(f"URL: {response.get('html_url')}")
        
    except Exception as e:
        print(f"✗ Erro: {e}")


# ============================================================================
# PASSO 5: ALTERNATIVE - USAR COM REQUESTS (MAIS FÁCIL)
# ============================================================================

def create_release_with_requests(
    owner: str,
    repo: str,
    tag_name: str,
    release_name: str,
    body: str,
    prerelease: bool = False,
    token: Optional[str] = None
) -> dict:
    """
    Versão com requests (instale: pip install requests)
    """
    try:
        import requests
    except ImportError:
        print("Instale requests: pip install requests")
        return {}
    
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        raise ValueError("GITHUB_TOKEN não configurado")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "tag_name": tag_name,
        "name": release_name,
        "body": body,
        "draft": False,
        "prerelease": prerelease
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 201:
        raise RuntimeError(f"Erro {response.status_code}: {response.text}")
    
    return response.json()


# ============================================================================
# PASSO 6: FLOW COMPLETO (DO_RELEASE.PY)
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("GITHUB RELEASE API - SETUP GUIDE")
    print("=" * 70)
    print()
    print("Para criar releases automaticamente:")
    print()
    print("1. Gere um token em https://github.com/settings/tokens")
    print("2. Configure em seu ambiente:")
    print("   export GITHUB_TOKEN='seu-token'")
    print("3. Execute este script:")
    print("   python create_release_api.py")
    print()
    print("Ou use GitHub CLI (mais simples):")
    print("   gh release create v2.0.1-pre --title 'v2.0.1 Pre-Release' \\")
    print("     --notes-file RELEASE_NOTES_v2.0.1-pre.md --prerelease")
    print()
