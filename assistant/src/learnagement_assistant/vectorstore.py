"""L'index FAISS (produit scalaire sur vecteurs normalisés) et les morceaux qu'il désigne."""

import json
from pathlib import Path
from typing import Self

import faiss

from learnagement_assistant.chunks import Chunk, SearchHit
from learnagement_assistant.embedder import Embeddings

# Les filtres (formation, catégorie) s'appliquent après la recherche : on lit plus large.
CANDIDATES_PER_HIT = 20
MISSING = -1


class FAISSVectorStore:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index: faiss.Index = faiss.IndexFlatIP(dimension)
        self.chunks: list[Chunk] = []

    def add_embeddings(self, embeddings: Embeddings, chunks: list[Chunk]) -> None:
        self.index.add(embeddings)
        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding: Embeddings,
        top_k: int,
        formation: str | None = None,
        category: str | None = None,
    ) -> list[SearchHit]:
        candidates = min(top_k * CANDIDATES_PER_HIT, len(self.chunks))
        scores, indices = self.index.search(query_embedding, candidates)
        hits: list[SearchHit] = []
        for score, position in zip(scores[0], indices[0], strict=True):
            if len(hits) >= top_k:
                break
            if position == MISSING:
                continue
            chunk = self.chunks[position]
            if formation and chunk["formation"] != formation:
                continue
            if category and chunk.get("category") != category:
                continue
            hits.append({"score": float(score), "chunk": chunk})
        return hits

    def save(self, index_file: Path, metadata_file: Path) -> None:
        faiss.write_index(self.index, str(index_file))
        metadata_file.write_text(json.dumps(self.chunks, ensure_ascii=False, indent=2), "utf-8")

    @classmethod
    def load(cls, index_file: Path, metadata_file: Path) -> Self:
        index = faiss.read_index(str(index_file))
        store = cls(index.d)
        store.index = index
        store.chunks = json.loads(metadata_file.read_text("utf-8"))
        return store
