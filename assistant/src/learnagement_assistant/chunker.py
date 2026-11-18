"""Découpe le texte des pages en morceaux qui se chevauchent."""

from learnagement_assistant.chunks import Chunk, Page

DEFAULT_CHUNK_SIZE = 800
DEFAULT_OVERLAP = 150


class TextChunker:
    def __init__(
        self, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP
    ) -> None:
        if overlap >= chunk_size:
            raise ValueError("Le chevauchement doit rester plus petit que le morceau.")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        pieces = []
        start = 0
        while start < len(text):
            piece = text[start : start + self.chunk_size].strip()
            if piece:
                pieces.append(piece)
            start += self.chunk_size - self.overlap
        return pieces

    def chunk_pages(self, pages: list[Page]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page in pages:
            for piece in self.chunk_text(page["text"]):
                chunks.append(
                    Chunk(
                        chunk_id=f"chunk_{len(chunks)}",
                        formation=page["formation"],
                        source=page["source"],
                        file_name=page["file_name"],
                        page=page["page"],
                        text=piece,
                    )
                )
        return chunks
