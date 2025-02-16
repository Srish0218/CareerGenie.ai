import fitz  # PyMuPDF
import docx


def extract_resume_text(file_obj, file_extension):
    """Extracts text from a resume file (PDF/DOCX) using fitz and python-docx."""

    if file_extension == "pdf":
        text = ""
        pdf_document = fitz.open(stream=file_obj, filetype="pdf")  # Read PDF from BytesIO
        for page in pdf_document:
            text += page.get_text("text") + "\n"
        return text.strip()

    elif file_extension == "docx":
        text = []
        doc = docx.Document(file_obj)  # Read DOCX from BytesIO
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text).strip()

    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
