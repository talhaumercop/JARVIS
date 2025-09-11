import os
from typing import Optional

from dotenv import load_dotenv

# File format readers
import docx
import PyPDF2

from agents import function_tool  # if you are using MCP/OpenAI SDK

load_dotenv()

@function_tool
def extract_text(file_path: str) -> Optional[str]:
    """
    Extracts and returns text from a document.
    Supported formats: .txt, .md, .docx, .pdf
    """
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        elif ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        elif ext == ".pdf":
            text = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)

        else:
            return f"⚠️ Unsupported file format: {ext}"

    except Exception as e:
        return f"❌ Error reading file {file_path}: {e}"


