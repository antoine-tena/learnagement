"""Réponses structurées pour les compétences (MECA, BEE, générique)."""

import re


class CompetencesAnswerMixin:
    """Méthodes de formatage des compétences pour FileService."""

    def answer_competences(self, text, formation):
        formation = formation.lower()

        if formation == "meca":
            return self.answer_meca_competences(text)

        if formation == "bee":
            return self.answer_bee_competences(text)

        response = f"## Compétences principales — {formation.upper()}\n\n"

        acs = re.findall(r"(AC\s*\d+\.\d+\s+.*?)(?=AC\s*\d+\.\d+|$)", text, flags=re.DOTALL)

        if not acs:
            return self.answer_sections(text, formation, "Compétences principales")

        grouped = {}

        for ac in acs:
            clean_ac = self.clean_text(ac)
            match = re.match(r"AC\s*(\d+)\.", clean_ac)

            bloc = f"Bloc {match.group(1)}" if match else "Autres compétences"
            grouped.setdefault(bloc, []).append(clean_ac)

        for bloc, items in grouped.items():
            response += f"### {bloc}\n"
            for item in items:
                response += f"- {item}\n"
            response += "\n"

        return response

    def answer_meca_competences(self, text):
        response = "## Compétences principales — MECA\n\n"

        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(clean_lines)

        blocks = [
            "Concevoir des produits manufacturés",
            "Industrialiser des produits manufacturés",
            "Gérer un projet dans le domaine industriel",
            "Optimiser les procédés de fabrication",
            "Concevoir des systèmes mécatroniques",
            "Concevoir des produits en matériaux composites",
        ]

        for title in blocks:
            section = self.extract_section_around_title(clean_text, title, blocks)

            if not section:
                continue

            situations = self.extract_items_after(section, "Situations professionnelles")
            composantes = self.extract_items_after(section, "Composantes essentielles")

            response += f"### {title}\n\n"

            if situations:
                response += "**Situations professionnelles :**\n"
                for item in situations[:10]:
                    response += f"- {item}\n"
                response += "\n"

            if composantes:
                response += "**Composantes essentielles :**\n"
                for item in composantes[:8]:
                    response += f"- {item}\n"
                response += "\n"

        return response

    def answer_bee_competences(self, text):
        response = "## Compétences principales — BEE\n\n"

        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(clean_lines)

        blocks = [
            "CONCEVOIR LE SYSTÈME CONSTRUCTIF",
            "GARANTIR LA PERFORMANCE",
            "INTÉGRER DES SOLUTIONS DURABLES ADAPTÉES",
            "PILOTER UN PROJET DE BÂTIMENT",
        ]

        for title in blocks:
            section = self.extract_section_around_title(clean_text, title, blocks)

            if not section:
                continue

            situations = self.extract_items_after(section, "Situations professionnelles")
            composantes = self.extract_items_after(section, "Composantes essentielles")

            response += f"### {title.title()}\n\n"

            if situations:
                response += "**Situations professionnelles :**\n"
                for item in situations[:10]:
                    response += f"- {item}\n"
                response += "\n"

            if composantes:
                response += "**Composantes essentielles :**\n"
                for item in composantes[:8]:
                    response += f"- {item}\n"
                response += "\n"

        return response

    def answer_block_competences(self, text, response, blocks):
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(clean_lines)

        lower_text = clean_text.lower()

        for title in blocks:
            start = lower_text.find(title.lower())

            if start == -1:
                continue

            next_positions = []

            for other in blocks:
                if other == title:
                    continue

                pos = lower_text.find(other.lower(), start + len(title))
                if pos != -1:
                    next_positions.append(pos)

            end = min(next_positions) if next_positions else len(clean_text)
            section = clean_text[start:end]

            response += f"### {title}\n\n"

            situations = self.extract_items_between(
                section, "Situations professionnelles", "Composantes essentielles"
            )

            composantes = self.extract_items_between(
                section, "Composantes essentielles", "APPRENTISSAGES"
            )

            if not situations:
                situations = self.extract_items_after(section, "Situations professionnelles")

            if not composantes:
                composantes = self.extract_items_after(section, "Composantes essentielles")

            if situations:
                response += "**Situations professionnelles :**\n"
                for item in situations[:10]:
                    response += f"- {item}\n"
                response += "\n"

            if composantes:
                response += "**Composantes essentielles :**\n"
                for item in composantes[:10]:
                    response += f"- {item}\n"
                response += "\n"

        return response
