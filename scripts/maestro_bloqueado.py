#!/usr/bin/env python3
"""Herramienta maestro para educar agentes y mantener el manual ADE."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"
MEMORY = ROOT / "memory"
PRACTICAS = ROOT / "practicas"
RAW = ROOT / "data" / "raw"
SITE = ROOT / "site" / "index.html"
AGENT_CONTEXT = MEMORY / "agentes"

TOPIC_RULES = {
    "MANOVA": ("manova", "multivariado", "multiples"),
    "ANCOVA": ("ancova", "covarianza"),
    "probabilidad": ("probabilidad", "estadistica", "estadística", "azar", "bayes", "variable aleatoria", "variables-aleatorias"),
    "logica": ("logica", "hipotesis", "algoritmos", "conocimiento cientifico"),
    "ANOVA": ("anova", "prueba-f", "valor-p"),
    "factorial": ("factorial", "2^2", "2x2", "2-y-2", "fraccionado"),
    "Taguchi": ("taguchi", "l4"),
    "regresion": ("regresion", "modelos de regresion", "modelado"),
    "presentaciones": ("pptx", "diapositiva", "presentacion", "slides"),
    "muestreo": ("muestreo", "gini", "grandes numeros"),
    "aplicacion": ("material", "acustica", "separadores", "llantas", "miel", "azucar", "cafe"),
}


def today() -> str:
    return dt.date.today().isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)


def all_materials() -> list[Path]:
    roots = [RAW, ROOT / "docs", PRACTICAS, ROOT / "data" / "manifests"]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(files)


def topic_for(path: Path) -> str:
    text = rel(path).lower()
    for topic, needles in TOPIC_RULES.items():
        if any(needle in text for needle in needles):
            return topic
    return "general"


def count_by_extension(files: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in files:
        ext = path.suffix.lower().lstrip(".") or "sin_extension"
        counts[ext] = counts.get(ext, 0) + 1
    return counts


def count_by_topic(files: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in files:
        topic = topic_for(path)
        counts[topic] = counts.get(topic, 0) + 1
    return counts


def extract_tex_sections(limit_per_file: int = 18) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    tex_files = sorted((ROOT / "docs" / "libro_latex").rglob("*.tex"))
    pattern = re.compile(r"\\(?:section|subsection|subsubsection)\*?\{(.+?)\}")
    cleanup = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{([^{}]*)\})?")
    for path in tex_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        found = 0
        for match in pattern.finditer(text):
            title = match.group(1)
            title = title.replace("\\texorpdfstring", "")
            title = cleanup.sub(lambda item: item.group(1) or "", title)
            title = re.sub(r"\s+", " ", title).strip("{} ")
            if title:
                sections.append((rel(path), title))
                found += 1
            if found >= limit_per_file:
                break
    return sections


def format_counts(title: str, counts: dict[str, int]) -> str:
    lines = [f"## {title}", ""]
    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def format_sources_by_topic(files: list[Path], max_per_topic: int = 18) -> str:
    grouped: dict[str, list[Path]] = {}
    for path in files:
        grouped.setdefault(topic_for(path), []).append(path)

    lines = ["## Fuentes agrupadas por tema", ""]
    for topic in sorted(grouped):
        lines.append(f"### {topic}")
        for path in grouped[topic][:max_per_topic]:
            lines.append(f"- `{rel(path)}`")
        extra = len(grouped[topic]) - max_per_topic
        if extra > 0:
            lines.append(f"- ... {extra} fuentes mas")
        lines.append("")
    return "\n".join(lines)


def write_agent_packet(name: str, body: str) -> Path:
    AGENT_CONTEXT.mkdir(parents=True, exist_ok=True)
    path = AGENT_CONTEXT / name
    path.write_text(body, encoding="utf-8")
    return path


def cmd_revision_local(_: argparse.Namespace) -> None:
    files = all_materials()
    sections = extract_tex_sections()
    extension_counts = count_by_extension(files)
    topic_counts = count_by_topic(files)
    mission_path = ROOT / "docs" / "mision_proyecto.md"
    mission_note = ""
    if mission_path.exists():
        mission_note = f"\nDocumento rector: `{rel(mission_path)}`.\n"

    common = f"""# Paquete comun de revision local

Fecha: {today()}

Este paquete fue generado sin llamadas externas. Usa inventario local, nombres de archivos, practicas editables y capitulos LaTeX.
{mission_note}
Regla superior: organizar el conocimiento segun el temario oficial y la narrativa de aprendizaje, no segun el documento de origen.

{format_counts("Materiales por extension", extension_counts)}

{format_counts("Materiales por tema detectado", topic_counts)}

{format_sources_by_topic(files)}
"""

    tex_lines = ["## Secciones detectadas en el libro LaTeX", ""]
    for source, title in sections[:120]:
        tex_lines.append(f"- `{source}`: {title}")

    master = common + "\n" + "\n".join(tex_lines) + """

## Decision del maestro

Prioridad inmediata:

1. Convertir las fuentes con datos y practicas ya existentes en practicas completas.
2. Separar actividades experimentales de actividades de analisis.
3. Usar el libro LaTeX como columna didactica.
4. Usar PDFs, Excel, DOCX y PPTX como evidencia y material de apoyo.
5. Mantener la pagina como indice de avance, no como producto final cerrado.
"""
    packets = {
        "00_maestro_contexto.md": master,
        "01_estadistica_contexto.md": common + """
## Enfoque para agente estadistico

Revisar cada fuente preguntando:

- Cual es la unidad experimental?
- Hay factores y niveles claramente definidos?
- Hay repeticiones reales o solo mediciones repetidas?
- El analisis propuesto corresponde al diseno?
- Que supuestos deben verificarse antes de ANOVA, MANOVA, ANCOVA o regresion?

Temas con alta prioridad: ANOVA, factorial, Taguchi, MANOVA, ANCOVA y regresion.
""",
        "02_didactica_contexto.md": common + "\n" + "\n".join(tex_lines[:80]) + """

## Enfoque para agente didactico

Ordenar el manual como una ruta:

1. Observar y medir.
2. Comparar grupos.
3. Introducir factores y niveles.
4. Estudiar interacciones.
5. Reducir experimentos con Taguchi.
6. Modelar respuestas continuas.
7. Analizar multiples respuestas.
""",
        "03_lenguaje_contexto.md": common + """
## Enfoque para agente de lenguaje

Mantener una escritura clara, universitaria y cercana. Corregir acentos, titulos y nombres cuando el texto vaya a publicacion, pero conservar nombres de archivo sin renombrarlos automaticamente.
""",
        "04_estilo_roman_contexto.md": common + "\n" + "\n".join(tex_lines[:100]) + """

## Enfoque para agente de estilo

El patron local mas fuerte es: situacion cotidiana -> pregunta experimental -> objetivo -> factores/niveles -> medicion -> analisis -> interpretacion prudente.

No copiar literalmente el libro. Usar su arquitectura explicativa.
""",
        "05_editorial_contexto.md": common + """
## Enfoque para agente editorial

Mantener tres productos sincronizados:

- Practicas Markdown en `practicas/`.
- Libro LaTeX en `docs/libro_latex/`.
- Pagina HTML en `site/index.html`.

La pagina debe mostrar avance y acceso a practicas, no una portada larga.
""",
        "06_revisor_cientifico_editorial_contexto.md": common + """
## Enfoque para agente revisor

Aplicar revision final cientifica, metodologica, editorial y didactica.

Puntos no negociables:

- No aprobar afirmaciones sin evidencia.
- Detectar sesgos, pseudorreplicacion, causalidad exagerada y conclusiones no sostenidas.
- Revisar que cada material pueda estudiarse de forma autonoma por estudiantes universitarios.
- En presentaciones, descomprimir diapositivas saturadas; nunca reducir letra para meter contenido.
- Evaluar si el PDF final parece libro universitario profesional.

Politica obligatoria: `docs/politicas/politica_presentaciones_material_didactico.md`.
""",
    }

    written = [write_agent_packet(name, body) for name, body in packets.items()]
    review_path = MEMORY / "revision_local.md"
    review_path.write_text(master, encoding="utf-8")
    append(
        MEMORY / "bitacora_aprendizaje.md",
        f"\n## {today()} - revision local\n\nEl maestro genero paquetes locales para {len(written)} agentes en `memory/agentes/` y actualizo `memory/revision_local.md`.\n",
    )

    print("Revision local generada.")
    print(f"- {rel(review_path)}")
    for path in written:
        print(f"- {rel(path)}")


def cmd_agentes(_: argparse.Namespace) -> None:
    for path in sorted(AGENTS.glob("*.md")):
        print(f"- {rel(path)}")


def cmd_inventario(_: argparse.Namespace) -> None:
    counts: dict[str, int] = {}
    files = sorted(p for p in RAW.rglob("*") if p.is_file())
    for path in files:
        ext = path.suffix.lower().lstrip(".") or "sin_extension"
        counts[ext] = counts.get(ext, 0) + 1

    print("Inventario de materiales")
    print("========================")
    for ext, count in sorted(counts.items()):
        print(f"{ext}: {count}")
    print()
    print("Primeras fuentes:")
    for path in files[:80]:
        print(f"- {rel(path)}")


def cmd_ensenar(args: argparse.Namespace) -> None:
    nota = args.nota.strip()
    tema = args.tema.strip()
    if not nota:
        raise SystemExit("La nota no puede estar vacia.")

    entry = f"\n## {today()} - {tema}\n\n{nota}\n"
    append(MEMORY / "bitacora_aprendizaje.md", entry)
    append(MEMORY / "estilo_roman.md", f"\n## Aprendizaje {today()} - {tema}\n\n{nota}\n")
    print("Aprendizaje registrado en memoria.")


def slugify(text: str) -> str:
    allowed = []
    for ch in text.lower():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in " -_":
            allowed.append("-")
    slug = "".join(allowed)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "practica"


def cmd_nueva_practica(args: argparse.Namespace) -> None:
    titulo = args.titulo.strip()
    tema = args.tema.strip()
    fuente = args.fuente.strip()
    slug = slugify(titulo)
    path = PRACTICAS / f"{slug}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"Ya existe {rel(path)}. Usa --force para reemplazar.")

    body = f"""# {titulo}

## Situacion de partida

Pendiente de redactar en estilo Roman: iniciar con una situacion cercana que haga visible el problema experimental.

## Objetivo general

Construir una practica de {tema} a partir de la fuente indicada y convertirla en una actividad didactica verificable.

## Evidencia de partida

- Fuente principal: `{fuente or 'pendiente'}`
- Tema: {tema or 'pendiente'}
- Fecha de creacion: {today()}

## Diseno experimental

| Elemento | Definicion inicial |
|---|---|
| Unidad experimental | Pendiente |
| Factores | Pendiente |
| Niveles | Pendiente |
| Tratamientos | Pendiente |
| Repeticiones | Pendiente |
| Variables respuesta | Pendiente |
| Variables controladas | Pendiente |

## Procedimiento

1. Revisar la fuente principal.
2. Extraer problema, factores, variables y datos disponibles.
3. Proponer actividad experimental o de analisis.
4. Validar con el agente estadistico.
5. Reescribir con el agente de estilo.
6. Publicar en la pagina.

## Analisis esperado

Pendiente.

## Limitaciones

No usar conclusiones hasta verificar datos y supuestos.
"""
    path.write_text(body, encoding="utf-8")
    append(MEMORY / "bitacora_aprendizaje.md", f"\n## {today()} - nueva practica\n\nCreada `{rel(path)}` sobre {tema}.\n")
    print(f"Practica creada: {rel(path)}")


def read_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except UnicodeDecodeError:
        pass
    return path.stem.replace("-", " ").title()


def cmd_pagina(_: argparse.Namespace) -> None:
    practices = sorted(
        path for path in PRACTICAS.glob("*.md") if path.name != "plantilla_practica.md"
    )
    agent_count = len(list(AGENTS.glob("*.md")))
    cards = []
    index_path = ROOT / "docs" / "indice_didactico_ade.md"
    if index_path.exists():
        cards.append(
            f"""<article class="practice index">
  <h3>Indice didactico maestro</h3>
  <p>Ruta secuencial del manual: <code>{html.escape(rel(index_path))}</code></p>
</article>"""
        )
    mission_path = ROOT / "docs" / "mision_proyecto.md"
    if mission_path.exists():
        cards.append(
            f"""<article class="practice index">
  <h3>Mision del proyecto</h3>
  <p>Documento rector: <code>{html.escape(rel(mission_path))}</code></p>
</article>"""
        )
    for path in practices:
        title = read_title(path)
        cards.append(
            f"""<article class="practice">
  <h3>{html.escape(title)}</h3>
  <p>Archivo editable: <code>{html.escape(rel(path))}</code></p>
</article>"""
        )

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Practicas ADE</title>
  <style>
    :root {{
      --ink: #1f2933;
      --muted: #52616b;
      --line: #d8dee4;
      --accent: #0f766e;
      --accent-2: #b45309;
      --bg: #f7f8f3;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.5;
    }}
    header {{
      padding: 32px clamp(18px, 4vw, 56px) 22px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(30px, 4vw, 48px);
      letter-spacing: 0;
    }}
    .subtitle {{
      max-width: 820px;
      color: var(--muted);
      margin: 0;
      font-size: 18px;
    }}
    main {{
      padding: 24px clamp(18px, 4vw, 56px) 48px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .metric strong {{
      display: block;
      font-size: 28px;
      color: var(--accent);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }}
    .practice {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 8px;
      padding: 16px;
      min-height: 130px;
    }}
    .practice.index {{
      border-left-color: var(--accent-2);
    }}
    .practice h3 {{
      margin: 0 0 10px;
      font-size: 18px;
    }}
    code {{
      color: var(--accent-2);
      overflow-wrap: anywhere;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Practicas de Analisis y Diseno de Experimentos</h1>
    <p class="subtitle">Indice vivo del manual ADE. Las practicas se educan desde terminal y se alimentan del libro LaTeX, PDFs, hojas de calculo y notas del curso.</p>
  </header>
  <main>
    <section class="summary" aria-label="Resumen">
      <div class="metric"><strong>{len(practices)}</strong> practicas editables</div>
      <div class="metric"><strong>{agent_count}</strong> agentes activos</div>
      <div class="metric"><strong>{today()}</strong> ultima generacion</div>
    </section>
    <section class="grid" aria-label="Practicas">
      {''.join(cards) if cards else '<p>No hay practicas todavia.</p>'}
    </section>
  </main>
</body>
</html>
"""
    SITE.parent.mkdir(parents=True, exist_ok=True)
    SITE.write_text(html_doc, encoding="utf-8")
    print(f"Pagina actualizada: {rel(SITE)}")


def run_interactive_menu() -> None:
    actions = {
        "1": ("Revision local: revisar informacion y repartirla a agentes", cmd_revision_local),
        "2": ("Inventario de materiales", cmd_inventario),
        "3": ("Lista de agentes", cmd_agentes),
        "4": ("Regenerar pagina de practicas", cmd_pagina),
    }

    while True:
        print("\nMaestro ADE")
        print("===========")
        print(f"Proyecto: {ROOT}")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("5. Ensenar una regla nueva")
        print("0. Salir")

        choice = input("\nElige una opcion: ").strip()
        if choice == "0":
            print("Listo. Cierro el maestro.")
            return
        if choice in actions:
            print()
            actions[choice][1](argparse.Namespace())
            input("\nPresiona Enter para volver al menu...")
            continue
        if choice == "5":
            tema = input("Tema: ").strip() or "general"
            nota = input("Nota: ").strip()
            if nota:
                cmd_ensenar(argparse.Namespace(tema=tema, nota=nota))
            else:
                print("No guarde nada porque la nota estaba vacia.")
            input("\nPresiona Enter para volver al menu...")
            continue
        print("Opcion no reconocida.")


def main() -> None:
    if len(sys.argv) == 1:
        run_interactive_menu()
        return

    parser = argparse.ArgumentParser(description="Maestro ADE")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("agentes", help="Lista agentes disponibles")
    p.set_defaults(func=cmd_agentes)

    p = sub.add_parser("inventario", help="Resume materiales descomprimidos")
    p.set_defaults(func=cmd_inventario)

    p = sub.add_parser("revision-local", help="Revisa materiales locales y reparte contexto a agentes")
    p.set_defaults(func=cmd_revision_local)

    p = sub.add_parser("ensenar", help="Registra una correccion o aprendizaje")
    p.add_argument("--tema", required=True)
    p.add_argument("--nota", required=True)
    p.set_defaults(func=cmd_ensenar)

    p = sub.add_parser("nueva-practica", help="Crea una practica editable")
    p.add_argument("--titulo", required=True)
    p.add_argument("--tema", default="")
    p.add_argument("--fuente", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_nueva_practica)

    p = sub.add_parser("pagina", help="Regenera la pagina de practicas")
    p.set_defaults(func=cmd_pagina)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
