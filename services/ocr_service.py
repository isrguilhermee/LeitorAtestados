import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os

# Caminho completo do executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR"  # Ajuste se instalou em outro local

def extract_text(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        pages = convert_from_path(file_path, dpi=300)
        for page in pages:
            text += pytesseract.image_to_string(page, lang="por")
    else:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="por")
    return text
