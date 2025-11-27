import io
import csv
from typing import Optional
from fastapi import UploadFile

# Import optional dependencies for file parsing
try:
    import docx
except ImportError:
    docx = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from pptx import Presentation
except ImportError:
    Presentation = None


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from an uploaded file based on its content type or extension.
    """
    filename = file.filename.lower()
    content = await file.read()
    
    # Reset file cursor for libraries that might need it, though we read bytes
    # Most libraries below will use io.BytesIO(content)
    
    text = ""
    
    if filename.endswith('.txt') or filename.endswith('.md') or filename.endswith('.py') or filename.endswith('.xml') or filename.endswith('.json') or filename.endswith('.js') or filename.endswith('.jsx') or filename.endswith('.ts') or filename.endswith('.tsx') or filename.endswith('.html') or filename.endswith('.css'):
        # Text files
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try fallback encodings if needed, or just ignore errors
            text = content.decode('utf-8', errors='replace')
            
    elif filename.endswith('.csv'):
        # CSV files
        try:
            decoded = content.decode('utf-8')
            f = io.StringIO(decoded)
            reader = csv.reader(f)
            rows = list(reader)
            text = "\n".join([",".join(row) for row in rows])
        except Exception as e:
            text = f"Error reading CSV: {str(e)}"
            
    elif filename.endswith('.pdf'):
        # PDF files
        if pypdf:
            try:
                pdf_file = io.BytesIO(content)
                reader = pypdf.PdfReader(pdf_file)
                pages_text = []
                for page in reader.pages:
                    pages_text.append(page.extract_text())
                text = "\n\n".join(pages_text)
            except Exception as e:
                text = f"Error reading PDF: {str(e)}"
        else:
            text = "PDF support not available (pypdf not installed)"
            
    elif filename.endswith('.docx'):
        # Word files
        if docx:
            try:
                doc_file = io.BytesIO(content)
                doc = docx.Document(doc_file)
                text = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                text = f"Error reading DOCX: {str(e)}"
        else:
            text = "DOCX support not available (python-docx not installed)"
            
    elif filename.endswith('.pptx'):
        # PowerPoint files
        if Presentation:
            try:
                pptx_file = io.BytesIO(content)
                prs = Presentation(pptx_file)
                slides_text = []
                for slide in prs.slides:
                    slide_text = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            slide_text.append(shape.text)
                    slides_text.append("\n".join(slide_text))
                text = "\n\n--- Slide ---\n\n".join(slides_text)
            except Exception as e:
                text = f"Error reading PPTX: {str(e)}"
        else:
            text = "PPTX support not available (python-pptx not installed)"
            
    elif filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
        # Image files - Placeholder for now as we don't have OCR set up
        # In a real app, we might use an OCR library or send the image to a vision model
        text = f"[Image file: {file.filename}] (Image content extraction not implemented yet)"
        
    else:
        text = f"[Unsupported file type: {file.filename}]"

    return text
