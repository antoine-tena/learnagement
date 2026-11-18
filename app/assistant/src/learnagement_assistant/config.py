"""Chemins et réglages de l'assistant : les PDF lus, les morceaux découpés, l'index FAISS."""

import os
from pathlib import Path

# Les PDF et l'index restent hors du repo (`**/data` est ignoré) : ASSISTANT_DATA_DIR les place
# ailleurs, par défaut dans app/assistant/data/.
DATA_DIR = Path(os.environ.get("ASSISTANT_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))

RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "indexes"

CHUNKS_FILE = PROCESSED_DIR / "chunks.json"
ENRICHED_CHUNKS_FILE = PROCESSED_DIR / "enriched_chunks.json"

FAISS_INDEX_FILE = INDEX_DIR / "faiss_index.bin"
FAISS_METADATA_FILE = INDEX_DIR / "faiss_metadata.json"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_CATEGORY = "general"

CATEGORY_KEYWORDS = {
    "competences": ["competence", "compétence"],
    "metiers": ["metier", "métier", "emploi", "marche", "marché"],
    "projets": ["projet", "pratique"],
    "techniques": ["technique", "outils", "technologie"],
    "bonnes_pratiques": ["bonne", "pratique"],
    "experiences": ["experience", "expérience"],
}
