"""Cherche dans l'index les morceaux les plus proches d'une question."""

from learnagement_assistant.chunks import SearchHit
from learnagement_assistant.config import FAISS_INDEX_FILE, FAISS_METADATA_FILE
from learnagement_assistant.embedder import TextEmbedder
from learnagement_assistant.vectorstore import FAISSVectorStore

DEFAULT_TOP_K = 5


class Retriever:
    def __init__(self) -> None:
        self.embedder = TextEmbedder()
        self.store = FAISSVectorStore.load(FAISS_INDEX_FILE, FAISS_METADATA_FILE)

    def retrieve(
        self,
        query: str,
        formation: str | None = None,
        category: str | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[SearchHit]:
        query_embedding = self.embedder.embed_texts([query])
        return self.store.search(
            query_embedding, top_k=top_k, formation=formation, category=category
        )
