from pathlib import Path

from docling.document_converter import DocumentConverter
from loguru import logger


class DocumentParserError(Exception):
    """Custom exception for document parsing errors"""


class DocumentParserService:
    """Service for parsing documents using Docling"""

    def __init__(self):
        """Initialize Docling converter"""
        self.converter = DocumentConverter()
        logger.info("✅ Document Parser Service initialized")

    def parse_document(self, file_path: Path) -> str:
        """
        Parse document and extract text content

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text in markdown format

        Raises:
            DocumentParserError: If parsing fails
        """
        try:
            if not file_path.exists():
                raise DocumentParserError(f"File not found: {file_path}")

            logger.info(f"📄 Parsing document: {file_path.name}")

            # Convert document using Docling
            result = self.converter.convert(str(file_path))

            # Export to markdown format
            extracted_text = result.document.export_to_markdown()

            if not extracted_text or not extracted_text.strip():
                raise DocumentParserError("No text could be extracted from document")

            text_length = len(extracted_text)
            logger.info(
                f"✅ Document parsed successfully - Extracted {text_length:,} characters"
            )

            return extracted_text

        except Exception as e:
            error_msg = f"Failed to parse document: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise DocumentParserError(error_msg) from e


# Singleton instance
document_parser = DocumentParserService()
