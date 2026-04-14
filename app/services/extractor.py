import fitz
from dataclasses import dataclass


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

    doc.close()

    return ExtractionResult(pages=pages, total_pages=len(pages))

def extract_from_txt(content: bytes) -> ExtractionResult:
    text = content.decode("utf-8")
    pages=[text]
    
    return ExtractionResult(pages=pages, total_pages=1)

def extract(content: bytes, content_type: str) -> ExtractionResult:
    if content_type == "application/pdf":
        return extract_from_pdf(content)
    elif content_type == "text/plain":
        return extract_from_txt(content)