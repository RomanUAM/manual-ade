from __future__ import annotations

from pathlib import Path

from .knowledge_base import KnowledgeBase
from .models import Artifact


EXISTING_ARTIFACTS = {
    "muestreo-gatos": [
        ("book_chapter", "docs/libro_latex/Capitulos/04-anova.tex", "Capitulo del libro"),
        ("pdf", "site/manual_base_latex_compilado.pdf", "PDF publico"),
        ("web", "site/index.html", "Pagina publica"),
    ],
    "anova-lentejas": [
        ("book_chapter", "docs/libro_latex/Capitulos/00-ANOVA.tex", "Capitulo del libro"),
        ("practice", "practicas/anova-de-un-factor-comparar-grupos-con-evidencia.md", "Practica editable"),
        ("pdf", "site/manual_base_latex_compilado.pdf", "PDF publico"),
        ("web", "site/index.html", "Pagina publica"),
    ],
    "factorial-papel": [
        ("book_chapter", "docs/libro_latex/Capitulos/02-conceptos.tex", "Capitulo del libro"),
        ("practice", "practicas/diseno-factorial-2x2-sustancias-e-interacciones-visuales.md", "Practica editable"),
        ("pdf", "site/manual_base_latex_compilado.pdf", "PDF publico"),
        ("web", "site/index.html", "Pagina publica"),
    ],
    "taguchi-violeta": [
        ("book_chapter", "docs/libro_latex/Capitulos/03-disenos-clasicos.tex", "Capitulo del libro"),
        ("practice", "practicas/taguchi-l4-violeta-africana-y-sistemas-biologicos-confinados.md", "Practica editable"),
        ("pdf", "site/manual_base_latex_compilado.pdf", "PDF publico"),
        ("web", "site/index.html", "Pagina publica"),
    ],
}


def register_existing_artifacts(root: Path, kb: KnowledgeBase) -> None:
    for node_id, artifacts in EXISTING_ARTIFACTS.items():
        for kind, path, description in artifacts:
            artifact = Artifact(kind, path, node_id, "hag.generators", description)
            if (root / path).exists():
                kb.add_artifact(node_id, artifact)
    kb.save()


def generate_gap_report(root: Path, kb: KnowledgeBase, missing: dict[str, list[str]]) -> str:
    path = root / "artifacts" / "hag" / "brechas_ecosistema.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Brechas del ecosistema HAG", ""]
    if not missing:
        lines.append("No hay brechas detectadas.")
    for node_id, kinds in missing.items():
        node = kb.nodes[node_id]
        lines.append(f"## {node.title}")
        lines.append("")
        lines.append(f"Pregunta: {node.question}")
        lines.append("")
        lines.append("Faltan:")
        for kind in kinds:
            lines.append(f"- {kind}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path.relative_to(root))
