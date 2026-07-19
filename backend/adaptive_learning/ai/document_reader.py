from pathlib import Path

from docx import Document

def extract_docx(path):
    document = Document(path)

    text = []

    for paragraph in document.paragraphs:
        content = paragraph.text.strip()

        if content:
            text.append(content)

    return "\n".join(text)

def extract_txt(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
    
def extract_pdf(path):
    raise NotImplementedError


def extract_pptx(path):
    raise NotImplementedError

def extract_text(path):
    extension = Path(path).suffix.lower()

    if extension == ".docx":
        return extract_docx(path)

    if extension == ".txt":
        return extract_txt(path)

    if extension == ".pdf":
        return extract_pdf(path)

    if extension == ".pptx":
        return extract_pptx(path)

    raise ValueError(f"Unsupported file type: {extension}")