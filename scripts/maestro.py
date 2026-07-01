#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "agents"
MEMORY = ROOT / "memory"
PRACTICAS = ROOT / "practicas"
DOCS = ROOT / "docs"
RAW = ROOT / "data" / "raw"
MANIFESTS = ROOT / "data" / "manifests"
SITE = ROOT / "site" / "index.html"
SITE_MANUAL_PDF = ROOT / "site" / "manual_integrado_ade.pdf"
SITE_DRAFT_PDF = ROOT / "site" / "borrador_integracion_ade.pdf"
SITE_BASE_MANUAL_PDF = ROOT / "site" / "manual_base_latex_compilado.pdf"
SITE_PRESENTATION_PDF = ROOT / "site" / "presentacion_integrada_ade.pdf"
SITE_HAG = ROOT / "site" / "hag"
REPO_URL = "https://github.com/RomanUAM/manual-ade"
PROJECT_AUTHORS = [
    "Roman Anselmo Mora-Gutierrez",
    "Edwin Montes-Orozco",
    "Eric Alfredo Rincon-Garcia",
    "Sergio G. de-los-Cobos-Silva",
    "Pedro Lara-Velazquez",
    "Miguel Angel Gutierrez-Andrade",
    "Gilberto Sinuhe Torres-Cockrell",
    "Isrrael Satiago Rubio",
    "Oswaldo Sanchez Andrade",
    "Oscar Antonio Manzanares Betancourt",
    "Yadira Alatriste Martinez",
    "Cesar Simon Lopez Monsalvo",
    "Luis Angel Meza Zarate",
]


def today() -> str:
    return dt.date.today().isoformat()


def today_label() -> str:
    months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    now = dt.date.today()
    return f"{now.day} {months[now.month - 1]} {now.year}"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def all_files() -> list[Path]:
    files: list[Path] = []
    for root in (RAW, MANIFESTS, DOCS, PRACTICAS):
        if root.exists():
            files.extend(p for p in root.rglob("*") if p.is_file())
    return sorted(files)


def topic(path: Path) -> str:
    name = rel(path).lower()
    rules = {
        "MANOVA": ["manova", "multivariado"],
        "ANCOVA": ["ancova", "covarianza"],
        "ANOVA": ["anova", "prueba-f", "valor-p"],
        "factorial": ["factorial", "2x2", "2^2"],
        "Taguchi": ["taguchi", "l4"],
        "regresion": ["regresion", "modelado"],
        "probabilidad": ["probabilidad", "estadistica", "azar", "bayes"],
        "logica": ["logica", "hipotesis", "algoritmos"],
        "muestreo": ["muestreo", "gini", "gatos"],
        "presentaciones": ["presentacion", "diapositiva", "pptx"],
    }
    for key, words in rules.items():
        if any(word in name for word in words):
            return key
    return "general"


def counts(items: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return out


def safe_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_research_matrix() -> list[dict]:
    path = MEMORY / "materiales_investigados.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in data if item.get("status") == "leido" and item.get("confidence", 0) > 0]


def research_matrix_html(items: list[dict]) -> str:
    if not items:
        return """
        <section class="research-matrix">
          <h2>Matriz de lectura investigadora</h2>
          <p>Pendiente de generar. Ejecuta <code>python3 scripts/investigar_material.py</code> para clasificar por contenido real.</p>
        </section>"""
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(item.get("chapter", "Sin clasificacion"), []).append(item)
    blocks = []
    for chapter in sorted(grouped):
        cards = []
        for item in sorted(grouped[chapter], key=lambda x: -int(x.get("confidence", 0)))[:3]:
            fields = item.get("fields", {})
            evidence = ""
            for key in ("problema", "factores", "respuesta", "diseno", "practica"):
                values = fields.get(key) or []
                if values:
                    evidence = values[0]
                    break
            cards.append(f"""
              <article>
                <h4>{html.escape(item.get("title", "Material leido"))}</h4>
                <p>{html.escape(item.get("use", ""))}</p>
                <small>{html.escape(evidence[:260])}</small>
              </article>""")
        blocks.append(f"""
          <div class="research-group">
            <h3>{html.escape(chapter)}</h3>
            <div class="research-cards">{''.join(cards)}</div>
          </div>""")
    return f"""
    <section class="research-matrix">
      <h2>Matriz de lectura investigadora</h2>
      <p>Esta agrupacion se construye leyendo contenido: problema, factores, variables respuesta, diseno, practica y decision. No clasifica por nombre de archivo.</p>
      {''.join(blocks)}
    </section>"""


def system_architecture_html() -> str:
    steps = [
        ("Ingesta", "Lee material local y registra estado de lectura."),
        ("Extraccion", "Convierte documentos en fichas de conocimiento."),
        ("Normalizacion", "Usa vocabulario experimental comun."),
        ("Agrupacion", "Ordena por preguntas de aprendizaje."),
        ("Sintesis", "Construye narrativa, practica y actividad."),
        ("Produccion", "Publica pagina, PDF y practicas editables."),
        ("Revision", "Audita rigor, didactica y calidad editorial."),
        ("Aprendizaje", "Guarda reglas nuevas en memoria."),
    ]
    cards = "".join(f"<article><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></article>" for title, body in steps)
    return f"""
    <section class="system-architecture">
      <h2>Sistema autoadaptable de conocimiento</h2>
      <p>Los agentes funcionan como operaciones sobre una base de notas. No son personajes: son tareas verificables de ingenieria de conocimiento aplicada a IA educativa.</p>
      <div>{cards}</div>
    </section>"""


def authors_html() -> str:
    names = "".join(f"<li>{html.escape(name)}</li>" for name in PROJECT_AUTHORS)
    return f"""
    <section class="authors">
      <h2>Autores y colaboradores academicos</h2>
      <p>La pagina presenta materiales generados o autorizados por el proyecto. Las referencias externas se usan solo como insumo interno y no se redistribuyen.</p>
      <ul>{names}</ul>
    </section>"""


def hag_summary() -> dict:
    graph_path = ROOT / "knowledge" / "hag_graph.json"
    audit_path = ROOT / "evidence" / "hag" / "audit_result.json"
    extraction_path = ROOT / "evidence" / "hag" / "extraction_report.json"
    data = {"nodes": [], "audit": {"status": "pendiente", "failures": []}, "extraction": {}}
    if graph_path.exists():
        try:
            data["nodes"] = json.loads(graph_path.read_text(encoding="utf-8")).get("nodes", [])
        except (OSError, json.JSONDecodeError):
            data["nodes"] = []
    if audit_path.exists():
        try:
            data["audit"] = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data["audit"] = {"status": "error", "failures": ["No se pudo leer evidence/hag/audit_result.json"]}
    if extraction_path.exists():
        try:
            data["extraction"] = json.loads(extraction_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data["extraction"] = {"error": "No se pudo leer evidence/hag/extraction_report.json"}
    return data


def hag_panel_html() -> str:
    data = hag_summary()
    node_count = len(data["nodes"])
    status = data["audit"].get("status", "pendiente")
    failures = data["audit"].get("failures", [])
    status_label = "Rechaza entrega" if status == "fail" else "Acepta entrega"
    return f"""
    <section class="hag-panel">
      <div>
        <h2>Sistema HAG</h2>
        <p>Motor auditable de conocimiento: grafo unico, agentes con evidencia y brechas visibles. Si falta algun recurso, el sistema lo declara en lugar de ocultarlo.</p>
      </div>
      <div class="hag-status">
        <strong>{html.escape(status_label)}</strong>
        <span>{node_count} nodos de conocimiento</span>
        <span>{len(failures)} brechas activas</span>
      </div>
      <a href="hag/">Abrir dashboard HAG</a>
    </section>"""


def source_code_html() -> str:
    links = [
        ("Repositorio completo", REPO_URL),
        ("Motor Python HAG", f"{REPO_URL}/tree/main/hag"),
        ("Scripts Python", f"{REPO_URL}/tree/main/scripts"),
        ("Agentes", f"{REPO_URL}/tree/main/agents"),
        ("Pruebas", f"{REPO_URL}/tree/main/tests"),
        ("Descargar ZIP", f"{REPO_URL}/archive/refs/heads/main.zip"),
    ]
    items = "".join(f'<a href="{html.escape(url)}" target="_blank">{html.escape(label)}</a>' for label, url in links)
    return f"""
    <section class="source-code">
      <div>
        <h2>Codigo fuente y carpeta Python</h2>
        <p>GitHub Pages publica solo la carpeta <code>site/</code>. El sistema Python completo vive en el repositorio: <code>hag/</code>, <code>scripts/</code>, <code>agents/</code> y <code>tests/</code>.</p>
      </div>
      <div class="source-links">{items}</div>
    </section>"""


def chatbot_html() -> str:
    return """
    <section class="chatbot">
      <div>
        <h2>Chatbot academico local</h2>
        <p>Consulta la base de conocimiento generada por el HAG. Responde solo con materiales integrados: practica, manual y presentacion enriquecida.</p>
      </div>
      <div class="chat-row">
        <input id="chat-query" type="search" placeholder="Pregunta por Taguchi, MANOVA, Gini, ANCOVA..." aria-label="Pregunta al chatbot academico">
        <button id="chat-button" type="button">Consultar</button>
      </div>
      <div id="chat-answer" class="chat-answer">Escribe una pregunta para recuperar materiales conectados.</div>
    </section>
    <script>
    (() => {
      const repo = "https://github.com/RomanUAM/manual-ade/blob/main/";
      const input = document.getElementById("chat-query");
      const button = document.getElementById("chat-button");
      const answer = document.getElementById("chat-answer");
      let kb = [];
      fetch("chatbot_kb.json").then(r => r.ok ? r.json() : {items: []}).then(data => { kb = data.items || []; }).catch(() => { kb = []; });
      function esc(value) {
        return String(value || "").replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
      }
      function ask() {
        const q = (input.value || "").toLowerCase().trim();
        if (!q) {
          answer.innerHTML = "Escribe una pregunta para recuperar materiales conectados.";
          return;
        }
        const terms = q.split(/\\s+/).filter(Boolean);
        const scored = kb.map(item => {
          const text = [item.title, item.topic, item.chapter, item.summary, ...(item.activities || [])].join(" ").toLowerCase();
          const score = terms.reduce((acc, term) => acc + (text.includes(term) ? 1 : 0), 0);
          return {item, score};
        }).filter(x => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 3);
        if (!scored.length) {
          answer.innerHTML = "<p>No encontre una coincidencia integrada. Eso debe registrarse como brecha del HAG, no inventarse.</p>";
          return;
        }
        answer.innerHTML = scored.map(({item}) => {
          const links = (item.links || []).map(link => {
            const path = String(link.path || "");
            const href = path.startsWith("site/") ? path.replace(/^site\\//, "") : `${repo}${encodeURIComponent(path).replaceAll('%2F','/')}`;
            return `<a target="_blank" href="${href}">${esc(link.label)}</a>`;
          }).join("");
          return `<article><h3>${esc(item.title)}</h3><p>${esc(item.summary)}</p><div>${links}</div></article>`;
        }).join("");
      }
      button.addEventListener("click", ask);
      input.addEventListener("keydown", event => { if (event.key === "Enter") ask(); });
    })();
    </script>"""


def write_hag_dashboard() -> None:
    SITE_HAG.mkdir(parents=True, exist_ok=True)
    data = hag_summary()
    graph_src = ROOT / "knowledge" / "hag_graph.json"
    audit_src = ROOT / "evidence" / "hag" / "audit_result.json"
    extraction_src = ROOT / "evidence" / "hag" / "extraction_report.json"
    gaps_src = ROOT / "artifacts" / "hag" / "brechas_ecosistema.md"
    if graph_src.exists():
        shutil.copy2(graph_src, SITE_HAG / "hag_graph.json")
    if audit_src.exists():
        shutil.copy2(audit_src, SITE_HAG / "audit_result.json")
    if extraction_src.exists():
        shutil.copy2(extraction_src, SITE_HAG / "extraction_report.json")
    if gaps_src.exists():
        shutil.copy2(gaps_src, SITE_HAG / "brechas_ecosistema.md")

    nodes = data["nodes"]
    failures = data["audit"].get("failures", [])
    extraction = data.get("extraction", {})
    reader = extraction.get("reader", {})
    node_cards = []
    for node in nodes:
        artifacts = node.get("artifacts", [])
        wanted = ["book_chapter", "presentation", "practice", "exercise", "solution", "evaluation", "code", "infographic"]
        labels = {
            "book_chapter": "Guia",
            "presentation": "Presentacion",
            "practice": "Practica",
            "exercise": "Ejercicios",
            "solution": "Soluciones",
            "evaluation": "Evaluacion",
            "code": "Simulador",
            "infographic": "Infografia",
        }
        links = []
        by_kind = {item.get("kind"): item for item in artifacts}
        for kind in wanted:
            item = by_kind.get(kind)
            if not item:
                links.append(f"<span class=\"missing\">{html.escape(labels[kind])}</span>")
                continue
            path = item.get("path", "")
            url = html.escape(f"{REPO_URL}/blob/main/{path}")
            links.append(f"<a href=\"{url}\" target=\"_blank\">{html.escape(labels[kind])}</a>")
        node_cards.append(f"""
        <article>
          <h3>{html.escape(node.get("title", node.get("id", "Nodo")))}</h3>
          <p>{html.escape(node.get("question", ""))}</p>
          <div class="resource-links">{''.join(links)}</div>
        </article>""")
    failure_items = "".join(f"<li>{html.escape(item)}</li>" for item in failures) or "<li>Sin brechas registradas.</li>"
    failure_title = "Brechas activas" if failures else "Ecosistema conectado"
    failure_intro = "Mientras existan estas brechas, HAG rechaza la entrega completa del ecosistema." if failures else "Cada capitulo cuenta con los recursos minimos para estudiar, practicar, explicar, simular y evaluar."
    object_types = extraction.get("object_types", {})
    type_items = "".join(f"<span>{html.escape(key)}: {value}</span>" for key, value in sorted(object_types.items())) or "<span>Pendiente</span>"
    scanned_dirs = ", ".join(reader.get("top_level_dirs_scanned", [])) or "pendiente"
    skipped_dirs = ", ".join(reader.get("top_level_dirs_skipped", [])) or "pendiente"
    page = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard HAG</title>
<style>
body{{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f6f8fb;color:#1c2630;line-height:1.5}}
header,main{{padding:28px clamp(18px,4vw,64px)}} header{{background:#fff;border-bottom:1px solid #d9e0e5}} h1{{margin:0;font-size:clamp(30px,4vw,48px)}} .subtitle{{color:#5b6773;max-width:900px}} .status{{display:inline-flex;gap:10px;flex-wrap:wrap;margin-top:12px}} .status span{{border:1px solid #d9e0e5;border-radius:999px;background:#edf7f5;padding:6px 10px;font-size:14px}} .actions{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}} .actions a{{background:#0f766e;color:white;text-decoration:none;border-radius:8px;padding:10px 12px;font-weight:750}} section{{background:white;border:1px solid #d9e0e5;border-radius:8px;padding:18px;margin:18px 0}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}} article{{border:1px solid #d9e0e5;border-radius:8px;padding:14px;background:#fff}} article h3{{margin:0 0 8px}} .resource-links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}} .resource-links a,.resource-links span{{display:inline-block;background:#edf7f5;border:1px solid #d9e0e5;border-radius:8px;padding:7px 9px;font-size:13px;text-decoration:none;color:#0f766e;font-weight:700}} .resource-links .missing{{background:#fff4e6;color:#a23e19}} article span{{display:inline-block;background:#edf7f5;border:1px solid #d9e0e5;border-radius:999px;padding:4px 8px;margin:4px 4px 0 0;font-size:12px}} li{{margin:6px 0}} code{{color:#a23e19}}
</style>
</head>
<body>
<header>
  <h1>Dashboard HAG</h1>
  <p class="subtitle">Vista publica del sistema de autocrítica: grafo de conocimiento, artefactos conectados y brechas que impiden declarar terminado el ecosistema.</p>
  <div class="status"><span>Estado: {html.escape(data["audit"].get("status", "pendiente"))}</span><span>Nodos: {len(nodes)}</span><span>Brechas: {len(failures)}</span><span>Objetos: {html.escape(str(extraction.get("objects_extracted", "pendiente")))}</span></div>
  <div class="actions"><a href="../">Volver al manual</a><a href="{html.escape(REPO_URL)}" target="_blank">Repositorio completo</a><a href="{html.escape(REPO_URL)}/tree/main/hag" target="_blank">Carpeta Python HAG</a><a href="hag_graph.json">Grafo JSON</a><a href="audit_result.json">Auditoria JSON</a><a href="extraction_report.json">Extraccion JSON</a><a href="brechas_ecosistema.md">Brechas MD</a></div>
</header>
<main>
  <section><h2>Motor de extraccion y reutilizacion</h2><p>El HAG primero extrae objetos de aprendizaje y bancos reutilizables antes de generar contenido nuevo. La lectura PDF operativa usa una ventana inicial por archivo; la lectura profunda queda pendiente para capitulos especificos.</p><div class="status"><span>Archivos escaneados: {html.escape(str(extraction.get("files_scanned", "pendiente")))}</span><span>Objetos extraidos: {html.escape(str(extraction.get("objects_extracted", "pendiente")))}</span><span>PDF detectados: {html.escape(str(reader.get("pdf_total", "pendiente")))}</span><span>PDF leidos: {html.escape(str(reader.get("pdf_read", "pendiente")))}</span><span>Paginas por PDF: {html.escape(str(reader.get("pdf_pages_per_file", "pendiente")))}</span>{type_items}</div><p><strong>Carpetas de trabajo exploradas:</strong> {html.escape(scanned_dirs)}.</p><p><strong>Carpetas tecnicas omitidas:</strong> {html.escape(skipped_dirs)}.</p></section>
  <section><h2>Ruta de aprendizaje por capitulo</h2><p>Cada capitulo debe tener guia, presentacion, practica, ejercicios, solucion, evaluacion, simulador e infografia. Si falta algo, el HAG lo genera como primera version editable y lo deja conectado.</p><div class="grid">{''.join(node_cards)}</div></section>
  <section><h2>{html.escape(failure_title)}</h2><p>{html.escape(failure_intro)}</p><ul>{failure_items}</ul></section>
  <section><h2>Como ejecutarlo localmente</h2><pre><code>python3 scripts/hag.py build
python3 scripts/hag.py audit
python3 scripts/hag_api.py --port 8787</code></pre></section>
</main>
</body>
</html>"""
    (SITE_HAG / "index.html").write_text(page, encoding="utf-8")


CHAPTERS = [
    {
        "question": "Por que necesitamos disenar experimentos?",
        "promise": "El estudiante descubre que experimentar no es probar cosas al azar, sino construir evidencia para decidir.",
        "motivation": "Toda decision de ingenieria implica ruido, variabilidad y riesgo de atribuir causas falsas.",
        "intuition": "Como comparar dos recetas, dos materiales o dos procesos sin enganarse por una observacion aislada.",
        "guided": "Reconstruir una situacion cotidiana hasta convertirla en pregunta, variable respuesta y unidad experimental.",
        "practices": "Observacion guiada, diagnostico de un experimento mal planteado y mini practica de formulacion.",
        "errors": "Confundir observacion con experimento; medir sin definir respuesta; cambiar varias condiciones sin control.",
        "case": "Experiencias de clase, logica de hipotesis y materiales introductorios del curso se integran como una sola entrada narrativa.",
        "connection": "Una vez que existe pregunta experimental, el siguiente problema es aprender a medir con variabilidad.",
    },
    {
        "question": "Como convertir datos dispersos en informacion confiable?",
        "promise": "El estudiante entiende que media, varianza y muestreo son herramientas para no decidir por impresion.",
        "motivation": "Dos equipos pueden observar el mismo fenomeno y llegar a conclusiones distintas si muestrean diferente.",
        "intuition": "La variabilidad se entiende como el movimiento natural de los datos alrededor de una historia central.",
        "guided": "Construir una tabla de frecuencias, una media y una varianza a partir de observaciones de campo.",
        "practices": "Muestreo empirico, analisis de datos de campus y lectura critica de valores atipicos.",
        "errors": "Usar pocos datos; borrar atipicos sin justificar; comparar promedios sin mirar dispersion.",
        "case": "El trabajo de gatos y los materiales de estadistica descriptiva se funden en un capitulo sobre incertidumbre observable.",
        "connection": "Cuando sabemos medir variabilidad, podemos preguntar si varios grupos son realmente diferentes.",
    },
    {
        "question": "Como saber si varios tratamientos producen respuestas distintas?",
        "promise": "El estudiante aprende ANOVA como razonamiento de variabilidad, no como tabla mecanica.",
        "motivation": "En ingenieria rara vez basta comparar dos valores; se comparan procesos, grupos o tratamientos completos.",
        "intuition": "ANOVA pregunta si la variacion entre grupos es grande frente a la variacion natural dentro de ellos.",
        "guided": "Resolver paso a paso un ANOVA de un factor: hipotesis, suma de cuadrados, F, valor p y decision.",
        "practices": "Comparacion sencilla de tratamientos y autoevaluacion de supuestos. Las hojas de calculo se usan por dentro para construir tablas y graficas, no como material descargable principal.",
        "errors": "Decir que hay diferencia sin revisar supuestos; interpretar valor p como tamano del efecto; olvidar replicas.",
        "case": "Los ejercicios de ANOVA y las hojas de calculo se convierten en una historia de comparacion: que cambia, cuanto cambia y con que incertidumbre.",
        "connection": "Si una respuesta depende de mas de un factor, necesitamos estudiar efectos simultaneos.",
    },
    {
        "question": "Que ocurre cuando dos factores actuan al mismo tiempo?",
        "promise": "El estudiante distingue efectos principales e interacciones antes de calcular.",
        "motivation": "Un material, proceso o tratamiento puede cambiar su comportamiento segun la combinacion de condiciones.",
        "intuition": "Una interaccion aparece cuando una respuesta no puede explicarse sumando efectos por separado.",
        "guided": "Comparar una matriz de dos factores y leer graficamente si las lineas sugieren interaccion.",
        "practices": "ANOVA de dos factores, lectura de graficas de interaccion y diagnostico de interpretaciones erroneas.",
        "errors": "Reportar solo efectos principales; ignorar interaccion; mezclar factores con variables controladas.",
        "case": "Los materiales de ANOVA factorial se reconstruyen como puente entre comparacion y diseno experimental.",
        "connection": "Para estudiar interacciones con orden, hay que aprender a construir tratamientos factoriales.",
    },
    {
        "question": "Como se construye un experimento factorial 2x2?",
        "promise": "El estudiante aprende a pasar de factores y niveles a tratamientos observables.",
        "motivation": "Un diseno factorial permite obtener mas informacion sin multiplicar desordenadamente las pruebas.",
        "intuition": "Cuatro combinaciones bien planeadas pueden revelar efectos que una prueba aislada no mostraria.",
        "guided": "Construir la matriz 2x2, definir blanco, replicas, controles y variable respuesta antes de mirar cualquier ANOVA.",
        "practices": "Comparar tres rutas: hongos en tortillas como observacion biologica, lentejas como contraste controlable y curcuma-cloro en papel como 2^2 completo con luxometro.",
        "errors": "Hacer una practica vistosa sin diseno; llamar replica a medir dos veces la misma unidad; olvidar el blanco; concluir interaccion sin matriz factorial.",
        "case": "El caso curcuma-cloro-post-it se usa como practica central: 1/4 g de curcuma y 5/10 g de cloro generan cuatro tratamientos, un blanco, seis repeticiones y una respuesta de bloqueo de luz.",
        "connection": "Cuando el experimento llega a contextos reales, aparecen replicas desiguales y restricciones.",
    },
    {
        "question": "Como adaptar el diseno experimental a procesos reales?",
        "promise": "El estudiante aprende que la realidad industrial exige rigor, pero tambien decisiones practicas.",
        "motivation": "Los procesos manuales, materiales y productos no siempre permiten condiciones perfectas.",
        "intuition": "Un buen diseno no elimina la realidad: la documenta, la controla y declara sus limites.",
        "guided": "Analizar un proceso con replicas no balanceadas y decidir que conclusiones son defendibles.",
        "practices": "Separadores artesanales, material compuesto, proceso manual y comparacion de escenarios.",
        "errors": "Forzar conclusiones; ocultar desbalance; interpretar ruido operativo como efecto del tratamiento.",
        "case": "Los proyectos aplicados se integran como laboratorio de decisiones reales en ingenieria.",
        "connection": "Si el numero de factores crece, necesitamos estrategias para reducir tratamientos.",
    },
    {
        "question": "Como explorar varios factores sin hacer todos los experimentos?",
        "promise": "El estudiante entiende Taguchi como diseno reducido y no como receta automatica.",
        "motivation": "En sistemas biologicos, industriales o costosos, no siempre se pueden probar todas las combinaciones.",
        "intuition": "Una matriz bien elegida permite mirar patrones sin agotar materiales, tiempo o muestras.",
        "guided": "Leer una matriz L4, asignar factores, observar respuestas ordinales y discutir limites.",
        "practices": "Violeta africana, cafe, miel, azucar, observacion visual, datos continuos discretizados por cuantiles y analisis exploratorio.",
        "errors": "Tratar escalas ordinales como mediciones perfectas; vender exploracion como conclusion definitiva.",
        "case": "La practica biologica se reconstruye como historia de adaptacion cuando el resultado esperado no ocurre.",
        "connection": "Cuando la respuesta cambia de forma continua, el siguiente paso es modelarla.",
    },
    {
        "question": "Como modelar una respuesta continua?",
        "promise": "El estudiante usa regresion para explicar tendencias, no solo para dibujar una linea.",
        "motivation": "Muchas decisiones de ingenieria dependen de estimar cuanto cambia una respuesta al modificar una condicion.",
        "intuition": "Un modelo es una version simplificada de la realidad que debe interpretarse y revisarse.",
        "guided": "Ajustar un modelo lineal, interpretar pendiente, revisar residuos y discutir prediccion.",
        "practices": "Modelado de problemas, regresion lineal y simulacion de escenarios.",
        "errors": "Confundir ajuste con verdad; extrapolar fuera del rango; ignorar residuos.",
        "case": "Los materiales de modelado se integran como continuidad natural de la comparacion experimental.",
        "connection": "A veces la comparacion de tratamientos debe ajustarse por variables adicionales.",
    },
    {
        "question": "Como comparar tratamientos cuando hay covariables?",
        "promise": "El estudiante comprende ANCOVA como comparacion ajustada, no como ANOVA adornado.",
        "motivation": "Una diferencia entre grupos puede deberse parcialmente a una variable que no era el tratamiento.",
        "intuition": "Ajustar es preguntar que diferencia queda si ponemos a los grupos en condiciones comparables.",
        "guided": "Identificar covariable, revisar relacion con la respuesta e interpretar medias ajustadas.",
        "practices": "Ejercicio de ANCOVA con variables explicativas y discusion de amenazas a la validez.",
        "errors": "Ajustar por variables posteriores al tratamiento; ignorar pendiente; esconder confusion.",
        "case": "El material de ANCOVA se integra como capitulo de justicia comparativa entre tratamientos.",
        "connection": "Cuando una sola respuesta no basta, el analisis debe volverse multivariado.",
    },
    {
        "question": "Como decidir cuando existen varias respuestas importantes?",
        "promise": "El estudiante entiende MANOVA como forma de no fragmentar una decision compleja.",
        "motivation": "Un sistema puede mejorar en una respuesta y empeorar en otra; decidir exige mirar el conjunto.",
        "intuition": "MANOVA compara perfiles de respuesta, no variables aisladas una por una.",
        "guided": "Distinguir matriz de respuestas, grupos, contraste multivariado e interpretacion prudente.",
        "practices": "Rendimiento termico, ejemplos MANOVA y lectura critica de resultados.",
        "errors": "Hacer muchos ANOVA separados sin controlar la decision global; concluir sin interpretar dimensiones.",
        "case": "Las presentaciones y ejemplos MANOVA se integran en una narrativa de decision multirrespuesta.",
        "connection": "La ultima etapa es integrar pregunta, diseno, datos, analisis y comunicacion.",
    },
    {
        "question": "Como construir un proyecto experimental completo?",
        "promise": "El estudiante une todo lo aprendido en una investigacion defendible.",
        "motivation": "La ingenieria exige comunicar decisiones con evidencia, limites y trazabilidad.",
        "intuition": "Un proyecto es una cadena: pregunta clara, diseno coherente, datos confiables y conclusion prudente.",
        "guided": "Armar el mapa completo de un proyecto: problema, factores, datos, analisis, discusion y anexos.",
        "practices": "Proyecto acustico, inductancia, compositos y banco de evaluaciones como rutas integradoras.",
        "errors": "Empezar por el analisis sin pregunta; ocultar fallas; concluir mas de lo que el diseno permite.",
        "case": "Los proyectos finales se transforman en modelos de escritura, revision y defensa de decisiones.",
        "connection": "El manual queda abierto: cada semestre alimenta nuevas experiencias y mejores versiones.",
    },
]

CHAPTER_RESOURCES = {
    1: [
        ("PDF", "Analisis de Experimentos", "data/raw/curso-2026p/Analisis-de-Experimentos.pdf"),
        ("PDF", "Diseno de experimentos en ingenieria", "data/raw/curso-2026p/Diseno-de-experimentos-en-ingenieria.pdf"),
        ("PDF", "Logica, hipotesis y conocimiento cientifico", "data/raw/logica/Logica-hipotesis-y-construccion-del-conocimiento-cientifico.pdf"),
    ],
    2: [
        ("LaTeX", "Muestreo y variabilidad: gatos y grandes numeros", "docs/libro_latex/Capitulos/04-anova.tex"),
        ("PDF", "Indice de Gini y metodos de muestreo", "data/raw/curso-2026p/Una-exploracion-del-Indice-de-Gini-mundial-a-traves-de-cinco-metodos-de-muestreo (1).pdf"),
        ("TXT", "Manifiesto de Estadistica", "data/manifests/estadistica_zip_manifest.txt"),
    ],
    3: [
        ("PDF", "ANOVA de un factor", "data/raw/curso-2026p/ANOVA-de-un-factor-Prueba-F-y-valor-P.pdf"),
        ("LaTeX", "Capitulo ANOVA", "docs/libro_latex/Capitulos/00-ANOVA.tex"),
    ],
    4: [
        ("PDF", "ANOVA de dos factores", "data/raw/curso-2026p/ANOVA-de-2-Factores.pdf"),
        ("PDF", "ANOVA factorial 2 y 2", "data/raw/curso-2026p/ANOVA-Factorial-2-y-2-Analisis-de-efectos-principales-interacciones-y-replicas-desiguales.pdf"),
    ],
    5: [
        ("LaTeX", "Practica de lentejas, germinacion y hongos", "docs/libro_latex/00Notas.tex"),
        ("LaTeX", "Diseno factorial 2x2 en papel", "docs/libro_latex/Capitulos/02-conceptos.tex"),
        ("PDF", "Practica factorial 2^2", "data/raw/curso-2026p/Examen 1/Practica 2^2 A&D.pdf"),
        ("PDF", "Sustancias e interacciones visuales en papel", "data/raw/curso-2026p/Sustancias-interacciones-y-cambios-visuales-en-papel-introduccion-al-diseno-factorial-2.pdf"),
    ],
    6: [
        ("PDF", "Proceso manual factorial no balanceado", "data/raw/curso-2026p/Optimizacion-de-un-Proceso-Manual-mediante-un-Diseno-Factorial-2-No-Balanceado.pdf"),
        ("PDF", "Separadores artesanales", "data/raw/curso-2026p/Examen 1/reporte separadores artesanales.pdf"),
    ],
    7: [
        ("LaTeX", "Taguchi y violeta africana", "docs/libro_latex/Capitulos/03-disenos-clasicos.tex"),
        ("PDF", "Diseno Taguchi con Python", "data/raw/curso-2026p/De-Datos-Continuos-a-Diseno-Taguchi-Analisis-Experimental-con-Python.pdf"),
        ("PDF", "Video 1 Taguchi", "data/raw/curso-2026p/Practica 1/Video 1_taguchi.pdf"),
    ],
    8: [
        ("PDF", "Modelado parte II", "data/raw/curso-2026p/Modelado-Parte-II.pdf"),
        ("PDF", "Modelado de problemas", "data/raw/curso-2026p/Modelado-de-Problemas (1).pdf"),
    ],
    9: [
        ("PDF", "ANCOVA con covariables", "data/raw/curso-2026p/Analisis-de-Covarianza-ANCOVA-con-3-Variables-Explicativas-y-1-Variable-Respuesta.pdf"),
    ],
    10: [
        ("PDF", "Ejemplo practico de MANOVA", "data/raw/curso-2026p/Ejemplo-Practico-de-MANOVA.pdf"),
        ("PPTX", "Rendimiento termico multivariado", "data/raw/curso-2025/global/Análisis Multivariado del Rendimiento Térmico en Procesadores de Alto Desempeño..pptx"),
    ],
    11: [
        ("PDF", "Proyecto final DAEI", "data/raw/curso-2025/Proyecto/PROYECTO FINAL DAEI.pdf"),
        ("PDF", "Compositos acusticos", "data/raw/curso-2025/Proyecto/Propuesta de diseño experimental para compósitos acústicos.pdf"),
    ],
}

INTERNAL_INPUTS = {
    3: ["ANOVA.xlsx"],
    5: ["Un caso real con hongos, tortillas y una leccion que no olvidaras", "Experimento Tortillas", "Plantilla factorial 2x2", "PRACTICA_FACTORIAL.xlsx", "Factorial 2^2 corregido"],
    6: ["Analisis Excel de material compuesto"],
    11: ["DatosAcustica.xlsx"],
}

MATERIAL_NOTES = {
    "docs/libro_latex/00Notas.tex": "Practica de lentejas: compara miel, azucar, cafe y blanco para estudiar germinacion, altura, raiz, presencia de hongos y condensacion. Sirve para explicar ANOVA de un factor desde un sistema biologico sencillo.",
    "data/manifests/estadistica_zip_manifest.txt": "Manifiesto de materiales no extraidos por espacio en disco. Confirma que existen casos de natalidad y hongos, tortillas y evaluaciones relacionadas que deben integrarse como historias didacticas cuando se extraigan.",
    "docs/libro_latex/Capitulos/03-disenos-clasicos.tex": "Violeta africana con Taguchi L4(2^3): cafe, miel y azucar como factores; hongos, halo cafe, tejido verde y necrosis como respuestas. Muestra que un resultado inesperado puede abrir nuevas preguntas experimentales.",
    "data/raw/curso-2026p/De-Datos-Continuos-a-Diseno-Taguchi-Analisis-Experimental-con-Python.pdf": "Transforma datos continuos en niveles por cuantiles para reconstruir un diseno 3^2. Sirve para explicar discretizacion, balance y limites de un Taguchi reconstruido.",
    "data/raw/curso-2026p/Examen 1/Practica 2^2 A&D.pdf": "Practica 2^2 completa: curcuma y cloro sobre post-it, cuatro tratamientos, blanco, seis repeticiones, fotos, luxometro y ANOVA factorial para evaluar bloqueo de luz e interaccion.",
    "data/raw/curso-2026p/Sustancias-interacciones-y-cambios-visuales-en-papel-introduccion-al-diseno-factorial-2.pdf": "Version didactica de la practica curcuma-cloro: introduce factores, niveles, tratamientos, blanco experimental, repeticiones y medicion de transmision luminosa.",
    "data/raw/curso-2026p/ANOVA-de-2-Factores.pdf": "Ejemplo balanceado con dos factores: profesor y materia, cuarenta observaciones y percepcion estudiantil como respuesta. Sirve para separar efectos principales e interaccion.",
    "data/raw/curso-2026p/ANOVA-de-un-factor-Prueba-F-y-valor-P.pdf": "Presenta ANOVA de un factor como comparacion de variabilidad entre grupos y dentro de grupos; util para explicar hipotesis, F y valor p sin empezar por la formula.",
    "docs/libro_latex/Capitulos/00-ANOVA.tex": "Capitulo base para convertir comparacion de medias en narrativa: pregunta, variabilidad, prueba F, decision e interpretacion prudente.",
    "docs/libro_latex/Capitulos/02-conceptos.tex": "Fuente conceptual para ordenar unidad experimental, factores, niveles, tratamientos, replicas, controles y variable respuesta antes de calcular.",
    "data/raw/curso-2026p/Optimizacion-de-un-Proceso-Manual-mediante-un-Diseno-Factorial-2-No-Balanceado.pdf": "Caso de proceso manual con restricciones reales y replicas desiguales. Sirve para discutir que hacer cuando el experimento no queda perfectamente balanceado.",
    "data/raw/curso-2026p/Examen 1/reporte separadores artesanales.pdf": "Caso aplicado de producto artesanal. Debe usarse para discutir decisiones de diseno, variabilidad operativa y comunicacion de resultados.",
    "data/raw/curso-2026p/Analisis-de-Covarianza-ANCOVA-con-3-Variables-Explicativas-y-1-Variable-Respuesta.pdf": "Introduce comparacion ajustada: cuando una respuesta depende del tratamiento y tambien de covariables que deben controlarse estadisticamente.",
    "data/raw/curso-2026p/Ejemplo-Practico-de-MANOVA.pdf": "Caso multirrespuesta para mostrar por que varias variables no deben analizarse como decisiones aisladas si describen un mismo sistema.",
    "data/raw/curso-2025/Proyecto/PROYECTO FINAL DAEI.pdf": "Modelo de proyecto integrador: problema, diseno, datos, analisis, discusion y defensa de conclusiones.",
    "data/raw/curso-2025/Proyecto/Propuesta de diseño experimental para compósitos acústicos.pdf": "Proyecto sobre compositos acusticos. Sirve para conectar diseno experimental con materiales, respuesta fisica y aplicacion de ingenieria.",
}


def link_for(path_text: str) -> str:
    path = ROOT / path_text
    if path.exists():
        return "../" + quote(path_text, safe="/#")
    return quote(path_text, safe="/#")


def cmd_pagina(_: argparse.Namespace | None = None) -> None:
    manual_pdf = ROOT / "output" / "pdf" / "manual_integrado_ade.pdf"
    draft_pdf = ROOT / "output" / "pdf" / "borrador_integracion_ade.pdf"
    base_manual_pdf = ROOT / "output" / "pdf" / "manual_base_latex_compilado.pdf"
    presentation_pdf = ROOT / "output" / "pdf" / "presentacion_integrada_ade.pdf"
    SITE.parent.mkdir(parents=True, exist_ok=True)
    if manual_pdf.exists():
        shutil.copy2(manual_pdf, SITE_MANUAL_PDF)
    if draft_pdf.exists():
        shutil.copy2(draft_pdf, SITE_DRAFT_PDF)
    if base_manual_pdf.exists():
        shutil.copy2(base_manual_pdf, SITE_BASE_MANUAL_PDF)
    if presentation_pdf.exists():
        shutil.copy2(presentation_pdf, SITE_PRESENTATION_PDF)
    files = all_files()
    topic_counts = counts([topic(p) for p in files])
    ext_counts = counts([p.suffix.lower().lstrip(".") or "sin_extension" for p in files])
    practices = sorted(p for p in PRACTICAS.glob("*.md") if p.name != "plantilla_practica.md")
    agent_count = len(list(AGENTS.glob("*.md")))

    nav = []
    chapters_html = []
    for i, chapter in enumerate(CHAPTERS, 1):
        anchor = f"capitulo-{i}"
        nav.append(f'<a href="#{anchor}"><span>{i:02d}</span>{html.escape(chapter["question"])}</a>')
        resource_cards = []
        for kind, label, path_text in CHAPTER_RESOURCES.get(i, []):
            if kind.upper() in {"XLSX", "TXT", "LATEX", "TEX"}:
                continue
            exists = (ROOT / path_text).exists()
            state = "Disponible" if exists else "Indexado"
            note = MATERIAL_NOTES.get(path_text, "Fuente local leida como apoyo del capitulo. Debe usarse para extraer conceptos, datos, ejemplos, errores y actividades, no para organizar el manual por archivo.")
            resource_cards.append(
                f"""<article class="resource-card">
                  <span class="kind">Insumo interno: {html.escape(kind)}</span>
                  <strong>{html.escape(label)}</strong>
                  <small>{html.escape(state)} en la base local; no se abre desde esta pagina</small>
                  <p>{html.escape(note)}</p>
                  <p class="policy">La pagina publica solo productos derivados: manual, practicas, presentaciones enriquecidas y chatbot. Los PDF fuente quedan fuera de <code>site/</code> por derechos y trazabilidad.</p>
                </article>"""
            )
        internal_items = "".join(f"<li>{html.escape(item)}</li>" for item in INTERNAL_INPUTS.get(i, []))
        internal_html = ""
        if internal_items:
            internal_html = f"""
              <div class="internal-inputs">
                <h4>Insumos internos de calculo</h4>
                <p>Se aprovechan para tablas, graficas y actividades interactivas; no se muestran como material descargable principal.</p>
                <ul>{internal_items}</ul>
              </div>"""
        chapters_html.append(f"""
        <section class="chapter" id="{anchor}">
          <div class="num">{i:02d}</div>
          <div>
            <h2>{html.escape(chapter["question"])}</h2>
            <p class="promise">{html.escape(chapter["promise"])}</p>
            <div class="chapter-map">
              <span>Pregunta</span><span>Historia</span><span>Intuicion</span><span>Practica</span><span>Decision</span>
            </div>
            <div class="learning-path">
              <article><h3>Motivacion</h3><p>{html.escape(chapter["motivation"])}</p></article>
              <article><h3>Intuicion</h3><p>{html.escape(chapter["intuition"])}</p></article>
              <article><h3>Ejemplo guiado</h3><p>{html.escape(chapter["guided"])}</p></article>
              <article><h3>Practicas</h3><p>{html.escape(chapter["practices"])}</p></article>
              <article><h3>Errores frecuentes</h3><p>{html.escape(chapter["errors"])}</p></article>
              <article><h3>Casos reales</h3><p>{html.escape(chapter["case"])}</p></article>
            </div>
            <div class="chapter-resources">
              <h3>Material aprovechado dentro de este capitulo</h3>
              <p>Estas fuentes no son botones de descarga. Son evidencia local que el HAG lee para construir ejemplos, datos, actividades y explicaciones dentro del manual enriquecido.</p>
              <div class="resource-grid">{''.join(resource_cards)}</div>
              {internal_html}
            </div>
            <div class="connection"><strong>Conexion:</strong> {html.escape(chapter["connection"])}</div>
          </div>
        </section>""")

    topic_badges = "".join(f"<span><b>{html.escape(k)}</b>{v}</span>" for k, v in sorted(topic_counts.items()) if k != "general")
    ext_badges = "".join(f"<span><b>{html.escape(k)}</b>{v}</span>" for k, v in sorted(ext_counts.items()) if k in {"pdf", "docx", "pptx", "mp4"})
    practice_list = "".join(f"<li><code>{html.escape(rel(p))}</code></li>" for p in practices)
    pdf_viewer_src = "manual_integrado_ade.pdf" if SITE_MANUAL_PDF.exists() else "manual_base_latex_compilado.pdf"
    pdf_base_src = "manual_base_latex_compilado.pdf"
    pdf_presentation_src = "presentacion_integrada_ade.pdf"

    page = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manual ADE</title>
<style>
:root{{--ink:#1c2630;--muted:#5b6773;--line:#d9e0e5;--accent:#0f766e;--accent2:#a23e19;--bg:#f6f8fb;--panel:#fff;--soft:#edf7f5;--warn:#fff4e6;--blue:#edf4ff;--violet:#f3efff}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg);line-height:1.5}}
header{{padding:34px clamp(18px,4vw,64px) 26px;background:#fff;border-bottom:1px solid var(--line)}} h1{{margin:0 0 8px;font-size:clamp(30px,4vw,50px);letter-spacing:0;max-width:1040px;line-height:1.05}} .subtitle{{max-width:980px;color:var(--muted);font-size:18px;margin:0}}
.layout{{display:grid;grid-template-columns:300px 1fr;gap:26px;padding:24px clamp(18px,4vw,64px) 56px}} nav{{position:sticky;top:0;align-self:start;max-height:calc(100vh - 24px);overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px}}
nav h2{{font-size:15px;margin:0 0 10px;color:var(--muted);text-transform:uppercase}} nav a{{display:flex;gap:8px;padding:8px;border-radius:6px;color:var(--ink);text-decoration:none;font-size:14px}} nav a:hover{{background:var(--soft)}} nav span{{color:var(--accent);font-weight:800;min-width:28px}}
.resources,.pdf-viewer,.authors,.hag-panel,.source-code{{background:var(--panel);border:1px solid var(--line);border-radius:8px}} .badges{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}} .badges span{{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:6px 10px;font-size:13px}} .badges b{{color:var(--accent);margin-right:6px}}
.chapter{{display:grid;grid-template-columns:72px 1fr;gap:18px;padding:28px 0;border-top:1px solid var(--line);scroll-margin-top:12px}} .num{{width:56px;height:56px;display:grid;place-items:center;background:var(--accent);color:white;border-radius:8px;font-weight:800}} .chapter h2{{margin:0 0 6px;font-size:clamp(24px,3vw,34px);letter-spacing:0;line-height:1.12}} .promise{{margin:0 0 14px;color:var(--muted);font-size:18px;max-width:900px}} .chapter-map{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}} .chapter-map span{{border:1px solid var(--line);border-radius:999px;background:#fff;padding:5px 10px;font-size:12px;color:var(--muted);font-weight:700}} .learning-path{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}} .learning-path article{{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fff}} .learning-path h3{{margin:0 0 6px;font-size:13px;color:var(--accent);text-transform:uppercase}} .learning-path p{{margin:0}} .chapter-resources{{margin-top:16px;border-left:4px solid var(--accent2);padding:10px 0 0 14px}} .chapter-resources h3{{margin:0 0 4px;font-size:14px;color:var(--muted);text-transform:uppercase}} .chapter-resources p{{margin:0 0 10px;color:var(--muted)}} .resource-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px}} .resource-card{{display:block;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:12px;background:var(--soft)}} .resource-card strong{{display:block;margin:4px 0}} .resource-card small{{display:block;color:var(--muted);font-size:12px}} .resource-card p{{margin:8px 0 0;color:var(--ink);font-size:13px;line-height:1.42}} .resource-card .policy{{background:#fff;border-left:3px solid var(--accent2);padding:8px;color:var(--muted)}} .kind{{font-size:12px;font-weight:800;color:var(--accent2)}} .connection{{margin-top:14px;background:var(--warn);border:1px solid #fed7aa;border-radius:8px;padding:10px 12px}}
.internal-inputs{{margin-top:10px;background:var(--violet);border:1px solid var(--line);border-radius:8px;padding:10px}} .internal-inputs h4{{margin:0 0 4px;font-size:13px;color:#4c1d95;text-transform:uppercase}} .internal-inputs ul{{margin:6px 0 0;padding-left:18px}}
.pdf-viewer{{padding:18px;margin:18px 0;background:#fff}} .pdf-actions{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}} .pdf-actions a{{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;border-radius:8px;padding:10px 12px;font-weight:750}} .pdf-actions a.secondary{{background:#243447}} .pdf-viewer iframe{{width:100%;height:560px;border:1px solid var(--line);border-radius:8px;background:#fff}} .resources,.authors,.hag-panel,.source-code,.chatbot{{padding:16px;margin-top:18px}} .authors ul{{columns:2;gap:28px;margin:10px 0 0;padding-left:20px}} .authors li{{break-inside:avoid;margin:4px 0}} .hag-panel{{display:grid;grid-template-columns:1fr auto auto;gap:16px;align-items:center;background:var(--blue)}} .hag-panel h2,.source-code h2,.chatbot h2{{margin:0 0 4px}} .hag-panel p,.source-code p,.chatbot p{{margin:0;color:var(--muted)}} .hag-status{{display:grid;gap:4px;font-size:13px}} .hag-status strong{{color:var(--accent2)}} .hag-panel a,.source-links a,.chat-answer a{{background:var(--accent);color:#fff;text-decoration:none;border-radius:8px;padding:10px 12px;font-weight:800;white-space:nowrap}} .source-code,.chatbot{{display:grid;grid-template-columns:1fr;gap:12px;background:#fff;border:1px solid var(--line);border-radius:8px}} .source-links,.chat-answer article div{{display:flex;flex-wrap:wrap;gap:10px}} .source-links a:nth-child(even),.chat-answer a:nth-child(even){{background:#243447}} .chat-row{{display:grid;grid-template-columns:1fr auto;gap:10px}} .chat-row input{{width:100%;border:1px solid var(--line);border-radius:8px;padding:11px 12px;font:inherit}} .chat-row button{{border:0;background:var(--accent2);color:#fff;border-radius:8px;padding:11px 14px;font-weight:800;cursor:pointer}} .chat-answer{{border:1px solid var(--line);background:var(--soft);border-radius:8px;padding:12px}} .chat-answer article{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px;margin-top:10px}} .chat-answer h3{{margin:0 0 6px}} code{{color:var(--accent2);overflow-wrap:anywhere}} @media(max-width:900px){{.hero-grid,.layout,.hag-panel,.chat-row{{grid-template-columns:1fr}}.reader-route{{grid-template-columns:repeat(2,1fr)}}nav{{position:relative;max-height:none}}.chapter{{grid-template-columns:1fr}}.learning-path{{grid-template-columns:1fr}}.authors ul{{columns:1}}.pdf-viewer iframe{{height:380px}}}}
</style>
</head>
<body>
<header><h1>Diseno y Analisis de Experimentos en Ingenieria</h1><p class="subtitle">Manual universitario de practicas, casos y actividades para estudiar diseno experimental con aplicaciones de ingenieria.</p></header>
<div class="layout">
<nav><h2>Preguntas del manual</h2>{''.join(nav)}</nav>
<main>
{authors_html()}
{hag_panel_html()}
{source_code_html()}
{chatbot_html()}
<section class="pdf-viewer"><h2>Manual enriquecido del curso</h2><p>PDF principal para estudiantes. Integra la narrativa del manual con practicas, presentaciones, actividades, errores frecuentes y criterios de evaluacion. El manual base queda como referencia historica, no como experiencia final.</p><div class="pdf-actions"><a href="{html.escape(pdf_viewer_src)}" target="_blank">Abrir manual enriquecido</a><a class="secondary" href="{html.escape(pdf_presentation_src)}" target="_blank">Abrir presentacion</a><a class="secondary" href="{html.escape(pdf_base_src)}" target="_blank">Manual base</a></div><iframe src="{html.escape(pdf_viewer_src)}"></iframe></section>
{''.join(chapters_html)}
<section class="resources"><h2>Fuentes y materiales del curso</h2><p>Estos materiales se usan para construir ejemplos, practicas, casos y actividades. La lectura principal debe seguir el manual y los capitulos.</p><div class="badges">{topic_badges}</div><div class="badges">{ext_badges}</div></section>
</main></div></body></html>"""
    SITE.parent.mkdir(parents=True, exist_ok=True)
    tmp = SITE.with_suffix(".html.tmp")
    tmp.write_text(page, encoding="utf-8")
    os.replace(tmp, SITE)
    write_hag_dashboard()
    print(f"Pagina actualizada: {rel(SITE)}")


def cmd_agentes(_: argparse.Namespace | None = None) -> None:
    for path in sorted(AGENTS.glob("*.md")):
        print(f"- {rel(path)}")


def cmd_inventario(_: argparse.Namespace | None = None) -> None:
    files = all_files()
    print(f"Archivos locales indexados: {len(files)}")
    for key, value in sorted(counts([topic(p) for p in files]).items()):
        print(f"- {key}: {value}")


def cmd_investigar(_: argparse.Namespace | None = None) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "investigar_material.py")], check=True)


def cmd_compilar(_: argparse.Namespace | None = None) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "compilar_materiales.py")], check=True)


def cmd_servir(args: argparse.Namespace | None = None) -> None:
    port = getattr(args, "port", 8765)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "servir_pagina.py"), "--port", str(port)], check=True)


def cmd_auditar(_: argparse.Namespace | None = None) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "auditar_publicacion.py")], check=True)


def cmd_hag(args: argparse.Namespace | None = None) -> None:
    action = getattr(args, "action", "build")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "hag.py"), action])
    if result.returncode == 0:
        return
    if result.returncode == 2 and action in {"build", "audit", "ecosystem"}:
        print("\nHAG rechazo la entrega porque encontro brechas reales.")
        print("Esto no es un fallo de Python: revisa evidence/hag/audit_result.json o site/hag/.")
        return
    raise subprocess.CalledProcessError(result.returncode, result.args)


def cmd_extraer_conocimiento(_: argparse.Namespace | None = None) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "hag.py"), "extract"], check=True)


def cmd_integrar_presentaciones(_: argparse.Namespace | None = None) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "hag.py"), "integrate-presentations"], check=True)


def cmd_hag_api(args: argparse.Namespace | None = None) -> None:
    port = getattr(args, "port", 8787)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "hag_api.py"), "--port", str(port)], check=True)


def cmd_revision_local(_: argparse.Namespace | None = None) -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)
    agent_dir = MEMORY / "agentes"
    agent_dir.mkdir(parents=True, exist_ok=True)
    summary = f"""# Revision local

Fecha: {today()}

Archivos indexados: {len(all_files())}

Documentos rectores:

- `docs/mision_proyecto.md`
- `docs/filosofia_construccion_manual.md`
- `docs/politicas/politica_presentaciones_material_didactico.md`
- `docs/politicas/politica_aprovechamiento_integral_conocimiento.md`
- `docs/mandato_comun_agentes.md`
- `docs/sistema_autoadaptable_base_notas.md`

Base de conocimiento local:

- `memory/materiales_investigados.json`
- `memory/matriz_investigacion_material.md`
- `memory/bitacora_aprendizaje.md`
- `knowledge/learning_objects.json`
- `knowledge/reuse_map.md`
- `knowledge/bancos/`

Mandato: no producir inventarios. Convertir la materia prima en capitulos-pregunta con motivacion, intuicion, ejemplo guiado, practicas, errores, casos, actividades y conexion.

Regla operativa: ningun agente clasifica por nombre de archivo. Todo material debe convertirse en ficha de conocimiento con problema, factores, niveles, unidad experimental, respuesta, controles, diseno, evidencia, limites y uso didactico.
"""
    safe_write(MEMORY / "revision_local.md", summary)
    for agent in sorted(AGENTS.glob("*.md")):
        name = agent.stem + "_contexto.md"
        safe_write(agent_dir / name, summary + f"\nAgente fuente: `{rel(agent)}`.\n")
    print("Revision local generada.")
    print("- memory/revision_local.md")


def cmd_ensenar(args: argparse.Namespace) -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)
    note = f"\n## {today()} - {args.tema}\n\n{args.nota}\n"
    with (MEMORY / "bitacora_aprendizaje.md").open("a", encoding="utf-8") as f:
        f.write(note)
    print("Aprendizaje registrado en memoria.")


def menu() -> None:
    while True:
        print("\nMaestro ADE")
        print("===========")
        print("1. Revision local")
        print("2. Inventario")
        print("3. Agentes")
        print("4. Regenerar pagina")
        print("5. Ensenar regla")
        print("6. Investigar material")
        print("7. Compilar PDFs")
        print("8. Servir pagina publica")
        print("9. Auditar publicacion")
        print("10. Construir HAG")
        print("11. Auditar HAG")
        print("12. Servir API HAG")
        print("13. Extraer conocimiento")
        print("14. Generar ecosistema de aprendizaje")
        print("15. Integrar presentaciones en manual y practicas")
        print("0. Salir")
        choice = input("\nElige una opcion: ").strip()
        if choice == "0":
            print("Listo.")
            return
        if choice == "1":
            cmd_revision_local()
        elif choice == "2":
            cmd_inventario()
        elif choice == "3":
            cmd_agentes()
        elif choice == "4":
            cmd_pagina()
        elif choice == "5":
            tema = input("Tema: ").strip() or "general"
            nota = input("Nota: ").strip()
            if nota:
                cmd_ensenar(argparse.Namespace(tema=tema, nota=nota))
        elif choice == "6":
            cmd_investigar()
        elif choice == "7":
            cmd_compilar()
        elif choice == "8":
            cmd_servir(argparse.Namespace(port=8765))
        elif choice == "9":
            cmd_auditar()
        elif choice == "10":
            cmd_hag(argparse.Namespace(action="build"))
        elif choice == "11":
            cmd_hag(argparse.Namespace(action="audit"))
        elif choice == "12":
            cmd_hag_api(argparse.Namespace(port=8787))
        elif choice == "13":
            cmd_extraer_conocimiento()
        elif choice == "14":
            cmd_hag(argparse.Namespace(action="ecosystem"))
        elif choice == "15":
            cmd_integrar_presentaciones()
        else:
            print("Opcion no reconocida.")


def main() -> None:
    if len(sys.argv) == 1:
        menu()
        return
    parser = argparse.ArgumentParser(description="Maestro ADE")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("pagina").set_defaults(func=cmd_pagina)
    sub.add_parser("inventario").set_defaults(func=cmd_inventario)
    sub.add_parser("investigar").set_defaults(func=cmd_investigar)
    sub.add_parser("compilar").set_defaults(func=cmd_compilar)
    p_serve = sub.add_parser("servir")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.set_defaults(func=cmd_servir)
    sub.add_parser("auditar-publicacion").set_defaults(func=cmd_auditar)
    p_hag = sub.add_parser("hag")
    p_hag.add_argument("action", choices=["init", "extract", "ecosystem", "integrate-presentations", "build", "audit", "status"], nargs="?", default="build")
    p_hag.set_defaults(func=cmd_hag)
    sub.add_parser("extraer-conocimiento").set_defaults(func=cmd_extraer_conocimiento)
    sub.add_parser("integrar-presentaciones").set_defaults(func=cmd_integrar_presentaciones)
    p_hag_api = sub.add_parser("hag-api")
    p_hag_api.add_argument("--port", type=int, default=8787)
    p_hag_api.set_defaults(func=cmd_hag_api)
    sub.add_parser("agentes").set_defaults(func=cmd_agentes)
    sub.add_parser("revision-local").set_defaults(func=cmd_revision_local)
    p = sub.add_parser("ensenar")
    p.add_argument("--tema", required=True)
    p.add_argument("--nota", required=True)
    p.set_defaults(func=cmd_ensenar)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
