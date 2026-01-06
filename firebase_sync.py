"""
Firebase Sync Manager - Sincroniza histórico, bookmarks e senhas com Firebase
Usa Pyrebase4 (cliente Python não-oficial para Firebase Realtime Database)

Instalação:
    pip install pyrebase4

Configuração:
    - Cria conta Google/Firebase (https://firebase.google.com)
    - Usa as credenciais públicas do projeto PixletWEBAPP
"""

import json
import os
from datetime import datetime

try:
    import pyrebase4
except ImportError:
    pyrebase4 = None


# Configuração Firebase (credenciais públicas do projeto PixletWEBAPP)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyA-piyweqyb1H682ocISUBZFAUuFB4OA_U",
    "authDomain": "pixlet-333b1.firebaseapp.com",
    "projectId": "pixlet-333b1",
    "storageBucket": "pixlet-333b1.appspot.com",
    "messagingSenderId": "24565360033",
    "appId": "1:24565360033:web:16911c608dd3737c33d7e0",
    "databaseURL": "https://pixlet-333b1-default-rtdb.europe-west1.firebaseio.com"
}


class FirebaseSync:
    """Gerenciador de sincronização com Firebase"""
    
    def __init__(self, user_id: str = None):
        """
        Inicializa Firebase Sync
        user_id: identificador do utilizador (email ou UUID)
        """
        if not pyrebase4:
            raise ImportError('Pyrebase4 não instalado. Execute: pip install pyrebase4')
        
        self.user_id = user_id or 'anonymous'
        self.db = None
        self.auth = None
        self.is_connected = False
        self._init_firebase()

    def _init_firebase(self):
        """Inicializa conexão Firebase"""
        try:
            firebase = pyrebase4.initialize_app(FIREBASE_CONFIG)
            self.auth = firebase.auth()
            self.db = firebase.database()
            self.is_connected = True
        except Exception as e:
            print(f'Erro ao inicializar Firebase: {e}')
            self.is_connected = False

    def register(self, email: str, password: str) -> bool:
        """Regista novo utilizador"""
        if not self.is_connected:
            return False
        try:
            self.auth.create_user_with_email_and_password(email, password)
            return True
        except Exception as e:
            print(f'Erro no registo: {e}')
            return False

    def login(self, email: str, password: str) -> bool:
        """Faz login e retorna True se bem-sucedido"""
        if not self.is_connected:
            return False
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user_id = user['localId']
            return True
        except Exception as e:
            print(f'Erro no login: {e}')
            return False

    def sync_history(self, history_data: list) -> bool:
        """Sincroniza histórico para Firebase"""
        if not self.is_connected:
            return False
        try:
            path = f'users/{self.user_id}/history'
            self.db.child(path).set(history_data)
            return True
        except Exception as e:
            print(f'Erro ao sincronizar histórico: {e}')
            return False

    def sync_bookmarks(self, bookmarks_data: list) -> bool:
        """Sincroniza bookmarks para Firebase"""
        if not self.is_connected:
            return False
        try:
            path = f'users/{self.user_id}/bookmarks'
            self.db.child(path).set(bookmarks_data)
            return True
        except Exception as e:
            print(f'Erro ao sincronizar bookmarks: {e}')
            return False

    def sync_passwords(self, passwords_data: list) -> bool:
        """Sincroniza senhas encriptadas para Firebase"""
        if not self.is_connected:
            return False
        try:
            path = f'users/{self.user_id}/passwords'
            # As senhas já estão encriptadas localmente
            self.db.child(path).set(passwords_data)
            return True
        except Exception as e:
            print(f'Erro ao sincronizar senhas: {e}')
            return False

    def get_history(self) -> list:
        """Recupera histórico de Firebase"""
        if not self.is_connected:
            return []
        try:
            path = f'users/{self.user_id}/history'
            data = self.db.child(path).get()
            return data.val() or []
        except Exception as e:
            print(f'Erro ao recuperar histórico: {e}')
            return []

    def get_bookmarks(self) -> list:
        """Recupera bookmarks de Firebase"""
        if not self.is_connected:
            return []
        try:
            path = f'users/{self.user_id}/bookmarks'
            data = self.db.child(path).get()
            return data.val() or []
        except Exception as e:
            print(f'Erro ao recuperar bookmarks: {e}')
            return []

    def get_passwords(self) -> list:
        """Recupera senhas de Firebase"""
        if not self.is_connected:
            return []
        try:
            path = f'users/{self.user_id}/passwords'
            data = self.db.child(path).get()
            return data.val() or []
        except Exception as e:
            print(f'Erro ao recuperar senhas: {e}')
            return []

    def logout(self):
        """Faz logout"""
        self.user_id = 'anonymous'
        self.auth = None

    def set_sync_enabled(self, enabled: bool):
        """Define se sync está ativado"""
        if not self.is_connected:
            return False
        try:
            path = f'users/{self.user_id}/sync_enabled'
            self.db.child(path).set(enabled)
            return True
        except Exception:
            return False

    def is_sync_enabled(self) -> bool:
        """Verifica se sync está ativado"""
        if not self.is_connected:
            return False
        try:
            path = f'users/{self.user_id}/sync_enabled'
            data = self.db.child(path).get()
            return data.val() or False
        except Exception:
            return False
