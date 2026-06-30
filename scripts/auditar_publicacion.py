#!/usr/bin/env python3
from __future__ import annotations

import sys
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
