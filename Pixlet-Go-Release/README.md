# 🌐 Pixlet-Go Browser v2.0.1-pre

Um navegador embarcado em Python (PySide6 + Qt WebEngine) com suporte a abas, histórico, bookmarks, senhas encriptadas e sincronização Firebase.

## 🚀 Primeiros Passos

### Passo 1: Abra como Administrador

Clique com o botão **direito** em:

**`Installer (OPEN HERE).bat`**

E selecione **"Executar como administrador"**

### Passo 2: Siga o Assistente de Instalação

O assistente Wizard lhe guiará por:

1. **📦 Instalar Dependências** — Instala pacotes Python necessários
2. **⭐ Criar Atalho** — Cria um atalho na Área de Trabalho
3. **🌐 Executar Navegador** — Inicia o navegador Pixlet

### Passo 3: Use o Navegador

- Navegue por URLs
- Abra múltiplas abas
- Guarde bookmarks
- Aceda ao histórico
- Guarde senhas encriptadas (opcional)
- Sincronize com Firebase (opcional)

---

## 📋 Requisitos

- **Windows 10/11**
- **Python 3.8+** (será oferecida opção de instalar)
- **Privilégios de Administrador** (para instalar dependências)

## 📦 Dependências Instaladas Automaticamente

```
PySide6
Qt WebEngine
cryptography (para encriptação de senhas)
pyrebase4 (para sincronização Firebase - opcional)
```

---

## 🎯 Funcionalidades

✅ Navegação web com PySide6 + QWebEngine  
✅ Múltiplas abas  
✅ Barra de endereço inteligente  
✅ Histórico com timestamps  
✅ Bookmarks/Favoritos  
✅ Gestor de Senhas (encriptadas com Fernet)  
✅ Sincronização Firebase (cloud backup)  
✅ Snapshots locais automáticos  
✅ UI em português  

---

## ⚙️ Configuração Avançada

### Ativar Sincronização Firebase

1. No navegador, abra **Tools → Firebase Sync → Login to Firebase**
2. Registe-se ou faça login
3. Clique **Sync Now** para sincronizar dados

### Gestor de Senhas

As senhas são encriptadas localmente com a biblioteca `cryptography` e guardadas em `local_data/passwords.json`.

---

## 📂 Estrutura de Ficheiros

```
Pixlet-Go-Release/
├── Installer (OPEN HERE).bat    ← ABRA ISTO COMO ADMIN
├── README.md                    ← Este ficheiro
└── _src/                        ← Ficheiros da aplicação
    ├── qt_browser.py            (navegador principal)
    ├── installer_wizard.py      (assistente de instalação)
    ├── installer.py             (instalador clássico)
    ├── firebase_sync.py         (sincronização cloud)
    ├── requirements.txt         (dependências)
    ├── create_icon.py           (gerador de ícones)
    ├── create_shortcut.vbs      (script de atalhos)
    └── Pixlet.svg              (ícone da aplicação)
```

---

## 🆘 Suporte

Se encontrar problemas:

1. **Erro de Privilégios:** Abra o `.bat` como administrador
2. **Erro de Dependências:** Execute novamente o passo "Instalar Dependências"
3. **Navegador não abre:** Verifique se Python 3.8+ está instalado
4. **Firebase não funciona:** Instale `pyrebase4`: `pip install pyrebase4`

---

## 📝 Licença

Pixlet-Go é um projeto open-source. Veja https://github.com/MCAI14/Pixlet-Go

---

**Desenvolvido por:** MCAI14  
**Data:** 7 de Janeiro de 2026  
**Versão:** 2.0.1-pre
