from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_core.runnables import chain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from loguru import logger

import env
from app.documents.core.token import count_tokens
from utils.log_function import log_function

nvidia_llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    api_key=env.NVIDIA_API_KEY,
    temperature=0.0,
    max_tokens=2048,
)

cloudflare_llm = ChatCloudflareWorkersAI(
    account_id=env.CLOUDFLARE_ACCOUNT_ID,
    api_token=env.CLOUDFLARE_API_TOKEN,
    model="@cf/meta/llama-3-8b-instruct",
    temperature=0.0,
    max_tokens=2048,
)


@chain
@log_function
def choose_llm(input_data):
    if isinstance(input_data, list):
        prompt_text = "\n".join(
            [msg.content for msg in input_data if hasattr(msg, "content")]
        )
    else:
        prompt_text = input_data.to_string()

    token_count = count_tokens(prompt_text)

    logger.info(f"Số lượng token (ước tính local): {token_count}")

    if token_count > env.CHOOSE_LLM_TOKEN_COUNT_THRESHOLD:
        logger.debug("Chọn NVIDIA")
        return nvidia_llm

    logger.debug("Chọn Cloudflare AI")
    return cloudflare_llm
