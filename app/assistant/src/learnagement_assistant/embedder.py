"""Transforme un texte en vecteur normalisé avec sentence-transformers."""

import numpy as np
import numpy.typing as npt
from sentence_transformers import SentenceTransformer

from learnagement_assistant.chunks import Chunk
from learnagement_assistant.config import EMBEDDING_MODEL_NAME

type Embeddings = npt.NDArray[np.float32]


class TextEmbedder:
    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def embed_texts(self, texts: list[str]) -> Embeddings:
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)

    def embed_chunks(self, chunks: list[Chunk]) -> Embeddings:
        return self.embed_texts([chunk["text"] for chunk in chunks])
