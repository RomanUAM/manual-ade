from __future__ import annotations

import html
import json
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


def _slug(text: str) -> str:
    keep = []
    for char in text.lower():
        if char.isalnum():
            keep.append(char)
        elif char in {" ", "-", "_"}:
            keep.append("-")
    return "-".join(part for part in "".join(keep).split("-") if part)


def _learning_objects_for_node(root: Path, node_id: str, topic: str) -> list[dict]:
    path = root / "knowledge" / "learning_objects.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    topic_low = topic.lower()
    node_low = node_id.lower()
    selected = []
    for item in payload.get("objects", []):
        haystack = " ".join(
            [
                item.get("title", ""),
                item.get("excerpt", ""),
                item.get("source_path", ""),
                " ".join(item.get("topics", [])),
            ]
        ).lower()
        if topic_low in haystack or node_low in haystack:
            selected.append(item)
    return selected[:8]


def _evidence_lines(objects: list[dict]) -> list[str]:
    if not objects:
        return ["- Pendiente: ejecutar `python3 scripts/maestro.py extraer-conocimiento` y revisar banco local."]
    lines = []
    for item in objects[:5]:
        lines.append(
            f"- {item.get('object_type', 'objeto')}: {item.get('title', 'sin titulo')} "
            f"({item.get('source_kind', 'fuente')})"
        )
    return lines


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _student_guide(node, objects: list[dict]) -> str:
    evidence = "\n".join(_evidence_lines(objects))
    return f"""# {node.title}

## Pregunta de aprendizaje

{node.question}

## Para que le sirve al estudiante

Este paquete convierte el tema en una experiencia de aprendizaje: primero plantea una situacion cercana, despues formaliza el problema experimental, luego practica con datos o simulacion y finalmente toma una decision con evidencia.

## Historia corta

{node.summary}

La idea no es memorizar una tecnica. La idea es aprender a mirar un fenomeno con suficiente orden para no confundir variabilidad natural con efecto experimental.

## Lo que debe entender en 30 segundos

- Que se quiere comparar o explicar.
- Cual es la unidad experimental.
- Que factores se manipulan o se observan.
- Que variable respuesta permite decidir.
- Que error comun debe evitarse.

## Material ya aprovechado

{evidence}

## Secuencia didactica

1. Motivacion: reconocer el problema real.
2. Intuicion: explicar la idea sin formulas.
3. Metodo: definir factores, niveles, respuesta y control.
4. Practica: ejecutar o simular una version pequena.
5. Analisis: interpretar tablas, graficas y decision.
6. Cierre: conectar con el siguiente tema.
"""


def _practice(node, objects: list[dict]) -> str:
    evidence = "\n".join(_evidence_lines(objects))
    return f"""# Practica: {node.title}

## Objetivo

Responder: {node.question}

## Materiales

- Hoja de registro o archivo de datos.
- Calculadora, hoja de calculo o Python.
- Evidencia visual cuando exista.
- Bitacora de decisiones del equipo.

## Procedimiento

1. Escribe la pregunta experimental en una frase.
2. Define unidad experimental, variable respuesta, factores y niveles.
3. Registra datos sin modificar observaciones incomodas.
4. Construye una tabla limpia de resultados.
5. Grafica la respuesta antes de calcular.
6. Aplica el metodo estadistico correspondiente.
7. Redacta una conclusion prudente: que se puede afirmar y que no.

## Errores que se buscan detectar

- Cambiar mas de una condicion sin registrarlo.
- Confundir tratamiento con medicion.
- Concluir con una sola observacion.
- Olvidar controles, replicas o limitaciones.

## Material fuente integrado

{evidence}
"""


def _presentation(node) -> str:
    return f"""# Presentacion: {node.title}

## Diapositiva 1. Pregunta

{node.question}

## Diapositiva 2. Situacion cercana

Presenta un caso que el estudiante pueda imaginar antes de ver formulas.

## Diapositiva 3. Que se mide

Unidad experimental, variable respuesta, factores y niveles.

## Diapositiva 4. Error comun

Mostrar lo que normalmente se hace mal y por que parece razonable.

## Diapositiva 5. Metodo

Explicar el metodo con un diagrama, no con una tabla saturada.

## Diapositiva 6. Ejemplo guiado

Resolver una decision paso a paso.

## Diapositiva 7. Practica

Indicar que hara el estudiante y que evidencia entregara.

## Diapositiva 8. Conexion

Explicar como este tema prepara el siguiente.
"""


def _exercise(node) -> str:
    return f"""# Ejercicios: {node.title}

1. Identifica la unidad experimental en el caso del capitulo.
2. Escribe una hipotesis nula y una alternativa en lenguaje cotidiano.
3. Senala dos fuentes de variabilidad que podrian confundir la decision.
4. Propón una grafica inicial antes de calcular.
5. Redacta una conclusion que no prometa mas de lo que los datos permiten.
"""


def _solution(node) -> str:
    return f"""# Soluciones orientativas: {node.title}

Estas soluciones son guias de razonamiento, no respuestas mecanicas.

1. La unidad experimental es el objeto minimo sobre el que se aplica o observa la condicion de estudio.
2. La hipotesis nula declara que no hay evidencia de cambio atribuible al tratamiento; la alternativa plantea diferencia o efecto.
3. La variabilidad puede venir del material, operador, ambiente, medicion, tiempo o seleccion de unidades.
4. La grafica debe mostrar distribucion y comparacion, no solo promedios.
5. La conclusion debe mencionar evidencia, limite y decision practica.
"""


def _evaluation(node) -> str:
    return f"""# Evaluacion: {node.title}

## Criterios

- Formula una pregunta experimental clara: 20%.
- Identifica factores, niveles, respuesta y unidad experimental: 25%.
- Usa una grafica o tabla que ayude a decidir: 20%.
- Interpreta sin exagerar causalidad: 20%.
- Conecta la practica con el siguiente tema: 15%.

## Pregunta de cierre

Que decision de ingenieria cambiaria despues de analizar esta evidencia?
"""


def _code(node_id: str, node) -> str:
    return f'''#!/usr/bin/env python3
"""Simulador didactico para {node.title}.

Genera datos pequenos para que el estudiante observe variabilidad antes de
aplicar un analisis formal.
"""

from __future__ import annotations

import random
import statistics


def simular(seed: int = 7) -> None:
    random.seed(seed)
    control = [random.gauss(10.0, 1.2) for _ in range(8)]
    tratamiento = [random.gauss(11.0, 1.2) for _ in range(8)]
    print("Pregunta:", {node.question!r})
    print("Media control:", round(statistics.mean(control), 3))
    print("Media tratamiento:", round(statistics.mean(tratamiento), 3))
    print("Diferencia observada:", round(statistics.mean(tratamiento) - statistics.mean(control), 3))
    print("Advertencia: una diferencia observada no basta; hay que compararla con la variabilidad.")


if __name__ == "__main__":
    simular()
'''


def _infographic_svg(node) -> str:
    title = html.escape(node.title)
    question = html.escape(node.question)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620">
  <rect width="1100" height="620" fill="#f6f8fb"/>
  <text x="60" y="70" font-family="Arial" font-size="34" font-weight="700" fill="#1c2630">{title}</text>
  <text x="60" y="115" font-family="Arial" font-size="22" fill="#425466">{question}</text>
  <g font-family="Arial" font-size="20" fill="#1c2630">
    <rect x="70" y="180" width="180" height="90" rx="8" fill="#edf7f5" stroke="#0f766e"/>
    <text x="105" y="232">Motivar</text>
    <rect x="290" y="180" width="180" height="90" rx="8" fill="#ffffff" stroke="#d9e0e5"/>
    <text x="330" y="232">Intuir</text>
    <rect x="510" y="180" width="180" height="90" rx="8" fill="#fff4e6" stroke="#a23e19"/>
    <text x="548" y="232">Medir</text>
    <rect x="730" y="180" width="180" height="90" rx="8" fill="#edf4ff" stroke="#2563eb"/>
    <text x="760" y="232">Analizar</text>
    <rect x="400" y="360" width="300" height="100" rx="8" fill="#ffffff" stroke="#0f766e"/>
    <text x="445" y="405">Decidir con evidencia</text>
    <text x="438" y="438" font-size="16" fill="#5b6773">No con intuicion aislada</text>
  </g>
</svg>
'''


def generate_student_ecosystem_artifacts(root: Path, kb: KnowledgeBase) -> None:
    """Create first-version learning packages for every HAG node.

    These are editable student-facing artifacts. They prevent the ecosystem from
    stopping at "missing resource" counters and give each chapter a usable path:
    narrative, practice, presentation, exercises, solution, evaluation, code and
    infographic.
    """
    base = root / "docs" / "ecosistema_aprendizaje"
    for node_id, node in kb.nodes.items():
        topic = str(node.metadata.get("tema", node.title))
        objects = _learning_objects_for_node(root, node_id, topic)
        folder = base / _slug(node_id)
        artifacts = {
            "book_chapter": (folder / "guia_estudiante.md", _student_guide(node, objects), "Guia narrativa del estudiante"),
            "practice": (folder / "practica.md", _practice(node, objects), "Practica editable centrada en el estudiante"),
            "presentation": (folder / "presentacion.md", _presentation(node), "Guion de presentacion didactica"),
            "exercise": (folder / "ejercicios.md", _exercise(node), "Banco inicial de ejercicios"),
            "solution": (folder / "soluciones.md", _solution(node), "Soluciones orientativas"),
            "evaluation": (folder / "evaluacion.md", _evaluation(node), "Rubrica y preguntas de evaluacion"),
            "code": (folder / "simulador.py", _code(node_id, node), "Simulador didactico Python"),
            "infographic": (folder / "infografia.svg", _infographic_svg(node), "Infografia del flujo de aprendizaje"),
        }
        for kind, (path, content, description) in artifacts.items():
            if not path.exists():
                _write(path, content)
            kb.add_artifact(
                node_id,
                Artifact(kind, str(path.relative_to(root)), node_id, "hag.generators.student_ecosystem", description),
            )
    kb.save()


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
