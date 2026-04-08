from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

import env
from app.documents.core.llm import llm
from app.documents.core.prompt import document_summary_prompt


class SummarizationError(Exception):
    pass


class AISummarizationService:
    def __init__(self):
        logger.info("✅ AI Summarization Service initialized")

    def _truncate_text(
        self, text: str, max_length: int = env.MAX_SUMMARY_TEXT_LENGTH
    ) -> str:
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        logger.warning(
            f"⚠️  Text truncated from {len(text):,} to {max_length:,} characters"
        )
        return truncated

    def _build_summary_prompt(self, text: str, filename: str) -> str:
        return document_summary_prompt.DOCUMENT_SUMMARY_PROMPT.format(
            filename=filename, text=text
        )

    def summarize(self, text: str, filename: str) -> str:
        try:
            if not text or not text.strip():
                raise SummarizationError("Cannot summarize empty text")

            logger.info(
                f"🤖 Starting AI summarization for '{filename}' - Text length: {len(text):,} chars"
            )

            safe_text = self._truncate_text(text)

            prompt_content = self._build_summary_prompt(safe_text, filename)

            full_chain = llm | StrOutputParser()

            input_messages = [HumanMessage(content=prompt_content)]

            summary = full_chain.invoke(input_messages)

            if not summary:
                raise SummarizationError("LLM returned empty summary")

            return summary

        except Exception as e:
            error_msg = f"Failed to generate summary: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise SummarizationError(error_msg) from e


ai_summarizer = AISummarizationService()
