"""Service principal de lecture et réponse sur les fichiers PDF."""

import re

import fitz

from apc_dash.polytech_rag.app.config import RAW_PDF_DIR
from apc_dash.polytech_rag.app.services.project_service import ProjectService

from .competences import CompetencesAnswerMixin
from .extractors import TextExtractorsMixin


class FileService(CompetencesAnswerMixin, TextExtractorsMixin):
    def read_pdf(self, formation, category):
        formation = formation.lower()
        category = category.lower()

        pdf_path = RAW_PDF_DIR / formation / f"{category}.pdf"

        if not pdf_path.exists():
            return None, f"Fichier introuvable : {pdf_path}"

        doc = fitz.open(pdf_path)
        pages = []

        for page in doc:
            text = page.get_text().strip()
            if text:
                pages.append(text)

        doc.close()
        return "\n".join(pages), None

    def generate_answer(self, formation, category, level="tous", keyword=""):
        text, error = self.read_pdf(formation, category)

        if error:
            return error

        if category == "projets":
            return self.answer_projects(text, formation, level, keyword)

        if category == "competences":
            return self.answer_competences(text, formation)

        if category == "metiers":
            return self.answer_jobs(text, formation)

        if category == "techniques":
            return self.answer_sections(text, formation, "Compétences techniques à maîtriser")

        if category == "bonnes_pratiques":
            return self.answer_sections(text, formation, "Bonnes pratiques professionnelles")

        if category == "experiences":
            return self.answer_sections(text, formation, "Expériences pratiques et ressources")

        return self.answer_sections(text, formation, category)

    def answer_projects(self, text, formation, level="tous", keyword=""):
        service = ProjectService()
        projects = service.extract_projects(text)
        projects = service.filter_projects(projects, level=level, keyword=keyword)
        return service.format_projects(projects, formation)

    def answer_sections(self, text, formation, title):
        sections = self.extract_numbered_sections(text)
        response = f"## {title} — {formation.upper()}\n\n"

        if not sections:
            response += self.clean_text(text[:2500])
            return response

        for section in sections:
            response += f"### {section['title']}\n\n"

            bullets = self.extract_bullets(section["content"])

            if bullets:
                for bullet in bullets[:7]:
                    response += f"- {bullet}\n"
            else:
                content = self.clean_text(section["content"])
                response += content[:700] + "...\n"

            response += "\n"

        checklist = self.extract_checklist(text)
        if checklist:
            response += "## Checklist importante\n\n"
            for item in checklist[:10]:
                response += f"- {item}\n"

        return response

    def answer_jobs(self, text, formation):
        response = f"## Métiers et débouchés — {formation.upper()}\n\n"

        stop_words = ["Secteurs", "Tendances", "Conseils", "Sources"]

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = "\n".join(lines)

        pattern = (
            r"(?=(Data Engineer|Data Scientist|Data Analyst|"
            r"ML Engineer[^\n]*|Architecte Data[^\n]*|"
            r"Ingénieur [^\n]+|Chef de Projet[^\n]*|"
            r"Responsable [^\n]+|Chargé de Mission[^\n]+))"
        )

        parts = re.split(pattern, full_text)
        jobs = []

        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""

            for stop in stop_words:
                idx = content.find(stop)
                if idx != -1:
                    content = content[:idx]

            if len(content) < 80:
                continue

            competences = self.extract_after_label(content, "Compétences clés")
            salary = self.extract_salary(content)

            description = content.split("Compétences clés")[0].strip()
            description = self.clean_text(description)

            jobs.append(
                {
                    "title": title,
                    "description": description[:450],
                    "competences": competences[:300],
                    "salary": salary,
                }
            )

        if not jobs:
            return response + self.clean_text(text[:2500])

        for job in jobs[:8]:
            response += f"### {job['title']}\n"

            if job["description"]:
                response += f"- **Description :** {job['description']}...\n"

            if job["competences"]:
                response += f"- **Compétences clés :** {job['competences']}\n"

            if job["salary"]:
                response += f"- **Salaire :** {job['salary']}\n"

            response += "\n"

        return response
