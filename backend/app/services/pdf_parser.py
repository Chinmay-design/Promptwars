import os
import re
from typing import Dict, Any, List
import pypdf

class DocumentParserService:
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parses PDF, Markdown, or Code file and returns extracted text sections and metadata.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocumentParserService._parse_pdf(file_path)
        elif ext in [".md", ".txt", ".markdown"]:
            return DocumentParserService._parse_text(file_path)
        elif ext in [".py", ".r", ".jl", ".ipynb", ".sh"]:
            return DocumentParserService._parse_code(file_path)
        else:
            return DocumentParserService._parse_text(file_path)

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        full_text = ""
        page_count = 0
        try:
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            for page in reader.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
        except Exception as e:
            full_text = f"Error reading PDF: {str(e)}"

        return DocumentParserService._structure_extracted_content(full_text, page_count=page_count, file_type="pdf")

    @staticmethod
    def _parse_text(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading text file: {str(e)}"
        return DocumentParserService._structure_extracted_content(content, page_count=1, file_type="markdown")

    @staticmethod
    def _parse_code(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading code file: {str(e)}"
        
        # Extract docstrings and comments as description
        comments = re.findall(r"(?:#|//|/\*|'''|\"\"\")(.*?)(?:\*/|'''|\"\"\"|\n)", content, re.DOTALL)
        comment_summary = "\n".join([c.strip() for c in comments if len(c.strip()) > 5])
        
        return {
            "full_text": content,
            "summary_text": comment_summary or content[:2000],
            "page_count": 1,
            "file_type": "code",
            "sections": {
                "header": content[:500],
                "body": content,
                "comments": comment_summary
            }
        }

    @staticmethod
    def _structure_extracted_content(text: str, page_count: int, file_type: str) -> Dict[str, Any]:
        clean_text = re.sub(r"\s+", " ", text).strip()
        
        # Simple section segmenter
        abstract_match = re.search(r"(?:abstract|summary)\s*[:\-—]?\s*(.*?)(?:introduction|background|1\.|1\s+[A-Z])", clean_text, re.IGNORECASE)
        abstract = abstract_match.group(1).strip() if abstract_match else clean_text[:600]
        
        # Try to find methods/dataset sections
        methods_match = re.search(r"(?:methods|methodology|experimental setup)\s*[:\-—]?\s*(.*?)(?:results|evaluation|discussion)", clean_text, re.IGNORECASE)
        methods_text = methods_match.group(1).strip() if methods_match else ""

        return {
            "full_text": clean_text,
            "summary_text": clean_text[:3000],
            "abstract": abstract[:1500],
            "methods_text": methods_text[:2000],
            "page_count": page_count,
            "file_type": file_type,
            "char_count": len(clean_text)
        }

pdf_parser = DocumentParserService()
