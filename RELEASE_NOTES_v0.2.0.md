# PIXLET BROWSER v0.2.0 - Release Notes

## Como Criar a Release

A tag `v0.2.0` foi criada no repositório. Para criar a release, execute um dos seguintes:

### Opção 1: GitHub CLI (recomendado)

```bash
gh release create v0.2.0 --title "v0.2.0 - Icon Support & OneDrive Support" --notes-file RELEASE_NOTES.md
```

### Opção 2: Interface Web

1. Aceda a [https://github.com/MCAI14/Pixlet-Go/releases](https://github.com/MCAI14/Pixlet-Go/releases)
2. Clique em "Create a new release"
3. Selecione a tag "v0.2.0"
4. Preencha o título e descrição (veja abaixo)

### Opção 3: Python Script (com token)

```bash
export GITHUB_TOKEN="seu-token-aqui"
python create_release.py
```

## Conteúdo da Release

### Título

**v0.2.0 - Icon Support & OneDrive Support**

### Descrição

Pixlet Browser v0.2.0 - Melhorias Significativas

## ✨ Novas Funcionalidades

### 1. Suporte para Ícone SVG

- Converter SVG para ICO usando Pillow + cairosvg ou ImageMagick
- Aplicar ícone personalizado aos atalhos (.lnk)
- Novo botão "Gerar ícone" no installer
- Ficheiro `Pixlet.svg` incluído

### 2. Melhor Suporte para OneDrive

- Detectar corretamente a Área de Trabalho em sistemas com OneDrive ativado
- Usar Windows Registry para encontrar o caminho correto
- Fallback automático para múltiplos idiomas (português, inglês, francês, espanhol, etc.)
- Funciona em sistemas com Desktop redirecionado para OneDrive

### 3. Criação Melhorada de Atalhos

- Criar atalhos `.lnk` (melhor que `.bat`) com ícone personalizado
- Suporte via `win32com` (Python) ou VBScript (padrão Windows)
- Fallback automático se um método falhar
- Mensagens de erro descritivas e diálogo de ajuda visual

### 4. Instruções em Português

- Ficheiro `CRIAR_ATALHO.txt` com instruções passo-a-passo para criar manualmente
- Diálogo visual de ajuda no installer com cópia para clipboard

## 📁 Ficheiros Adicionados

- `create_icon.py` - Script para converter SVG em ícone (com suporte a múltiplos métodos)
- `create_shortcut.vbs` - Script VBScript para criar atalhos com ícone
- `Pixlet.svg` - Ícone original em formato SVG
- `CRIAR_ATALHO.txt` - Instruções completas em português
- `create_release.py` - Script para criar releases via GitHub API

## 🔧 Melhorias Técnicas

- Melhor tratamento de erros em imports opcionais
- Suporte robusto para múltiplas línguas e configurações do Windows
- Código mais modular e testável
- Anotações `# type: ignore` para evitar avisos de linters
- Detecção de Desktop via Windows Registry (mais confiável)

## 📦 Requisitos Opcionais

Para gerar ícones a partir do SVG, instale (opcional):

```bash
pip install pillow cairosvg
```

Ou use **ImageMagick** ou **Inkscape** (já disponível em muitos sistemas).

#### 🔄 Changelog Detalhado

- [x] Detecção de Desktop com suporte a OneDrive
- [x] Conversão de SVG para ICO (múltiplos métodos)
- [x] Criação de atalhos com ícone personalizado (.lnk)
- [x] Tratamento robusto de erros e fallbacks
- [x] Instruções completas em português
- [x] Suporte para 7+ idiomas (Desktop folder names)
- [x] Script de criação de releases

#### 🐛 Bugs Corrigidos

- Atalhos eram criados em `USERPROFILE` em vez da Área de Trabalho com OneDrive
- Falta de suporte para nomes de pasta em português
- Imports opcionais causavam erros sem mensagens claras

#### 🌍 Compatibilidade

- **Windows:** 7 ou superior
- **Python:** 3.9 ou superior
- **PySide6:** 6.0 ou superior (para o navegador)

#### 📚 Documentação

- Instruções em português em `CRIAR_ATALHO.txt`
- Diálogo de ajuda visual no installer
- Comentários detalhados no código Python
- Script `create_release.py` para referência futura

---

### Tags

- `browser`
- `python`
- `windows`
- `installer`
- `qt`
- `icon`
- `svg`
- `onedrive`

### Versão Anterior

[v0.1.0](https://github.com/MCAI14/Pixlet-Go/releases/tag/v0.1.0)

---

**Criado em:** 5 de Janeiro de 2026
**Desenvolvido por:** MCAI14
**Repositório:** https://github.com/MCAI14/Pixlet-Go
