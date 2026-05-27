"""
Zilliz Cloud Retriever Module.
Uses Zilliz Cloud (Milvus) for vector storage and local embedding model.
"""
import os
import logging
from pymilvus import MilvusClient, Collection, DataType
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ZillizRetriever:
    """Retrieval Augmented Generation (RAG) Retriever using Zilliz Cloud"""
    
    def __init__(self, collection_name: str, endpoint: str = None, token: str = None):
        self.collection_name = collection_name
        self.dimension = 384 # all-MiniLM-L6-v2 dimension
        
        # Load Embedding Model
        logger.info("Loading embedding model: all-MiniLM-L6-v2...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded.")

        # Connect to Zilliz
        self.endpoint = endpoint or os.getenv("ZILLIZ_ENDPOINT")
        self.token = token or os.getenv("ZILLIZ_API_KEY")
        
        if not self.endpoint or not self.token:
            raise ValueError("ZILLIZ_ENDPOINT and ZILLIZ_API_KEY must be set")

        self.client = MilvusClient(uri=self.endpoint, token=self.token)
        logger.info(f"Connected to Zilliz Cloud: {self.endpoint}")

        # Ensure Collection Exists
        if not self.client.has_collection(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                dimension=self.dimension,
                auto_id=True,
                consistency_level="Strong"
            )
            logger.info(f"Created collection: {collection_name}")

    def ingest(self, documents: list[str], metadatas: list[dict]):
        """Ingest documents into Zilliz"""
        if not documents:
            return

        # Generate Embeddings
        vectors = self.embedding_model.encode(documents).tolist()
        
        # Prepare Data
        data = [
            {"vector": vec, "text": doc, "metadata": str(meta)}
            for vec, doc, meta in zip(vectors, documents, metadatas)
        ]
        
        # Insert
        self.client.insert(collection_name=self.collection_name, data=data)
        logger.info(f"Ingested {len(documents)} documents into Zilliz.")

    def retrieve(self, query: str, top_k: int = 5) -> str:
        """Retrieve relevant context from Zilliz"""
        # Generate Query Embedding
        query_vec = self.embedding_model.encode(query).tolist()
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vec],
            limit=top_k,
            output_fields=["text", "metadata"],
        )
        
        context_parts = []
        if results and results[0]:
            for hit in results[0]:
                metadata = eval(hit['entity'].get('metadata', '{}'))
                source = metadata.get('source', 'unknown')
                score = hit['distance']
                text = hit['entity']['text']
                context_parts.append(f"[来自 {source}] (相关性: {score:.4f})\n{text}")
        
        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Retrieved {len(context_parts)} chunks from Zilliz for query: {query[:30]}...")
        return context
