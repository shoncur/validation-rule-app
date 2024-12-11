import os
import sys
import requests
import json
from PyQt5.QtWidgets import QCheckBox, QApplication, QDialog, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QTabWidget, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from base import BASE_URL

class LoginPopup(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon("your_icon.png"))  # Add your icon file path
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.email_label = QLabel("Email:", self)
        self.email_entry = QLineEdit(self)
        self.password_label = QLabel("Password:", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)

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

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_entry.setEchoMode(QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)

    def login(self):
        email = self.email_entry.text()
        password = self.password_entry.text()

        url = f'{BASE_URL}/login'
        headers = {'Content-Type': 'application/json'}

        try:
            data = {'email': f'{email}', 'password': f'{password}'}
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            global arena_session_id
            arena_session_id = response.json()['arenaSessionId']

            print(response)
        except Exception as error:
            print(f'Invalid entry: {error}')
            self.error_label.setText(f'Enter a valid email/password')
            return

        self.accept()

class COApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('CO Validation')
        self.init_ui()

    def init_ui(self):
        # Section for CO input
        co_input_label = QLabel('Enter a CO number for validation')
        co_label = QLabel('CO-')
        self.co_textbox = QLineEdit()
        validate_button = QPushButton('Validate')
        validate_button.clicked.connect(self.validate_clicked)

        co_input_layout = QHBoxLayout()
        co_input_layout.addWidget(co_label)
        co_input_layout.addWidget(self.co_textbox)
        co_input_layout.addWidget(validate_button)

        # Create a layout for unsupported types of change
        self.unsupported_layout = QVBoxLayout()

        # Create a QTextEdit widget for displaying general error/status messages
        initial_label = QLabel('Initial Release')
        self.result_text_edit = QTextEdit()
        self.result_text_edit.setReadOnly(True)
        self.result_text_edit.setMinimumHeight(200)
        self.result_text_edit.setMinimumWidth(600)

        # Create a QTextEdit widget for displaying results of process_document_update
        doc_update_label = QLabel('Document Update')
        self.document_update_result_edit = QTextEdit()
        self.document_update_result_edit.setReadOnly(True)
        self.document_update_result_edit.setMinimumHeight(200)
        self.document_update_result_edit.setMinimumWidth(600)

        # Lifecycle update now
        life_update_label = QLabel('Lifecycle Update')
        self.life_update_result_edit = QTextEdit()
        self.life_update_result_edit.setReadOnly(True)
        self.life_update_result_edit.setMinimumHeight(200)
        self.life_update_result_edit.setMinimumWidth(600)

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(co_input_label)
        main_layout.addLayout(co_input_layout)
        main_layout.addWidget(initial_label)
        main_layout.addWidget(self.result_text_edit)
        main_layout.addWidget(doc_update_label)
        main_layout.addWidget(self.document_update_result_edit)
        main_layout.addWidget(life_update_label)
        main_layout.addWidget(self.life_update_result_edit)
        main_layout.addLayout(self.unsupported_layout)

        self.setLayout(main_layout)

    def process_initial_release(self, co_url, co_headers):
        try:

            # Get all items in Change
            items_url = f'{co_url}/items'
            items_response = requests.get(items_url, headers=co_headers).json()
            print(json.dumps(items_response, indent=2))

            initial_release_numbers = []
            initial_release_sourcing = []
            is_document_list = []

            revisions = []

            primary_status_list = []
            primary_file_formats = []
            primary_file_names = []

            not_initial_release_numbers = []
            initial_release_checklist = []

            # We need to go to the specific item and check if there is sourcing
            # This needs to change because the check mark is not indicative of there actually being content (ie. specs)

            results_list = items_response.get('results', [])
            for result in results_list:
                affected_item_revision = result.get('affectedItemRevision')
                if affected_item_revision is None:
                    item_guid = result.get('newItemRevision')['guid']
                    item_number = result.get('newItemRevision')['number']
                    lifecycle_phase = result.get('newLifecyclePhase')['name']
                    revision = result.get('newRevisionNumber')
                    initial_release_numbers.append(item_number)

                    revisions.append(revision)

                    # FOR SOURCING
                    # NOTE: THAT ALL 'DOCUMENT' TYPES WILL NOT REQUIRE SOURCING
                    item_url = f'{BASE_URL}/items/{item_guid}/sourcing'
                    item_response = requests.get(item_url, headers=co_headers).json()
                    sourcing_count = item_response.get('count')

                    is_document = False
                    sourcing = False

                    if sourcing_count == 0:
                        # We need to check if it is a document type or not
                        # Document type does not need sourcing, other types do not

                        # Check the prefixes file and see if this item is a document or not
                        with open('document_prefixes.txt', 'r') as file:
                            prefixes = [line.strip() for line in file]

                        for prefix in prefixes:
                            if item_number.startswith(prefix):
                                is_document = True
                                is_document_list.append(is_document)
                                # If it's a document, we need to make sure that it's going straight to production release
                                break  # No need to check the rest of the prefixes if it turns out it's a document

                        if is_document:
                            sourcing = True
                            initial_release_sourcing.append(sourcing)
                            if lifecycle_phase != 'Production Release':
                                result_text = '<span style="color: #ff0000;"><b>Initial release documents must ALWAYS go straight to Production Release</b></span><br><br>'
                                self.result_text_edit.append(result_text)
                        else:
                            sourcing = False
                            initial_release_sourcing.append(sourcing)
                            is_document_list.append(is_document)

                    else:
                        sourcing = True
                        initial_release_sourcing.append(sourcing)
                        is_document_list.append(is_document)  # This is only here to ensure that the is_document_list and the other lists line up, if sourcing is there, it does not matter if it is a document or not
                        # Maybe we want to fetch the information for the sourcing?

                    # Everything must be checkmarked
                    specs_check = result.get('specsView')['includedInThisChange']
                    bom_check = result.get('bomView')['includedInThisChange']
                    sourcing_check = result.get('sourcingView')['includedInThisChange']
                    files_check = result.get('filesView')['includedInThisChange']
                    item_check_stats = [specs_check, bom_check, sourcing_check, files_check]
                    initial_release_checklist.append(item_check_stats)
                    # PDF must be the primary file
                    item_url = f'{BASE_URL}/items/{item_guid}/files'
                    item_response = requests.get(item_url, headers=co_headers).json()

                    item_files_count = item_response.get('count')
                    if item_files_count == 0:
                        result_text = f'<span style="color: #ff0000;">There are no files associated with {item_number}</span><br><br>'
                        self.result_text_edit.append(result_text)
                    else:
                        # We need to make sure that there is a primary file
                        files_list = item_response.get('results', [])
                        has_primary = False
                        for file in files_list:
                            primary_status = file.get('primary')
                            file_name = file.get('file')['name']
                            if primary_status:
                                has_primary = True
                                format_type = file.get('file')['format']
                                primary_file_formats.append(format_type)
                                primary_status_list.append(has_primary)
                                primary_file_names.append(file_name)
                                break
                        if not has_primary:
                            primary_status_list.append(has_primary)
                            primary_file_names.append('')
                else:
                    not_initial_release_numbers.append(result.get('newItemRevision')['number'])

            result_text = f'\n<span style="font-weight: bold;">Items that are believed to be initial release:</span><br>'
            for i, item in enumerate(initial_release_numbers):
                sourcing = initial_release_sourcing[i]
                is_document = is_document_list[i]
                primary_file_name = primary_file_names[i]
                primary_file_format = primary_file_formats[i]
                primary_status = primary_status_list[i]
                revision = revisions[i]

                result_text += f'    - {item}<br>'
                result_text += f'<span style="color: #0096ff; font-weight: bold;">&nbsp;&nbsp;&nbsp;Sourcing status:</span><br>'

                if is_document and sourcing:
                    result_text += f'<span style="color: #00cc00; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sourcing included</span><br>'
                if is_document and not sourcing:
                    result_text += f'<span style="color: #00cc00; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This item is a document, sourcing is not required</span><br>'
                if not is_document and sourcing:
                    result_text += f'<span style="color: #00cc00; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sourcing included</span><br>'
                if not is_document and not sourcing:
                    result_text += f'<span style="color: #ff0000; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This item is missing sourcing</span><br>'

                result_text += f'<span style="color: #0096ff; font-weight: bold;">&nbsp;&nbsp;&nbsp;File Status:</span><br>'

                if primary_status:
                    result_text += f'<span style="color: #00cc00; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Item has a primary file</span><br>'
                    result_text += f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Primary file name: {primary_file_name}<br>'
                    if primary_file_format != 'pdf':
                        result_text += f'<span style="color: #ff0000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Primary file is not a pdf</span><br>'
                else:
                    result_text += f'<span style="color: #ff0000; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Item does not have a primary file</span><br>'

                result_text += f'<span style="color: #0096ff; font-weight: bold;">&nbsp;&nbsp;&nbsp;Revision:</span><br>&nbsp;&nbsp;&nbsp;{revision}<br>'

                if revision != 'A':
                    result_text += f'<span style="color: #00cc00; font-weight: bold;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Initial Release should always be rev A</span><br>'

            result_text += f'\n<span style="font-weight: bold;">Items that are NOT believed to be initial release:</span><br>'
            for item in not_initial_release_numbers:
                result_text += f'    - {item}<br>'

            result_text += f'\n<span style="font-weight: bold;">Modifications Checklist:</span><br>'
            for i, item in enumerate(initial_release_checklist):
                item_number = initial_release_numbers[i]
                result_text += f'    - {item_number}:<br>'

                if item[0] == True:
                    result_text += '&nbsp;&nbsp;&nbsp;Specs: <span style="color: #00cc00;">\u2713</span><br>'
                else:
                    result_text += '&nbsp;&nbsp;&nbsp;Specs: <span style="color: #ff0000;">\u2717</span><br>'

                if item[1] == True:
                    result_text += '&nbsp;&nbsp;&nbsp;BOM: <span style="color: #00cc00;">\u2713</span><br>'
                else:
                    result_text += '&nbsp;&nbsp;&nbsp;BOM: <span style="color: #ff0000;">\u2717</span><br>'

                if item[2] == True:
                    result_text += '&nbsp;&nbsp;&nbsp;Sourcing: <span style="color: #00cc00;">\u2713</span><br>'
                else:
                    result_text += '&nbsp;&nbsp;&nbsp;Sourcing: <span style="color: #ff0000;">\u2717</span><br>'

                if item[3] == True:
                    result_text += '&nbsp;&nbsp;&nbsp;Files: <span style="color: #00cc00;">\u2713</span><br>'
                else:
                    result_text += '&nbsp;&nbsp;&nbsp;Files: <span style="color: #ff0000;">\u2717</span><br>'

            # Set the result_text to the QTextEdit
            self.result_text_edit.setHtml(result_text)
            print(f'Result in process_initial_release: {self.result_text_edit.toPlainText()}')
        except Exception as e:
            print(f'Error in process_initial_release: {str(e)}')

    def process_document_update(self, co_guid, co_headers):
        # Check that there are redlines included in the files
        file_url = f'{BASE_URL}/changes/{co_guid}/files'
        file_response = requests.get(file_url, headers=co_headers).json()

        # Search through all files to get category guid's
        category_ids = [category_id['file']['category']['guid'] for category_id in file_response['results']]
        cat_names = []

        for c in category_ids:
            cat_url = f'{BASE_URL}/settings/files/categories/{c}'
            cat_response = requests.get(cat_url, headers=co_headers).json()
            cat_name = cat_response['name']
            cat_names.append(cat_name)

        if 'Redlines' in cat_names:
            result_text = '<br><span style="color: #00cc00; font-weight: bold;">**This CO has redlines included**</span><br>'
        else:
            result_text = '<br><span style="color: #cc0000; font-weight: bold;">**This CO is missing redlines**</span><br>'

        result_text += '<span style="font-weight: bold;">All file categories used in this CO:</span><br>'
        for category in cat_names:
            result_text += f'\t- {category}<br>'

        # Display the results in the new QTextEdit widget
        self.document_update_result_edit.setHtml(result_text)

    def process_lifecycle_update(self, co_url, co_headers):
        items_url = f'{co_url}/items'
        items_response = requests.get(items_url, headers=co_headers).json()
        #print(json.dumps(items_response, indent=2))

        lifecycle_update_numbers = []
        not_lifecycle_update_numbers = []
        list_of_phases = []

        results_list = items_response.get('results', [])
        for result in results_list:
            affected_item_revision = result.get('affectedItemRevision')
            if affected_item_revision is None:
                not_lifecycle_update_numbers.append(result.get('newItemRevision')['number'])
            else:
                lifecycle_update_numbers.append(result.get('newItemRevision')['number'])
                # Get the old lifecycle phase

                # Get the new lifecycle phase
                new_phase = result.get('newLifecyclePhase')['name']
                list_of_phases.append(new_phase)

        result_text = f'\n<span style="font-weight: bold;">Items undergoing lifecycle update (not initial release): </span><br>'
        for i, item in enumerate(lifecycle_update_numbers):
            result_text += f'    - {item}<br>'
            result_text += f'<span style="color: #0096ff; font-weight: bold;">&nbsp;&nbsp;&nbsp;Previous Lifecycle Phase: </span><br>'
            result_text += f'<span style="color: #0096ff; font-weight: bold;">&nbsp;&nbsp;&nbsp;New Lifecycle Phase: {list_of_phases[i]}</span><br>'

    def dispatch_process(self, type_of_change_value, co_url, co_guid, co_headers):
        if type_of_change_value == "Initial Release":
            self.process_initial_release(co_url, co_headers)
        elif type_of_change_value == "Document/File Update" or "Document Update":
            print('doc up')
            self.process_document_update(co_guid, co_headers)
        elif type_of_change_value == "Lifecycle Update":
            print('life up')
            self.process_lifecycle_update(co_url, co_headers)
        else:
            self.display_unsupported_type(type_of_change_value)

    def display_unsupported_type(self, unsupported_type):
        unsupported_label = QLabel(f'Unsupported Type of Change: {unsupported_type}')
        self.unsupported_layout.addWidget(unsupported_label)

    def validate_clicked(self):
        self.clear_process_widgets()
        self.clear_unsupported_type_display()

        # Get the CO number from the textbox
        co_number = 'CO-' + self.co_textbox.text()

        # Perform the validation process (you can add your logic here)
        try:
            co_url = f'{BASE_URL}/changes?number={co_number}'
            co_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type':'application/json'}
            co_response = requests.get(co_url, headers=co_headers).json()

            co_guid = co_response['results'][0]['guid']
            co_url = f'{BASE_URL}/changes/{co_guid}'
            co_response = requests.get(co_url, headers=co_headers).json()

            type_of_change_attribute = next(
                (attr for attr in co_response.get('additionalAttributes', []) if attr.get('name') == 'Type of Change'),
                None
            )

            type_of_change_value = type_of_change_attribute.get('value') if type_of_change_attribute else None

            if type_of_change_value:
                for type in type_of_change_value:
                    self.dispatch_process(type, co_url, co_guid, co_headers)
            else:
                self.error_status_label.setStyleSheet("color: red")
                self.error_status_label.setText('Type of Change not found')

        except Exception as e:
            result_text = f'Error - {str(e)}'
            self.result_text_edit.setPlainText(result_text)

    def clear_process_widgets(self):
        self.result_text_edit.clear()
        self.document_update_result_edit.clear()

    def clear_unsupported_type_display(self):
        # Clear the unsupported type display
        for i in reversed(range(self.unsupported_layout.count())):
            widget = self.unsupported_layout.itemAt(i).widget()
            self.unsupported_layout.removeWidget(widget)
            widget.setParent(None)

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