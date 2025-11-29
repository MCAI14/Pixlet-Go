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
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget,
    QWidget, QVBoxLayout, QMessageBox
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
        self.add_tab('https://www.google.com')

    def add_tab(self, url: str = 'about:blank'):
        tab = BrowserTab(url)
        index = self.tabs.addTab(tab, 'Nova Aba')
        self.tabs.setCurrentIndex(index)
        # atualizar título quando mudar
        tab.view.titleChanged.connect(lambda t, i=index: self.tabs.setTabText(i, t))
        tab.view.urlChanged.connect(lambda q, i=index: self.on_url_changed(i, q))

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

    def on_url_changed(self, index, qurl):
        if index == self.tabs.currentIndex():
            self.urlbar.setText(qurl.toString())


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
