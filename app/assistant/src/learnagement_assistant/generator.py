"""Met en forme les morceaux trouvés, sans modèle de langue : chaque extrait cite sa source."""

from learnagement_assistant.chunks import SearchHit

EXCERPT_LENGTH = 700
NOTHING_FOUND = "Je n'ai pas trouvé d'information suffisante dans les documents."


class SimpleGenerator:
    def generate(self, hits: list[SearchHit]) -> str:
        if not hits:
            return NOTHING_FOUND
        lines = ["Réponse basée sur les documents :\n"]
        for rank, hit in enumerate(hits, start=1):
            chunk = hit["chunk"]
            lines.append(
                f"{rank}. Source : {chunk['file_name']} — page {chunk['page']}\n"
                f"{chunk['text'][:EXCERPT_LENGTH]}...\n"
            )
        return "\n".join(lines)
