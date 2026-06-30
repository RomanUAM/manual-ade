#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"

SCAN_ROOTS = [
    ROOT / "docs" / "libro_latex",
    ROOT / "practicas",
    ROOT / "data" / "manifests",
    ROOT / "data" / "raw" / "curso-2026p",
    ROOT / "data" / "raw" / "curso-2025",
]

TEXT_EXTS = {".tex", ".md", ".txt"}
PDF_TIMEOUT = 2
MAX_FILES = 38

CORE_HINTS = [
    "00Notas.tex",
    "03-disenos-clasicos.tex",
    "00-ANOVA.tex",
    "02-conceptos.tex",
    "05-factoriales.tex",
    "04-anova.tex",
    "Practica 2^2 A&D.pdf",
    "Sustancias-interacciones",
    "ANOVA-de-un-factor",
    "ANOVA-de-2-Factores",
    "De-Datos-Continuos-a-Diseno-Taguchi",
    "Optimizacion-de-un-Proceso-Manual",
    "reporte separadores",
    "Miel-azucar-o-cafe",
    "Ejemplo-Practico-de-MANOVA",
    "Analisis-de-Covarianza",
    "PROYECTO FINAL DAEI",
    "compo",
    "estadistica_zip_manifest",
]


CHAPTER_RULES = [
    (
        "01. Necesidad de disenar experimentos",
        ["hipotesis", "evidencia", "decision", "suposiciones", "conocimiento", "etico"],
    ),
    (
        "02. Datos, variabilidad y muestreo",
        ["muestreo", "media", "varianza", "dispersion", "gini", "azar", "probabilidad"],
    ),
    (
        "03. ANOVA de un factor",
        ["anova de un factor", "prueba f", "valor p", "varianza entre", "lenteja", "germinacion"],
    ),
    (
        "04. Dos factores e interaccion",
        ["dos factores", "interaccion", "efectos principales", "profesor", "materia"],
    ),
    (
        "05. Diseno factorial 2^2",
        ["2^2", "2²", "factorial", "curcuma", "cloro", "post-it", "luxometro", "tortilla"],
    ),
    (
        "06. Factoriales aplicados y realidad operativa",
        ["no balanceado", "separadores", "artesanales", "proceso manual", "replicas desiguales"],
    ),
    (
        "07. Taguchi y disenos reducidos",
        ["taguchi", "l4", "violeta africana", "cafe", "miel", "azucar", "necrosis", "halo"],
    ),
    (
        "08. Modelado y regresion",
        ["regresion", "modelo lineal", "residuos", "prediccion", "modelado"],
    ),
    (
        "09. ANCOVA",
        ["ancova", "covarianza", "covariable", "medias ajustadas"],
    ),
    (
        "10. MANOVA y multiples respuestas",
        ["manova", "multivariado", "multiples respuestas", "matriz de respuestas"],
    ),
    (
        "11. Proyecto experimental completo",
        ["proyecto", "acustic", "composito", "inductancia", "defensa", "conclusiones"],
    ),
]

FIELD_RULES = {
    "problema": ["problema", "planteamiento", "situacion", "introduccion", "objetivo principal"],
    "factores": ["factor", "factores", "niveles", "tratamientos", "matriz"],
    "respuesta": ["variable respuesta", "variables de respuesta", "respuesta", "lux", "germinacion", "hongos", "necrosis"],
    "diseno": ["anova", "factorial", "taguchi", "ancova", "manova", "regresion", "muestreo"],
    "practica": ["procedimiento", "materiales", "repeticiones", "replicas", "blanco", "unidad experimental"],
    "decision": ["conclusion", "interpretacion", "decision", "significativo", "p-valor", "f calculada"],
}


@dataclass
class Reading:
    path: str
    title: str
    chapter: str
    confidence: int
    fields: dict[str, list[str]]
    use: str
    status: str
    derechos: str
    publicacion: str


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def clean(text: str) -> str:
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_text(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            result = subprocess.run(
                ["pdftotext", "-f", "1", "-l", "3", str(path), "-"],
                text=True,
                capture_output=True,
                timeout=PDF_TIMEOUT,
            )
            text = result.stdout.strip()
            if text:
                return clean(text), "leido"
            return clean(result.stderr), "sin_texto"
        except subprocess.TimeoutExpired:
            return "", "pendiente_por_pdf_lento"
        except FileNotFoundError:
            return "", "pendiente_sin_pdftotext"
    if suffix in TEXT_EXTS:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                return clean(handle.read(30000)), "leido"
        except OSError:
            return "", "pendiente_por_io"
    return "", "omitido"


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\\\\(?:section|subsection)\{", text)
    out = []
    for part in parts:
        part = clean(part)
        if 45 <= len(part) <= 320:
            out.append(part)
    return out


def best_chapter(text: str) -> tuple[str, int]:
    low = text.lower()
    best_name = "Sin clasificacion suficiente"
    best_score = 0
    for name, words in CHAPTER_RULES:
        score = sum(low.count(word) for word in words)
        if score > best_score:
            best_name = name
            best_score = score
    return best_name, best_score


def extract_fields(text: str) -> dict[str, list[str]]:
    low_sentences = [(s, s.lower()) for s in sentences(text)]
    fields: dict[str, list[str]] = {}
    for field, words in FIELD_RULES.items():
        found = []
        for original, low in low_sentences:
            if any(word in low for word in words):
                found.append(original)
            if len(found) == 2:
                break
        fields[field] = found
    return fields


def title_from_text(path: Path, text: str) -> str:
    for sentence in sentences(text):
        cleaned = re.sub(r"^[0-9.\-\s]+", "", sentence).strip()
        if 12 <= len(cleaned) <= 95:
            return cleaned
    return path.stem.replace("-", " ").replace("_", " ")


def learning_use(chapter: str, fields: dict[str, list[str]], status: str) -> str:
    if status != "leido":
        return "Pendiente de lectura completa; solo debe usarse como pista hasta extraer contenido."
    joined = " ".join(" ".join(v) for v in fields.values()).lower()
    if "curcuma" in joined or "cloro" in joined or "lux" in joined:
        return "Caso central para construir diseno 2^2: factores, niveles, blanco, replicas, medicion y lectura de interaccion."
    if "lenteja" in joined:
        return "Practica biologica sencilla para explicar ANOVA de un factor desde germinacion, crecimiento y hongos."
    if "violeta africana" in joined or "taguchi" in joined:
        return "Caso para explicar diseno reducido, respuestas visuales y aprendizaje cuando el resultado inicial no ocurre."
    if "profesor" in joined and "materia" in joined:
        return "Caso balanceado para separar efectos principales e interaccion en ANOVA de dos factores."
    if "proyecto" in joined:
        return "Modelo para el cierre del manual: pasar de pregunta experimental a defensa de resultados."
    return f"Fuente para desarrollar {chapter.lower()} con evidencia extraida del contenido, no del nombre."


def rights_status(path: Path) -> tuple[str, str]:
    name = rel(path).lower()
    own_project_markers = [
        "docs/libro_latex/",
        "practicas/",
        "data/manifests/",
    ]
    if any(marker in name for marker in own_project_markers):
        return "propio", "publicable"

    external_markers = [
        "articulo",
        "article",
        "bitstream",
        "journal",
        "paper",
        "tesis",
        "thesis",
        "libro",
        "book",
    ]
    authorized_course_markers = [
        "proyecto final daei",
        "practica",
        "reporte separadores",
        "sustancias-interacciones",
        "miel",
        "taguchi",
        "anova-de",
        "analisis-de-covarianza",
        "ejemplo-practico-de-manova",
    ]
    if any(marker in name for marker in external_markers):
        return "referencia_externa", "solo_interno"
    if any(marker in name for marker in authorized_course_markers):
        return "curso_autorizado", "publicable"
    if path.suffix.lower() in TEXT_EXTS:
        return "propio", "publicable"
    return "desconocido", "pendiente_permiso"


def candidate_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and (path.suffix.lower() == ".pdf" or path.suffix.lower() in TEXT_EXTS):
                    files.append(path)
    core: list[Path] = []
    rest: list[Path] = []
    for path in files:
        name = rel(path)
        if any(hint.lower() in name.lower() for hint in CORE_HINTS):
            core.append(path)
        else:
            rest.append(path)
    priority = ["curcuma", "cloro", "lenteja", "taguchi", "anova", "factorial", "tortilla", "hongos", "proyecto"]

    def key(path: Path) -> tuple[int, str]:
        name = rel(path).lower()
        bonus = 0 if any(word in name for word in priority) else 1
        return bonus, name

    ordered = sorted(core, key=key)
    if len(ordered) < MAX_FILES:
        ordered.extend(sorted(rest, key=key)[: MAX_FILES - len(ordered)])
    return ordered[:MAX_FILES]


def build() -> list[Reading]:
    readings: list[Reading] = []
    for path in candidate_files():
        text, status = read_text(path)
        chapter, confidence = best_chapter(text)
        fields = extract_fields(text) if text else {k: [] for k in FIELD_RULES}
        derechos, publicacion = rights_status(path)
        readings.append(
            Reading(
                path=rel(path),
                title=title_from_text(path, text) if text else path.stem.replace("-", " "),
                chapter=chapter,
                confidence=confidence,
                fields=fields,
                use=learning_use(chapter, fields, status),
                status=status,
                derechos=derechos,
                publicacion=publicacion,
            )
        )
    return readings


def write_outputs(readings: list[Reading]) -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)
    data = [r.__dict__ for r in readings]
    (MEMORY / "materiales_investigados.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Matriz investigadora del material", "", "Clasificacion por contenido leido, no por nombre de archivo.", ""]
    by_chapter: dict[str, list[Reading]] = {}
    for reading in readings:
        by_chapter.setdefault(reading.chapter, []).append(reading)
    for chapter in sorted(by_chapter):
        lines.append(f"## {chapter}")
        lines.append("")
        for reading in sorted(by_chapter[chapter], key=lambda r: (-r.confidence, r.path))[:8]:
            lines.append(f"### {reading.title}")
            lines.append(f"- Archivo: `{reading.path}`")
            lines.append(f"- Estado: {reading.status}; confianza: {reading.confidence}")
            lines.append(f"- Derechos: {reading.derechos}; publicacion: {reading.publicacion}")
            lines.append(f"- Uso didactico: {reading.use}")
            for field in ("problema", "factores", "respuesta", "diseno", "practica", "decision"):
                evidence = reading.fields.get(field) or []
                if evidence:
                    lines.append(f"- {field.capitalize()}: {evidence[0]}")
            lines.append("")
    (MEMORY / "matriz_investigacion_material.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    readings = build()
    write_outputs(readings)
    read_count = sum(1 for r in readings if r.status == "leido")
    print(f"Materiales revisados: {len(readings)}")
    print(f"Leidos con texto: {read_count}")
    print("- memory/materiales_investigados.json")
    print("- memory/matriz_investigacion_material.md")


if __name__ == "__main__":
    main()
