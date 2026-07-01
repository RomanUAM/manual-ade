from __future__ import annotations

import json
from pathlib import Path

from .models import Artifact, KnowledgeNode, Relation


DEFAULT_NODES = [
    KnowledgeNode(
        id="muestreo-gatos",
        kind="practica",
        title="Gatos y grandes numeros",
        question="Como cambia nuestra percepcion al aumentar el tamano de muestra?",
        summary="Practica de muestreo empirico para estudiar media, varianza, estabilidad y TCL.",
        metadata={"tema": "muestreo", "estado": "integrado"},
    ),
    KnowledgeNode(
        id="anova-lentejas",
        kind="practica",
        title="Miel, azucar o cafe",
        question="Como saber si varios tratamientos producen respuestas distintas?",
        summary="Practica biologica para introducir unidad experimental, replicas, tratamientos y ANOVA.",
        prerequisites=["muestreo-gatos"],
        metadata={"tema": "ANOVA", "estado": "integrado"},
    ),
    KnowledgeNode(
        id="factorial-papel",
        kind="practica",
        title="Sustancias e interacciones visuales en papel",
        question="Como se construye un experimento factorial 2x2?",
        summary="Practica de curcuma y cloro para estudiar factores, niveles, blanco e interaccion.",
        prerequisites=["anova-lentejas"],
        metadata={"tema": "factorial", "estado": "integrado"},
    ),
    KnowledgeNode(
        id="taguchi-violeta",
        kind="practica",
        title="Taguchi y violeta africana",
        question="Como explorar varios factores sin hacer todos los experimentos?",
        summary="Practica de diseno reducido con respuestas visuales y analisis exploratorio.",
        prerequisites=["factorial-papel"],
        metadata={"tema": "Taguchi", "estado": "integrado"},
    ),
]


DEFAULT_RELATIONS = [
    Relation("muestreo-gatos", "prerrequisito_de", "anova-lentejas"),
    Relation("anova-lentejas", "prerrequisito_de", "factorial-papel"),
    Relation("factorial-papel", "prerrequisito_de", "taguchi-violeta"),
]


class KnowledgeBase:
    def __init__(self, root: Path, path: Path | None = None) -> None:
        self.root = root
        self.path = path or root / "knowledge" / "hag_graph.json"
        self.nodes: dict[str, KnowledgeNode] = {}
        self.relations: list[Relation] = []

    def load(self) -> "KnowledgeBase":
        if not self.path.exists():
            self.seed()
            return self
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.nodes = {item["id"]: KnowledgeNode.from_dict(item) for item in data.get("nodes", [])}
        self.relations = [Relation(**item) for item in data.get("relations", [])]
        return self

    def seed(self) -> None:
        self.nodes = {node.id: node for node in DEFAULT_NODES}
        self.relations = list(DEFAULT_RELATIONS)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "hag.knowledge_graph.v1",
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "relations": [relation.to_dict() for relation in self.relations],
        }
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_artifact(self, node_id: str, artifact: Artifact) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"Nodo inexistente: {node_id}")
        self.nodes[node_id].add_artifact(artifact)

    def artifacts_by_kind(self, node_id: str) -> dict[str, list[Artifact]]:
        node = self.nodes[node_id]
        grouped: dict[str, list[Artifact]] = {}
        for artifact in node.artifacts:
            grouped.setdefault(artifact.kind, []).append(artifact)
        return grouped

    def missing_required_artifacts(self, required: set[str]) -> dict[str, list[str]]:
        missing: dict[str, list[str]] = {}
        for node_id, node in self.nodes.items():
            existing = {artifact.kind for artifact in node.artifacts if artifact.exists(self.root)}
            absent = sorted(required - existing)
            if absent:
                missing[node_id] = absent
        return missing
