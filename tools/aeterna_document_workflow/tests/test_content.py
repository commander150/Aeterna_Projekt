from __future__ import annotations

import codecs
import unittest

from tools.aeterna_document_workflow.content import inspect_markdown_bytes
from tools.aeterna_document_workflow.model import WorkflowError

from .helpers import markdown


class ContentTests(unittest.TestCase):
    def test_hash_fingerprint_and_formatting_independence(self) -> None:
        first = markdown("AET-DOC-TARGET", "Target")
        second = first.replace(b"kind: document", b"kind:    document")
        one = inspect_markdown_bytes(first)
        two = inspect_markdown_bytes(second)
        self.assertNotEqual(one.sha256, two.sha256)
        self.assertEqual(one.metadata_fingerprint, two.metadata_fingerprint)
        self.assertEqual("LF", one.newline)

    def test_crlf_and_bom_are_detected(self) -> None:
        crlf = markdown("AET-DOC-TARGET", "Target", newline="\r\n")
        snapshot = inspect_markdown_bytes(codecs.BOM_UTF8 + crlf)
        self.assertEqual("CRLF", snapshot.newline)
        self.assertTrue(snapshot.bom)

    def test_mixed_newlines_are_rejected(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target").replace(b"---\n", b"---\r\n", 1)
        with self.assertRaisesRegex(WorkflowError, "mixed"):
            inspect_markdown_bytes(data)

    def test_lone_cr_is_rejected(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target").replace(b"Baseline", b"Base\rline")
        with self.assertRaisesRegex(WorkflowError, "lone CR"):
            inspect_markdown_bytes(data)


if __name__ == "__main__":
    unittest.main()
