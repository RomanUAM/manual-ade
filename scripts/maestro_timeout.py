#!/usr/bin/env python3
"""Maestro ADE: coordina agentes, memoria, practicas y pagina local."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"
MEMORY = ROOT / "memory"
PRACTICAS = ROOT / "practicas"
RAW = ROOT / "data" / "raw"
MANIFESTS = ROOT / "data" / "manifests"
DOCS = ROOT / "docs"
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
    roots = [RAW, MANIFESTS, DOCS, PRACTICAS]
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


def count_by(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


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


def extract_tex_sections(limit_per_file: int = 18) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    pattern = re.compile(r"\\(?:section|subsection|subsubsection)\*?\{(.+?)\}")
    cleanup = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{([^{}]*)\})?")
    for path in sorted((DOCS / "libro_latex").rglob("*.tex")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found = 0
        for match in pattern.finditer(text):
            title = match.group(1).replace("\\texorpdfstring", "")
            title = cleanup.sub(lambda item: item.group(1) or "", title)
            title = re.sub(r"\s+", " ", title).strip("{} ")
            if title:
                sections.append((rel(path), title))
                found += 1
            if found >= limit_per_file:
                break
    return sections


def cmd_agentes(_: argparse.Namespace) -> None:
    for path in sorted(AGENTS.glob("*.md")):
        print(f"- {rel(path)}")


def cmd_inventario(_: argparse.Namespace) -> None:
    files = all_materials()
    ext_counts = count_by([path.suffix.lower().lstrip(".") or "sin_extension" for path in files])
    topic_counts = count_by([topic_for(path) for path in files])
    print("Inventario de materiales")
    print("========================")
    print(format_counts("Por extension", ext_counts))
    print()
    print(format_counts("Por tema", topic_counts))
    print()
    for path in files[:80]:
        print(f"- {rel(path)}")


def cmd_revision_local(_: argparse.Namespace) -> None:
    files = all_materials()
    sections = extract_tex_sections()
    ext_counts = count_by([path.suffix.lower().lstrip(".") or "sin_extension" for path in files])
    topic_counts = count_by([topic_for(path) for path in files])
    mission = DOCS / "mision_proyecto.md"
    mission_note = f"\nDocumento rector: `{rel(mission)}`.\n" if mission.exists() else ""

    common = f"""# Paquete comun de revision local

Fecha: {today()}

Este paquete fue generado sin llamadas externas. Usa inventario local, manifiestos, practicas editables y capitulos LaTeX.
{mission_note}
Regla superior: organizar el conocimiento segun el temario oficial y la narrativa de aprendizaje, no segun el documento de origen.

{format_counts("Materiales por extension", ext_counts)}

{format_counts("Materiales por tema detectado", topic_counts)}

{format_sources_by_topic(files)}
"""
    tex_lines = ["## Secciones detectadas en el libro LaTeX", ""]
    for source, title in sections[:120]:
        tex_lines.append(f"- `{source}`: {title}")

    packets = {
        "00_maestro_contexto.md": common + "\n" + "\n".join(tex_lines),
        "01_estadistica_contexto.md": common + "\n## Enfoque\n\nValidar disenos, supuestos, pruebas, sesgos, pseudorreplicacion y limites.",
        "02_didactica_contexto.md": common + "\n## Enfoque\n\nOrdenar como ruta de aprendizaje: observar, medir, comparar, interactuar, modelar y decidir.",
        "03_lenguaje_contexto.md": common + "\n## Enfoque\n\nRedactar claro, universitario, cercano y preciso.",
        "04_estilo_roman_contexto.md": common + "\n## Enfoque\n\nSituacion cotidiana -> pregunta experimental -> objetivo -> factores/niveles -> medicion -> analisis -> interpretacion prudente.",
        "05_editorial_contexto.md": common + "\n## Enfoque\n\nSincronizar practicas Markdown, libro LaTeX, pagina HTML e identidad visual.",
        "06_revisor_cientifico_editorial_contexto.md": common + "\n## Enfoque\n\nRevision final cientifica, metodologica, editorial y didactica. Descomprimir diapositivas saturadas y exigir calidad de libro universitario.",
    }
    AGENT_CONTEXT.mkdir(parents=True, exist_ok=True)
    for name, body in packets.items():
        (AGENT_CONTEXT / name).write_text(body, encoding="utf-8")
    review_path = MEMORY / "revision_local.md"
    review_path.write_text(packets["00_maestro_contexto.md"], encoding="utf-8")
    append(MEMORY / "bitacora_aprendizaje.md", f"\n## {today()} - revision local\n\nRevision local regenerada para {len(packets)} agentes.\n")
    print("Revision local generada.")
    print(f"- {rel(review_path)}")
    for name in packets:
        print(f"- {rel(AGENT_CONTEXT / name)}")


def cmd_ensenar(args: argparse.Namespace) -> None:
    nota = args.nota.strip()
    tema = args.tema.strip() or "general"
    if not nota:
        raise SystemExit("La nota no puede estar vacia.")
    entry = f"\n## {today()} - {tema}\n\n{nota}\n"
    append(MEMORY / "bitacora_aprendizaje.md", entry)
    append(MEMORY / "estilo_roman.md", f"\n## Aprendizaje {today()} - {tema}\n\n{nota}\n")
    print("Aprendizaje registrado en memoria.")


def slugify(text: str) -> str:
    slug = "".join(ch if ch.isalnum() else "-" for ch in text.lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "practica"


def cmd_nueva_practica(args: argparse.Namespace) -> None:
    title = args.titulo.strip()
    path = PRACTICAS / f"{slugify(title)}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"Ya existe {rel(path)}. Usa --force para reemplazar.")
    body = f"""# {title}

## Situacion de partida

Pendiente de redactar desde una situacion cercana.

## Objetivo general

Construir una practica de {args.tema or 'tema pendiente'} a partir del material disponible.

## Evidencia de partida

- Fuente principal: `{args.fuente or 'pendiente'}`
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

1. Revisar evidencia.
2. Extraer problema, factores, variables y datos.
3. Validar con agentes.
4. Publicar.

## Limitaciones

No usar conclusiones sin verificar datos y supuestos.
"""
    path.write_text(body, encoding="utf-8")
    append(MEMORY / "bitacora_aprendizaje.md", f"\n## {today()} - nueva practica\n\nCreada `{rel(path)}`.\n")
    print(f"Practica creada: {rel(path)}")


def read_title(path: Path) -> str:
    return path.stem.replace("-", " ").title()


def cmd_pagina(_: argparse.Namespace) -> None:
    practices = sorted(path for path in PRACTICAS.glob("*.md") if path.name != "plantilla_practica.md")
    agent_count = len(list(AGENTS.glob("*.md")))
    files = all_materials()
    topic_counts = count_by([topic_for(path) for path in files])
    ext_counts = count_by([path.suffix.lower().lstrip(".") or "sin_extension" for path in files])
    modules = [
        {
            "num": 1,
            "title": "Pensar experimentalmente",
            "goal": "Transformar una observacion cotidiana en una pregunta experimental clara.",
            "remember": "Distinguir observar, medir, comparar y explicar.",
            "topics": ["experimento", "unidad experimental", "variable respuesta", "control"],
            "materials": ["Analisis-de-Experimentos.pdf", "Diseno-de-experimentos-en-ingenieria.pdf", "Logica-hipotesis-y-construccion-del-conocimiento-cientifico.pdf"],
            "practice": "Del problema cotidiano a la pregunta experimental",
            "agents": "Didactica, lenguaje, estilo Roman",
        },
        {
            "num": 2,
            "title": "Datos, muestreo y variabilidad",
            "goal": "Entender que la variabilidad es informacion para decidir.",
            "remember": "La muestra modifica lo que creemos ver en los datos.",
            "topics": ["muestreo", "media", "varianza", "datos atipicos"],
            "materials": ["Capitulos/04-anova.tex", "Indice de Gini y metodos de muestreo", "Trabajo de gatos"],
            "practice": "Muestreo y grandes numeros en un fenomeno observable",
            "agents": "Estadistica, didactica",
        },
        {
            "num": 3,
            "title": "ANOVA de un factor",
            "goal": "Comparar tres o mas grupos usando evidencia y no solo medias visibles.",
            "remember": "ANOVA compara variabilidad entre grupos contra variabilidad dentro de grupos.",
            "topics": ["hipotesis", "F", "valor p", "supuestos"],
            "materials": ["ANOVA-de-un-factor-Prueba-F-y-valor-P.pdf", "ANOVA.xlsx", "Capitulos/00-ANOVA.tex"],
            "practice": "Comparar tratamientos con una sola respuesta",
            "agents": "Estadistica, lenguaje",
        },
        {
            "num": 4,
            "title": "ANOVA de dos factores",
            "goal": "Separar efectos principales de interacciones.",
            "remember": "Una interaccion aparece cuando el efecto de un factor cambia segun el nivel del otro.",
            "topics": ["factor A", "factor B", "efectos principales", "interaccion"],
            "materials": ["ANOVA-de-2-Factores.pdf", "ANOVA-Factorial-2-y-2.pdf"],
            "practice": "Dos factores, una respuesta y una decision experimental",
            "agents": "Estadistica, didactica",
        },
        {
            "num": 5,
            "title": "Diseno factorial 2x2",
            "goal": "Construir tratamientos combinando niveles bajos y altos.",
            "remember": "El diseno 2x2 permite estudiar dos factores y su interaccion con cuatro tratamientos.",
            "topics": ["2^2", "tratamientos", "repeticiones", "blanco experimental"],
            "materials": ["Capitulos/02-conceptos.tex", "Practica 2^2 A&D.pdf", "Plantilla factorial 2x2"],
            "practice": "Sustancias, interacciones y cambios visuales en papel",
            "agents": "Estadistica, didactica, estilo Roman",
        },
        {
            "num": 6,
            "title": "Factoriales aplicados",
            "goal": "Usar disenos factoriales en procesos manuales, productos y materiales.",
            "remember": "En aplicaciones reales hay replicas desiguales, ruido y limites de control.",
            "topics": ["replicas desiguales", "proceso manual", "materiales", "decision"],
            "materials": ["Optimizacion de proceso manual", "Separadores artesanales", "Material compuesto"],
            "practice": "Optimizacion de un proceso manual no balanceado",
            "agents": "Estadistica, editorial, revisor",
        },
        {
            "num": 7,
            "title": "Diseno Taguchi",
            "goal": "Reducir tratamientos manteniendo la logica experimental.",
            "remember": "Taguchi ayuda a explorar factores con menos corridas, pero exige interpretacion prudente.",
            "topics": ["L4(2^3)", "robustez", "escala ordinal", "exploratorio"],
            "materials": ["Capitulos/03-disenos-clasicos.tex", "Video 1_taguchi.pdf", "Violeta africana"],
            "practice": "Violeta africana en sistemas biologicos confinados",
            "agents": "Estadistica, didactica, estilo Roman",
        },
        {
            "num": 8,
            "title": "Regresion y modelado",
            "goal": "Explicar una respuesta continua mediante variables predictoras.",
            "remember": "Un modelo no solo ajusta datos: tambien debe interpretarse y diagnosticarse.",
            "topics": ["modelo lineal", "predictor", "respuesta", "diagnostico"],
            "materials": ["Modelado-Parte-II.pdf", "Modelos de regresion.pdf", "Regresion-Lineal.pdf"],
            "practice": "Modelar una respuesta continua en un proceso experimental",
            "agents": "Estadistica, lenguaje",
        },
        {
            "num": 9,
            "title": "ANCOVA",
            "goal": "Comparar tratamientos considerando covariables.",
            "remember": "Una covariable puede cambiar la interpretacion de diferencias entre grupos.",
            "topics": ["covariable", "ajuste", "medias ajustadas", "confusion"],
            "materials": ["Analisis-de-Covarianza-ANCOVA.pdf"],
            "practice": "Comparar grupos ajustando una respuesta por covariables",
            "agents": "Estadistica, revisor",
        },
        {
            "num": 10,
            "title": "MANOVA",
            "goal": "Analizar experimentos con multiples respuestas simultaneas.",
            "remember": "MANOVA evita fragmentar decisiones cuando varias respuestas describen el desempeno.",
            "topics": ["multiples respuestas", "multivariado", "respuesta conjunta", "interpretacion"],
            "materials": ["Ejemplo-Practico-de-MANOVA.pdf", "Rendimiento termico.pptx", "Articulo Manova.pdf"],
            "practice": "Multiples respuestas en rendimiento termico",
            "agents": "Estadistica, editorial, revisor",
        },
        {
            "num": 11,
            "title": "Proyecto integrador",
            "goal": "Unir problema, diseno, datos, analisis, conclusion y limites.",
            "remember": "Un proyecto experimental vale por la coherencia entre pregunta, metodo y evidencia.",
            "topics": ["proyecto", "datos", "discusion", "limitaciones"],
            "materials": ["DatosAcustica.xlsx", "Proyecto Final DAEI.pdf", "Compositos acusticos.pdf"],
            "practice": "Proyecto final de diseno experimental aplicado",
            "agents": "Maestro, estadistica, editorial, revisor",
        },
    ]

    nav_items = []
    module_cards = []
    for module in modules:
        anchor = f"modulo-{module['num']}"
        nav_items.append(f"<a href=\"#{anchor}\"><span>{module['num']:02d}</span>{html.escape(module['title'])}</a>")
        topics = "".join(f"<li>{html.escape(item)}</li>" for item in module["topics"])
        materials = "".join(f"<li>{html.escape(item)}</li>" for item in module["materials"])
        module_cards.append(
            f"""<section class="module" id="{anchor}">
  <div class="module-number">{module['num']:02d}</div>
  <div class="module-body">
    <h2>{html.escape(module['title'])}</h2>
    <p class="goal">{html.escape(module['goal'])}</p>
    <div class="remember"><strong>En 30 segundos:</strong> {html.escape(module['remember'])}</div>
    <div class="module-grid">
      <div>
        <h3>Conceptos clave</h3>
        <ul>{topics}</ul>
      </div>
      <div>
        <h3>Material que se aprovecha</h3>
        <ul>{materials}</ul>
      </div>
      <div>
        <h3>Producto didactico</h3>
        <p>{html.escape(module['practice'])}</p>
        <p class="agents">{html.escape(module['agents'])}</p>
      </div>
    </div>
  </div>
</section>"""
        )

    topic_badges = "".join(
        f"<span><strong>{html.escape(topic)}</strong>{count}</span>"
        for topic, count in sorted(topic_counts.items())
        if topic != "general"
    )
    ext_badges = "".join(
        f"<span><strong>{html.escape(ext)}</strong>{count}</span>"
        for ext, count in sorted(ext_counts.items())
        if ext in {"pdf", "xlsx", "docx", "pptx", "mp4", "tex", "txt", "md"}
    )
    practice_links = "".join(
        f"<li><code>{html.escape(rel(path))}</code></li>" for path in practices
    )
    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Manual ADE</title>
  <style>
    :root {{ --ink:#1f2933; --muted:#52616b; --line:#d8dee4; --accent:#0f766e; --accent-2:#b45309; --bg:#f7f8f3; --panel:#fff; --soft:#eef6f4; --warn:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:var(--bg); line-height:1.5; }}
    header {{ padding:28px clamp(18px,4vw,56px); border-bottom:1px solid var(--line); background:#fff; }}
    h1 {{ margin:0 0 8px; font-size:clamp(30px,4vw,46px); letter-spacing:0; }}
    h2, h3 {{ letter-spacing:0; }}
    .subtitle {{ max-width:980px; color:var(--muted); margin:0; font-size:18px; }}
    .layout {{ display:grid; grid-template-columns:280px 1fr; gap:22px; padding:22px clamp(18px,4vw,56px) 48px; }}
    nav {{ position:sticky; top:0; align-self:start; background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; max-height:calc(100vh - 24px); overflow:auto; }}
    nav h2 {{ font-size:15px; margin:0 0 10px; color:var(--muted); text-transform:uppercase; }}
    nav a {{ display:flex; gap:8px; align-items:flex-start; padding:8px; border-radius:6px; color:var(--ink); text-decoration:none; font-size:14px; }}
    nav a:hover {{ background:var(--soft); }}
    nav span {{ color:var(--accent); font-weight:700; min-width:28px; }}
    main {{ min-width:0; }}
    .summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin-bottom:18px; }}
    .metric {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px 16px; }}
    .metric strong {{ display:block; font-size:28px; color:var(--accent); }}
    .mission {{ background:var(--panel); border:1px solid var(--line); border-left:5px solid var(--accent-2); border-radius:8px; padding:16px; margin-bottom:18px; }}
    .mission h2 {{ margin:0 0 8px; font-size:20px; }}
    .badges {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
    .badges span {{ background:var(--soft); border:1px solid var(--line); border-radius:999px; padding:6px 10px; font-size:13px; }}
    .badges strong {{ margin-right:6px; color:var(--accent); }}
    .module {{ display:grid; grid-template-columns:64px 1fr; gap:14px; background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; margin-bottom:14px; scroll-margin-top:12px; }}
    .module-number {{ width:52px; height:52px; display:grid; place-items:center; border-radius:8px; background:var(--accent); color:#fff; font-weight:800; }}
    .module h2 {{ margin:0 0 6px; font-size:24px; }}
    .goal {{ margin:0 0 10px; color:var(--muted); font-size:17px; }}
    .remember {{ background:var(--warn); border:1px solid #fed7aa; border-radius:8px; padding:10px 12px; margin-bottom:12px; }}
    .module-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .module-grid h3 {{ margin:0 0 6px; font-size:14px; text-transform:uppercase; color:var(--muted); }}
    ul {{ margin:0; padding-left:18px; }}
    .agents {{ color:var(--muted); font-size:14px; margin:8px 0 0; }}
    .resources {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; margin-top:18px; }}
    .resources h2 {{ margin:0 0 10px; }}
    code {{ color:var(--accent-2); overflow-wrap:anywhere; }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns:1fr; }}
      nav {{ position:relative; max-height:none; }}
      .module {{ grid-template-columns:1fr; }}
      .module-grid {{ grid-template-columns:1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Manual integral de Diseno y Analisis de Experimentos</h1>
    <p class="subtitle">Ruta didactica para estudiar la UEA desde el material disponible: teoria, practicas, datos, examenes, proyectos, presentaciones, codigo e imagenes reorganizados por aprendizaje.</p>
  </header>
  <div class="layout">
    <nav aria-label="Temario">
      <h2>Temario navegable</h2>
      {''.join(nav_items)}
    </nav>
    <main>
      <section class="summary" aria-label="Resumen">
        <div class="metric"><strong>{len(modules)}</strong> modulos</div>
        <div class="metric"><strong>{len(practices)}</strong> practicas editables</div>
        <div class="metric"><strong>{agent_count}</strong> agentes activos</div>
        <div class="metric"><strong>{today()}</strong> actualizacion</div>
      </section>
      <section class="mission">
        <h2>Mision didactica</h2>
        <p>El manual no se organiza por carpetas de origen. Integra el material existente en una secuencia universitaria: primero pensar experimentalmente, despues medir y comparar, luego estudiar interacciones, reducir experimentos, modelar y cerrar con proyectos integradores.</p>
        <div class="badges">{topic_badges}</div>
      </section>
      {''.join(module_cards)}
      <section class="resources">
        <h2>Material disponible y productos vivos</h2>
        <p>El maestro aprovecha fuentes locales y manifiestos sin gastar llamadas externas. Estadistica permanece indexada por manifiesto por falta de espacio en disco.</p>
        <div class="badges">{ext_badges}</div>
        <h3>Practicas editables</h3>
        <ul>{practice_links}</ul>
        <h3>Documentos rectores</h3>
        <ul>
          <li><code>docs/mision_proyecto.md</code></li>
          <li><code>docs/indice_didactico_ade.md</code></li>
          <li><code>docs/politicas/politica_presentaciones_material_didactico.md</code></li>
        </ul>
      </section>
    </main>
  </div>
</body>
</html>
"""
    SITE.parent.mkdir(parents=True, exist_ok=True)
    tmp_site = SITE.with_suffix(".html.tmp")
    tmp_site.write_text(html_doc, encoding="utf-8")
    os.replace(tmp_site, SITE)
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
            actions[choice][1](argparse.Namespace())
            input("\nPresiona Enter para volver al menu...")
        elif choice == "5":
            tema = input("Tema: ").strip() or "general"
            nota = input("Nota: ").strip()
            if nota:
                cmd_ensenar(argparse.Namespace(tema=tema, nota=nota))
            input("\nPresiona Enter para volver al menu...")
        else:
            print("Opcion no reconocida.")


def main() -> None:
    if len(sys.argv) == 1:
        run_interactive_menu()
        return
    parser = argparse.ArgumentParser(description="Maestro ADE")
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("agentes", help="Lista agentes disponibles")
    p.set_defaults(func=cmd_agentes)
    p = sub.add_parser("inventario", help="Resume materiales")
    p.set_defaults(func=cmd_inventario)
    p = sub.add_parser("revision-local", help="Revisa materiales locales y reparte contexto")
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
    p = sub.add_parser("pagina", help="Regenera la pagina")
    p.set_defaults(func=cmd_pagina)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
