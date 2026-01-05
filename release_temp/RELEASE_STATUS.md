## ✅ Pixlet Browser v0.2.0 - Release Preparation Complete

### Status Atual

✅ **Tag criada:** `v0.2.0` (enviada para GitHub)
✅ **Commits feitos:** Todos os ficheiros commitados e enviados (push)
✅ **Documentação:** Release notes preparadas

### Próximas Passos

Para completar a release, aceda a um dos links abaixo e crie a release:

#### 1. Via GitHub CLI (mais rápido)

```bash
gh release create v0.2.0 --title "v0.2.0 - Icon Support & OneDrive Support" --notes-file RELEASE_NOTES_v0.2.0.md
```

#### 2. Via Interface Web (mais fácil)

Aceda a: **https://github.com/MCAI14/Pixlet-Go/releases/new**

Preencha com:

- **Tag:** v0.2.0 (já aparece na dropdown)
- **Title:** v0.2.0 - Icon Support & OneDrive Support
- **Description:** Copie o conteúdo de `RELEASE_NOTES_v0.2.0.md`

#### 3. Via Python Script (se tiver token)

```bash
export GITHUB_TOKEN="seu-token-aqui"
python create_release.py
```

---

## 📝 Ficheiros Inclusos na Release

### Código Principal

- `qt_browser.py` - Navegador basado em Qt WebEngine
- `installer.py` - Instalador completo com suporte a ícones e OneDrive

### Novos Ficheiros v0.2.0

- `Pixlet.svg` - Ícone original (design vector)
- `create_icon.py` - Converter SVG para ICO
- `create_shortcut.vbs` - Criar atalhos via VBScript
- `create_release.py` - Criar releases via GitHub API

### Documentação

- `CRIAR_ATALHO.txt` - Instruções em português
- `RELEASE_NOTES_v0.2.0.md` - Notas desta release
- `README.md` - Documentação principal

### Configuração

- `requirements.txt` - Dependências Python
- `.gitignore` - Ficheiros ignorados pelo Git

---

## 🎯 Resumo das Mudanças v0.2.0

### Melhorias Implementadas

1. **Detecção de Desktop com OneDrive**

   - Usa Windows Registry (confiável)
   - Fallback para múltiplos idiomas
   - Suporta 7+ configurações diferentes
2. **Conversão de SVG para Ícone**

   - Método 1: Pillow + cairosvg (Python)
   - Método 2: ImageMagick (CLI)
   - Método 3: Inkscape (CLI)
3. **Criação de Atalhos Avançada**

   - Atalhos `.lnk` com ícone
   - Via win32com (Python) ou VBScript (default)
   - Fallback automático
   - Diálogo de ajuda visual
4. **Instruções em Português**

   - Ficheiro de ajuda passo-a-passo
   - Diálogo visual no installer
   - Suporte para múltiplas línguas

---

## 🔗 Links Úteis

- **Repositório:** https://github.com/MCAI14/Pixlet-Go
- **Release Page:** [https://github.com/MCAI14/Pixlet-Go/releases]()
- **Tag v0.2.0:** https://github.com/MCAI14/Pixlet-Go/releases/tag/v0.2.0
- **Criar Release:** https://github.com/MCAI14/Pixlet-Go/releases/new

---

## 📋 Checklist Final

- [X] Código testado e sem erros
- [X] Todos os ficheiros commitados
- [X] Tag criada e enviada
- [X] Release notes preparadas
- [X] Documentação atualizada
- [ ] **Release criada** ← Próximo passo

---

**Criado:** 5 de Janeiro de 2026
**Desenvolvido por:** MCAI14
**Status:** Pronto para release
