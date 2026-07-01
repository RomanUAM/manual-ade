from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Relation:
    source: str
    kind: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class Artifact:
    kind: str
    path: str
    node_id: str
    generated_by: str
    description: str

    def exists(self, root: Path) -> bool:
        return (root / self.path).exists()

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class KnowledgeNode:
    id: str
    kind: str
    title: str
    question: str
    summary: str
    prerequisites: list[str] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_artifact(self, artifact: Artifact) -> None:
        existing = {(item.kind, item.path) for item in self.artifacts}
        if (artifact.kind, artifact.path) not in existing:
            self.artifacts.append(artifact)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeNode":
        artifacts = [Artifact(**item) for item in data.get("artifacts", [])]
        return cls(
            id=data["id"],
            kind=data["kind"],
            title=data["title"],
            question=data.get("question", ""),
            summary=data.get("summary", ""),
            prerequisites=list(data.get("prerequisites", [])),
            artifacts=artifacts,
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class AgentReport:
    agent_id: str
    status: str
    task: str
    evidence_files: list[str]
    findings: list[str]
    generated_artifacts: list[str]
    rejects_delivery: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
