from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    "artifacts",
    "evidence",
    "knowledge",
    "memory",
    "output",
    "site",
    "tmp",
}

TEXT_EXTS = {".tex", ".md", ".txt", ".py", ".csv", ".json", ".yml", ".yaml"}
PDF_MAX_CHARS = 80000
PDF_TIMEOUT_SECONDS = 1
PDF_FIRST_PAGES = 1
FIGURE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}
PRESENTATION_EXTS = {".ppt", ".pptx", ".key"}
SPREADSHEET_EXTS = {".xls", ".xlsx", ".csv", ".tsv"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi"}
DOCUMENT_EXTS = {".pdf", ".doc", ".docx", ".tex", ".md", ".txt"}
CODE_EXTS = {".py", ".r", ".R", ".ipynb", ".js", ".ts", ".m", ".jl"}
SUPPORTED_EXTS = TEXT_EXTS | FIGURE_EXTS | PRESENTATION_EXTS | SPREADSHEET_EXTS | VIDEO_EXTS | DOCUMENT_EXTS | CODE_EXTS

OBJECT_HINTS = {
    "concepto": ["concepto", "definicion", "fundamento", "teorema", "hipotesis", "variable", "factor"],
    "ejemplo": ["ejemplo", "caso", "aplicacion", "miel", "lenteja", "tortilla", "gatos", "separadores"],
    "ejercicio": ["ejercicio", "actividad", "calcule", "resuelva", "pregunta", "reto"],
    "figura": ["figura", "imagen", "fotografia", "grafica", "diagrama", "boxplot", "captura"],
    "algoritmo": ["algoritmo", "codigo", "python", "script", "simulacion", "modelo"],
    "practica": ["practica", "procedimiento", "materiales", "replicas", "tratamientos", "unidad experimental"],
    "error_comun": ["error", "sesgo", "limitacion", "confundir", "no controlar", "mal", "incorrecto"],
    "analogia": ["como si", "similar", "analog", "cotidiano", "intuicion"],
    "historia": ["historia", "surgio", "necesidad", "problema real", "contexto"],
    "evaluacion": ["examen", "evaluacion", "rubrica", "criterio", "calificacion"],
    "narrativa": ["por que", "para que", "conexion", "siguiente", "decision", "evidencia"],
}

TOPIC_HINTS = {
    "probabilidad": ["probabilidad", "azar", "distribucion", "normal", "muestreo", "tcl", "gini"],
    "anova": ["anova", "prueba f", "valor p", "varianza", "tratamientos"],
    "factorial": ["factorial", "2^2", "2x2", "interaccion", "niveles"],
    "taguchi": ["taguchi", "l4", "robusto", "arreglo ortogonal"],
    "regresion": ["regresion", "modelo lineal", "prediccion", "residuos"],
    "ancova": ["ancova", "covariable", "covarianza"],
    "manova": ["manova", "multivariado", "multiples respuestas"],
    "optimizacion": ["optimizacion", "parametro", "minimizar", "maximizar"],
    "ia": ["inteligencia artificial", "aprendizaje automatico", "machine learning", "ia"],
    "visualizacion": ["visualizacion", "grafica", "diagrama", "figura", "plot"],
    "ingenieria_economica": ["costo", "economica", "inversion", "beneficio", "rentabilidad"],
}

USE_RULES = {
    "concepto": ["libro", "presentacion", "guia_profesor"],
    "ejemplo": ["libro", "manual_practicas", "presentacion", "pagina"],
    "ejercicio": ["banco_problemas", "evaluacion", "manual_practicas"],
    "figura": ["libro", "presentacion", "pagina", "infografia"],
    "algoritmo": ["simulador", "libro", "pseudocodigo", "ejercicios"],
    "practica": ["manual_practicas", "libro", "presentacion", "evaluacion"],
    "error_comun": ["libro", "presentacion", "evaluacion", "actividad_diagnostica"],
    "analogia": ["libro", "presentacion", "video"],
    "historia": ["libro", "guia_profesor", "presentacion"],
    "evaluacion": ["banco_problemas", "rubrica", "guia_profesor"],
    "narrativa": ["libro", "presentacion", "video", "guia_profesor"],
}


@dataclass
class LearningObject:
    id: str
    source_path: str
    source_kind: str
    object_type: str
    title: str
    topics: list[str]
    excerpt: str
    reusable_in: list[str]
    rights: str
    status: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def stable_id(*parts: str) -> str:
    text = "|".join(parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def source_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in FIGURE_EXTS:
        return "fotografia_o_figura"
    if suffix in PRESENTATION_EXTS:
        return "presentacion"
    if suffix in SPREADSHEET_EXTS:
        return "datos_tabulares"
    if suffix in VIDEO_EXTS:
        return "video"
    if suffix in CODE_EXTS:
        return "codigo"
    if suffix in DOCUMENT_EXTS:
        return "documento"
    return "otro"


def rights_for(path: Path) -> str:
    text = str(path).lower()
    if any(marker in text for marker in ("articulo", "article", "journal", "bitstream", "book", "libro externo")):
        return "referencia_externa"
    if "data/raw" in text and path.suffix.lower() in {".pdf", ".docx", ".pptx", ".xlsx", ".mp4"}:
        return "curso_autorizado_o_pendiente"
    return "propio_o_generado"


def new_stats() -> dict:
    return {
        "text_files_read": 0,
        "pdf_total": 0,
        "pdf_read": 0,
        "pdf_without_text": 0,
        "pdf_timeout": 0,
        "pdf_errors": 0,
        "pdf_pages_per_file": PDF_FIRST_PAGES,
        "unsupported_files_skipped": 0,
        "scan_mode": "project_worktree_excluding_generated_outputs",
        "top_level_dirs_scanned": [],
        "top_level_dirs_skipped": sorted(EXCLUDED_DIRS),
    }


def read_pdf_text(path: Path, stats: dict) -> str:
    stats["pdf_total"] += 1
    try:
        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-f", "1", "-l", str(PDF_FIRST_PAGES), str(path), "-"],
            text=True,
            capture_output=True,
            timeout=PDF_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        stats["pdf_timeout"] += 1
        return ""
    except (OSError, ValueError):
        stats["pdf_errors"] += 1
        return ""

    if result.returncode != 0:
        stats["pdf_errors"] += 1
        return ""
    text = result.stdout[:PDF_MAX_CHARS]
    if clean(text):
        stats["pdf_read"] += 1
        return text
    stats["pdf_without_text"] += 1
    return ""


def read_text(path: Path, stats: dict) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf_text(path, stats)
    if path.suffix.lower() not in TEXT_EXTS:
        return ""
    try:
        stats["text_files_read"] += 1
        return path.read_text(encoding="utf-8", errors="ignore")[:50000]
    except OSError:
        return ""


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_for(path: Path, text: str) -> str:
    if text:
        for line in text.splitlines():
            line = clean(re.sub(r"^[#%\\section{subecparagph\{\}\s\d.-]+", "", line))
            if 12 <= len(line) <= 110:
                return line
    return path.stem.replace("-", " ").replace("_", " ")


def topics_for(path: Path, text: str) -> list[str]:
    haystack = f"{path} {text}".lower()
    topics = [topic for topic, hints in TOPIC_HINTS.items() if any(hint in haystack for hint in hints)]
    return topics or ["pendiente_clasificacion"]


def object_types_for(path: Path, text: str) -> list[tuple[str, list[str]]]:
    kind = source_kind(path)
    if kind == "fotografia_o_figura":
        return [("figura", ["archivo visual reutilizable"])]
    if kind == "presentacion":
        return [("narrativa", ["presentacion pendiente de expansion"]), ("figura", ["posibles esquemas o figuras en diapositivas"])]
    if kind == "datos_tabulares":
        return [("ejemplo", ["datos reutilizables"]), ("ejercicio", ["posible actividad con datos reales"])]
    if kind == "video":
        return [("narrativa", ["explicacion audiovisual pendiente de transcripcion"])]
    if kind == "codigo":
        return [("algoritmo", ["codigo fuente reutilizable"])]

    low = text.lower()
    found = [(obj_type, [hint for hint in hints if hint in low][:3]) for obj_type, hints in OBJECT_HINTS.items() if any(hint in low for hint in hints)]
    if found:
        return found[:5]
    if kind == "documento":
        return [("concepto", ["documento pendiente de extraccion profunda"])]
    return [("concepto", ["archivo pendiente de lectura semantica"])]


def excerpt_for(path: Path, text: str, obj_type: str) -> str:
    if not text:
        return f"Archivo {source_kind(path)} registrado para extraccion profunda."
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    hints = OBJECT_HINTS.get(obj_type, [])
    for sentence in sentences:
        sentence = clean(sentence)
        if 60 <= len(sentence) <= 360 and any(hint in sentence.lower() for hint in hints):
            return sentence
    for sentence in sentences:
        sentence = clean(sentence)
        if 60 <= len(sentence) <= 360:
            return sentence
    return clean(text[:320])


def is_excluded(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and not is_excluded(path, root) and path.suffix.lower() in SUPPORTED_EXTS:
            files.append(path)
    return sorted(files)


def count_unsupported_files(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and not is_excluded(path, root) and path.suffix.lower() not in SUPPORTED_EXTS:
            total += 1
    return total


def top_level_scan_summary(root: Path) -> tuple[list[str], list[str]]:
    scanned: list[str] = []
    skipped: list[str] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        if path.name in EXCLUDED_DIRS:
            skipped.append(path.name)
        else:
            scanned.append(path.name)
    return scanned, skipped


def extract_learning_objects(root: Path) -> tuple[list[LearningObject], dict]:
    objects: list[LearningObject] = []
    stats = new_stats()
    scanned, skipped = top_level_scan_summary(root)
    stats["top_level_dirs_scanned"] = scanned
    stats["top_level_dirs_skipped"] = skipped
    stats["unsupported_files_skipped"] = count_unsupported_files(root)
    for path in scan_files(root):
        if "__pycache__" in path.parts:
            continue
        text = read_text(path, stats)
        topics = topics_for(path, text)
        title = title_for(path, text)
        for obj_type, reasons in object_types_for(path, text):
            object_id = stable_id(rel(root, path), obj_type, title)
            objects.append(
                LearningObject(
                    id=object_id,
                    source_path=rel(root, path),
                    source_kind=source_kind(path),
                    object_type=obj_type,
                    title=title,
                    topics=topics,
                    excerpt=excerpt_for(path, text, obj_type),
                    reusable_in=USE_RULES.get(obj_type, ["libro"]),
                    rights=rights_for(path),
                    status="extraido" if text or source_kind(path) != "documento" else "pendiente_extraccion_profunda",
                    reasons=reasons,
                )
            )
    return objects, stats


def write_banks(root: Path, objects: list[LearningObject], stats: dict[str, int]) -> list[str]:
    knowledge = root / "knowledge"
    banks = knowledge / "bancos"
    banks.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    payload = {
        "schema": "hag.learning_objects.v1",
        "count": len(objects),
        "objects": [obj.to_dict() for obj in objects],
    }
    main = knowledge / "learning_objects.json"
    main.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(rel(root, main))

    by_type: dict[str, list[LearningObject]] = {}
    for obj in objects:
        by_type.setdefault(obj.object_type, []).append(obj)

    bank_names = {
        "ejemplo": "banco_ejemplos.json",
        "figura": "banco_figuras.json",
        "algoritmo": "banco_codigo.json",
        "narrativa": "banco_narrativas.json",
        "error_comun": "banco_errores_comunes.json",
        "evaluacion": "banco_evaluaciones.json",
    }
    for obj_type, filename in bank_names.items():
        path = banks / filename
        items = [obj.to_dict() for obj in by_type.get(obj_type, [])]
        path.write_text(json.dumps({"schema": f"hag.{obj_type}.v1", "count": len(items), "objects": items}, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(rel(root, path))

    reuse = knowledge / "reuse_map.md"
    lines = ["# Mapa de reutilizacion del conocimiento", ""]
    lines.append("Este mapa registra donde puede reutilizarse cada objeto antes de crear contenido nuevo.")
    lines.append("")
    for obj in objects:
        uses = ", ".join(obj.reusable_in)
        topics = ", ".join(obj.topics)
        lines.append(f"- `{obj.id}` **{obj.object_type}** ({topics}) desde `{obj.source_path}` -> {uses}")
    reuse.write_text("\n".join(lines), encoding="utf-8")
    written.append(rel(root, reuse))

    report = root / "evidence" / "hag" / "extraction_report.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(
            {
                "schema": "hag.extraction_report.v1",
                "files_scanned": len(scan_files(root)),
                "objects_extracted": len(objects),
                "reader": stats,
                "banks_written": written,
                "object_types": {key: len(value) for key, value in sorted(by_type.items())},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    written.append(rel(root, report))
    return written


def run_extraction(root: Path) -> list[str]:
    objects, stats = extract_learning_objects(root)
    return write_banks(root, objects, stats)
