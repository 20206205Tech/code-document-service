# from langchain_core.messages import HumanMessage
# from langchain_core.output_parsers import StrOutputParser
# from .llm import choose_llm

# RAG_PROMPT = """
# Bạn là một trợ lý ảo thông minh. Hãy trả lời câu hỏi dựa trên ngữ cảnh được cung cấp dưới đây.
# Nếu thông tin không có trong ngữ cảnh, hãy nói rằng bạn không biết, đừng tự bịa ra câu trả lời.

# NGỮ CẢNH:
# {context}

# CÂU HỎI:
# {question}

# TRẢ LỜI:
# """

# def generate_answer(question: str, context: str):
#     chain = choose_llm | StrOutputParser()

#     prompt = RAG_PROMPT.format(context=context, question=question)
#     response = chain.invoke([HumanMessage(content=prompt)])

#     return response
