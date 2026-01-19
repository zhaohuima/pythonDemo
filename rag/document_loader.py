"""
PDF Document Loader with Section Detection
Extracts text from PDF files and detects section/chapter headings.
"""

import os
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFLoader:
    """Load and extract text from PDF documents with section detection."""

    def __init__(self, documents_dir: str = "knowledge_base/documents"):
        """
        Initialize the PDF loader.

        Args:
            documents_dir: Directory containing PDF files
        """
        self.documents_dir = Path(documents_dir)
        self._section_patterns = [
            # Chapter patterns
            r'^(Chapter\s+\d+[:\.\s]+.+)$',
            r'^(第\s*[一二三四五六七八九十\d]+\s*章[:\.\s]*.*)$',
            # Section patterns
            r'^(\d+\.\s+.+)$',
            r'^(\d+\.\d+\s+.+)$',
            r'^(\d+\.\d+\.\d+\s+.+)$',
            # Heading patterns (all caps or title case with specific keywords)
            r'^(SECTION\s+\d+[:\.\s]+.+)$',
            r'^(Part\s+\d+[:\.\s]+.+)$',
            r'^(Appendix\s+[A-Z\d]+[:\.\s]*.*)$',
        ]

    def _detect_section(self, text: str, current_section: str) -> str:
        """
        Detect if text contains a section/chapter heading.

        Args:
            text: Text to check for section heading
            current_section: Current section name

        Returns:
            New section name if detected, otherwise current section
        """
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines of each page
            line = line.strip()
            if not line or len(line) > 100:  # Skip empty or very long lines
                continue

            for pattern in self._section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

        return current_section

    def load_pdf(self, file_path: str) -> List[Dict]:
        """
        Load a single PDF file and extract text with metadata.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of dictionaries with content and metadata
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.error("pypdf not installed. Run: pip install pypdf")
            return []

        documents = []
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return []

        try:
            reader = PdfReader(str(file_path))
            current_section = "Introduction"

            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                    if not text or not text.strip():
                        continue

                    # Detect section from page content
                    current_section = self._detect_section(text, current_section)

                    documents.append({
                        "content": text.strip(),
                        "metadata": {
                            "source": file_path.name,
                            "page": page_num,
                            "section": current_section
                        }
                    })
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num} from {file_path.name}: {e}")
                    continue

            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")

        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            return []

        return documents

    def load_all_documents(self) -> List[Dict]:
        """
        Load all PDF files from the documents directory.

        Returns:
            List of all documents with content and metadata
        """
        all_documents = []

        if not self.documents_dir.exists():
            logger.warning(f"Documents directory not found: {self.documents_dir}")
            return []

        pdf_files = list(self.documents_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {self.documents_dir}")
            return []

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            documents = self.load_pdf(str(pdf_file))
            all_documents.extend(documents)

        logger.info(f"Total pages loaded: {len(all_documents)}")
        return all_documents

    def get_document_list(self) -> List[Dict]:
        """
        Get list of PDF files in the documents directory.

        Returns:
            List of dictionaries with file info
        """
        if not self.documents_dir.exists():
            return []

        pdf_files = []
        for pdf_file in self.documents_dir.glob("*.pdf"):
            stat = pdf_file.stat()
            pdf_files.append({
                "filename": pdf_file.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": stat.st_mtime
            })

        return sorted(pdf_files, key=lambda x: x["filename"])
