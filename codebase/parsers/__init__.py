"""Language parser abstraction — Core does not depend on a single AST toolkit."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class ParsedSymbol:
    name: str
    kind: str
    line_start: int
    line_end: int
    exported: bool = False
    certainty: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedImport:
    module: str
    names: list[str] = field(default_factory=list)
    line: int = 1
    certainty: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParseResult:
    language: str
    path: str
    symbols: list[ParsedSymbol] = field(default_factory=list)
    imports: list[ParsedImport] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LanguageParser(Protocol):
    name: str
    extensions: tuple[str, ...]

    def parse(self, path: Path, source: str) -> ParseResult: ...


def discover_parsers() -> list[LanguageParser]:
    """Load built-in parsers. New languages register here without touching Orchestrator."""
    from codebase.parsers.javascript_lite import JavaScriptLiteParser
    from codebase.parsers.python_parser import PythonParser

    return [PythonParser(), JavaScriptLiteParser()]


def parser_for_extension(ext: str, parsers: list[LanguageParser] | None = None) -> LanguageParser | None:
    parsers = parsers if parsers is not None else discover_parsers()
    ext = ext.lower()
    for parser in parsers:
        if ext in parser.extensions:
            return parser
    return None
