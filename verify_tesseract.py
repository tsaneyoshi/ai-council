import pytesseract
from PIL import Image, ImageDraw
import sys
import os

def check_tesseract():
    print(f"Python executable: {sys.executable}")
    print(f"Path: {os.environ.get('PATH')}")
    
    try:
        # Create a simple image
        img = Image.new('RGB', (100, 30), color='white')
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Test", fill='black')
        
        # Try to run tesseract
        text = pytesseract.image_to_string(img)
        print(f"OCR Result: '{text.strip()}'")
        print("Tesseract execution successful.")
        
    except Exception as e:
        print(f"Error executing tesseract: {e}")
        # Check if tesseract is in path
        import shutil
        tesseract_path = shutil.which("tesseract")
        print(f"Tesseract binary found at: {tesseract_path}")

if __name__ == "__main__":
    check_tesseract()
