"""Lit les PDF d'un dossier par formation (`raw_pdfs/<formation>/*.pdf`), page par page."""

from pathlib import Path

import pymupdf

from learnagement_assistant.chunks import Page


class PDFLoader:
    def load_pdf(self, pdf_path: Path, formation: str) -> list[Page]:
        with pymupdf.open(pdf_path) as document:
            return [
                {
                    "formation": formation,
                    "source": str(pdf_path),
                    "file_name": pdf_path.name,
                    "page": page_number,
                    "text": pdf_page.get_text(),
                }
                for page_number, pdf_page in enumerate(document, start=1)
            ]

    def load_all_pdfs(self, raw_pdf_dir: Path) -> list[Page]:
        pages: list[Page] = []
        for formation_dir in sorted(raw_pdf_dir.iterdir()):
            if formation_dir.is_dir():
                for pdf_file in sorted(formation_dir.glob("*.pdf")):
                    pages.extend(self.load_pdf(pdf_file, formation_dir.name.lower()))
        return pages
