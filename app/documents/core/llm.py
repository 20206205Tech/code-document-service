from langchain_cloudflare import ChatCloudflareWorkersAI

import env

llm = ChatCloudflareWorkersAI(
    account_id=env.CLOUDFLARE_ACCOUNT_ID,
    api_token=env.CLOUDFLARE_API_TOKEN,
    model="@cf/meta/llama-3.1-8b-instruct",
    temperature=0.1,
    max_tokens=4000,
)
