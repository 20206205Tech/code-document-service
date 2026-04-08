from pathlib import Path

from docling.document_converter import DocumentConverter
from loguru import logger


class DocumentParserError(Exception):
    pass


class DocumentParserService:
    def __init__(self):
        self.converter = DocumentConverter()
        logger.info("✅ Document Parser Service initialized")

    def parse_document(self, file_path: Path) -> str:
        try:
            if not file_path.exists():
                raise DocumentParserError(f"File not found: {file_path}")

            logger.info(f"📄 Parsing document: {file_path.name}")

            result = self.converter.convert(str(file_path))

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


document_parser = DocumentParserService()
