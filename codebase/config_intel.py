"""Configuration intelligence — detected vs inferred."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.fs_index import FilesystemIndex

CONFIG_MAP = {
    "package.json": "npm_manifest",
    "package-lock.json": "npm_lock",
    "pnpm-lock.yaml": "pnpm_lock",
    "yarn.lock": "yarn_lock",
    "tsconfig.json": "typescript_config",
    "jsconfig.json": "javascript_config",
    "pyproject.toml": "python_project",
    "requirements.txt": "pip_requirements",
    "Pipfile": "pipenv",
    "go.mod": "go_module",
    "Cargo.toml": "rust_cargo",
    "Dockerfile": "docker",
    "docker-compose.yml": "compose",
    "docker-compose.yaml": "compose",
    "Makefile": "make",
    ".eslintrc.js": "eslint",
    ".eslintrc.cjs": "eslint",
    "eslint.config.js": "eslint",
    "pytest.ini": "pytest",
    "tox.ini": "tox",
    ".github/workflows": "github_actions_dir",
    "vercel.json": "vercel",
    "next.config.js": "nextjs",
    "next.config.mjs": "nextjs",
    ".env.example": "env_template",
    ".env.sample": "env_template",
}


@dataclass
class ConfigRecord:
    path: str
    config_type: str
    detection: str  # detected | inferred
    certainty: str
    evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConfigIntelligence:
    configurations: list[ConfigRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "configurations": [c.to_dict() for c in self.configurations],
            "notes": self.notes,
        }


def analyze_configuration(root: str | Path, fs: FilesystemIndex) -> ConfigIntelligence:
    root_path = Path(root).resolve()
    configs: list[ConfigRecord] = []
    paths = {f.path for f in fs.files}

    for path in sorted(paths):
        name = Path(path).name
        matched = None
        if path in CONFIG_MAP:
            matched = CONFIG_MAP[path]
        elif name in CONFIG_MAP:
            matched = CONFIG_MAP[name]
        elif path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            matched = "github_actions"
        if matched:
            configs.append(
                ConfigRecord(
                    path=path,
                    config_type=matched,
                    detection="detected",
                    certainty="observed",
                    evidence=[path],
                )
            )

    # inferred: presence of src/app suggests framework layout — label inferred
    if any(p.startswith("src/") for p in paths) and any(
        c.config_type == "nextjs" for c in configs
    ):
        configs.append(
            ConfigRecord(
                path="src/",
                config_type="app_source_layout",
                detection="inferred",
                certainty="inferred",
                evidence=["src/", "next.config.*"],
                notes=["Layout inference only; not a runtime claim."],
            )
        )

    # env templates only — never real .env contents
    for f in fs.files:
        if f.path.endswith(".example") or f.path in {".env.example", ".env.sample"}:
            if not any(c.path == f.path for c in configs):
                configs.append(
                    ConfigRecord(
                        path=f.path,
                        config_type="env_template",
                        detection="detected",
                        certainty="observed",
                        evidence=[f.path],
                    )
                )

    return ConfigIntelligence(
        configurations=configs,
        notes=[
            "Detected = file present. Inferred = heuristic layout/tooling guess.",
            "Real .env files are boundary-blocked for content.",
        ],
    )
