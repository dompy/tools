# OCR Translation Tool

This tool provides an easy-to-use interface for translating PDF documents from French to German. It utilizes OCR (Optical Character Recognition) technology to extract text from PDF files and then translates it using the DeepL API.

## Features

- **PDF to Text Conversion**: Extract text from PDF files using OCR.
- **Translation**: Translate the extracted text from French to German.
- **User-Friendly Interface**: Simple and intuitive GUI for easy operation.
- **API Key Customization**: Option to change the DeepL API key as needed.

## Requirements

- Python 3.x
- PyQt5
- pytesseract
- DeepL API Key (Free or Paid)

## Dependencies

This project relies on several external libraries, which are listed in the requirements.txt file. Key dependencies include:

- PyQt5: Python bindings for the Qt application framework.
- pdf2image: Converts PDF files into images.
- python-docx: Reads, queries, and modifies Microsoft Word 2007/2010 docx files.
- pytesseract: Python wrapper for Google's Tesseract-OCR Engine.
- deepl: Python client for the DeepL Translator API for language translation.
- numpy: Fundamental package for scientific computing.
- opencv-python: OpenCV library for computer vision tasks.

These libraries are used for various functions such as PDF processing, image manipulation, OCR capabilities, and GUI development.

## Setup

1. **Install Dependencies**: Ensure that Python 3.x is installed on your system. Install the required Python libraries using pip:

   ```bash
   pip install -r requirements.txt 
   ```
   
in your virtual environment.

2. **DeepL API Key**: You need a DeepL API key to use the translation feature. You can obtain a free API key from [DeepL's website](https://support.deepl.com/hc/en-us/articles/360019358899-Access-to-DeepL-s-API).

3. **Clone the Repository**: Clone this repository to your local machine or download the source code.

   ```bash
   git clone https://github.com/dompy/tools.git
   ```
   
4. **Run the Application**: Navigate to the directory containing the tool and run it using Python:

   ```bash
   python ocr_tool.py
   ```
   
## Usage
- Open a PDF: Click on the "Open PDF" button and select a PDF file in French.
- Translate: The tool will automatically process the PDF, perform OCR, and translate the text to German.
- View Results: The original and translated texts will be displayed in the application and generate a doc file for each language.

## Customization
- Change API Key: If you have your own DeepL API key, you can change it through the application's interface.

## Contact
For any inquiries or suggestions, please contact:

Dominik Pytlik

Email: dominik.pytlik@gmail.com
Location: Switzerland
Date: December 2023