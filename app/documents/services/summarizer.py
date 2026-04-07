from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

import env
from app.documents.core.llm import choose_llm
from app.documents.core.prompt import document_summary_prompt


class SummarizationError(Exception):
    """Custom exception for summarization errors"""


class AISummarizationService:
    """Service for AI-powered document summarization"""

    def __init__(self):
        """Initialize summarization service"""
        logger.info("✅ AI Summarization Service initialized")

    def _truncate_text(
        self, text: str, max_length: int = env.MAX_SUMMARY_TEXT_LENGTH
    ) -> str:
        """
        Truncate text to prevent token limit issues

        Args:
            text: Text to truncate
            max_length: Maximum character length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        logger.warning(
            f"⚠️  Text truncated from {len(text):,} to {max_length:,} characters"
        )
        return truncated

    def _build_summary_prompt(self, text: str) -> str:
        # return document_summary_prompt.DOCUMENT_SUMMARY_PROMPT
        return document_summary_prompt.DOCUMENT_SUMMARY_PROMPT.format(text=text)

    def summarize(self, text: str) -> str:
        """
        Summarize document text using AI

        Args:
            text: Extracted document text

        Returns:
            AI-generated summary

        Raises:
            SummarizationError: If summarization fails
        """
        try:
            if not text or not text.strip():
                raise SummarizationError("Cannot summarize empty text")

            logger.info(
                f"🤖 Starting AI summarization - Text length: {len(text):,} chars"
            )

            # Truncate text if too long
            safe_text = self._truncate_text(text)
            prompt_content = self._build_summary_prompt(safe_text)

            # TẠO CHUỖI XỬ LÝ (PIPE)
            # Dữ liệu đi vào choose_llm_router -> Trả về LLM phù hợp -> LLM thực thi prompt
            full_chain = choose_llm | StrOutputParser()

            logger.info("⏳ Executing LangChain Pipe...")

            # Gửi input vào đầu chuỗi
            # Vì choose_llm_router bên llm.py đang xử lý list message:
            input_messages = [HumanMessage(content=prompt_content)]

            # Chỉ gọi .invoke() MỘT LẦN duy nhất cho cả chuỗi
            summary = full_chain.invoke(input_messages)

            if not summary:
                raise SummarizationError("LLM returned empty summary")

            logger.info(
                f"✅ Summarization completed - Summary length: {len(summary):,} chars"
            )
            return summary

        except Exception as e:
            error_msg = f"Failed to generate summary: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SummarizationError(error_msg) from e


# Singleton instance
ai_summarizer = AISummarizationService()
