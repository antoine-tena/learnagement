"""Extracteurs de texte et de sections pour FileService."""

import re


class TextExtractorsMixin:
    """Méthodes utilitaires d'extraction et de nettoyage de texte PDF."""

    def extract_items_between(self, text, start_label, end_label):
        start = text.lower().find(start_label.lower())

        if start == -1:
            return []

        end = text.lower().find(end_label.lower(), start + len(start_label))

        if end == -1:
            part = text[start:]
        else:
            part = text[start:end]

        return self.extract_bullet_items(part.replace(start_label, ""))

    def extract_items_after(self, text, label):
        start = text.lower().find(label.lower())

        if start == -1:
            return []

        part = text[start:]
        return self.extract_bullet_items(part.replace(label, ""))

    def extract_bullet_items(self, text):
        text = text.replace("•", "\n•")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        items = []

        for line in lines:
            if line.startswith("•"):
                item = line.replace("•", "").strip()
                if item and not item.startswith("…"):
                    items.append(self.clean_text(item))

        return items

    def extract_numbered_sections(self, text):
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        sections = []
        current_title = None
        current_content = []

        pattern = re.compile(r"^\d+\.\s+.+")

        for line in lines:
            if pattern.match(line):
                if current_title:
                    sections.append({"title": current_title, "content": "\n".join(current_content)})

                current_title = line
                current_content = []
            else:
                if current_title:
                    current_content.append(line)

        if current_title:
            sections.append({"title": current_title, "content": "\n".join(current_content)})

        return sections

    def extract_bullets(self, text):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        bullets = []

        for line in lines:
            if line.startswith("•"):
                bullets.append(line.replace("•", "").strip())
            elif line.startswith("■"):
                bullets.append(line.replace("■", "").strip())
            elif line.startswith("✓"):
                bullets.append(line.replace("✓", "").strip())
            elif line.startswith("→"):
                bullets.append(line.strip())

        return bullets

    def extract_checklist(self, text):
        if "Checklist" not in text:
            return []

        checklist_text = text.split("Checklist", 1)[1]
        lines = [line.strip() for line in checklist_text.splitlines() if line.strip()]

        items = []

        for line in lines:
            if line.startswith("■"):
                items.append(line.replace("■", "").strip())

        return items

    def extract_after_label(self, text, label):
        pattern = rf"{re.escape(label)}\s*:\s*(.*?)(?=Junior|Senior|ACs|Blocs|Bloc|$)"
        match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)

        if not match:
            return ""

        return self.clean_text(match.group(1))

    def extract_salary(self, text):
        match = re.search(r"(Junior\s*:\s*[^€]+€\s*Senior\s*:\s*[^€]+€)", text, flags=re.IGNORECASE)

        if match:
            return self.clean_text(match.group(1))

        return ""

    def extract_section_around_title(self, text, title, all_titles):
        lower_text = text.lower()
        title_lower = title.lower()

        positions = []
        for t in all_titles:
            pos = lower_text.find(t.lower())
            if pos != -1:
                positions.append((pos, t))

        positions = sorted(positions)

        current_pos = lower_text.find(title_lower)

        if current_pos == -1:
            return ""

        start = current_pos

        for pos, _t in reversed(positions):
            if pos < current_pos:
                previous_text = text[pos:current_pos]
                if len(previous_text) < 2500:
                    start = pos
                break

        end = len(text)

        for pos, _t in positions:
            if pos > current_pos:
                end = pos
                break

        return text[start:end]

    def clean_text(self, text):
        text = text.replace("■", "")
        text = text.replace("I", "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
