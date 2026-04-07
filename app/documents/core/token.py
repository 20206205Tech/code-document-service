import tiktoken
from loguru import logger

from utils.log_function import log_function

try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except Exception as e:
    logger.error(f"Không thể khởi tạo tokenizer: {e}")
    tokenizer = None


@log_function
def count_tokens(text: str) -> int:
    if not tokenizer:
        logger.warning("Tokenizer chưa được khởi tạo. Trả về 0.")
        return 0

    if not text:
        return 0

    try:
        token_count = len(tokenizer.encode(text))
        return token_count
    except Exception as e:
        logger.error(f"Lỗi khi đếm token: {e}")
        return 0


def estimate_tokens_from_chars(char_count: int) -> int:
    """
    Estimate token count from character count

    Rough estimate: 1 token ≈ 4 characters (for English)
    For Vietnamese, this ratio might be different

    Args:
        char_count: Number of characters

    Returns:
        Estimated token count
    """
    return char_count // 4


def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token limit

    Args:
        text: Input text
        max_tokens: Maximum allowed tokens

    Returns:
        Truncated text
    """
    if not tokenizer:
        # Fallback to character-based truncation
        estimated_chars = max_tokens * 4
        return text[:estimated_chars]

    try:
        tokens = tokenizer.encode(text)

        if len(tokens) <= max_tokens:
            return text

        # Truncate tokens and decode back
        truncated_tokens = tokens[:max_tokens]
        truncated_text = tokenizer.decode(truncated_tokens)

        logger.info(f"✂️  Text truncated from {len(tokens):,} to {max_tokens:,} tokens")

        return truncated_text

    except Exception as e:
        logger.error(f"❌ Error truncating text: {e}")
        # Fallback to character-based truncation
        estimated_chars = max_tokens * 4
        return text[:estimated_chars]
