"""Répond à une question guidée (formation, catégorie) à partir de l'index."""

from learnagement_assistant.config import DEFAULT_CATEGORY
from learnagement_assistant.generator import SimpleGenerator
from learnagement_assistant.retriever import Retriever

GUIDED_QUERIES = {
    "competences": "Quelles sont les compétences principales de la formation {formation} ?",
    "metiers": "Quels sont les métiers et débouchés de la formation {formation} ?",
    "projets": "Quels projets pratiques peut-on réaliser en formation {formation} ?",
    "techniques": "Quelles compétences techniques faut-il maîtriser en formation {formation} ?",
    "bonnes_pratiques": "Quelles sont les bonnes pratiques pour réussir en formation {formation} ?",
    "experiences": "Quelles expériences pratiques sont utiles pour la formation {formation} ?",
    DEFAULT_CATEGORY: "Donne les informations importantes sur la formation {formation}.",
}


class QueryService:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.generator = SimpleGenerator()

    def build_guided_query(self, formation: str, category: str) -> str:
        template = GUIDED_QUERIES.get(category, GUIDED_QUERIES[DEFAULT_CATEGORY])
        return template.format(formation=formation)

    def answer_guided(self, formation: str, category: str) -> str:
        formation, category = formation.lower(), category.lower()
        query = self.build_guided_query(formation, category)
        hits = self.retriever.retrieve(query, formation=formation, category=category)
        return self.generator.generate(hits)
