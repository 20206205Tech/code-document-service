DOCUMENT_SUMMARY_PROMPT = """
Bạn là chuyên gia phân tích tài liệu. Nhiệm vụ của bạn là tóm tắt tài liệu dưới đây một cách chi tiết, chính xác và dễ hiểu.

YÊU CẦU:
- Tóm tắt các ý chính và thông tin quan trọng nhất
- Giữ nguyên các số liệu, ngày tháng, tên riêng quan trọng
- Cấu trúc tóm tắt rõ ràng, mạch lạc
- Sử dụng ngôn ngữ Tiếng Việt
- Độ dài: 200-500 từ tùy theo nội dung

NỘI DUNG TÀI LIỆU:
{text}

TÓM TẮT:
""".strip()
