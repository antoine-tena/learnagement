"""Seconde étape de l'index : morceaux rangés (JSON) → vecteurs → index FAISS."""

import json

from learnagement_assistant.chunks import Chunk
from learnagement_assistant.config import (
    ENRICHED_CHUNKS_FILE,
    FAISS_INDEX_FILE,
    FAISS_METADATA_FILE,
    INDEX_DIR,
)
from learnagement_assistant.embedder import TextEmbedder
from learnagement_assistant.vectorstore import FAISSVectorStore


def main() -> None:
    if not ENRICHED_CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {ENRICHED_CHUNKS_FILE}")
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    chunks: list[Chunk] = json.loads(ENRICHED_CHUNKS_FILE.read_text("utf-8"))
    print(f"Morceaux : {len(chunks)}")
    embeddings = TextEmbedder().embed_chunks(chunks)
    store = FAISSVectorStore(dimension=embeddings.shape[1])
    store.add_embeddings(embeddings, chunks)
    store.save(FAISS_INDEX_FILE, FAISS_METADATA_FILE)
    print("Index FAISS créé.")


if __name__ == "__main__":
    main()
