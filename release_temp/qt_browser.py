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
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget,
    QWidget, QVBoxLayout, QMessageBox, QMenuBar, QStatusBar,
    QDialog, QLabel, QPushButton, QFormLayout, QFileDialog
)
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView


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
