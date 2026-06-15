"""Vector memory using ChromaDB + sentence-transformers."""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import config


class VectorMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"},
        )
        print(f"[Memory] Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)

    def add(self, text, metadata=None, doc_id=None):
        import uuid
        doc_id = doc_id or str(uuid.uuid4())
        embedding = self.embedder.encode(text).tolist()
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
        )
        return doc_id

    def query(self, text, n_results=3):
        if self.collection.count() == 0:
            return []
        embedding = self.embedder.encode(text).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, self.collection.count()),
        )
        return results.get("documents", [[]])[0]

    def count(self):
        return self.collection.count()

    def clear(self):
        self.client.delete_collection("memories")
        self.collection = self.client.get_or_create_collection(name="memories")
