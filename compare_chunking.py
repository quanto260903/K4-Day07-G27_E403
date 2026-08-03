"""
compare_chunking.py — So sánh 3 kiểu chunking trên CÙNG 1 câu hỏi.

CÁCH DÙNG (dành cho người mới):
  1. Sửa biến QUERY bên dưới thành câu hỏi bạn muốn thử.
  2. Chạy:  python compare_chunking.py
  3. Đọc kết quả in ra terminal — xem giải thích ở cuối file README hoặc hỏi lại trợ lý.
"""
from __future__ import annotations

from ingest import build_knowledge_base
from main import _select_embedder, DEFAULT_DATA_DIR
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker

# 1) CÂU HỎI BẠN MUỐN THỬ — sửa dòng này, giữ nguyên dấu ngoặc kép.
QUERY = "Người mua được hoàn tiền trong trường hợp nào?"

# 2) BA CHIẾN LƯỢC CHUNKING SẼ SO SÁNH — không cần sửa, trừ khi muốn đổi chunk_size.
CHUNKERS = {
    "fixed_size": FixedSizeChunker(chunk_size=200),
    "by_sentences": SentenceChunker(),
    "recursive": RecursiveChunker(chunk_size=200),
}


def main() -> None:
    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"Backend nhúng đang dùng: {backend}")
    if backend == "mock embeddings fallback":
        print(
            "  -> Đây là embedder GIẢ LẬP: kết quả không phản ánh đúng ngữ nghĩa,\n"
            "     chỉ hợp để kiểm tra script chạy được. Xem hướng dẫn dùng embedder\n"
            "     thật (EMBEDDING_PROVIDER=local) ở cuối file này.\n"
        )
    print(f"Câu hỏi: {QUERY}\n")

    for name, chunker in CHUNKERS.items():
        # Với mỗi chiến lược: đọc lại toàn bộ tài liệu trong data/k4_ecommerce,
        # chia nhỏ (chunk) theo chiến lược này, rồi nạp vào một EmbeddingStore mới.
        store = build_knowledge_base(DEFAULT_DATA_DIR, embedding_fn=embedder, chunker=chunker)
        print(f"=== {name}  ({store.get_collection_size()} chunk trong store) ===")

        # Tìm 3 chunk giống câu hỏi nhất (top_k=3).
        for rank, result in enumerate(store.search(QUERY, top_k=3), start=1):
            preview = result["content"][:120].replace("\n", " ")
            doc_id = result["metadata"].get("doc_id")
            print(f"{rank}. score={result['score']:.3f}  tài liệu={doc_id}")
            print(f"   nội dung: {preview}...")
        print()


if __name__ == "__main__":
    main()

# ĐỂ SO SÁNH CÓ Ý NGHĨA THẬT (không dùng embedder giả lập):
#   pip install -r requirements-local.txt
#   (PowerShell)  $env:EMBEDDING_PROVIDER = "local"
#   (Bash)        export EMBEDDING_PROVIDER=local
#   rồi chạy lại: python compare_chunking.py
