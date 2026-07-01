from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .knowledge_base import KnowledgeBase


REQUIRED_ARTIFACT_KINDS = {
    "book_chapter",
    "practice",
    "presentation",
    "pdf",
    "web",
    "infographic",
    "code",
    "exercise",
    "solution",
    "evaluation",
}

REQUIRED_KNOWLEDGE_BANKS = [
    "knowledge/learning_objects.json",
    "knowledge/reuse_map.md",
    "knowledge/bancos/banco_ejemplos.json",
    "knowledge/bancos/banco_figuras.json",
    "knowledge/bancos/banco_codigo.json",
    "knowledge/bancos/banco_narrativas.json",
    "knowledge/bancos/banco_errores_comunes.json",
    "knowledge/bancos/banco_evaluaciones.json",
    "evidence/hag/extraction_report.json",
]


@dataclass
class AuditResult:
    status: str
    failures: list[str]
    warnings: list[str]
    evidence: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class HAGAuditor:
    def __init__(self, root: Path) -> None:
        self.root = root

    def run(self, kb: KnowledgeBase) -> AuditResult:
        failures: list[str] = []
        warnings: list[str] = []
        evidence: list[str] = []

        missing = kb.missing_required_artifacts(REQUIRED_ARTIFACT_KINDS)
        for node_id, kinds in missing.items():
            failures.append(f"{node_id}: faltan artefactos {', '.join(kinds)}")

        for bank in REQUIRED_KNOWLEDGE_BANKS:
            path = self.root / bank
            if not path.exists():
                failures.append(f"Falta banco de conocimiento requerido: {bank}")
                continue
            evidence.append(bank)

        extraction_report = self.root / "evidence" / "hag" / "extraction_report.json"
        if extraction_report.exists():
            try:
                extraction = json.loads(extraction_report.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                failures.append("evidence/hag/extraction_report.json no es JSON valido.")
            else:
                if extraction.get("objects_extracted", 0) <= 0:
                    failures.append("El motor de extraccion no produjo objetos de aprendizaje.")
                if extraction.get("files_scanned", 0) <= 0:
                    failures.append("El motor de extraccion no recorrio archivos del proyecto.")

        evidence_dir = self.root / "evidence" / "hag"
        reports = [
            report
            for report in sorted(evidence_dir.glob("*.json"))
            if report.name not in {"audit_result.json", "extraction_report.json"}
        ] if evidence_dir.exists() else []
        if not reports:
            failures.append("No hay evidencia JSON de agentes ejecutados.")
        for report in reports:
            try:
                data = json.loads(report.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                failures.append(f"Evidencia invalida: {report.relative_to(self.root)}")
                continue
            evidence.append(str(report.relative_to(self.root)))
            if not data.get("generated_artifacts"):
                failures.append(f"{report.name}: agente sin artefactos generados.")
            if data.get("rejects_delivery"):
                failures.append(f"{report.name}: agente rechazo la entrega.")

        chapter_dir = self.root / "docs" / "libro_latex" / "Capitulos"
        if chapter_dir.exists():
            for path in sorted(chapter_dir.glob("*.tex")):
                text = path.read_text(encoding="utf-8", errors="ignore")
                if "\\appendix" in text:
                    failures.append(f"{path.relative_to(self.root)} contiene appendix interno.")
                sections = re.findall(r"(?m)^\\section(?!\\*)", text)
                if path.name != "00-ruta-didactica.tex" and len(sections) > 1:
                    failures.append(f"{path.relative_to(self.root)} contiene {len(sections)} secciones principales.")
        else:
            warnings.append("No existe carpeta de capitulos LaTeX.")

        status = "pass" if not failures else "fail"
        return AuditResult(status, failures, warnings, evidence)
