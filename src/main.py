import os
import sys

import requests
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from base import BASE_URL

class LoginPopup(QDialog):
    def __init__(self):
        super().__init__()

        # Remove the "What's this?" button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("Login")
        self.email_label = QLabel("Email:", self)
        self.email_entry = QLineEdit(self)
        self.password_label = QLabel("Password:", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red")

        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def login(self):
        email = self.email_entry.text()
        password = self.password_entry.text()
        
        url = f'{BASE_URL}/login'
        headers = {'Content-Type':'application/json'}

        try:
            data = {
                'email':f'{email}',
                'password':f'{password}'
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            global arena_session_id
            arena_session_id = response.json()['arenaSessionId']
        except Exception as error:
            print(f'Invalid entry: {error}')
            self.error_label.setText(f'Enter a valid email/password')
            return

        self.accept()

class COApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('CO Validation')

        self.label = QLabel('Temp label', self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Get absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct absolute file path to the image file
    #logo_path = get_resource_path("resources/galvanize_logo.png")
    #app.setWindowIcon(QIcon(logo_path))
 
    # Show login popup
    login_popup = LoginPopup()
    if login_popup.exec_() != QDialog.Accepted:
        sys.exit(0)

    # Create main window
    window = COApp()
    window.show()
    sys.exit(app.exec_())