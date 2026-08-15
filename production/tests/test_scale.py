#!/usr/bin/env python3
"""Scale measurements for Production Operations (measured, not claimed)."""

from __future__ import annotations

import json
import resource
import time
import unittest
from pathlib import Path

from production.adapters.local import LocalFakeAdapter
from production.loop import run_production_operation
from production.model import DeploymentTarget

OUT = Path(__file__).resolve().parents[2] / "docs" / "PHASE-9-SCALE.json"


def _rss_mb() -> float:
    # macOS ru_maxrss is bytes; Linux is KB — normalize roughly
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if rss > 10_000_000:  # likely bytes (darwin)
        return rss / (1024 * 1024)
    return rss / 1024


def run_n(n: int) -> dict:
    start = time.perf_counter()
    mem0 = _rss_mb()
    artifacts = 0
    evidence = 0
    for i in range(n):
        result = run_production_operation(
            release_candidate={
                "id": f"eos.rc.scale{i}",
                "status": "ready",
                "readiness": "READY_FOR_DEPLOYMENT",
            },
            target=DeploymentTarget(
                f"eos.target.s{i}",
                f"app-{i}",
                "local",
                "1.0.0",
                f"eos.artifact.s{i}",
                "local_fake",
            ),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(),
        )
        assert result.operation.status == "succeeded"
        artifacts += 1
        evidence += len(result.operation.evidence)
    elapsed = time.perf_counter() - start
    mem1 = _rss_mb()
    return {
        "projects": n,
        "execution_time_sec": round(elapsed, 4),
        "memory_rss_mb_delta": round(max(mem1 - mem0, 0), 4),
        "memory_rss_mb_end": round(mem1, 4),
        "artifact_count": artifacts,
        "evidence_count": evidence,
    }


class ScaleTests(unittest.TestCase):
    def test_scale_10_100_1000(self) -> None:
        results = {
            "measured_at": time.time(),
            "note": "Measured locally with LocalFakeAdapter; do not claim 10k/100k without measurement",
            "runs": [run_n(10), run_n(100), run_n(1000)],
        }
        OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(results["runs"][0]["projects"], 10)
        self.assertEqual(results["runs"][1]["projects"], 100)
        self.assertEqual(results["runs"][2]["projects"], 1000)
        for r in results["runs"]:
            self.assertGreater(r["execution_time_sec"], 0)
            self.assertEqual(r["artifact_count"], r["projects"])


if __name__ == "__main__":
    unittest.main()
