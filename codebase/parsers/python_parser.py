"""Python parser using stdlib ast only."""

from __future__ import annotations

import ast
from pathlib import Path

from codebase.parsers import ParseResult, ParsedImport, ParsedSymbol


class PythonParser:
    name = "python-stdlib-ast"
    extensions = (".py",)

    def parse(self, path: Path, source: str) -> ParseResult:
        result = ParseResult(language="python", path=str(path))
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            result.errors.append(f"syntax_error:{exc}")
            return result

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.symbols.append(
                    ParsedSymbol(
                        name=node.name,
                        kind="function",
                        line_start=getattr(node, "lineno", 1),
                        line_end=getattr(node, "end_lineno", getattr(node, "lineno", 1)),
                        exported=not node.name.startswith("_"),
                    )
                )
            elif isinstance(node, ast.ClassDef):
                result.symbols.append(
                    ParsedSymbol(
                        name=node.name,
                        kind="class",
                        line_start=getattr(node, "lineno", 1),
                        line_end=getattr(node, "end_lineno", getattr(node, "lineno", 1)),
                        exported=not node.name.startswith("_"),
                    )
                )
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        result.symbols.append(
                            ParsedSymbol(
                                name=f"{node.name}.{item.name}",
                                kind="method",
                                line_start=getattr(item, "lineno", 1),
                                line_end=getattr(item, "end_lineno", getattr(item, "lineno", 1)),
                            )
                        )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append(
                            ParsedImport(
                                module=alias.name,
                                names=[alias.asname or alias.name],
                                line=getattr(node, "lineno", 1),
                            )
                        )
                else:
                    mod = node.module or ""
                    names = [a.name for a in node.names]
                    result.imports.append(
                        ParsedImport(module=mod, names=names, line=getattr(node, "lineno", 1))
                    )

        result.exports = [s.name for s in result.symbols if s.exported and "." not in s.name]
        return result
