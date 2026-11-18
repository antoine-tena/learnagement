from pathlib import Path

import numpy as np

from learnagement_assistant.chunks import Chunk
from learnagement_assistant.generator import NOTHING_FOUND, SimpleGenerator
from learnagement_assistant.vectorstore import FAISSVectorStore


def _chunk(position: int, formation: str, category: str) -> Chunk:
    return {
        "chunk_id": f"chunk_{position}",
        "formation": formation,
        "source": "x.pdf",
        "file_name": f"{category}.pdf",
        "page": position + 1,
        "text": f"texte {position}",
        "category": category,
    }


def _store() -> FAISSVectorStore:
    store = FAISSVectorStore(dimension=3)
    embeddings = np.eye(3, dtype=np.float32)
    chunks = [
        _chunk(0, "idu", "metiers"),
        _chunk(1, "meca", "metiers"),
        _chunk(2, "idu", "projets"),
    ]
    store.add_embeddings(embeddings, chunks)
    return store


def test_search_ranks_the_closest_chunk_first() -> None:
    query = np.array([[0.1, 0.9, 0.0]], dtype=np.float32)
    hits = _store().search(query, top_k=2)
    assert [hit["chunk"]["chunk_id"] for hit in hits] == ["chunk_1", "chunk_0"]


def test_search_filters_by_formation_and_category() -> None:
    query = np.array([[0.1, 0.9, 0.5]], dtype=np.float32)
    hits = _store().search(query, top_k=5, formation="idu", category="metiers")
    assert [hit["chunk"]["chunk_id"] for hit in hits] == ["chunk_0"]


def test_store_survives_save_and_load(tmp_path: Path) -> None:
    index_file, metadata_file = tmp_path / "index.bin", tmp_path / "chunks.json"
    _store().save(index_file, metadata_file)
    loaded = FAISSVectorStore.load(index_file, metadata_file)
    query = np.array([[0.0, 0.0, 1.0]], dtype=np.float32)
    assert loaded.search(query, top_k=1)[0]["chunk"]["chunk_id"] == "chunk_2"


def test_generator_cites_each_source() -> None:
    query = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
    answer = SimpleGenerator().generate(_store().search(query, top_k=1))
    assert "1. Source : metiers.pdf — page 1" in answer
    assert SimpleGenerator().generate([]) == NOTHING_FOUND
