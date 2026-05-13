"""
RAG Corpus Ingestion Script.
Chunks text files by semantic paragraphs and stores them in ChromaDB with embeddings.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from pathlib import Path

def chunk_text_by_semantic_paragraphs(text: str, min_length: int = 50, max_chunk_size: int = 2000) -> list[str]:
    """
    按语义段落切分，合并短段落，限制最大块大小
    
    Args:
        text: 原始文本
        min_length: 最小段落长度（跳过太短的段落）
        max_chunk_size: 最大块大小（合并后超过此长度则切分）
    
    Returns:
        语义段落列表
    """
    # 1. 按双换行切分段落
    raw_paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) >= min_length]
    
    # 2. 合并相邻短段落，直到达到合理大小
    chunks = []
    current_chunk = ""
    
    for para in raw_paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            # 如果当前块不为空，添加分隔符
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # 保存当前块
            if current_chunk:
                chunks.append(current_chunk)
            # 开始新块
            current_chunk = para
    
    # 保存最后一个块
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def ingest_corpus(corpus_dir: str, collection_name: str, db_path: str = "./chroma_data"):
    """将语料库分块并存入 ChromaDB"""
    print(f"📂 Scanning corpus directory: {corpus_dir}")
    
    # 初始化 ChromaDB 客户端（持久化到本地磁盘）
    # 如果集合已存在，先删除再重建
    client = chromadb.PersistentClient(path=db_path)
    try:
        client.delete_collection(collection_name)
    except ValueError:
        pass  # 集合不存在，忽略
    
    collection = client.get_or_create_collection(collection_name)
    
    total_chunks = 0
    
    # 遍历所有文本文件
    corpus_path = Path(corpus_dir)
    text_files = list(corpus_path.rglob("*.txt"))
    
    if not text_files:
        print("⚠️  No .txt files found in corpus directory.")
        return
    
    for file_path in text_files:
        text = file_path.read_text(encoding='utf-8')
        chunks = chunk_text_by_semantic_paragraphs(text)
        
        if not chunks:
            continue
        
        # Determine metadata weight based on filename
        fname = file_path.name.lower()
        if "wisdom_compilation" in fname or "missing_years_highlights" in fname:
            weight = 2.0
        else:
            weight = 1.0
            
        # 生成文档 ID
        ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path.name, "file_path": str(file_path), "weight": weight} for _ in chunks]
        
        # 添加到 ChromaDB（ChromaDB 会自动用内置模型生成 embedding）
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        total_chunks += len(chunks)
        weight_label = "weighted(2.0)" if weight > 1.0 else "normal(1.0)"
        print(f"  ✅ {file_path.name}: {len(chunks)} chunks [{weight_label}]")
    
    print(f"\n🎉 Ingestion complete: {total_chunks} chunks stored in collection '{collection_name}'")
    print(f"💾 Database saved to: {db_path}")

if __name__ == "__main__":
    ingest_corpus(
        corpus_dir="/workspace/corpus/buffett/shareholder_letters",
        collection_name="buffett_letters"
    )
