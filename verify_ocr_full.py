from reportlab.pdfgen import canvas
from pdf2image import convert_from_bytes
import pytesseract
import io
import os

def verify_full_chain():
    print("Creating dummy PDF...")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello World OCR Test")
    c.save()
    pdf_bytes = buffer.getvalue()
    print(f"PDF created. Size: {len(pdf_bytes)} bytes")

    print("Converting PDF to image...")
    try:
        images = convert_from_bytes(pdf_bytes)
        print(f"Converted to {len(images)} images.")
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        # Check for poppler
        import shutil
        print(f"pdftoppm path: {shutil.which('pdftoppm')}")
        return

    print("Running OCR on image...")
    try:
        text = pytesseract.image_to_string(images[0])
        print(f"OCR Result: '{text.strip()}'")
    except Exception as e:
        print(f"Error running OCR: {e}")

if __name__ == "__main__":
    verify_full_chain()
