#!/usr/bin/env python3
from __future__ import annotations

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

FORBIDDEN = [
    "data/raw",
    "Articulo",
    "articulo",
    "bitstream",
    ".tex",
    ".txt",
]

REQUIRED = [
    SITE / "index.html",
    SITE / "manual_base_latex_compilado.pdf",
]

LATEX_CHAPTERS = ROOT / "docs" / "libro_latex" / "Capitulos"


def main() -> None:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"Falta salida publica requerida: {path.relative_to(ROOT)}")

    html_path = SITE / "index.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        for needle in FORBIDDEN:
            if needle in html:
                errors.append(f"La pagina publica contiene referencia prohibida: {needle}")

    if LATEX_CHAPTERS.exists():
        for path in sorted(LATEX_CHAPTERS.glob("*.tex")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "\\appendix" in text:
                errors.append(f"Capitulo con appendix interno: {path.relative_to(ROOT)}")
            sections = re.findall(r"(?m)^\\section(?!\\*)", text)
            if path.name != "00-ruta-didactica.tex" and len(sections) > 1:
                errors.append(
                    f"Jerarquia editorial rota en {path.relative_to(ROOT)}: "
                    f"{len(sections)} secciones principales en un solo archivo"
                )

    if errors:
        print("Auditoria de publicacion: FALLA")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("Auditoria de publicacion: OK")
    print("- site/index.html")
    print("- site/manual_base_latex_compilado.pdf")


if __name__ == "__main__":
    main()
