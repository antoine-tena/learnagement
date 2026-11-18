"""Première étape de l'index : PDF → morceaux nettoyés et rangés par catégorie (JSON)."""

import json
from pathlib import Path

from learnagement_assistant.chunker import TextChunker
from learnagement_assistant.chunks import Chunk
from learnagement_assistant.cleaner import TextCleaner
from learnagement_assistant.config import (
    CHUNKS_FILE,
    ENRICHED_CHUNKS_FILE,
    PROCESSED_DIR,
    RAW_PDF_DIR,
)
from learnagement_assistant.loader import PDFLoader
from learnagement_assistant.metadata_builder import MetadataBuilder


def _write_json(chunks: list[Chunk], path: Path) -> None:
    path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), "utf-8")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pages = PDFLoader().load_all_pdfs(RAW_PDF_DIR)
    print(f"Pages chargées : {len(pages)}")
    cleaner = TextCleaner()
    for page in pages:
        page["text"] = cleaner.clean(page["text"])
    chunks = TextChunker().chunk_pages(pages)
    print(f"Morceaux créés : {len(chunks)}")
    _write_json(chunks, CHUNKS_FILE)
    _write_json(MetadataBuilder().enrich_chunks(chunks), ENRICHED_CHUNKS_FILE)
    print("Morceaux enregistrés.")


if __name__ == "__main__":
    main()
