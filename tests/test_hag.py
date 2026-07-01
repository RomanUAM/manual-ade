from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hag.audit import REQUIRED_ARTIFACT_KINDS
from hag.director import HAGDirector
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


if __name__ == "__main__":
    unittest.main()
