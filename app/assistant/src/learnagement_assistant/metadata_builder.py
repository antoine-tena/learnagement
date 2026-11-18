"""Range chaque morceau dans une catégorie d'après le nom de son fichier."""

from learnagement_assistant.chunks import Chunk
from learnagement_assistant.config import CATEGORY_KEYWORDS, DEFAULT_CATEGORY


class MetadataBuilder:
    def detect_category(self, file_name: str) -> str:
        name = file_name.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in name for keyword in keywords):
                return category
        return DEFAULT_CATEGORY

    def enrich_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        return [{**chunk, "category": self.detect_category(chunk["file_name"])} for chunk in chunks]
