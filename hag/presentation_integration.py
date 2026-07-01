from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from textwrap import dedent
from zipfile import ZipFile


PRESENTATION_SOURCES = [
    {
        "id": "gini-muestreo",
        "title": "Muestreo e indice de Gini",
        "topic": "muestreo",
        "chapter": "02-variabilidad-datos",
        "path": "data/raw/curso-2026p/Una-exploracion-del-Indice-de-Gini-mundial-a-traves-de-cinco-metodos-de-muestreo (1).pdf",
        "problem": "Comprender como distintos metodos de muestreo modifican la representacion de una realidad social.",
    },
    {
        "id": "taguchi-python",
        "title": "De datos continuos a diseno Taguchi con Python",
        "topic": "taguchi",
        "chapter": "07-taguchi",
        "path": "data/raw/curso-2026p/De-Datos-Continuos-a-Diseno-Taguchi-Analisis-Experimental-con-Python.pdf",
        "problem": "Convertir factores continuos en niveles discretos para estudiar robustez y reproducibilidad.",
    },
    {
        "id": "manova-plantas",
        "title": "MANOVA con respuestas fisiologicas en plantas",
        "topic": "manova",
        "chapter": "09-ancova-manova",
        "path": "data/raw/curso-2026p/Ejemplo-Practico-de-MANOVA.pdf",
        "problem": "Decidir cuando varias respuestas correlacionadas deben analizarse como sistema.",
    },
    {
        "id": "rendimiento-termico",
        "title": "Rendimiento termico en procesadores",
        "topic": "manova factorial",
        "chapter": "09-ancova-manova",
        "path": "data/raw/curso-2025/global/Análisis Multivariado del Rendimiento Térmico en Procesadores de Alto Desempeño..pptx",
        "problem": "Equilibrar temperatura y rendimiento en computacion intensiva mediante diseno factorial y respuestas multiples.",
    },
    {
        "id": "ancova-covariables",
        "title": "ANCOVA con tres variables explicativas",
        "topic": "ancova",
        "chapter": "09-ancova-manova",
        "path": "data/raw/curso-2026p/Analisis-de-Covarianza-ANCOVA-con-3-Variables-Explicativas-y-1-Variable-Respuesta.pdf",
        "problem": "Ajustar una respuesta considerando covariables sin confundir control estadistico con causalidad.",
    },
]


@dataclass
class IntegratedPresentation:
    id: str
    title: str
    topic: str
    chapter: str
    source_path: str
    practice_path: str
    manual_path: str
    enriched_presentation_path: str
    summary: str
    activities: list[str]
    links: list[dict[str, str]]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def pdf_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages[:4]:
            pages.append(page.extract_text() or "")
    except Exception:
        return ""
    return "\n".join(pages)[:12000]


def pptx_text(path: Path) -> str:
    if not path.exists():
        return ""
    texts: list[str] = []
    try:
        with ZipFile(path) as zf:
            slides = sorted(name for name in zf.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
            for name in slides:
                xml = zf.read(name).decode("utf-8", errors="ignore")
                parts = re.findall(r"<a:t>(.*?)</a:t>", xml)
                if parts:
                    texts.append(" ".join(parts))
    except (OSError, KeyError):
        return ""
    return "\n".join(texts)[:16000]


def source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        return pptx_text(path)
    if suffix == ".pdf":
        return pdf_text(path)
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:12000]
    except OSError:
        return ""


def bullets_from_text(text: str) -> list[str]:
    sentences = [clean(item) for item in re.split(r"(?<=[.!?])\s+|\n+", text)]
    useful = []
    for sentence in sentences:
        low = sentence.lower()
        if 45 <= len(sentence) <= 240 and any(word in low for word in ["objetivo", "factor", "variable", "metodo", "anova", "manova", "taguchi", "muestreo", "resultado", "decision", "temperatura", "respuesta"]):
            useful.append(sentence)
        if len(useful) == 6:
            break
    return useful


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def practice_text(item: dict, bullets: list[str]) -> str:
    evidence = "\n".join(f"- {line}" for line in bullets) or "- Pendiente de lectura profunda del material fuente."
    return f"""# Practica generada: {item['title']}

## Problema de aprendizaje

{item['problem']}

## Material fuente

Material local del proyecto. No se publica como descarga si no es material propio o autorizado; se usa como evidencia para construir la experiencia didactica.

## Evidencia extraida de la presentacion

{evidence}

## Objetivo

Convertir la presentacion en una experiencia practica: definir una pregunta, reconocer factores o variables, analizar evidencia y cerrar con una decision justificada.

## Procedimiento

1. Lee la historia del problema y escribe que decision se desea tomar.
2. Identifica factores, niveles, variables respuesta, covariables o unidades de observacion.
3. Construye una tabla minima de datos o usa los datos reportados por la presentacion.
4. Dibuja una grafica que permita comparar antes de calcular.
5. Aplica el metodo correspondiente al tema: {item['topic']}.
6. Redacta una conclusion con evidencia, limite y recomendacion.

## Producto del estudiante

- Tabla de variables.
- Grafica inicial.
- Interpretacion estadistica.
- Decision de ingenieria o aprendizaje.
- Error comun detectado y forma de evitarlo.
"""


def manual_text(item: dict, bullets: list[str]) -> str:
    title = latex_escape(item["title"])
    problem = latex_escape(item["problem"])
    topic = latex_escape(item["topic"])
    evidence = "\n".join(f"\\item {latex_escape(line)}" for line in bullets[:4]) or "\\item Pendiente de lectura profunda del material fuente."
    return f"""\\section{{Presentacion convertida en practica: {title}}}

Esta seccion nace de una presentacion existente y se incorpora al manual para que el material no permanezca aislado. La presentacion deja de ser un apoyo oral y se transforma en una ruta de estudio: problema, variables, datos, analisis, decision y actividad.

\\begin{{idea}}
{problem}
\\end{{idea}}

\\subsection{{Evidencia didactica extraida}}

\\begin{{itemize}}
{evidence}
\\end{{itemize}}

\\subsection{{Como entra al manual}}

El tema se integra al capitulo relacionado con \\textbf{{{topic}}}. Si el estudiante solo observa la presentacion, ve una secuencia visual. En el manual, esa misma secuencia se expande con la pregunta de ingenieria, la razon del metodo, la interpretacion y los limites de la conclusion.

\\subsection{{Practica asociada}}

La practica generada pide al estudiante transformar la presentacion en una decision: definir variables, organizar datos, graficar, aplicar el metodo y redactar una conclusion prudente. Si no existia practica, el sistema crea una primera version editable. Si existia una practica relacionada, esta se usa para enriquecer la narrativa y no como bloque aislado.

\\subsection{{Actividad de evaluacion}}

Explique que parte de la presentacion corresponde a contexto, cual corresponde a diseno, cual corresponde a evidencia y cual corresponde a decision. Si falta alguno de estos elementos, proponga como completarlo.
"""


def enriched_presentation_text(item: dict, bullets: list[str]) -> str:
    evidence = "\n".join(f"- {line}" for line in bullets[:5]) or "- Pendiente de lectura profunda."
    return f"""# Presentacion enriquecida: {item['title']}

## Narrativa sugerida

La presentacion debe iniciar con el problema: {item['problem']}

## Contenido recuperado

{evidence}

## Diapositivas que deben existir

1. Problema real.
2. Variables y factores.
3. Diseno o metodo estadistico.
4. Ejemplo con datos.
5. Error frecuente.
6. Actividad del estudiante.
7. Decision final.
8. Conexion con el siguiente tema.

## Regla editorial

Cada diapositiva debe sostener una sola idea. Cuando el material original concentra definicion, formula, tabla y resultado en una misma pagina, se descomprime en varias diapositivas: primero intuicion, despues diseno, despues datos, despues decision.
"""


def aggregator_text(items: list[IntegratedPresentation]) -> str:
    includes = "\n".join(f"\\input{{Capitulos/integraciones/{item.id}}}" for item in items)
    listing = "\n".join(
        f"\\item \\textbf{{{latex_escape(item.title)}}}: practica generada, seccion de manual y presentacion enriquecida."
        for item in items
    )
    return dedent(
        f"""
        \\capituloPregunta{{¿Cómo se convierten las presentaciones en prácticas y capítulos?}}

        Una presentacion aislada puede servir para exponer un tema, pero no siempre basta para que un estudiante aprenda de manera autonoma. En este manual, cada presentacion compatible con ADE debe dejar tres rastros verificables: una practica, una seccion narrativa del manual y una version enriquecida para estudiar.

        \\begin{{idea}}
        La regla operativa es simple: si existe una presentacion y falta la practica, se crea la practica; si existe la practica y la presentacion contiene mejores ejemplos, la practica y el manual se enriquecen; si falta la narrativa, se escribe antes de publicar.
        \\end{{idea}}

        \\section{{Presentaciones integradas por el sistema}}

        \\begin{{itemize}}
        {listing}
        \\end{{itemize}}

        {includes}
        """
    ).strip() + "\n"


def integrate_presentations(root: Path) -> list[IntegratedPresentation]:
    out: list[IntegratedPresentation] = []
    base = root / "docs" / "presentaciones_integradas"
    manual_dir = root / "docs" / "manual_integrado_latex" / "Capitulos" / "integraciones"
    for item in PRESENTATION_SOURCES:
        src = root / item["path"]
        text = source_text(src)
        bullets = bullets_from_text(text)
        folder = base / item["id"]
        practice = folder / "practica_generada.md"
        manual = manual_dir / f"{item['id']}.tex"
        enriched = folder / "presentacion_enriquecida.md"
        write(practice, practice_text(item, bullets))
        write(manual, manual_text(item, bullets))
        write(enriched, enriched_presentation_text(item, bullets))
        out.append(
            IntegratedPresentation(
                id=item["id"],
                title=item["title"],
                topic=item["topic"],
                chapter=item["chapter"],
                source_path=item["path"],
                practice_path=str(practice.relative_to(root)),
                manual_path=str(manual.relative_to(root)),
                enriched_presentation_path=str(enriched.relative_to(root)),
                summary=item["problem"],
                activities=[
                    "Identificar variables y factores.",
                    "Construir grafica inicial.",
                    "Redactar decision con evidencia.",
                ],
                links=[
                    {"label": "Practica generada", "path": str(practice.relative_to(root))},
                    {"label": "Manual", "path": str(manual.relative_to(root))},
                    {"label": "Presentacion enriquecida", "path": str(enriched.relative_to(root))},
                ],
            )
        )
    write(root / "docs" / "manual_integrado_latex" / "Capitulos" / "12-presentaciones-integradas.tex", aggregator_text(out))
    payload = {"schema": "hag.presentation_integration.v1", "count": len(out), "items": [asdict(item) for item in out]}
    write(root / "knowledge" / "presentation_integration.json", json.dumps(payload, ensure_ascii=False, indent=2))
    write(root / "site" / "chatbot_kb.json", json.dumps(payload, ensure_ascii=False, indent=2))
    return out
