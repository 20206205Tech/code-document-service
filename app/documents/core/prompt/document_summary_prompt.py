DOCUMENT_SUMMARY_PROMPT = """
Bạn là một chuyên gia phân tích tài liệu. Hãy tóm tắt tài liệu: "{filename}"

YÊU CẦU QUAN TRỌNG:
- BẮT BUỘC sử dụng 100% Tiếng Việt chuẩn xác, đúng ngữ pháp.
- Trình bày súc tích, đầy đủ ý nhưng KHÔNG viết quá lê thê.
- Tóm tắt các ý chính và thông tin quan trọng nhất.
- Giữ nguyên các số liệu, ngày tháng, tên riêng quan trọng.
- Cấu trúc tóm tắt rõ ràng, mạch lạc bằng các dấu đầu dòng (bullet points) nếu cần.

NỘI DUNG TÀI LIỆU:
{text}

TÓM TẮT BẰNG TIẾNG VIỆT:
""".strip()
