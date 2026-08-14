#!/usr/bin/env python3
from __future__ import annotations

import unittest

from codebase.snapshot import CodebaseSnapshot, SnapshotMeta, new_snapshot_id, utc_now_iso


class SnapshotTests(unittest.TestCase):
    def test_snapshot_id_and_fingerprint_stable_for_same_structure(self) -> None:
        meta = SnapshotMeta(
            analyzed_at=utc_now_iso(),
            git_revision="abc",
            git_branch="main",
            root="/tmp/r",
        )
        s1 = CodebaseSnapshot(
            id=new_snapshot_id("/tmp/r", "abc"),
            meta=meta,
            files=[{"path": "a.py"}],
            symbols=[{"id": "eos.symbol.a"}],
        )
        s2 = CodebaseSnapshot(
            id=new_snapshot_id("/tmp/r", "abc"),
            meta=SnapshotMeta(
                analyzed_at=utc_now_iso(),
                git_revision="abc",
                git_branch="main",
                root="/tmp/r",
            ),
            files=[{"path": "a.py"}],
            symbols=[{"id": "eos.symbol.a"}],
        )
        self.assertEqual(s1.fingerprint(), s2.fingerprint())
        self.assertTrue(s1.id.startswith("eos.snapshot."))


if __name__ == "__main__":
    unittest.main()
