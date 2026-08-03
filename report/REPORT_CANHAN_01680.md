# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tô Minh Quân]
**Nhóm:** [G27]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding trỏ gần như cùng một hướng trong không gian nhiều chiều, tức là hai đoạn văn bản mang ý nghĩa/ngữ cảnh gần giống nhau, bất kể độ dài câu chữ khác nhau bao nhiêu.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Người mua có thể đổi trả sản phẩm bị lỗi trong 7 ngày."
- Câu B: "Khách hàng được hoàn hàng nếu sản phẩm nhận được không đúng mô tả, trong vòng một tuần."
- Tại sao tương đồng: Cả hai câu cùng nói về chủ đề chính sách đổi trả, cùng nhắc đến điều kiện (hàng lỗi/sai mô tả) và khung thời gian tương đương (7 ngày ≈ một tuần), chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Người bán phải khai báo đúng giá và tình trạng hàng hóa."
- Câu B: "Hôm nay thời tiết rất đẹp, thích hợp để đi dạo."
- Tại sao khác: Hai câu không chia sẻ chủ đề, thực thể hay ý định nào — một câu thuộc miền chính sách TMĐT, câu còn lại là nhận xét đời thường không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm đến *hướng* của vector (tức nội dung ngữ nghĩa) chứ không bị ảnh hưởng bởi *độ lớn* (magnitude) — vốn thường lệch theo độ dài văn bản hoặc cường độ từ ngữ. Nhờ vậy hai câu cùng ý nghĩa nhưng một câu dài/nhiều từ hơn vẫn cho điểm tương tự cao, trong khi Euclidean distance sẽ bị "phạt" chỉ vì chênh lệch độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính: mỗi bước trượt cửa sổ tiến `step = chunk_size - overlap = 500 - 50 = 450` ký tự. Số chunk = `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`.
> Đáp án: **23 chunks** (đã kiểm chứng lại bằng công thức trong `python -c`, khớp với cách `FixedSizeChunker` trượt cửa sổ trong `src/chunking.py`).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với `overlap=100`: `step = 500 - 100 = 400` → số chunk = `ceil((10000-100)/400) = ceil(9900/400) = ceil(24.75) = 25` chunks — tăng từ 23 lên 25. Overlap lớn hơn làm bước trượt nhỏ hơn nên cần nhiều chunk hơn để phủ hết văn bản, nhưng đổi lại giảm nguy cơ một câu/ý bị cắt đứt ngay tại ranh giới hai chunk, giúp truy xuất không bỏ sót ngữ cảnh nằm vắt qua điểm cắt.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+|(?<=\.)\n` để tách câu: lookbehind bắt các dấu kết câu (`.`, `!`, `?`) rồi tách tại khoảng trắng theo sau, cộng thêm trường hợp xuống dòng ngay sau dấu chấm. Sau khi tách, lọc bỏ chuỗi rỗng/khoảng trắng thừa (`strip`), rồi gom từng nhóm tối đa `max_sentences_per_chunk` câu lại thành một chunk bằng `" ".join(...)`. Edge case xử lý: văn bản rỗng trả về `[]`, và `max_sentences_per_chunk` được ép tối thiểu bằng 1 trong `__init__` để tránh vòng lặp vô nghĩa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy thử lần lượt các separator theo độ ưu tiên (`\n\n` → `\n` → `. ` → `" "` → `""`): tách văn bản theo separator hiện tại, phần nào vẫn còn dài hơn `chunk_size` thì gọi đệ quy tiếp với danh sách separator còn lại (`rest`). Base case là khi `len(current_text) <= chunk_size` (trả về nguyên văn bản làm 1 chunk) hoặc hết separator (`remaining_separators` rỗng, cắt cứng theo `chunk_size`). Sau khi có các mảnh nhỏ, thuật toán gộp (`merged`) các mảnh liền kề lại với nhau miễn tổng độ dài không vượt `chunk_size`, để tránh tạo ra quá nhiều chunk nhỏ vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `EmbeddingStore` thử khởi tạo ChromaDB trong `__init__`; nếu không có thư viện thì tự động rơi về danh sách dict trong bộ nhớ (`self._store`). `add_documents` embed nội dung từng `Document` qua `embedding_fn` rồi lưu (`collection.add(...)` với Chroma, hoặc append record với `id/doc_id/content/metadata/embedding` khi in-memory). `search` embed câu truy vấn, tính **tích vô hướng (dot product)** giữa vector truy vấn và từng vector đã lưu (hàm `_dot` tái dùng từ `chunking.py`, vì embedding đã được chuẩn hoá norm=1 nên dot product ≈ cosine similarity), sắp xếp giảm dần theo score và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` **lọc trước, tìm kiếm sau**: trước tiên lọc `self._store` theo `metadata_filter` (khớp toàn bộ các cặp key/value yêu cầu bằng `all(...)`), sau đó mới chạy lại `_search_records` (embed + dot product + sort) chỉ trên tập đã lọc — cách này giúp kết quả trả về luôn nằm trong đúng phạm vi metadata mong muốn thay vì lọc sau khi đã lấy top-k. `delete_document` xoá theo `doc_id`: với in-memory là lọc lại danh sách loại bỏ mọi record có `doc_id` khớp rồi so sánh kích thước trước/sau để trả về `True/False`; với Chroma dùng `collection.delete(where={"doc_id": doc_id})`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` gọi `store.search(question, top_k=top_k)` để lấy các chunk liên quan nhất, nối nội dung các chunk lại bằng `"\n\n".join(...)` làm `context`. Prompt được dựng theo khuôn cố định "Answer the question using only the context below." kèm khối `Context:` và `Question:` — ép mô hình chỉ trả lời dựa trên ngữ cảnh được truy xuất (grounding) thay vì bịa thông tin ngoài phạm vi tài liệu. Cuối cùng gọi `llm_fn(prompt)` (được tiêm từ bên ngoài qua constructor) để sinh câu trả lời, giúp lớp `KnowledgeBaseAgent` không phụ thuộc cứng vào một nhà cung cấp LLM cụ thể.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0 -- D:\AI Thuc chien\Day07\K4-Day07-G27_E403\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\AI Thuc chien\Day07\K4-Day07-G27_E403
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Tôi muốn đổi trả sản phẩm bị lỗi." | "Tôi cần hoàn trả hàng vì hàng không đúng mô tả." | cao | 0.0031 | Sai |
| 2 | "Tôi muốn đổi trả sản phẩm bị lỗi." | "Thời tiết hôm nay rất đẹp." | thấp | -0.0665 | Đúng (rất thấp, gần như không liên quan) |
| 3 | "Người bán phải cung cấp thông tin sản phẩm chính xác." | "Người bán cần khai báo đúng giá và tình trạng hàng." | cao | -0.0429 | Sai |
| 4 | "Người bán phải cung cấp thông tin sản phẩm chính xác." | "Tôi thích ăn phở bò vào buổi sáng." | thấp | -0.0921 | Đúng |
| 5 | "Chính sách đổi trả áp dụng trong 7 ngày." | "Quy định hoàn tiền trong vòng một tuần." | cao | 0.0248 | Sai |

> Điểm thực tế được đo bằng `compute_similarity()` với embedder mặc định của Lab (`_mock_embed`/`MockEmbedder`) — sinh vector giả lập từ **hash MD5** của chuỗi, không phải embedding ngữ nghĩa thật.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là 3/5 cặp tôi dự đoán "cao" (cặp 1, 3, 5 — đều là các cặp câu diễn đạt khác nhau nhưng cùng ý nghĩa) lại ra điểm gần 0 hoặc âm, không hề cao hơn các cặp hoàn toàn không liên quan. Điều này khẳng định đúng cảnh báo trong README: `MockEmbedder` băm chuỗi bằng MD5 rồi sinh vector giả-ngẫu-nhiên theo seed, nên hai câu *đồng nghĩa* nhưng khác ký tự vẫn cho ra vector gần như độc lập — mock embedder không hề mã hoá ý nghĩa, nó chỉ hữu ích để kiểm thử tính đúng đắn của pipeline (shape, sort, top_k...), còn muốn đánh giá chất lượng truy xuất ngữ nghĩa thật thì bắt buộc phải dùng `LocalEmbedder`/`OpenAIEmbedder` (đặt `EMBEDDING_PROVIDER=local`) như README yêu cầu cho Giai đoạn 2.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **Lưu ý:** Nhóm chưa chốt 5 câu hỏi đánh giá chính thức (`REPORT_NHOM.md` — Bài tập 3.2 vẫn để trống) và bộ tài liệu trong `data/k4_ecommerce/` hiện mới có 2 file mẫu khởi động (`returns-policy.md`, `seller-listing.md`, đúng như ghi chú "dữ liệu khởi động" trong 2 file đó), chưa đủ 5-10 tài liệu công khai theo yêu cầu. Bảng dưới là **demo nháp cá nhân** để kiểm chứng pipeline `ingest.py → SentenceChunker → EmbeddingStore → KnowledgeBaseAgent` chạy đúng đầu-cuối, dùng `_mock_embed` (embedder mặc định). Cần chạy lại bảng này với: (1) bộ 5 câu hỏi chính thức của nhóm, (2) bộ tài liệu đầy đủ, (3) `EMBEDDING_PROVIDER=local` — vì mock không phản ánh chất lượng ngữ nghĩa (xem mục 4).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua cần làm gì để đổi trả hàng bị lỗi? | Block metadata mẫu của `k4-seller-listing` ("Khối metadata phía trên là template mẫu cho K4...") | -0.0219 | Không | Lặp lại nguyên văn chunk không liên quan (block hướng dẫn metadata, không phải nội dung chính sách) |
| 2 | Người bán có trách nhiệm gì khi đăng bán sản phẩm? | `k4-returns-policy::chunk_1` — "Người mua cần gửi yêu cầu đổi trả trong thời hạn được nêu trên trang sản phẩm..." | 0.0765 | Không (nhầm sang chunk về đổi trả, không phải đăng bán) | Trích lại chunk sai chủ đề |
| 3 | Sản phẩm nào không được phép đăng bán? | Block metadata mẫu của `k4-seller-listing` | 0.1557 | Không | Lặp lại chunk hướng dẫn metadata, không có danh mục hàng cấm cụ thể (vì tài liệu mẫu chưa có nội dung này) |
| 4 | Thời hạn gửi yêu cầu đổi trả là bao lâu? | `k4-returns-policy::chunk_2` — "Người bán có trách nhiệm phản hồi theo quy trình của sàn..." | 0.2883 | Không (đúng doc nhưng sai chunk — chunk không nêu con số thời hạn cụ thể) | Không trả lời được thời hạn cụ thể |
| 5 | Ai chịu trách nhiệm xử lý yêu cầu đổi trả từ người mua? | `k4-returns-policy::chunk_1` — "Người mua cần gửi yêu cầu đổi trả..." | 0.156 | Một phần (đúng doc, đúng hướng nhưng không nêu rõ "ai xử lý") | Trả lời gần đúng chủ đề nhưng thiếu thông tin cụ thể |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0-1 / 5 (demo nháp, dữ liệu khởi động chưa có nội dung chính sách đầy đủ + dùng mock embedder — số liệu này **không phản ánh** chất lượng chiến lược thật, chỉ xác nhận pipeline chạy được)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Cần điền sau buổi so sánh trong nhóm (Bài tập 3.4) — hiện nhóm chưa tổ chức demo chéo. Ghi chú lại: điều rút ra ngay từ demo cá nhân là 2 tài liệu mẫu hiện có quá ngắn và còn nguyên câu hướng dẫn metadata lẫn vào nội dung, nên retriever "vớt nhầm" đoạn hướng dẫn thay vì nội dung chính sách — đây là lý do nhóm cần thay bằng nguồn thật trước khi benchmark có ý nghĩa.*

---

## Tự Đánh Giá (Phần Cá Nhân)

> Điểm dưới đây là đề xuất dựa trên mức độ hoàn thành khách quan (test pass, độ đầy đủ của từng mục) — nên tự rà lại trước khi nộp, đặc biệt mục 5 vì còn phụ thuộc dữ liệu/benchmark chính thức của nhóm chưa hoàn tất.

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 5 / 10 (demo dùng dữ liệu khởi động + mock embedder, cần chạy lại với dữ liệu/embedder/benchmark chính thức của nhóm) |
| **Tổng phần cá nhân** | **55 / 60** (tạm tính, chờ cập nhật mục 5 sau khi nhóm chốt dữ liệu và benchmark) |
