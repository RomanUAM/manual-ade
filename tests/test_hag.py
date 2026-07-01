from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hag.audit import REQUIRED_ARTIFACT_KINDS
from hag.director import HAGDirector
from hag.extraction import run_extraction
from hag.knowledge_base import KnowledgeBase
from hag.models import Artifact


class HAGTests(unittest.TestCase):
    def test_seed_creates_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = KnowledgeBase(root).load()
            self.assertIn("anova-lentejas", kb.nodes)
            self.assertTrue(kb.path.exists())

    def test_audit_fails_when_required_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            director = HAGDirector(root)
            result = director.build()
            self.assertEqual(result.status, "fail")
            self.assertTrue(result.failures)
            self.assertTrue((root / "evidence" / "hag" / "audit_result.json").exists())

    def test_node_passes_artifact_requirement_when_all_kinds_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = KnowledgeBase(root).load()
            node_id = "anova-lentejas"
            for kind in REQUIRED_ARTIFACT_KINDS:
                path = root / "generated" / node_id / f"{kind}.txt"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(kind, encoding="utf-8")
                kb.add_artifact(node_id, Artifact(kind, str(path.relative_to(root)), node_id, "test", kind))
            missing = kb.missing_required_artifacts(REQUIRED_ARTIFACT_KINDS)
            self.assertNotIn(node_id, missing)

    def test_extraction_creates_reusable_knowledge_banks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "docs" / "nota.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                "Ejemplo de ANOVA con tratamientos, variable respuesta, error comun y actividad de evaluacion.",
                encoding="utf-8",
            )
            written = run_extraction(root)
            self.assertIn("knowledge/learning_objects.json", written)
            self.assertTrue((root / "knowledge" / "reuse_map.md").exists())
            self.assertTrue((root / "knowledge" / "bancos" / "banco_ejemplos.json").exists())
            self.assertTrue((root / "evidence" / "hag" / "extraction_report.json").exists())


if __name__ == "__main__":
    unittest.main()
