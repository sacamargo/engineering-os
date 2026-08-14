"""Lightweight JS/TS import/export regex parser (no full AST dependency)."""

from __future__ import annotations

import re
from pathlib import Path

from codebase.parsers import ParseResult, ParsedImport, ParsedSymbol

IMPORT_RE = re.compile(
    r"""^\s*import\s+(?:type\s+)?(?:([\w*\s{},]+)\s+from\s+)?['"]([^'"]+)['"]""",
    re.M,
)
REQUIRE_RE = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")
EXPORT_FN_RE = re.compile(
    r"""^\s*export\s+(?:async\s+)?function\s+(\w+)""",
    re.M,
)
EXPORT_CLASS_RE = re.compile(r"""^\s*export\s+class\s+(\w+)""", re.M)
FN_RE = re.compile(r"""^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)""", re.M)
CLASS_RE = re.compile(r"""^\s*(?:export\s+)?class\s+(\w+)""", re.M)


class JavaScriptLiteParser:
    name = "javascript-lite-regex"
    extensions = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")

    def parse(self, path: Path, source: str) -> ParseResult:
        lang = "typescript" if path.suffix.lower() in {".ts", ".tsx"} else "javascript"
        result = ParseResult(language=lang, path=str(path))
        lines = source.splitlines()

        def line_of(pos: int) -> int:
            return source[:pos].count("\n") + 1

        for match in IMPORT_RE.finditer(source):
            result.imports.append(
                ParsedImport(
                    module=match.group(2),
                    names=[match.group(1).strip()] if match.group(1) else [],
                    line=line_of(match.start()),
                    certainty="observed",
                )
            )
        for match in REQUIRE_RE.finditer(source):
            result.imports.append(
                ParsedImport(
                    module=match.group(1),
                    names=[],
                    line=line_of(match.start()),
                    certainty="observed",
                )
            )
        for match in FN_RE.finditer(source):
            exported = bool(EXPORT_FN_RE.match(lines[line_of(match.start()) - 1]))
            result.symbols.append(
                ParsedSymbol(
                    name=match.group(1),
                    kind="function",
                    line_start=line_of(match.start()),
                    line_end=line_of(match.start()),
                    exported=exported or match.group(0).lstrip().startswith("export"),
                    certainty="inferred" if lang == "typescript" else "observed",
                )
            )
        for match in CLASS_RE.finditer(source):
            result.symbols.append(
                ParsedSymbol(
                    name=match.group(1),
                    kind="class",
                    line_start=line_of(match.start()),
                    line_end=line_of(match.start()),
                    exported=match.group(0).lstrip().startswith("export"),
                    certainty="inferred" if lang == "typescript" else "observed",
                )
            )
        result.exports = [s.name for s in result.symbols if s.exported]
        result.errors.append("lite_parser:not_full_ast") if False else None
        # Mark parser limitation as unknown for deep TS types
        if lang == "typescript":
            result.errors.append("typescript_types:unknown")
        return result
