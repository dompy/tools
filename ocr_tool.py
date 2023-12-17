import sys
import os
import appdirs
import re
import numpy as np
import cv2
from PyQt5.QtWidgets import QInputDialog, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QMenuBar, QAction, QMessageBox, QSplitter, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from pdf2image import convert_from_path
from docx import Document
import pytesseract
import deepl

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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PDF to OCR by @MedMate")
        self.setMinimumSize(600, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setup_menu()
        self.setup_widgets()

    def show_about_dialog(self):
        QMessageBox.about(self, "Info", "PDF to OCR Application including translation to german\n\nContact\ndominik.pytlik@gmail.com\n\nSwitzerland\nDecember 2023")

    def process_pdf(self):
        if self.ocr_thread and self.ocr_thread.isRunning():
            # If the OCR thread is already running, do not open the file dialog again
            return        
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open File", "/", "PDF files (*.pdf)")
        if pdf_path:
            self.status_label.setText("translating... Please wait.")
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


    def setup_menu(self):
        self.menu_bar = QMenuBar(self)

        file_menu = self.menu_bar.addMenu('File')
        help_menu = self.menu_bar.addMenu('Help')
        about_menu = self.menu_bar.addMenu('Info')

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

    def change_api_key(self):
        new_key, ok = QInputDialog.getText(self, 'Change API Key', 
                                           'DeepL API Key: ', text=self.api_key)
        if ok and new_key:
            self.api_key = new_key
            self.save_api_key(new_key)

    def setup_widgets(self):
        layout = QVBoxLayout()
        
        # 'Open PDF' Button
        self.process_button = QPushButton("translate pdf to german")
        self.process_button.setStyleSheet(self.get_button_style("#75A1BF"))
        self.process_button.clicked.connect(self.process_pdf)

        # 'Close' Button
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(self.get_button_style("#75A1BF"))  # Pastel Red Button
        self.close_button.clicked.connect(self.close)  # Connect to the close event

        # Text Display and Edit Field
        self.text_display = QTextEdit()
        self.edit_field = QTextEdit()
        self.setup_text_edit_styles()

        # Splitter for Text Display and Edit Field
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.text_display)
        splitter.addWidget(self.edit_field)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #AEC6CF;")  # Pastel-colored font for status

        # Adding widgets to the layout
        self.layout.addWidget(self.process_button)  
        self.layout.addWidget(splitter, 1)
        self.layout.addWidget(self.status_label, 0)
        self.layout.addWidget(self.close_button)

        # Connect 'Open PDF' button to the processing function
        self.process_button.clicked.connect(self.process_pdf)

        # Set up the OCR thread
        self.ocr_thread = None
        
    def translate_text(self, text):
        translator = deepl.Translator(self.api_key)
        try:
            result = translator.translate_text(text, target_lang="DE")  # Change "DE" to your target language
            return result.text
        except Exception as e:
            QMessageBox.critical(self, "Translation Error", str(e))
            return ""
        
    def load_api_key(self):
        api_key_file_path = get_api_key_file_path()
        try:
            with open(api_key_file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""

    def save_api_key(self, key):
        api_key_file_path = get_api_key_file_path()
        with open(api_key_file_path, "w") as file:
            file.write(key)
        
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
                        
    def get_button_style(self, background_color):
        """ Returns the style sheet for buttons. """
        return f"""
            QPushButton {{
                background-color: {background_color};
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 20px;
                border-radius: 6px;
                min-width: 150px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: #F0ECD3; /* Light Cream */
                color: {background_color};
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
            }
        """
        self.text_display.setStyleSheet(style)
        self.edit_field.setStyleSheet(style)
        

# Create and run the application
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
