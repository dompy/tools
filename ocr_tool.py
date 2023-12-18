import sys
import platform
import os
import json
import subprocess
import appdirs
import re
import numpy as np
import cv2
from languages import get_system_language, get_language_dict, map_system_language_to_application_language
from PyQt5.QtWidgets import QComboBox, QInputDialog, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QMenuBar, QAction, QMessageBox, QSplitter, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from pdf2image import convert_from_path
from docx import Document
import pytesseract
import deepl


# set file path to store personal DeepL api key
def get_api_key_file_path():
    app_name = "OCR-Tool"
    app_author = "MedMate"  
    app_dir = appdirs.user_data_dir(app_name, app_author)
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "api_key.txt")



# Function to perform OCR on an image
def ocr_on_image(image):
    text = pytesseract.image_to_string(image)
    return text

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    images = convert_from_path(pdf_path)
    all_text = []
    for image in images:
        text = ocr_on_image(image)
        all_text.append(text)
    return '\n'.join(all_text)

class AspectRatioPixmapLabel(QLabel):
    def __init__(self, parent=None):
        super(AspectRatioPixmapLabel, self).__init__(parent)
        self._original_pixmap = QPixmap()

    def setPixmap(self, pixmap):
        self._original_pixmap = pixmap
        self.updatePixmap()

    def updatePixmap(self):
        if not self._original_pixmap.isNull():
            scaledPixmap = self._original_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            super(AspectRatioPixmapLabel, self).setPixmap(scaledPixmap)

    def resizeEvent(self, event):
        self.updatePixmap()


class OCRThread(QThread):
    ocr_complete = pyqtSignal(str)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        images = convert_from_path(self.pdf_path)
        all_text = []
        for image in images:
            open_cv_image = np.array(image)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
            preprocessed_image = self.preprocess_image(open_cv_image)
            text = pytesseract.image_to_string(preprocessed_image)
            all_text.append(text)
        final_text = '\n'.join(all_text)
        self.ocr_complete.emit(final_text)
        
    @staticmethod
    def preprocess_image(image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply a basic threshold
        _, thresh = cv2.threshold(gray, 100 , 255, cv2.THRESH_BINARY)
        
        return thresh

    
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = self.load_api_key()

        # Check if the language.txt file exists, if not, create with default values
        if not os.path.exists(self.get_language_file_path()):
            os_language = get_system_language()
            language_code, language_name = map_system_language_to_application_language(os_language)
            language_code = language_code.upper()
            self.save_language_preferences(language_name, language_code, language_name, language_code)

        # Load the system language preference and set self.language
        self.system_language, self.system_language_code, self.translation_language, self.translation_language_code = self.load_language_preferences()

        # Assuming self.language should be the translation language
        self.language = self.translation_language_code

        # Load the language dictionary based on the system language
        self.language_dict = get_language_dict(self.system_language_code)

        # Now initialize the UI components
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("PDF to OCR by @MedMate")
        self.setMinimumSize(900, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize the language_selector
        self.language_selector = QComboBox()
        self.populate_language_selector()        
        self.setup_menu()
        self.setup_widgets()


    def populate_language_selector(self):
        self.language_selector.clear()
        for language_name in self.language_dict.keys():
            self.language_selector.addItem(language_name)

        # Set the current selection in the language selector
        if self.translation_language_code in self.language_dict.values():
            current_translation_language_name = [name for name, code in self.language_dict.items() if code == self.translation_language_code][0]
            self.language_selector.setCurrentText(current_translation_language_name)
        else:
            # Handle the case where the current translation language is not valid
            pass


    def process_pdf(self):
        if self.ocr_thread and self.ocr_thread.isRunning():
            # If the OCR thread is already running, do not open the file dialog again
            return        
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open File", "/", "PDF files (*.pdf)")
        if pdf_path:
            self.status_label.setText("Translating... Please wait.")
            self.ocr_thread = OCRThread(pdf_path)
            self.ocr_thread.ocr_complete.connect(self.on_ocr_complete)
            self.ocr_thread.start()

    def on_ocr_complete(self, text):
        cleaned_text = self.clean_text(text)
        self.text_display.setPlainText(cleaned_text)
        self.status_label.setText("Translation completed.")

        # Save the original text to a DOC file and open it
        original_doc_path = "original_text.docx"
        self.save_to_doc(cleaned_text, original_doc_path)
        self.open_file(original_doc_path)

        # Translate the text and save to another DOC file
        translated_text = self.translate_text(cleaned_text)
        translated_doc_path = "translated_text.docx"
        self.edit_field.setPlainText(translated_text)
        self.save_to_doc(translated_text, translated_doc_path)
        self.open_file(translated_doc_path)

    def clean_text(self, text):
        # Keep alphabetic characters, numbers, and specific punctuation marks
        text = re.sub(r"[^a-zA-Z0-9-/.,;:'\s]", '', text)
        return text

    def translate_text(self, text):
        translator = deepl.Translator(self.api_key)
        try:
            result = translator.translate_text(text, target_lang=self.language)  # Use the selected language code
            return result.text
        except Exception as e:
            QMessageBox.critical(self, "Translation Error", str(e))
            return ""


    def setup_menu(self):
        self.menu_bar = QMenuBar(self)

        settings_menu = self.menu_bar.addMenu('Settings')
        file_menu = self.menu_bar.addMenu('File')
        help_menu = self.menu_bar.addMenu('Help')
        about_menu = self.menu_bar.addMenu('Info')

        set_app_lang = QAction('Set Application Language', self)
        set_app_lang.triggered.connect(self.set_app_language)
        settings_menu.addAction(set_app_lang)

        open_action = QAction('Open file', self)
        open_action.triggered.connect(self.process_pdf)
        file_menu.addAction(open_action)        
        
        change_api_action = QAction('Change API Key', self)
        change_api_action.triggered.connect(self.change_api_key)
        file_menu.addAction(change_api_action)
        
        exit_action = QAction('Close', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction('Info', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        self.layout.setMenuBar(self.menu_bar)
            
    def set_app_language(self):
        # Load the current language preferences
        _, current_language_code, _, translation_language_code = self.load_language_preferences()

        # Get a list of language names from the current dictionary
        language_names = list(get_language_dict(current_language_code).keys())

        # Find the index of the current language in the list
        current_index = language_names.index(self.system_language) if self.system_language in language_names else 0

        # Open the language selection dialog
        new_language_name, ok = QInputDialog.getItem(self, "Select Language", "Language:", language_names, current_index)
        
        if ok and new_language_name:
            # Get the new language code from the dictionary
            new_language_code = get_language_dict(current_language_code)[new_language_name]

            # Update the system language and code
            self.system_language = new_language_name
            self.system_language_code = new_language_code

            # Save the updated language preferences
            self.save_language_preferences(self.system_language, self.system_language_code, _, translation_language_code)

            self.system_language_dict = get_language_dict(self.system_language_code)

            # Update the language selector with new options
            self.populate_language_selector()

            # Update the translation language selector in the UI
            self.update_translation_language_selector()

    def update_translation_language_selector(self):
        # Clear the current items in the translation language selector
        self.language_selector.clear()

        # Add the new language options to the selector
        for language_name in self.system_language_dict.keys():
            self.language_selector.addItem(language_name)

        # Optionally, set the current translation language as the selected item
        current_translation_language_name = self.get_full_language_name(self.system_language_code)  # Replace '_' with the current translation language code
        self.language_selector.setCurrentText(current_translation_language_name)


    def show_about_dialog(self):
        QMessageBox.about(self, "Info", "PDF to OCR Application including translation\n\nContact\ndominik.pytlik@gmail.com\n\nSwitzerland\nDecember 2023")

    def load_api_key(self):
        api_key_file_path = get_api_key_file_path()
        try:
            with open(api_key_file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""

    def change_api_key(self):
        new_key, ok = QInputDialog.getText(self, 'Change API Key', 
                                           'DeepL API Key: ', text=self.api_key)
        if ok and new_key:
            self.api_key = new_key
            self.save_api_key(new_key)
        
    def save_api_key(self, key):
        api_key_file_path = get_api_key_file_path()
        with open(api_key_file_path, "w") as file:
            file.write(key)

            
    def setup_widgets(self):

        self.setup_labels_and_fields()
        
        # Vertical Splitter for Entire Layout
        main_splitter = QSplitter(Qt.Vertical)

        top_horizontal_splitter = QSplitter(Qt.Horizontal)
        top_horizontal_splitter.addWidget(self.process_button)
        top_horizontal_splitter.addWidget(self.language_selector)

        bottom_horizontal_splitter = QSplitter(Qt.Horizontal)
        bottom_horizontal_splitter.addWidget(self.text_display)
        bottom_horizontal_splitter.addWidget(self.edit_field)

        # Add horizontal splitters to the main vertical splitter
        main_splitter.addWidget(top_horizontal_splitter)
        main_splitter.addWidget(bottom_horizontal_splitter)

        # Connect the top and bottom splitter to move in sync
        top_horizontal_splitter.splitterMoved.connect(self.sync_splitter(bottom_horizontal_splitter))
        bottom_horizontal_splitter.splitterMoved.connect(self.sync_splitter(top_horizontal_splitter))

        # Adding widgets to the layout
        self.layout.addWidget(main_splitter)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.close_button)

        # Set up the OCR thread
        self.ocr_thread = None

    def sync_splitter(self, splitter_to_sync):
        def syncer(position, index):
            splitter_to_sync.blockSignals(True)
            splitter_to_sync.moveSplitter(position, index)
            splitter_to_sync.blockSignals(False)
        return syncer

    def setup_labels_and_fields(self):
        system_language, system_language_code, translation_language, self.translation_language_code = self.load_language_preferences()
        # Target Language Selector
        self.language_selector = QComboBox()
        self.language_selector.setStyleSheet(self.get_dropdown_style("#75A1BF"))
        self.language_selector.addItems(self.language_dict.keys())
        self.language_selector.setCurrentText(self.get_full_language_name(self.translation_language_code))
        self.language_selector.currentIndexChanged.connect(self.on_language_change)        

        # Text Display and Edit Field
        self.text_display = QTextEdit()
        self.edit_field = QTextEdit()
        self.setup_text_edit_styles()

        # 'Open PDF' Button
        self.process_button = QPushButton("Translate PDF")
        self.process_button.setStyleSheet(self.get_button_style("#75A1BF"))
        self.process_button.clicked.connect(self.process_pdf)
        
        # 'Close' Button
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(self.get_button_style("#75A1BF"))
        self.close_button.clicked.connect(self.close)        

        # Status Bar/Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #AEC6CF;")        

    def save_to_doc(self, text, doc_path):
        doc = Document()
        doc.add_paragraph(text)
        doc.save(doc_path)

    def open_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # macOS
            os.system(f"open {file_path}")
        else:  # linux variants
            os.system(f"xdg-open {file_path}")                

    def get_full_language_name(self, language_code):
        for name, code in self.language_dict.items():
            if code == language_code:
                return name
        return 'English'  # Default language

    
    # set file path to store target language preference
    def get_language_file_path(self):
        app_name = "OCR-Tool"
        app_author = "MedMate"  
        app_dir = appdirs.user_data_dir(app_name, app_author)
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, "language.txt")
            
    def load_language_preferences(self):
        language_file_path = self.get_language_file_path()

        # Check if the file exists, and create it with default values if it doesn't
        if not os.path.exists(language_file_path):
            self.save_language_preferences("English", "EN", "English", "EN")

        try:
            with open(language_file_path, 'r') as file:
                preferences = json.load(file)
                return (preferences.get('system_language', "English"),
                        preferences.get('system_language_code', "EN"),
                        preferences.get('translation_language', "English"),
                        preferences.get('translation_language_code', "EN"))
        except FileNotFoundError:
            return "English", "EN", "English", "EN"  # Default values

        
    def save_language_preferences(self, system_language, system_language_code, translation_language, translation_language_code):
        language_file_path = self.get_language_file_path()
        preferences = {
            'system_language': system_language,
            'system_language_code': system_language_code,  
            'translation_language': translation_language, 
            'translation_language_code': translation_language_code,  
        }
        with open(language_file_path, 'w') as file:
            json.dump(preferences, file)
 
    def on_language_change(self, index):
        full_language_name = self.language_selector.currentText()
        if full_language_name:
            self.translation_language_code = self.language_dict.get(full_language_name)
            if self.translation_language_code:
                # Load the current system language preferences
                system_language, system_language_code, _, _ = self.load_language_preferences()

                # Save both system and translation language preferences
                self.save_language_preferences(system_language, system_language_code, full_language_name, self.translation_language_code)
            else:
                # Handle the case where the language name is not in the dictionary
                pass
        else:
            # Handle the case where the language selector returns an empty string
            pass

                        
    def get_button_style(self, background_color):
        """ Returns the style sheet for buttons. """
        return f"""
            QPushButton {{
                background-color: {background_color};
                color: white;
                font-size: 20px;
                padding: 15px 10px;
                text-align: center;
                border-radius: 6px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #F0ECD3; /* Light Cream */
                color: {background_color};
            }}
        """

    def get_dropdown_style(self, background_color):
        """ Returns the style sheet for dropdown lists. """
        return f"""
            QComboBox {{
                background-color: {background_color};
                color: white;
                padding: 15px 10px;
                font-size: 20px;
                border-radius: 6px;
                min-width: 105px;
            }}
            QComboBox:hover {{
                background-color: #F0ECD3; /* Light Cream */
                color: {background_color};
            }}
            QComboBox::down-arrow {{
                image: none; /* This line removes the arrow */
            }}
            QComboBox::drop-down {{
                border: none; /* This line removes the border around the arrow area */
            }}
        """

    def setup_text_edit_styles(self):
        """ Sets the style for text edit fields. """
        style = """
            QTextEdit {
                font-size: 16px;
                color: black;
                background-color: #FFFDD0; /* Light Pastel Yellow */
                selection-color: black;
                selection-background-color: #B0E0E6; /* Powder Blue */
                padding: 15px 10px;
                border-radius: 6px;
                min-width: 105px;
            }
        """
        self.text_display.setStyleSheet(style)
        self.edit_field.setStyleSheet(style)
        
# Create and run the application
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
