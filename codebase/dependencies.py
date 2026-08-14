"""Dependency graph — distinguish import edges from inferred runtime coupling."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.symbols import SymbolIndex


@dataclass
class DependencyEdge:
    id: str
    source_path: str
    target: str
    kind: str  # import | package | inferred_runtime
    certainty: str
    evidence: list[str] = field(default_factory=list)
    external: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DependencyGraph:
    edges: list[DependencyEdge] = field(default_factory=list)
    external_packages: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edges": [e.to_dict() for e in self.edges],
            "external_packages": self.external_packages,
            "notes": self.notes,
        }


def _is_external(module: str, path_set: set[str]) -> bool:
    if module.startswith("."):
        return False
    # rough: if module maps to a repo file stem path
    candidate = module.replace(".", "/") + ".py"
    if candidate in path_set or any(p.endswith("/" + candidate) for p in path_set):
        return False
    if module.split(".")[0] in {"os", "sys", "re", "json", "pathlib", "typing", "unittest", "ast"}:
        return True
    return not module.startswith(".")


def build_dependency_graph(root: str | Path, symbols: SymbolIndex) -> DependencyGraph:
    root_path = Path(root).resolve()
    path_set = {m.path for m in symbols.modules}
    edges: list[DependencyEdge] = []
    packages: dict[str, dict[str, Any]] = {}
    notes = [
        "import edges are observed from parsers.",
        "inferred_runtime is never claimed from imports alone.",
    ]

    for result in symbols.parse_results:
        for imp in result.imports:
            external = _is_external(imp.module, path_set)
            target = imp.module
            if not external and imp.module.startswith("."):
                # unresolved relative — keep as observed import string
                certainty = "observed"
            elif external:
                certainty = "observed"
                top = imp.module.split(".")[0] or imp.module
                packages.setdefault(
                    top,
                    {
                        "name": top,
                        "ecosystem": "unknown",
                        "certainty": "observed",
                        "evidence": [f"{result.path}:{imp.line}"],
                    },
                )
            else:
                certainty = "observed"
            edge_id = f"eos.dep.{abs(hash((result.path, target, imp.line))) % 10**10}"
            edges.append(
                DependencyEdge(
                    id=edge_id,
                    source_path=result.path,
                    target=target,
                    kind="import",
                    certainty=certainty,
                    evidence=[f"{result.path}:{imp.line}"],
                    external=external,
                )
            )

    # package manifests
    for manifest, ecosystem in (
        ("package.json", "npm"),
        ("requirements.txt", "pip"),
        ("pyproject.toml", "pip"),
        ("go.mod", "go"),
        ("Cargo.toml", "cargo"),
    ):
        path = root_path / manifest
        if not path.exists():
            continue
        if manifest == "package.json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for section in ("dependencies", "devDependencies"):
                for name, version in (data.get(section) or {}).items():
                    packages[name] = {
                        "name": name,
                        "ecosystem": ecosystem,
                        "version_constraint": version,
                        "certainty": "observed",
                        "evidence": [manifest],
                    }
                    edges.append(
                        DependencyEdge(
                            id=f"eos.dep.pkg.{abs(hash(name)) % 10**10}",
                            source_path=manifest,
                            target=name,
                            kind="package",
                            certainty="observed",
                            evidence=[manifest],
                            external=True,
                        )
                    )
        elif manifest == "requirements.txt":
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                packages[name] = {
                    "name": name,
                    "ecosystem": ecosystem,
                    "certainty": "observed",
                    "evidence": [manifest],
                }

    return DependencyGraph(
        edges=edges,
        external_packages=sorted(packages.values(), key=lambda p: p["name"]),
        notes=notes,
    )
