from __future__ import annotations

import json
from pathlib import Path

from .agents import AGENT_CLASSES
from .audit import HAGAuditor, AuditResult, REQUIRED_ARTIFACT_KINDS
from .extraction import run_extraction
from .generators import generate_gap_report, register_existing_artifacts
from .knowledge_base import KnowledgeBase
from .models import AgentReport


class HAGDirector:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.kb = KnowledgeBase(root).load()
        self.auditor = HAGAuditor(root)

    def init(self) -> KnowledgeBase:
        self.kb.seed()
        return self.kb

    def run_agents(self) -> list[AgentReport]:
        reports: list[AgentReport] = []
        for agent_cls in AGENT_CLASSES:
            report = agent_cls(self.root).run(self.kb)
            reports.append(report)
        return reports

    def build(self) -> AuditResult:
        run_extraction(self.root)
        register_existing_artifacts(self.root, self.kb)
        self.run_agents()
        result = self.audit()
        missing = self.kb.missing_required_artifacts(REQUIRED_ARTIFACT_KINDS)
        gap_report = generate_gap_report(self.root, self.kb, missing)
        result.evidence.append(gap_report)
        self.write_audit(result)
        return result

    def audit(self) -> AuditResult:
        return self.auditor.run(self.kb)

    def write_audit(self, result: AuditResult) -> str:
        path = self.root / "evidence" / "hag" / "audit_result.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path.relative_to(self.root))
