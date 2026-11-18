"""Ramène le texte extrait d'un PDF à une seule ligne aux espaces simples."""

import re


class TextCleaner:
    def clean(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
