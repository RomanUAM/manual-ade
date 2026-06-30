#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
SITE = ROOT / "site"


def run_latex(folder: Path, passes: int = 2) -> None:
    for _ in range(passes):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=folder,
            check=True,
        )


def copy_pdf(source: Path, name: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, OUTPUT / name)
    shutil.copy2(source, SITE / name)


def main() -> None:
    manual_dir = ROOT / "docs" / "libro_latex"
    presentation_dir = ROOT / "docs" / "presentacion_integrada_latex"
    enrichment_dir = ROOT / "docs" / "manual_integrado_latex"

    run_latex(manual_dir)
    copy_pdf(manual_dir / "main.pdf", "manual_base_latex_compilado.pdf")

    run_latex(presentation_dir)
    copy_pdf(presentation_dir / "main.pdf", "presentacion_integrada_ade.pdf")

    if (enrichment_dir / "main.tex").exists():
        run_latex(enrichment_dir)
        copy_pdf(enrichment_dir / "main.pdf", "manual_integrado_ade.pdf")

    print("Materiales compilados:")
    print("- output/pdf/manual_base_latex_compilado.pdf")
    print("- output/pdf/presentacion_integrada_ade.pdf")
    print("- output/pdf/manual_integrado_ade.pdf")


if __name__ == "__main__":
    main()
