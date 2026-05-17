import fitz
from dataclasses import dataclass
from PIL import Image
import io
import os
import pytesseract
from app.services.transcriber import transcribe_audio


@dataclass
class ExtractionResult:
    pages: list[str]
    total_pages: int

def extract_from_pdf(content: bytes) -> ExtractionResult:
    pages = []

    doc = fitz.open(stream=content, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if(text.strip()):  # Only add pages that have text(that is skipping blank pages and pages with only images)
            pages.append(text)
    
    if len(pages) == 0:
        for page_num in range(len(doc)):
            page = doc[page_num]

            # PDF page to image
            pimg = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            image_data = pimg.tobytes("png")
            image = Image.open(io.BytesIO(image_data))
            
            text = pytesseract.image_to_string(image)
            if text.strip():
                pages.append(text)

    doc.close()

    return ExtractionResult(pages=pages, total_pages=len(pages))

def extract_from_txt(content: bytes) -> ExtractionResult:
    text = content.decode("utf-8")
    pages=[text]
    
    return ExtractionResult(pages=pages, total_pages=1)

def is_audio_or_video(content_type: str) -> bool:
    return (
        content_type.startswith("audio/") 
        or content_type.startswith("video/")
    )

def extract(content: bytes, content_type: str) -> ExtractionResult:
    if is_audio_or_video(content_type):
        text = transcribe_audio(content, content_type)
        if not text.strip():
            raise ValueError("No speech or audio content could be transcribed from the uploaded file.")
        return ExtractionResult(pages=[text], total_pages=1)

    if content_type == "application/pdf":
        return extract_from_pdf(content)
    elif content_type == "text/plain":
        return extract_from_txt(content)
    else:
        raise ValueError(f"Unsupported file type or format: {content_type}")