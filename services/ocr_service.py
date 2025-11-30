import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os


class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR."""
    
    def __init__(self, tesseract_cmd=None, language="por"):
        """
        Initialize OCR service.
        
        Args:
            tesseract_cmd: Path to Tesseract executable. If None, uses default.
            language: Language for OCR (default: 'por' for Portuguese)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Use macOS Homebrew path by default
            pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
        self.language = language
    
    def extract_text(self, file_path):
        """
        Extract text from an image or PDF file.
        
        Args:
            file_path: Path to the file (PDF, JPG, PNG, etc.)
            
        Returns:
            str: Extracted text
        """
        text = ""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            pages = convert_from_path(file_path, dpi=300)
            for page in pages:
                text += pytesseract.image_to_string(page, lang=self.language)
        else:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang=self.language)
        
        return text
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Extracted text
        """
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang=self.language)
    
    def extract_text_from_pdf(self, pdf_path, dpi=300):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            dpi: DPI for PDF conversion (default: 300)
            
        Returns:
            str: Extracted text from all pages
        """
        pages = convert_from_path(pdf_path, dpi=dpi)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page, lang=self.language)
        return text


# Legacy function for backward compatibility
def extract_text(file_path):
    """Legacy function wrapper for backward compatibility."""
    ocr = OCRService()
    return ocr.extract_text(file_path)
