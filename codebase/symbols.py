"""Symbol index built from language parsers."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.fs_index import FileRecord, FilesystemIndex
from codebase.parsers import ParseResult, discover_parsers, parser_for_extension


@dataclass
class SymbolRecord:
    id: str
    name: str
    kind: str
    path: str
    line_start: int
    line_end: int
    language: str
    exported: bool = False
    certainty: str = "observed"
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModuleRecord:
    id: str
    path: str
    language: str
    symbol_ids: list[str] = field(default_factory=list)
    certainty: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SymbolIndex:
    symbols: list[SymbolRecord] = field(default_factory=list)
    modules: list[ModuleRecord] = field(default_factory=list)
    parse_results: list[ParseResult] = field(default_factory=list)
    parsers_used: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbols": [s.to_dict() for s in self.symbols],
            "modules": [m.to_dict() for m in self.modules],
            "parsers_used": self.parsers_used,
            "errors": self.errors,
        }


def _symbol_id(path: str, name: str, kind: str, line: int) -> str:
    digest = hashlib.sha256(f"{path}|{name}|{kind}|{line}".encode()).hexdigest()[:10]
    return f"eos.symbol.{digest}"


def build_symbol_index(root: str | Path, fs: FilesystemIndex) -> SymbolIndex:
    root_path = Path(root).resolve()
    parsers = discover_parsers()
    used: set[str] = set()
    symbols: list[SymbolRecord] = []
    modules: list[ModuleRecord] = []
    parse_results: list[ParseResult] = []
    errors: list[str] = []

    for file in fs.files:
        if not file.content_readable or file.is_binary:
            continue
        parser = parser_for_extension(file.extension, parsers)
        if parser is None:
            continue
        full = root_path / file.path
        try:
            source = full.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"{file.path}:read_error:{exc}")
            continue
        result = parser.parse(full, source)
        used.add(parser.name)
        parse_results.append(result)
        errors.extend(f"{file.path}:{e}" for e in result.errors)
        module_id = f"eos.module.{hashlib.sha256(file.path.encode()).hexdigest()[:10]}"
        symbol_ids: list[str] = []
        for sym in result.symbols:
            sid = _symbol_id(file.path, sym.name, sym.kind, sym.line_start)
            symbol_ids.append(sid)
            symbols.append(
                SymbolRecord(
                    id=sid,
                    name=sym.name,
                    kind=sym.kind,
                    path=file.path,
                    line_start=sym.line_start,
                    line_end=sym.line_end,
                    language=result.language,
                    exported=sym.exported,
                    certainty=sym.certainty,
                    evidence=[f"{file.path}:{sym.line_start}"],
                )
            )
        modules.append(
            ModuleRecord(
                id=module_id,
                path=file.path,
                language=result.language,
                symbol_ids=symbol_ids,
            )
        )

    return SymbolIndex(
        symbols=symbols,
        modules=modules,
        parse_results=parse_results,
        parsers_used=sorted(used),
        errors=errors,
    )
