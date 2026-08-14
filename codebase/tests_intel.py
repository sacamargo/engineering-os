"""Test intelligence — detect tests without inventing coverage."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.fs_index import FilesystemIndex

TEST_PATH_RE = re.compile(
    r"(^|/)(tests?|__tests__|spec)/|(_test\.|\\.test\.|\\.spec\.|test_)",
    re.I,
)


@dataclass
class TestRecord:
    path: str
    framework: str | None
    framework_certainty: str
    linked_targets: list[str] = field(default_factory=list)
    link_certainty: str = "unknown"
    coverage: str | float = "unknown"
    certainty: str = "observed"
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestIntelligence:
    tests: list[TestRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"tests": [t.to_dict() for t in self.tests], "notes": self.notes}


def _detect_framework(root: Path, path: str) -> tuple[str | None, str]:
    text_hints = {
        "pytest": ("pytest", "conftest.py"),
        "unittest": ("unittest",),
        "jest": ("jest.config", "jest"),
        "vitest": ("vitest",),
        "mocha": ("mocha",),
        "go test": ("_test.go",),
    }
    # file name / nearby manifests
    if path.endswith("_test.go"):
        return "go test", "observed"
    if path.endswith(".py") and ("test_" in Path(path).name or path.startswith("tests/")):
        if (root / "pytest.ini").exists() or (root / "conftest.py").exists():
            return "pytest", "inferred"
        return "unittest", "inferred"
    if ".test." in path or ".spec." in path or path.startswith("__tests__/"):
        if (root / "jest.config.js").exists() or (root / "jest.config.ts").exists():
            return "jest", "inferred"
        if (root / "vitest.config.ts").exists():
            return "vitest", "inferred"
        return "javascript-test", "inferred"
    return None, "unknown"


def _approx_link(path: str, code_paths: set[str]) -> tuple[list[str], str]:
    name = Path(path).name
    stem = name
    for suffix in (".test.ts", ".test.js", ".spec.ts", ".spec.js", "_test.py", "_test.go"):
        if name.endswith(suffix):
            stem = name[: -len(suffix)]
            break
    if stem.startswith("test_"):
        stem = stem[5:]
    candidates = []
    for p in code_paths:
        if Path(p).stem == stem or Path(p).stem == stem.replace(".", "/"):
            candidates.append(p)
    if candidates:
        return candidates[:5], "inferred"
    return [], "unknown"


def analyze_tests(root: str | Path, fs: FilesystemIndex) -> TestIntelligence:
    root_path = Path(root).resolve()
    code_paths = {
        f.path
        for f in fs.files
        if f.extension in {".py", ".js", ".ts", ".tsx", ".go", ".java"}
        and not TEST_PATH_RE.search(f.path)
    }
    tests: list[TestRecord] = []
    for f in fs.files:
        if not TEST_PATH_RE.search(f.path):
            continue
        framework, f_cert = _detect_framework(root_path, f.path)
        links, l_cert = _approx_link(f.path, code_paths)
        tests.append(
            TestRecord(
                path=f.path,
                framework=framework,
                framework_certainty=f_cert,
                linked_targets=links,
                link_certainty=l_cert,
                coverage="unknown",
                certainty="observed",
                evidence=[f.path],
            )
        )
    return TestIntelligence(
        tests=tests,
        notes=[
            "Coverage is unknown unless a measured artifact is supplied — never emit 0% by default.",
            "Test↔code links are approximate filename heuristics (inferred).",
        ],
    )
