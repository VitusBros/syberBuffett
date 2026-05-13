"""
RAG Retriever Module.
Retrieves relevant context from ChromaDB based on user query.
Supports metadata-based weighting for re-ranking.
"""
import chromadb
import logging

logger = logging.getLogger(__name__)

class RAGRetriever:
    """检索增强生成 (RAG) 检索器"""
    
    def __init__(self, db_path: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)
        logger.info(f"RAG Retriever initialized: collection='{collection_name}', db='{db_path}'")
    
    def retrieve(self, query: str, top_k: int = 3, fetch_k: int = None) -> str:
        """
        根据用户问题检索相关片段，支持元数据加权重排序
        
        Args:
            query: 用户问题
            top_k: 返回最相关的 K 个片段
            fetch_k: 检索候选数量（默认 top_k * 3），用于加权重排序
            
        Returns:
            拼接后的上下文字符串
        """
        # Fetch more candidates than needed for re-ranking
        fetch_k = fetch_k or max(top_k * 3, 15)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'] or not results['documents'][0]:
            logger.warning(f"No relevant documents found for query: {query}")
            return ""
        
        # Build scored items with metadata weighting
        scored_items = []
        for doc, meta, distance in zip(
            results['documents'][0], 
            results['metadatas'][0],
            results['distances'][0]
        ):
            # Apply weight from metadata (default 1.0)
            weight = meta.get('weight', 1.0)
            # Weighted score: higher weight = lower effective distance
            weighted_distance = distance / weight
            scored_items.append({
                'doc': doc,
                'meta': meta,
                'distance': distance,
                'weighted_distance': weighted_distance,
                'weight': weight
            })
        
        # Sort by weighted distance and take top_k
        scored_items.sort(key=lambda x: x['weighted_distance'])
        top_items = scored_items[:top_k]
        
        context_parts = []
        for item in top_items:
            source = item['meta'].get('source', 'unknown')
            # 添加相关性评分（基于加权距离）
            relevance = f"相关性: {1 - item['weighted_distance']:.2f}"
            weight_note = f"[加权 x{item['weight']}]" if item['weight'] > 1.0 else ""
            context_parts.append(f"[来自 {source}] {weight_note}({relevance})\n{item['doc']}")
        
        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Retrieved {len(context_parts)} chunks for query: {query[:30]}... (weighted re-ranking applied)")
        return context
