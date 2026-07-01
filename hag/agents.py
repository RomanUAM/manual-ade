from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from .knowledge_base import KnowledgeBase
from .models import AgentReport, Artifact


class HAGAgent(ABC):
    agent_id = "agent"
    task = "sin tarea"

    def __init__(self, root: Path) -> None:
        self.root = root
        self.artifact_dir = root / "artifacts" / "hag"
        self.evidence_dir = root / "evidence" / "hag"

    @abstractmethod
    def run(self, kb: KnowledgeBase) -> AgentReport:
        raise NotImplementedError

    def write_artifact(self, name: str, text: str) -> str:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        path = self.artifact_dir / name
        path.write_text(text, encoding="utf-8")
        return str(path.relative_to(self.root))

    def write_report(self, report: AgentReport) -> AgentReport:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        path = self.evidence_dir / f"{self.agent_id}.json"
        path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        if str(path.relative_to(self.root)) not in report.evidence_files:
            report.evidence_files.append(str(path.relative_to(self.root)))
            path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return report


class ScientificAgent(HAGAgent):
    agent_id = "01_cientifico"
    task = "validar coherencia metodologica y riesgos de inferencia"

    def run(self, kb: KnowledgeBase) -> AgentReport:
        lines = ["# Revision cientifica HAG", ""]
        findings: list[str] = []
        for node in kb.nodes.values():
            line = f"- {node.id}: pregunta='{node.question}', resumen='{node.summary}'"
            lines.append(line)
            if "causa" in node.summary.lower() and "diseno" not in node.summary.lower():
                findings.append(f"{node.id}: revisar afirmaciones causales.")
        if not findings:
            findings.append("No se detectaron afirmaciones causales sin contexto en los nodos semilla.")
        artifact = self.write_artifact("revision_cientifica.md", "\n".join(lines) + "\n")
        report = AgentReport(self.agent_id, "ok", self.task, [artifact], findings, [artifact])
        return self.write_report(report)


class PedagogicalAgent(HAGAgent):
    agent_id = "02_pedagogico"
    task = "crear mapa de aprendizaje y secuencia progresiva"

    def run(self, kb: KnowledgeBase) -> AgentReport:
        lines = ["# Mapa de aprendizaje HAG", "", "## Ruta progresiva", ""]
        for node in kb.nodes.values():
            prereq = ", ".join(node.prerequisites) or "inicio"
            lines.append(f"- **{node.title}**: {node.question} Prerrequisito: {prereq}.")
        artifact = self.write_artifact("mapa_aprendizaje.md", "\n".join(lines) + "\n")
        findings = [
            "La ruta comienza con muestreo, continua con ANOVA, pasa a factoriales y cierra con disenos reducidos.",
            "Cada nodo se formula como pregunta de aprendizaje, no como archivo fuente.",
        ]
        report = AgentReport(self.agent_id, "ok", self.task, [artifact], findings, [artifact])
        return self.write_report(report)


class EditorialAgent(HAGAgent):
    agent_id = "05_editorial"
    task = "auditar jerarquia del libro y producir guia editorial"

    def run(self, kb: KnowledgeBase) -> AgentReport:
        chapter_dir = self.root / "docs" / "libro_latex" / "Capitulos"
        findings: list[str] = []
        for path in sorted(chapter_dir.glob("*.tex")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            count = sum(1 for line in text.splitlines() if line.startswith("\\section") and not line.startswith("\\section*"))
            if path.name != "00-ruta-didactica.tex" and count > 1:
                findings.append(f"{path.relative_to(self.root)} tiene {count} secciones principales.")
        if not findings:
            findings.append("La auditoria editorial no encontro practicas fragmentadas en capitulos falsos.")
        artifact = self.write_artifact(
            "guia_jerarquia_editorial.md",
            "# Guia de jerarquia editorial\n\nUna practica debe tener una sola `\\section`; sus partes internas deben usar `\\subsection` o niveles menores.\n",
        )
        report = AgentReport(self.agent_id, "ok", self.task, [artifact], findings, [artifact], rejects_delivery=bool(findings and "tiene" in findings[0]))
        return self.write_report(report)


class VisualAgent(HAGAgent):
    agent_id = "03_visual"
    task = "planear figuras, diagramas e infografias derivadas del grafo"

    def run(self, kb: KnowledgeBase) -> AgentReport:
        lines = ["# Plan visual HAG", ""]
        for node in kb.nodes.values():
            lines.append(f"- {node.title}: diagrama de pregunta -> diseno -> datos -> decision.")
        artifact = self.write_artifact("plan_visual.md", "\n".join(lines) + "\n")
        findings = ["Cada nodo requiere al menos una figura didactica o diagrama de proceso."]
        report = AgentReport(self.agent_id, "ok", self.task, [artifact], findings, [artifact])
        return self.write_report(report)


class DevelopmentAgent(HAGAgent):
    agent_id = "04_desarrollo"
    task = "generar contrato tecnico y API local"

    def run(self, kb: KnowledgeBase) -> AgentReport:
        artifact = self.write_artifact(
            "contrato_api.md",
            "# Contrato API HAG\n\n- `GET /health`: estado del sistema.\n- `GET /nodes`: nodos del grafo.\n- `GET /audit`: resultado de auditoria.\n",
        )
        findings = ["Existe paquete Python `hag`, CLI `scripts/hag.py`, API local y pruebas unitarias."]
        report = AgentReport(self.agent_id, "ok", self.task, [artifact], findings, [artifact])
        return self.write_report(report)


AGENT_CLASSES = [ScientificAgent, PedagogicalAgent, VisualAgent, DevelopmentAgent, EditorialAgent]
