"""
Navegador com PySide6 + QWebEngineView (Chromium via Qt WebEngine)
- Abas (tabs), barra de endereço, botões back/forward/reload, criar/fechar abas

Instalação:
    pip install PySide6

Executar:
    python qt_browser.py

Se a instalação falhar, tenta `pip install PyQt6 PyQt6-WebEngine` como alternativa.
"""

import sys
import os
import json
import datetime
import subprocess
import base64
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget,
    QWidget, QVBoxLayout, QMessageBox, QMenuBar, QStatusBar,
    QDialog, QLabel, QPushButton, QFormLayout, QFileDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

try:
    from cryptography.fernet import Fernet  # type: ignore
except ImportError:
    Fernet = None

try:
    from firebase_sync import FirebaseSync
except ImportError:
    FirebaseSync = None


class BrowserTab(QWidget):
    def __init__(self, url: str = 'https://www.google.com'):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))
        self.layout.addWidget(self.view)

    def set_url(self, url: str):
        self.view.setUrl(QUrl(url))

    def url(self):
        return self.view.url().toString()


class HistoryManager:
    """Gerencia histórico de navegação com timestamps"""
    def __init__(self, base_path: str):
        self.history_file = os.path.join(base_path, 'history.json')
        self.history = self.load_history()

    def add_entry(self, url: str, title: str = ''):
        """Adiciona entrada ao histórico"""
        entry = {
            'url': url,
            'title': title,
            'timestamp': datetime.datetime.now().isoformat(),
            'visited': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.history.append(entry)
        self.save_history()

    def load_history(self) -> list:
        """Carrega histórico de ficheiro"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        """Guarda histórico em ficheiro"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def clear_history(self):
        """Limpa todo o histórico"""
        self.history = []
        self.save_history()

    def get_recent(self, limit: int = 50) -> list:
        """Retorna últimas entradas"""
        return sorted(self.history, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]


class BookmarksManager:
    """Gerencia bookmarks/favoritos"""
    def __init__(self, base_path: str):
        self.bookmarks_file = os.path.join(base_path, 'bookmarks.json')
        self.bookmarks = self.load_bookmarks()

    def add_bookmark(self, url: str, title: str):
        """Adiciona bookmark"""
        bookmark = {
            'url': url,
            'title': title,
            'added': datetime.datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        self.save_bookmarks()

    def remove_bookmark(self, url: str):
        """Remove bookmark por URL"""
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.save_bookmarks()

    def load_bookmarks(self) -> list:
        """Carrega bookmarks"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_bookmarks(self):
        """Guarda bookmarks"""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class PasswordManager:
    """Gerencia senhas encriptadas"""
    def __init__(self, base_path: str):
        self.passwords_file = os.path.join(base_path, 'passwords.json')
        self.key_file = os.path.join(base_path, '.key')
        self.cipher = self._init_cipher()
        self.passwords = self.load_passwords()

    def _init_cipher(self):
        """Inicializa encriptação Fernet"""
        if not Fernet:
            return None
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                return Fernet(key)
            except Exception:
                return None
        else:
            try:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return Fernet(key)
            except Exception:
                return None

    def add_password(self, service: str, username: str, password: str):
        """Adiciona senha encriptada"""
        if not self.cipher:
            raise Exception('Encriptação não disponível. Instale: pip install cryptography')
        
        encrypted = self.cipher.encrypt(password.encode()).decode()
        entry = {
            'service': service,
            'username': username,
            'password': encrypted,
            'added': datetime.datetime.now().isoformat()
        }
        self.passwords.append(entry)
        self.save_passwords()

    def get_password(self, service: str, username: str) -> str:
        """Recupera senha desencriptada"""
        if not self.cipher:
            return None
        for entry in self.passwords:
            if entry['service'] == service and entry['username'] == username:
                try:
                    decrypted = self.cipher.decrypt(entry['password'].encode()).decode()
                    return decrypted
                except Exception:
                    return None
        return None

    def remove_password(self, service: str, username: str):
        """Remove entrada de senha"""
        self.passwords = [p for p in self.passwords if not (p['service'] == service and p['username'] == username)]
        self.save_passwords()

    def load_passwords(self) -> list:
        """Carrega senhas"""
        if os.path.exists(self.passwords_file):
            try:
                with open(self.passwords_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_passwords(self):
        """Guarda senhas"""
        try:
            with open(self.passwords_file, 'w', encoding='utf-8') as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pixlet - Qt Browser')
        self.resize(1200, 800)

        # Simple settings (in-memory for now)
        self.settings = {
            'homepage': 'https://www.google.com',
            'default_new_tab': 'about:blank'
        }

        # Inicializar managers
        base_path = self.storage_base()
        self.history_manager = HistoryManager(base_path)
        self.bookmarks_manager = BookmarksManager(base_path)
        self.password_manager = PasswordManager(base_path)

        # Inicializar Firebase Sync (opcional)
        self.firebase_sync = None
        self.sync_enabled = False
        if FirebaseSync:
            try:
                self.firebase_sync = FirebaseSync()
            except Exception:
                self.firebase_sync = None

        # Menu bar (File / View / Settings)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        new_tab_action = file_menu.addAction('New Tab')
        new_tab_action.triggered.connect(lambda: self.add_tab(self.settings.get('default_new_tab', 'about:blank')))
        file_menu.addSeparator()
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)

        view_menu = menubar.addMenu('View')
        toggle_tabs_action = view_menu.addAction('Toggle Tab Bar')
        toggle_tabs_action.triggered.connect(self.toggle_tab_bar)

        tools_menu = menubar.addMenu('Tools')
        settings_action = tools_menu.addAction('Settings')
        settings_action.triggered.connect(self.open_settings)
        save_snapshot_action = tools_menu.addAction('Save Snapshot')
        save_snapshot_action.triggered.connect(self.save_settings_snapshot)
        tools_menu.addSeparator()
        history_action = tools_menu.addAction('View History')
        history_action.triggered.connect(self.open_history_dialog)
        bookmarks_action = tools_menu.addAction('Manage Bookmarks')
        bookmarks_action.triggered.connect(self.open_bookmarks_dialog)
        passwords_action = tools_menu.addAction('Manage Passwords')
        passwords_action.triggered.connect(self.open_passwords_dialog)
        # Disable passwords action if encryption is not available
        try:
            passwords_action.setEnabled(bool(self.password_manager.cipher))
            if not self.password_manager.cipher:
                passwords_action.setToolTip('cryptography not installed; pip install cryptography')
        except Exception:
            pass
        tools_menu.addSeparator()
        firebase_menu = tools_menu.addMenu('Firebase Sync')
        login_firebase = firebase_menu.addAction('Login to Firebase')
        login_firebase.triggered.connect(self.firebase_login)
        sync_now = firebase_menu.addAction('Sync Now')
        sync_now.triggered.connect(self.firebase_sync_now)
        # Disable Firebase actions if firebase client not available
        try:
            enabled = bool(self.firebase_sync)
            login_firebase.setEnabled(enabled)
            sync_now.setEnabled(enabled)
            if not enabled:
                login_firebase.setToolTip('pyrebase4 not installed or Firebase unavailable; pip install pyrebase4')
                sync_now.setToolTip('pyrebase4 not installed or Firebase unavailable; pip install pyrebase4')
        except Exception:
            pass
        tools_menu.addSeparator()
        open_data_action = tools_menu.addAction('Open Data Folder')
        open_data_action.triggered.connect(self.open_data_folder)

        # Status bar
        self.setStatusBar(QStatusBar(self))

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        # Toolbar
        navtb = QToolBar('Navigation')
        self.addToolBar(navtb)

        back_btn = QAction('←', self)
        back_btn.triggered.connect(self.go_back)
        navtb.addAction(back_btn)

        forward_btn = QAction('→', self)
        forward_btn.triggered.connect(self.go_forward)
        navtb.addAction(forward_btn)

        reload_btn = QAction('⟲', self)
        reload_btn.triggered.connect(self.reload)
        navtb.addAction(reload_btn)

        new_btn = QAction('＋', self)
        new_btn.triggered.connect(self.add_tab)
        navtb.addAction(new_btn)

        navtb.addSeparator()

        bookmark_btn = QAction('⭐', self)
        bookmark_btn.triggered.connect(self.add_current_to_bookmarks)
        navtb.addAction(bookmark_btn)

        navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        go_btn = QAction('Ir', self)
        go_btn.triggered.connect(self.navigate_to_url)
        navtb.addAction(go_btn)

        # Primeira aba
        self.add_tab(self.settings.get('homepage', 'https://www.google.com'))

        # Load persisted settings if available
        try:
            self.load_latest_settings()
        except Exception:
            # ignore load errors
            pass

    def add_tab(self, url: str = 'about:blank'):
        tab = BrowserTab(url)
        index = self.tabs.addTab(tab, 'Nova Aba')
        self.tabs.setCurrentIndex(index)
        # atualizar título quando mudar
        tab.view.titleChanged.connect(lambda t, i=index: self.tabs.setTabText(i, t))
        tab.view.urlChanged.connect(lambda q, i=index: self.on_url_changed(i, q))
        # Update status when load finished
        tab.view.loadFinished.connect(lambda ok, i=index: self.statusBar().showMessage(f'Carregada: {tab.view.url().toString()}' if ok else 'Erro ao carregar'))
        # Adicionar ao histórico quando a página carrega
        tab.view.loadFinished.connect(lambda ok, i=index: self._record_history(i) if ok else None)

    def close_tab(self, i):
        if self.tabs.count() < 2:
            # não fechar a última aba
            return
        self.tabs.removeTab(i)

    def current_browser(self) -> QWebEngineView:
        widget = self.tabs.currentWidget()
        if widget:
            return widget.view
        return None

    def navigate_to_url(self):
        url_text = self.urlbar.text().strip()
        if not url_text:
            return
        if not url_text.startswith('http'):
            url_text = 'https://' + url_text
        view = self.current_browser()
        if view:
            view.setUrl(QUrl(url_text))

    @Slot()
    def go_back(self):
        view = self.current_browser()
        if view and view.history().canGoBack():
            view.back()

    @Slot()
    def go_forward(self):
        view = self.current_browser()
        if view and view.history().canGoForward():
            view.forward()

    @Slot()
    def reload(self):
        view = self.current_browser()
        if view:
            view.reload()

    def on_tab_changed(self, i):
        view = self.current_browser()
        if view:
            self.urlbar.setText(view.url().toString())
            self.setWindowTitle(view.title())
            self.statusBar().showMessage(f'Página: {view.url().toString()}')

    def on_url_changed(self, index, qurl):
        if index == self.tabs.currentIndex():
            self.urlbar.setText(qurl.toString())

    def toggle_tab_bar(self):
        bar = self.tabs.tabBar()
        visible = bar.isVisible()
        bar.setVisible(not visible)

    def open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec() == QDialog.Accepted:
            # update settings
            self.settings.update(dlg.get_values())
            self.append_status('Definições atualizadas')
            # persist immediately
            try:
                self.save_settings_snapshot()
            except Exception:
                pass

    def append_status(self, text: str):
        self.statusBar().showMessage(text, 5000)

    def storage_base(self) -> str:
        root = os.path.dirname(os.path.abspath(__file__))
        base = os.path.join(root, 'local_data')
        os.makedirs(base, exist_ok=True)
        return base

    def todays_folder(self) -> str:
        base = self.storage_base()
        dname = datetime.date.today().isoformat()
        folder = os.path.join(base, dname)
        os.makedirs(folder, exist_ok=True)
        return folder

    def save_settings_snapshot(self):
        folder = self.todays_folder()
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        fname = os.path.join(folder, f'settings_{ts}.json')
        data = {
            'settings': self.settings,
            'tabs': [self.tabs.widget(i).view.url().toString() for i in range(self.tabs.count())],
            'saved_at': ts
        }
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # also update current.json for quick load
        try:
            self.save_current_settings()
        except Exception:
            pass
        self.append_status(f'Snapshot guardado em {fname}')

    def load_latest_settings(self):
        # Prefer explicit current.json if present
        cur = os.path.join(self.storage_base(), 'current.json')
        if os.path.exists(cur):
            try:
                with open(cur, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                s = data.get('settings') if isinstance(data, dict) else None
                if s:
                    self.settings.update(s)
                    self.append_status(f'Definições carregadas de {cur}')
                    return
            except Exception:
                pass

        base = self.storage_base()
        # find latest date folder
        dates = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
        if not dates:
            return
        dates.sort()
        latest = dates[-1]
        folder = os.path.join(base, latest)
        # find latest settings file
        files = [f for f in os.listdir(folder) if f.startswith('settings_') and f.endswith('.json')]
        if not files:
            return
        files.sort()
        latest_file = os.path.join(folder, files[-1])
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        s = data.get('settings')
        if s:
            self.settings.update(s)
            self.append_status(f'Definições carregadas de {latest_file}')

    def save_current_settings(self):
        cur = os.path.join(self.storage_base(), 'current.json')
        data = {
            'settings': self.settings,
            'saved_at': datetime.datetime.now().isoformat()
        }
        with open(cur, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_current_settings(self):
        cur = os.path.join(self.storage_base(), 'current.json')
        if not os.path.exists(cur):
            return False
        try:
            with open(cur, 'r', encoding='utf-8') as f:
                data = json.load(f)
            s = data.get('settings')
            if s:
                self.settings.update(s)
                self.append_status(f'Definições carregadas de {cur}')
                return True
        except Exception:
            pass
        return False

    def open_data_folder(self):
        path = self.storage_base()
        try:
            if sys.platform.startswith('win'):
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Falha ao abrir a pasta de dados: {e}')

    def _record_history(self, index: int):
        """Registar página visitada no histórico"""
        if index < self.tabs.count():
            tab = self.tabs.widget(index)
            if tab:
                url = tab.view.url().toString()
                title = tab.view.title()
                if url and not url.startswith('about:'):
                    self.history_manager.add_entry(url, title)

    def add_current_to_bookmarks(self):
        """Adiciona página atual aos bookmarks"""
        view = self.current_browser()
        if not view:
            QMessageBox.warning(self, 'Erro', 'Nenhuma aba aberta')
            return
        url = view.url().toString()
        title = view.title()
        if not url:
            QMessageBox.warning(self, 'Erro', 'URL vazia')
            return
        try:
            self.bookmarks_manager.add_bookmark(url, title)
            self.append_status(f'Bookmark guardado: {title}')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao guardar bookmark: {e}')

    def open_history_dialog(self):
        """Abre diálogo de histórico"""
        dlg = HistoryDialog(self, self.history_manager)
        if dlg.exec() == QDialog.Accepted:
            url = dlg.get_selected_url()
            if url:
                self.add_tab(url)

    def open_bookmarks_dialog(self):
        """Abre diálogo de bookmarks"""
        dlg = BookmarksDialog(self, self.bookmarks_manager)
        if dlg.exec() == QDialog.Accepted:
            url = dlg.get_selected_url()
            if url:
                self.add_tab(url)

    def open_passwords_dialog(self):
        """Abre diálogo de senhas"""
        dlg = PasswordsDialog(self, self.password_manager)
        dlg.exec()

    def firebase_login(self):
        """Abre diálogo de login Firebase"""
        if not self.firebase_sync:
            QMessageBox.warning(self, 'Firebase', 'Firebase não disponível.\nInstale: pip install pyrebase4')
            return
        
        dlg = FirebaseLoginDialog(self, self.firebase_sync)
        if dlg.exec() == QDialog.Accepted:
            self.sync_enabled = True
            self.append_status('Conectado ao Firebase ✅')
            # Sincronizar automaticamente após login
            self.firebase_sync_now()

    def firebase_sync_now(self):
        """Sincroniza dados com Firebase agora"""
        if not self.firebase_sync or not self.sync_enabled:
            QMessageBox.warning(self, 'Firebase', 'Não autenticado no Firebase')
            return
        
        try:
            # Sincronizar histórico
            self.firebase_sync.sync_history(self.history_manager.history)
            # Sincronizar bookmarks
            self.firebase_sync.sync_bookmarks(self.bookmarks_manager.bookmarks)
            # Sincronizar senhas
            self.firebase_sync.sync_passwords(self.password_manager.passwords)
            
            self.append_status('Sincronização completa ✅')
            QMessageBox.information(self, 'Sucesso', 'Dados sincronizados com Firebase')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao sincronizar: {e}')


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setModal(True)
        self.current = dict(current_settings or {})

        form = QFormLayout(self)
        self.home_edit = QLineEdit(self.current.get('homepage', 'https://www.google.com'))
        form.addRow('Homepage:', self.home_edit)

        self.newtab_edit = QLineEdit(self.current.get('default_new_tab', 'about:blank'))
        form.addRow('Default new tab:', self.newtab_edit)

        # Buttons
        btns = QWidget()
        btn_layout = QVBoxLayout(btns)
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        form.addRow(btns)

    def get_values(self):
        return {
            'homepage': self.home_edit.text().strip(),
            'default_new_tab': self.newtab_edit.text().strip()
        }


class HistoryDialog(QDialog):
    """Diálogo para visualizar histórico"""
    def __init__(self, parent=None, history_manager=None):
        super().__init__(parent)
        self.setWindowTitle('Histórico de Navegação')
        self.setGeometry(100, 100, 700, 500)
        self.history_manager = history_manager
        self.selected_url = None

        layout = QVBoxLayout(self)
        
        label = QLabel('Clique num item para abrir, ou feche para cancelar:')
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_selected)
        layout.addWidget(self.list_widget)

        # Carregar histórico
        if history_manager:
            for entry in history_manager.get_recent(100):
                url = entry.get('url', '')
                title = entry.get('title', 'Sem título')
                visited = entry.get('visited', '')
                item_text = f"{title}\n{url}\n({visited})"
                item = QListWidgetItem(item_text)
                item.setData(256, url)  # Guardar URL em role 256
                self.list_widget.addItem(item)

        # Botões
        btn_layout = QHBoxLayout()
        open_btn = QPushButton('Abrir')
        open_btn.clicked.connect(self.on_item_selected)
        clear_btn = QPushButton('Limpar Histórico')
        clear_btn.clicked.connect(self.clear_all)
        close_btn = QPushButton('Fechar')
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def on_item_selected(self):
        """Abre URL selecionada"""
        item = self.list_widget.currentItem()
        if item:
            self.selected_url = item.data(256)
            self.accept()

    def clear_all(self):
        """Limpa histórico"""
        reply = QMessageBox.question(self, 'Confirmar', 'Deseja limpar todo o histórico?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.history_manager:
                self.history_manager.clear_history()
            self.list_widget.clear()
            QMessageBox.information(self, 'Sucesso', 'Histórico limpo')

    def get_selected_url(self):
        return self.selected_url


class BookmarksDialog(QDialog):
    """Diálogo para gerir bookmarks"""
    def __init__(self, parent=None, bookmarks_manager=None):
        super().__init__(parent)
        self.setWindowTitle('Bookmarks')
        self.setGeometry(100, 100, 700, 500)
        self.bookmarks_manager = bookmarks_manager
        self.selected_url = None

        layout = QVBoxLayout(self)

        label = QLabel('Bookmarks guardados:')
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_selected)
        layout.addWidget(self.list_widget)

        # Carregar bookmarks
        if bookmarks_manager:
            for bookmark in bookmarks_manager.bookmarks:
                url = bookmark.get('url', '')
                title = bookmark.get('title', 'Sem título')
                item_text = f"{title}\n{url}"
                item = QListWidgetItem(item_text)
                item.setData(256, url)
                self.list_widget.addItem(item)

        # Botões
        btn_layout = QHBoxLayout()
        open_btn = QPushButton('Abrir')
        open_btn.clicked.connect(self.on_item_selected)
        delete_btn = QPushButton('Remover')
        delete_btn.clicked.connect(self.remove_selected)
        close_btn = QPushButton('Fechar')
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def on_item_selected(self):
        """Abre bookmark selecionado"""
        item = self.list_widget.currentItem()
        if item:
            self.selected_url = item.data(256)
            self.accept()

    def remove_selected(self):
        """Remove bookmark selecionado"""
        item = self.list_widget.currentItem()
        if item:
            url = item.data(256)
            if self.bookmarks_manager:
                self.bookmarks_manager.remove_bookmark(url)
            self.list_widget.takeItem(self.list_widget.row(item))
            QMessageBox.information(self, 'Sucesso', 'Bookmark removido')

    def get_selected_url(self):
        return self.selected_url


class PasswordsDialog(QDialog):
    """Diálogo para gerir senhas encriptadas"""
    def __init__(self, parent=None, password_manager=None):
        super().__init__(parent)
        self.setWindowTitle('Gestor de Senhas')
        self.setGeometry(100, 100, 800, 500)
        self.password_manager = password_manager

        layout = QVBoxLayout(self)

        if not password_manager.cipher:
            warning = QLabel('⚠️ Encriptação não disponível.\nInstale: pip install cryptography')
            layout.addWidget(warning)
            close_btn = QPushButton('Fechar')
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            return

        label = QLabel('Senhas guardadas (encriptadas):')
        layout.addWidget(label)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['Serviço', 'Utilizador', ''])
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table_widget)

        # Carregar senhas
        if password_manager:
            for i, pwd in enumerate(password_manager.passwords):
                self.table_widget.insertRow(i)
                service = QTableWidgetItem(pwd.get('service', ''))
                username = QTableWidgetItem(pwd.get('username', ''))
                delete_btn = QPushButton('Apagar')
                delete_btn.clicked.connect(lambda checked, row=i: self.delete_password(row))
                self.table_widget.setItem(i, 0, service)
                self.table_widget.setItem(i, 1, username)
                self.table_widget.setCellWidget(i, 2, delete_btn)

        # Formulário para adicionar nova senha
        form_layout = QFormLayout()
        self.service_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Serviço:', self.service_edit)
        form_layout.addRow('Utilizador:', self.username_edit)
        form_layout.addRow('Senha:', self.password_edit)
        layout.addLayout(form_layout)

        # Botões
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Adicionar Senha')
        add_btn.clicked.connect(self.add_password)
        close_btn = QPushButton('Fechar')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def add_password(self):
        """Adiciona nova senha"""
        service = self.service_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not all([service, username, password]):
            QMessageBox.warning(self, 'Erro', 'Todos os campos são obrigatórios')
            return

        try:
            self.password_manager.add_password(service, username, password)
            QMessageBox.information(self, 'Sucesso', 'Senha adicionada')
            self.service_edit.clear()
            self.username_edit.clear()
            self.password_edit.clear()
            # Recarregar tabela
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao adicionar senha: {e}')

    def delete_password(self, row: int):
        """Remove senha da linha especificada"""
        service = self.table_widget.item(row, 0).text()
        username = self.table_widget.item(row, 1).text()
        reply = QMessageBox.question(self, 'Confirmar',
                                    f'Deseja apagar a senha para {service}/{username}?',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.password_manager.remove_password(service, username)
            self.refresh_table()
            QMessageBox.information(self, 'Sucesso', 'Senha removida')

    def refresh_table(self):
        """Recarrega tabela de senhas"""
        self.table_widget.setRowCount(0)
        if self.password_manager:
            for i, pwd in enumerate(self.password_manager.passwords):
                self.table_widget.insertRow(i)
                service = QTableWidgetItem(pwd.get('service', ''))
                username = QTableWidgetItem(pwd.get('username', ''))
                delete_btn = QPushButton('Apagar')
                delete_btn.clicked.connect(lambda checked, row=i: self.delete_password(row))
                self.table_widget.setItem(i, 0, service)
                self.table_widget.setItem(i, 1, username)
                self.table_widget.setCellWidget(i, 2, delete_btn)


class FirebaseLoginDialog(QDialog):
    """Diálogo de login Firebase"""
    def __init__(self, parent=None, firebase_sync=None):
        super().__init__(parent)
        self.setWindowTitle('Firebase Login')
        self.setGeometry(100, 100, 400, 250)
        self.firebase_sync = firebase_sync
        self.logged_in = False

        layout = QVBoxLayout(self)

        label = QLabel('Login com email e senha\npara sincronizar dados com a cloud')
        layout.addWidget(label)

        form_layout = QFormLayout()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Email:', self.email_edit)
        form_layout.addRow('Senha:', self.password_edit)
        layout.addLayout(form_layout)

        # Botões
        btn_layout = QHBoxLayout()
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.do_login)
        register_btn = QPushButton('Registar')
        register_btn.clicked.connect(self.do_register)
        cancel_btn = QPushButton('Cancelar')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def do_login(self):
        """Faz login Firebase"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()

        if not email or not password:
            QMessageBox.warning(self, 'Erro', 'Email e senha são obrigatórios')
            return

        try:
            if self.firebase_sync.login(email, password):
                QMessageBox.information(self, 'Sucesso', f'Bem-vindo, {email}!')
                self.logged_in = True
                self.accept()
            else:
                QMessageBox.warning(self, 'Erro', 'Login falhou')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha no login: {e}')

    def do_register(self):
        """Registra novo utilizador Firebase"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()

        if not email or not password:
            QMessageBox.warning(self, 'Erro', 'Email e senha são obrigatórios')
            return

        try:
            if self.firebase_sync.register(email, password):
                QMessageBox.information(self, 'Sucesso', 'Conta criada! Faça login agora.')
                self.do_login()
            else:
                QMessageBox.warning(self, 'Erro', 'Registo falhou (email pode já existir)')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha no registo: {e}')


def main():
    try:
        app = QApplication(sys.argv)
    except Exception as e:
        print('Erro ao criar QApplication:', e)
        return

    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        print('Erro no loop do app:', e)


if __name__ == '__main__':
    main()
