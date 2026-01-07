#!/usr/bin/env python3
"""
Script para criar release v2.0.1-pre via GitHub API
"""

import os
import json
import subprocess
import sys

# Ler token do ficheiro
token = None
with open('GITHUB_TOKEN.env', 'r') as f:
    for line in f:
        if line.startswith('GITHUB_TOKEN='):
            token = line.split('=')[1].strip()
            break

if not token:
    print('✗ Token não encontrado em GITHUB_TOKEN.env')
    sys.exit(1)

# Ler release notes
with open('RELEASE_NOTES_v2.0.1-pre.md', 'r', encoding='utf-8') as f:
    body = f.read()

# Criar payload
payload = {
    'tag_name': 'v2.0.1-pre',
    'name': 'v2.0.1 Pre-Release',
    'body': body,
    'draft': False,
    'prerelease': True
}

# Fazer POST via curl com headers corretos
headers = [
    f'Authorization: token {token}',
    'Accept: application/vnd.github.v3+json'
]

cmd = ['curl', '-X', 'POST']
for header in headers:
    cmd.extend(['-H', header])
cmd.extend(['-d', json.dumps(payload)])
cmd.append('https://api.github.com/repos/MCAI14/Pixlet-Go/releases')

print(f'Enviando request...')
result = subprocess.run(cmd, capture_output=True, text=True)

try:
    resp = json.loads(result.stdout)
except:
    print(f'✗ Erro ao parsear resposta: {result.stdout[:200]}')
    print(f'✗ stderr: {result.stderr}')
    sys.exit(1)

if 'html_url' in resp:
    url = resp['html_url']
    print(f'✓ Release criada com sucesso!')
    print(f'  URL: {url}')
elif 'message' in resp:
    print(f'✗ Erro: {resp["message"]}')
    if 'errors' in resp:
        print(f'  Detalhes: {resp["errors"]}')
else:
    print(f'✗ Resposta inesperada: {result.stdout[:500]}')
