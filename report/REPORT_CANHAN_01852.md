# Báo Cáo Cá Nhân - Lab 7: Embedding & Vector Store

**Họ tên:** Lê Khả Chính   
**Nhóm:** G27  
**Ngày:** 03/08/2026

---

## 1. Khởi động (Warm-up)

### Độ tương tự Cosine
Độ tương tự cosine cao nghĩa là hai đoạn văn bản có hướng vector gần giống nhau, vì vậy chúng có ý nghĩa hoặc chủ đề gần nhau. Nếu cosine similarity cao, hai câu thường nói về cùng một vấn đề hoặc cùng một khía cạnh của chủ đề. Ngược lại, cosine thấp cho thấy hai câu khác nhau về chủ đề hoặc không liên quan.

Ví dụ:
- Cao: “Khách hàng có thể đổi trả sản phẩm bị lỗi.” và “Người mua được hoàn tiền nếu sản phẩm không đúng mô tả.”
- Thấp: “Người bán cần viết mô tả sản phẩm rõ ràng.” và “Mạng neural có nhiều lớp học.”

Cosine similarity thường được dùng hơn Euclidean distance cho text embeddings vì nó đo mức độ giống nhau về hướng vector, phù hợp hơn khi so sánh ý nghĩa văn bản, trong khi khoảng cách Euclid bị ảnh hưởng bởi độ dài vector.

### Bài toán Chunking
Với tài liệu dài 10,000 ký tự, chunk_size = 500, overlap = 50:

$$
\text{số chunk} = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil 22.11 \right\rceil = 23
$$

Nếu overlap tăng lên 100 thì số chunk là:

$$
\left\lceil \frac{10000 - 100}{500 - 100} \right\rceil = \left\lceil 24.75 \right\rceil = 25
$$

Overlap lớn hơn làm tăng số chunk, nhưng giúp giữ ngữ cảnh tốt hơn ở các ranh giới giữa các chunk.

---

## 2. Hướng tiếp cận của tôi

Trong phần lập trình, tôi tập trung hoàn thành các chức năng cốt lõi trong các module:
- `SentenceChunker`: chia văn bản theo câu và gom thành chunk
- `RecursiveChunker`: chia theo các separator theo ưu tiên
- `compute_similarity`: tính cosine similarity và xử lý trường hợp vector zero
- `EmbeddingStore`: lưu embeddings, tìm kiếm, lọc metadata và xóa document
- `KnowledgeBaseAgent`: truy xuất context và tạo prompt cho RAG

Mục tiêu của tôi là làm cho hệ thống vừa chạy đúng, vừa có thể dùng để thực hiện retrieval cơ bản trên dữ liệu văn bản.

---

## 3. Hoàn thiện code

Tôi đã chạy kiểm thử bằng lệnh:

```bash
pytest tests/ -v
```

Kết quả:
- 42 tests passed
- 0 failed

Như vậy, các chức năng cốt lõi như chunking, similarity, search, filter và agent đã hoạt động đúng.

---

## 4. Dự đoán độ tương tự

| Cặp câu | Dự đoán | Kết quả thực tế |
|---|---|---|
| “Python programming tutorial” vs “Python coding guide” | Cao | Cao |
| “Return policy for damaged product” vs “Refund and exchange rules” | Cao | Cao |
| “Seller listing requirements” vs “How to publish a product for sale” | Cao | Thấp/không ổn định |
| “Payment security rules” vs “Brown bears live in forests” | Thấp | Thấp |
| “Shipping time estimate” vs “Neural networks in deep learning” | Thấp | Thấp |

Điều đáng ngạc nhiên nhất là một số cặp câu có ý nghĩa tương tự nhưng lại không cho điểm similarity cao khi dùng mock embedding. Điều này cho thấy mock embedding phù hợp để kiểm tra logic code hơn là đánh giá retrieval thực tế.

---

## 5. Kết quả truy xuất của tôi

Tôi đã thử chạy retrieval trên dữ liệu trong `data/k4_ecommerce` bằng chiến lược chunking cố định. Kết quả cho thấy:
- Một số câu hỏi trả về chunk liên quan ở top-3
- Nhưng vẫn có trường hợp retrieval bị lệch do chunk quá dài hoặc thiếu metadata rõ ràng

Nhận xét:
- Chunking ảnh hưởng lớn đến chất lượng truy xuất
- Metadata giúp cải thiện độ chính xác khi lọc kết quả
- Nếu dùng embedding chất lượng tốt hơn, kết quả retrieval sẽ tốt hơn đáng kể

---

## 6. Tự đánh giá

| Tiêu chí | Điểm |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 10/10 |
| Hoàn thiện code | 30/30 |
| Dự đoán độ tương tự | 4/5 |
| Kết quả truy xuất | 6/10 |
| **Tổng** | **55/60** |
