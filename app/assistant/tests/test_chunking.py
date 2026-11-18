import pytest

from learnagement_assistant.chunker import TextChunker
from learnagement_assistant.chunks import Page
from learnagement_assistant.cleaner import TextCleaner
from learnagement_assistant.metadata_builder import MetadataBuilder


def _page(text: str, file_name: str = "competences.pdf") -> Page:
    return {"formation": "idu", "source": "x.pdf", "file_name": file_name, "page": 1, "text": text}


def test_pieces_overlap_and_cover_the_text() -> None:
    chunker = TextChunker(chunk_size=10, overlap=3)
    assert chunker.chunk_text("abcdefghijklmnopqrstuvwxyz") == [
        "abcdefghij",
        "hijklmnopq",
        "opqrstuvwx",
        "vwxyz",
    ]


def test_overlap_as_large_as_the_piece_is_refused() -> None:
    with pytest.raises(ValueError):
        TextChunker(chunk_size=10, overlap=10)


def test_chunks_keep_their_page_and_get_an_id() -> None:
    chunks = TextChunker(chunk_size=5, overlap=1).chunk_pages([_page("abcdefgh")])
    assert [chunk["chunk_id"] for chunk in chunks] == ["chunk_0", "chunk_1"]
    assert chunks[1]["text"] == "efgh"
    assert chunks[1]["formation"] == "idu"


def test_cleaner_flattens_whitespace() -> None:
    assert TextCleaner().clean("  un\n\ndeux \t trois ") == "un deux trois"


@pytest.mark.parametrize(
    ("file_name", "category"),
    [
        ("Compétences IDU.pdf", "competences"),
        ("debouches_metiers.pdf", "metiers"),
        ("a.pdf", "general"),
    ],
)
def test_category_comes_from_the_file_name(file_name: str, category: str) -> None:
    chunk = TextChunker().chunk_pages([_page("texte", file_name)])[0]
    assert MetadataBuilder().enrich_chunks([chunk])[0]["category"] == category
