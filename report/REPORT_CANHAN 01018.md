# Báo Cáo Cá Nhân - Lab 7: Embedding & Vector Store

**Họ tên:** Sái Hồng Anh  
**Nhóm:** G27  
**Ngày:** 03/08/2026

---

## 1. Khởi động (Warm-up)

### Độ tương tự Cosine

**Độ tương tự cosine cao nghĩa là gì?**  
Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần giống nhau, tức là hai đoạn văn bản có nội dung hoặc ý nghĩa gần nhau trong không gian biểu diễn. Với text embeddings, điều này thường cho thấy hai câu đang nói về cùng chủ đề, cùng ý định hoặc có quan hệ ngữ nghĩa mạnh.

**Ví dụ có độ tương tự cao:**
- Câu A: "Khách hàng có thể đổi trả sản phẩm bị lỗi."
- Câu B: "Người mua được hoàn trả hàng nếu sản phẩm không đúng mô tả."
- Tại sao tương đồng: Cả hai câu đều nói về chính sách đổi trả/hoàn trả khi sản phẩm có vấn đề.

**Ví dụ có độ tương tự thấp:**
- Câu A: "Người bán cần cung cấp mô tả sản phẩm chính xác."
- Câu B: "Mạng neural có nhiều lớp để học đặc trưng dữ liệu."
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau: thương mại điện tử và học sâu.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector hơn là độ lớn, nên phù hợp khi cần so sánh ý nghĩa văn bản. Với embeddings, hai câu có thể có vector dài/ngắn khác nhau nhưng vẫn cùng hướng ngữ nghĩa, vì vậy cosine thường ổn định hơn khoảng cách Euclid.

### Bài toán tính toán Chunking

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Công thức:

```text
số chunk = ceil((độ_dài - overlap) / (chunk_size - overlap))
         = ceil((10000 - 50) / (500 - 50))
         = ceil(9950 / 450)
         = ceil(22.11)
         = 23 chunks
```

**Nếu overlap tăng lên 100 thì thay đổi thế nào?**  
Khi `overlap=100`, bước nhảy là `500 - 100 = 400`, nên số chunk là `ceil((10000 - 100) / 400) = ceil(24.75) = 25 chunks`. Overlap lớn hơn tạo nhiều chunk hơn và tốn thêm lưu trữ/tính toán, nhưng giúp giữ ngữ cảnh ở ranh giới giữa các chunk tốt hơn.

---

## 2. Hướng tiếp cận của tôi

### Các hàm chia nhỏ

**`SentenceChunker.chunk`**  
Tôi dùng regex `(?<=[.!?])(?:\s+|\n+)` để tách câu sau các dấu kết thúc câu như `.`, `!`, `?`, rồi loại bỏ khoảng trắng thừa. Sau đó các câu được gom theo `max_sentences_per_chunk`; nếu input rỗng thì trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`**  
Tôi triển khai chiến lược chia đệ quy theo thứ tự separator: đoạn văn, dòng, câu, khoảng trắng, rồi fallback theo ký tự. Base case là khi đoạn hiện tại đã nhỏ hơn hoặc bằng `chunk_size`; nếu không còn separator thì cắt cứng theo kích thước chunk để đảm bảo không bị lặp vô hạn.

### Lớp `EmbeddingStore`

**`add_documents` + `search`**  
Mỗi `Document` được chuyển thành record gồm `id`, `content`, `metadata`, và `embedding`. Khi tìm kiếm, truy vấn được embed rồi so sánh với từng record bằng cosine similarity, sau đó kết quả được sắp xếp giảm dần theo `score` và trả về tối đa `top_k`.

**`search_with_filter` + `delete_document`**  
Tôi lọc metadata trước khi search để giảm tập ứng viên, ví dụ lọc theo `department`, `lang`, hoặc `doc_id`. Với `delete_document`, tôi xóa tất cả record có `metadata["doc_id"]` hoặc `id` trùng với tài liệu cần xóa, rồi trả về `True` nếu kích thước store giảm.

### Tác tử `KnowledgeBaseAgent`

**`answer`**  
Agent truy xuất top-k chunk liên quan từ `EmbeddingStore`, ghép nội dung thành phần `Context`, rồi tạo prompt gồm context, câu hỏi và nhãn `Answer:`. Sau đó agent gọi `llm_fn(prompt)` để sinh câu trả lời theo mô hình RAG đơn giản.

---

## 3. Hoàn thiện code

### Kết quả kiểm thử

Lệnh đã chạy:

```text
pytest tests/ -v
```

Kết quả:

```text
collected 42 items
42 passed in 0.05s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Các nhóm chức năng đã pass gồm: project structure, chunkers, embedding store, knowledge base agent, cosine similarity, comparator, metadata filter, và delete document.

---

## 4. Dự đoán độ tương tự

Embedder dùng để lấy điểm thực tế: `_mock_embed` trong `src.embeddings`. Vì đây là mock embedder dùng cho unit test, điểm số không phản ánh hoàn toàn ngữ nghĩa thật.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python programming tutorial | Python coding guide | cao | 0.2239 | Đúng |
| 2 | Return policy for damaged product | Refund and exchange rules | cao | 0.1042 | Khá đúng |
| 3 | Seller listing requirements | How to publish a product for sale | cao | -0.1568 | Sai |
| 4 | Payment security rules | Brown bears live in forests | thấp | 0.0855 | Khá đúng |
| 5 | Shipping time estimate | Neural networks in deep learning | thấp | -0.0936 | Đúng |

**Kết quả bất ngờ nhất:**  
Cặp 3 đáng lẽ gần nhau về ý nghĩa vì đều nói về yêu cầu đăng bán sản phẩm, nhưng điểm mock embedding lại âm. Điều này cho thấy mock embeddings chỉ phù hợp để kiểm tra code chạy đúng, còn đánh giá chất lượng truy xuất thực tế nên dùng local embedding hoặc OpenAI embedding.

---

## 5. Kết quả truy xuất của tôi

Dữ liệu dùng để chạy cá nhân: `data/k4_ecommerce`  
Chunker dùng: `FixedSizeChunker(chunk_size=500, overlap=50)`  
Embedder dùng: `_mock_embed`  
Số chunk đã nạp: 3

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Relevant? | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is the return window for eligible products? | Chunk từ `k4-returns-policy`, nói về mô tả hàng hóa và trách nhiệm phản hồi theo quy trình sàn | 0.0965 | Có một phần | Agent dùng context chính sách đổi trả để trả lời theo phần liên quan có trong tài liệu |
| 2 | What products are not eligible for return? | Chunk từ `k4-seller-listing`, phần template metadata và đăng bán sản phẩm | 0.0612 | Chưa tốt | Agent có thể bị lệch vì top-1 không trực tiếp nói về ngoại lệ đổi trả |
| 3 | What information must a seller provide when creating a listing? | Chunk từ `k4-returns-policy`, nói về đổi trả và trách nhiệm người bán | 0.0446 | Chưa tốt | Agent thiếu grounding đúng về thông tin đăng bán |
| 4 | What happens if a seller lists prohibited or misleading products? | Chunk từ `k4-returns-policy`, có nhắc metadata và category | 0.0883 | Có một phần | Agent có context liên quan đến chính sách nhưng chưa phải chunk seller listing tốt nhất |
| 5 | Which metadata category should be used for seller listing rules? | Chunk từ `k4-returns-policy`, có nhắc category trong metadata | -0.0016 | Có một phần | Agent có thể trả lời ở mức khái quát dựa trên metadata, nhưng score thấp |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Nhận xét:**  
Code retrieval đã hoạt động đúng, nhưng chất lượng truy xuất với `_mock_embed` chưa ổn định về mặt ngữ nghĩa. Với đánh giá thật, nên chuyển sang `EMBEDDING_PROVIDER=local` hoặc một embedding model tốt hơn cho tiếng Việt/chính sách thương mại điện tử, đồng thời mở rộng dữ liệu nhóm từ 2 tài liệu mẫu lên 5-10 tài liệu công khai đúng yêu cầu.

**Điều hay nhất tôi học được:**  
Chunking, metadata và embedding backend ảnh hưởng trực tiếp đến chất lượng RAG. Unit test giúp xác nhận hệ thống đúng về mặt kỹ thuật, nhưng đánh giá retrieval thật cần dữ liệu sạch, câu hỏi chuẩn, và embedding có khả năng hiểu ngữ nghĩa.

---

## Tự Đánh Giá

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation - tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |
