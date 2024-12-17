from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QWidget, QScrollArea, QDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from get_path import get_resource_path
from base import BASE_URL
import sys
import requests

class LoginPopup(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.setWindowTitle("Login")
        self.email_label = QLabel("Email:", self)
        self.email_entry = QLineEdit(self)
        self.password_label = QLabel("Password:", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_checkbox = QCheckBox("Show Password", self)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red")

        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.show_password_checkbox)
        layout.addWidget(self.login_button)
        layout.addWidget(self.error_label)

        #self.setStyleSheet("QCheckBox { color: white; } QWidget { background-color: #2E2E2E; } QLineEdit { background-color: white; color: black;}")

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        email = self.email_entry.text()
        password = self.password_entry.text()
        
        url = f'{BASE_URL}/login'
        headers = {'Content-Type':'application/json'}

        try:
            data = {
                'email': f'{email}',
                'password': f'{password}'
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            global arena_session_id
            arena_session_id = response.json()['arenaSessionId']
        except Exception as error:
            print(f'Invalid entry: {error}')
            self.error_label.setText('Enter a valid email/password')
            return

        self.accept()

class COApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTTP Request Validator")
        self.setFixedSize(500, 400)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout()
        main_widget.setLayout(self.layout)

        # Instruction label
        self.instruction_label = QLabel("Enter a 6-digit code (e.g., CO-123456):")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.instruction_label)

        # Input layout
        input_layout = QHBoxLayout()
        self.prefix_label = QLabel("CO-")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("######")
        input_layout.addWidget(self.prefix_label)
        input_layout.addWidget(self.input_field)
        self.layout.addLayout(input_layout)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_submit)
        self.layout.addWidget(self.submit_button)

        # Scrollable area for HTTP request statuses
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.status_widget = QWidget()
        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(10)  # Add spacing between request items
        self.status_widget.setLayout(self.status_layout)
        self.scroll_area.setWidget(self.status_widget)
        self.layout.addWidget(self.scroll_area)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)

        # Track active requests
        self.active_requests = 0

    def handle_submit(self):
        digits = self.input_field.text()
        if len(digits) != 6 or not digits.isdigit():
            self.info_label.setText("Invalid input. Please enter exactly 6 digits.")
            return

        self.info_label.setText("")  # Clear previous messages
        self.clear_status_layout()  # Clear previous results
        self.input_field.clear()  # Optionally clear input field for next input

        # Disable the submit button during processing
        self.submit_button.setEnabled(False)

        # Simulating HTTP requests
        request_count = 6  # Number of HTTP requests to simulate
        self.active_requests = request_count
        for i in range(request_count):
            QTimer.singleShot(i * 1000, lambda index=i: self.add_request_ui(index))
            QTimer.singleShot((i + 1) * 1000, lambda index=i: self.complete_request(index, success=(index % 2 == 0)))

    def add_request_ui(self, index):
        # Horizontal layout for each request
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(5, 5, 5, 5)

        # Label for request number
        label = QLabel(f"Request {index + 1}:")
        h_layout.addWidget(label)

        # Loading indicator
        spinner = QLabel("\u231B")  # Hourglass symbol
        spinner.setObjectName(f"spinner_{index}")
        h_layout.addWidget(spinner)

        # Toggle button to show/hide details
        toggle_button = QPushButton("Show Details")
        toggle_button.setObjectName(f"toggle_button_{index}")
        toggle_button.setEnabled(False)  # Initially disable the button while loading
        toggle_button.clicked.connect(lambda: self.toggle_details(index, toggle_button))
        h_layout.addWidget(toggle_button)

        # Container for request row
        container = QWidget()
        container.setFixedHeight(40)  # Fixed height for each request
        container.setLayout(h_layout)
        self.status_layout.addWidget(container)

        # Hidden details container for request
        details_container = QWidget()
        details_container.setFixedHeight(60)  # Fixed height for details
        details_layout = QVBoxLayout()
        details_label = QLabel("Details loading...")  # Placeholder for loading details
        details_label.setObjectName(f"details_label_{index}")
        details_layout.addWidget(details_label)
        details_container.setLayout(details_layout)
        details_container.setObjectName(f"details_{index}")
        details_container.setVisible(False)  # Initially hidden
        self.status_layout.addWidget(details_container)

    def complete_request(self, index, success):
        # Update spinner to show success or failure
        spinner = self.findChild(QLabel, f"spinner_{index}")
        if spinner:
            spinner.setText("✔️" if success else "❌")

        # Update details with actual information
        details_label = self.findChild(QLabel, f"details_label_{index}")
        if details_label:
            details_label.setText(f"Request {index + 1} completed successfully: {success}")

        # Enable the toggle button once the request is complete
        toggle_button = self.findChild(QPushButton, f"toggle_button_{index}")
        if toggle_button:
            toggle_button.setEnabled(True)

        # Decrease active request count and re-enable submit button if all requests are complete
        self.active_requests -= 1
        if self.active_requests == 0:
            self.submit_button.setEnabled(True)

    def toggle_details(self, index, toggle_button):
        details_container = self.findChild(QWidget, f"details_{index}")
        if details_container:
            details_visible = details_container.isVisible()
            details_container.setVisible(not details_visible)  # Toggle visibility

            # Update button text
            toggle_button.setText("Hide Details" if not details_visible else "Show Details")

    def clear_status_layout(self):
        # Remove all children widgets from status layout
        while self.status_layout.count():
            child = self.status_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logo_path = get_resource_path("resources/galvanize_logo.png")
    app.setWindowIcon(QIcon(logo_path))

    login_popup = LoginPopup()
    if login_popup.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = COApp()
    window.show()
    sys.exit(app.exec())
