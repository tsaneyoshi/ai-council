from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create a white image
    img = Image.new('RGB', (400, 100), color='white')
    d = ImageDraw.Draw(img)
    
    # Add text
    text = "Success! OCR is working."
    # Use default font
    d.text((20, 40), text, fill='black')
    
    img.save('test_ocr.png')
    print("Created test_ocr.png")

if __name__ == "__main__":
    create_test_image()
