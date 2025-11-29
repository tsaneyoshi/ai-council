from PIL import Image, ImageDraw, ImageFont
import base64
import io

def create_handwriting_test_image():
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # Add text that might be hard for OCR but easy for Vision
    # We can't easily simulate "messy" handwriting without a font, 
    # but we can use a layout that implies it, or just standard text 
    # and rely on the fact that we are testing the PIPELINE, not the model's eyesight.
    # If the pipeline works, the model will see the image.
    
    text = "Handwriting Test:\nVision Model Check"
    d.text((20, 50), text, fill='blue')
    
    # Save to buffer
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    print(img_str)

if __name__ == "__main__":
    create_handwriting_test_image()
