# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Chính sách mua bán trên hai sàn TMĐT lớn (Shopee, Tiki), bao quát đủ 5 khía cạnh của chủ đề K4: đổi trả, điều kiện người bán, thanh toán, giao hàng, và quyền riêng tư.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng và hoàn tiền (Shopee) | [help.shopee.vn/portal/4/article/77251](https://help.shopee.vn/portal/4/article/77251) | 2026-08-03 / hiệu lực từ 11/3/2026 | 2210 | `doc_id, title, source_url, retrieved_at, document_version, customer_role=buyer, category=returns, language=vi` |
| 2 | Quy định về đăng bán sản phẩm trên Shopee | [help.shopee.vn/portal/4/article/77246](https://help.shopee.vn/portal/4/article/77246-QUY-%C4%90%E1%BB%8ANH-V%E1%BB%80-%C4%90%C4%82NG-B%C3%81N-S%E1%BA%A2N-PH%E1%BA%A8M-TR%C3%8AN-SHOPEE) | 2026-08-03 / công bố 14/8/2024 | 3238 | `customer_role=seller, category=listing, language=vi` |
| 3 | Chính sách vận chuyển Shopee | [help.shopee.vn/portal/4/article/77250](https://help.shopee.vn/portal/4/article/77250-CH%C3%8DNH-S%C3%81CH-V%E1%BA%ACN-CHUY%E1%BB%82N-SHOPEE) | 2026-08-03 / cập nhật 20/3/2026 | 2721 | `customer_role=both, category=shipping, language=vi` |
| 4 | Phương thức thanh toán trên Shopee | [help.shopee.vn/portal/4/article/79198-](https://help.shopee.vn/portal/4/article/79198-) | 2026-08-03 / not-stated | 1138 | `customer_role=buyer, category=payment, language=vi` |
| 5 | Chính sách bảo mật thông tin cá nhân (Tiki) | [tiki.vn/thong-tin/privacy-policy](https://tiki.vn/thong-tin/privacy-policy) | 2026-08-03 / hiệu lực từ 11/11/2022 | 1606 | `customer_role=both, category=privacy, language=vi` |
| 6 | Quyền và nghĩa vụ của Nhà Bán và Tiki | [hocvien.tiki.vn/faq/quyen-va-nghia-vu-cua-nha-ban-va-tiki](https://hocvien.tiki.vn/faq/quyen-va-nghia-vu-cua-nha-ban-va-tiki/) | 2026-08-03 / not-stated | 1723 | `customer_role=seller, category=seller-obligations, language=vi` |

> 6 tài liệu (trong khoảng 5–10 theo yêu cầu), thay thế 2 file mẫu khởi động (`returns-policy.md`, `seller-listing.md`) vốn dùng `source_url` giả (`example.com`). Đầy đủ trong `data/k4_ecommerce/`, kiểm kê khớp `sources.csv`. Số ký tự đo bằng `ingest.load_documents()` trên phần nội dung sau front matter.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng (trang trợ giúp chính thức Shopee, trang chính sách/học viện chính thức Tiki) và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | string (enum) | `buyer`, `seller`, `both` | Cho phép `search_with_filter()` thu hẹp kết quả về đúng đối tượng hỏi (ví dụ câu hỏi của người bán không nên trả về chính sách chỉ dành cho người mua). |
| `category` | string | `returns`, `listing`, `shipping`, `payment`, `privacy`, `seller-obligations` | Phân biệt chủ đề con trong miền TMĐT, giúp lọc trước khi tìm kiếm ngữ nghĩa khi câu hỏi đã rõ chủ đề (vd. chỉ tìm trong `category=shipping`). |
| `source_url` / `retrieved_at` / `document_version` | string | `https://help.shopee.vn/...`, `2026-08-03`, `"cập nhật 20/3/2026"` | Truy vết nguồn gốc và độ mới của thông tin — cần thiết khi chính sách TMĐT thay đổi thường xuyên, giúp phát hiện câu trả lời dựa trên bản chính sách đã lỗi thời. |
| `language` | string | `vi` | Lọc theo ngôn ngữ nếu sau này corpus mở rộng thêm tài liệu tiếng Anh. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `shopee-return-refund-policy` (2210 ký tự) | FixedSizeChunker (`fixed_size`, size=200) | 15 | 194.0 | Không — cửa sổ trượt cắt giữa từ/câu (vd. `"...Sản phẩm là hàng"` bị đứt ngay giữa cụm "hàng nhái/hàng giả") |
| `shopee-return-refund-policy` (2210 ký tự) | SentenceChunker (`by_sentences`) | 8 | 274.8 | Có — mỗi chunk là các câu trọn vẹn, không bị cắt giữa câu |
| `shopee-return-refund-policy` (2210 ký tự) | RecursiveChunker (`recursive`, size=200) | 15 | 146.0 | Có phần — ưu tiên tách theo `\n\n`/`\n` trước, ít cắt giữa câu hơn fixed nhưng chunk ngắn hơn nên đôi khi tách ý liệt kê (gạch đầu dòng) ra khỏi câu dẫn |
| `shopee-payment-methods` (1138 ký tự) | FixedSizeChunker (`fixed_size`, size=200) | 8 | 186.0 | Không — cắt giữa mục liệt kê (vd. đứt ngay giữa tên "Thẻ tín dụng/ghi nợ") |
| `shopee-payment-methods` (1138 ký tự) | SentenceChunker (`by_sentences`) | 7 | 161.7 | Có — mỗi hình thức thanh toán rơi trọn trong 1-2 câu, không bị đứt |
| `shopee-payment-methods` (1138 ký tự) | RecursiveChunker (`recursive`, size=200) | 8 | 141.4 | Có — tách theo dòng nên mỗi mục liệt kê (`1.`, `2.`...) thường trọn vẹn trong 1 chunk |
| `tiki-privacy-policy` (1606 ký tự) | FixedSizeChunker (`fixed_size`, size=200) | 11 | 191.5 | Không — cắt xuyên qua ranh giới các mục "Mục đích thu thập" / "Chia sẻ thông tin" |
| `tiki-privacy-policy` (1606 ký tự) | SentenceChunker (`by_sentences`) | 3 | 533.0 | Có phần — câu trọn vẹn nhưng chunk quá dài (gộp cả mục "Mục đích thu thập" và "Chia sẻ thông tin" vào 1 chunk), khó xác định phần liên quan khi truy xuất |
| `tiki-privacy-policy` (1606 ký tự) | RecursiveChunker (`recursive`, size=200) | 11 | 144.5 | Có — tách theo heading `##` trước, chunk đầu chỉ chứa `"## Mục đích thu thập"`, giữ ranh giới chủ đề rõ ràng |

> **Nhận xét chung:** `FixedSizeChunker` luôn cho chunk đều đặn về kích thước nhưng thường xuyên cắt giữa từ/câu/mục liệt kê — kém nhất về giữ ngữ cảnh. `SentenceChunker` giữ câu trọn vẹn nhưng độ dài chunk phụ thuộc hoàn toàn vào độ dài câu gốc (dao động 161.7–533.0 ký tự trong 3 tài liệu trên), có nguy cơ gộp nhiều chủ đề vào 1 chunk nếu văn bản có câu dài (như `tiki-privacy-policy`). `RecursiveChunker` cân bằng tốt nhất cho corpus dạng chính sách/FAQ có cấu trúc heading + liệt kê: ưu tiên tách theo đoạn/dòng trước khi cắt cứng theo `chunk_size`, nên vừa giữ được ranh giới chủ đề (heading, mục liệt kê) vừa kiểm soát được độ dài chunk (141.4–194.0 ký tự — ổn định hơn SentenceChunker).

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Người mua cần gửi yêu cầu trả hàng trong bao lâu sau khi nhận hàng thông thường (không phải thực phẩm tươi/đông lạnh)? | 15 (mười lăm) ngày kể từ lúc đơn hàng được cập nhật giao hàng thành công. | `shopee-return-refund-policy` — mục "Thời hạn gửi yêu cầu" |
| 2 | *(cần `metadata_filter={"customer_role": "seller"}`)* Người bán không được đăng bán những loại sản phẩm nào theo quy định của Shopee? | Sản phẩm phản động/bài xích tôn giáo/khiêu dâm/bạo lực; liên quan ma túy; quảng cáo thuốc lá/rượu/cần sa; văn hóa đồi trụy; tài liệu bí mật quốc gia/cá nhân; bộ phận cơ thể người; động vật hoang dã (ngà voi, sừng tê giác); nội dung phân biệt chủng tộc; hàng vi phạm sở hữu trí tuệ; và các mặt hàng khác trong danh sách cấm của Shopee. | `shopee-seller-listing-rules` — mục "Danh mục sản phẩm bị cấm đăng bán" |
| 3 | Shopee hỗ trợ những phương thức thanh toán nào cho người mua? | 10 hình thức: Ví ShopeePay, thẻ tín dụng/ghi nợ, trả góp bằng thẻ tín dụng, thanh toán QR, ứng dụng ngân hàng, thẻ nội địa NAPAS, Apple Pay, Google Pay, thanh toán khi nhận hàng (COD), và SPayLater. | `shopee-payment-methods` — toàn bộ tài liệu |
| 4 | Nếu hàng bị hư hỏng khi vận chuyển nhưng không phải lỗi của người mua, ai chịu chi phí vận chuyển hoàn trả? | Người bán chịu chi phí, áp dụng khi Shopee chấp thuận yêu cầu không do lỗi người mua, giao hàng không thành công, hoặc Shopee quyết định hoàn tiền ngay mà không cần trả hàng. | `shopee-return-refund-policy` — mục "Chi phí vận chuyển hoàn trả" |
| 5 | Tiki lưu trữ thông tin cá nhân của khách hàng trong bao lâu? | Cho đến khi khách hàng có yêu cầu hủy bỏ, hoặc khách hàng tự đăng nhập và xóa tài khoản; dữ liệu luôn được bảo mật trên máy chủ của Tiki. | `tiki-privacy-policy` — mục "Thời gian lưu trữ" |

> Cả 5 gold answer đều trích trực tiếp từ nội dung 6 tài liệu trong `data/k4_ecommerce/` (đúng quy tắc K4: không dùng chính sách ngoài corpus để chấm retrieval). Câu 2 bắt buộc dùng `search_with_filter(query, metadata_filter={"customer_role": "seller"})` vì nếu tìm không lọc, câu hỏi dễ bị nhiễu bởi các chunk về chính sách trả hàng dành cho người mua (cùng nói về "sản phẩm", "quy định") trong `shopee-return-refund-policy`.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
