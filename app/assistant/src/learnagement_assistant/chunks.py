"""La forme des pages et des morceaux qui passent d'une étape à l'autre."""

from typing import NotRequired, TypedDict


class Page(TypedDict):
    formation: str
    source: str
    file_name: str
    page: int
    text: str


class Chunk(Page):
    chunk_id: str
    category: NotRequired[str]


class SearchHit(TypedDict):
    score: float
    chunk: Chunk
