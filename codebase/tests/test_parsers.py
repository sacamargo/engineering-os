#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from codebase.parsers import discover_parsers, parser_for_extension
from codebase.parsers.python_parser import PythonParser


class ParserAbstractionTests(unittest.TestCase):
    def test_discover_and_select(self) -> None:
        parsers = discover_parsers()
        names = {p.name for p in parsers}
        self.assertIn("python-stdlib-ast", names)
        self.assertIn("javascript-lite-regex", names)
        self.assertIsNotNone(parser_for_extension(".py"))
        self.assertIsNotNone(parser_for_extension(".ts"))
        self.assertIsNone(parser_for_extension(".rs"))

    def test_python_parse(self) -> None:
        src = "import os\n\nclass A:\n    def m(self):\n        return 1\n\ndef f():\n    return 2\n"
        result = PythonParser().parse(Path("x.py"), src)
        kinds = {(s.name, s.kind) for s in result.symbols}
        self.assertIn(("A", "class"), kinds)
        self.assertIn(("f", "function"), kinds)
        self.assertTrue(any(i.module == "os" for i in result.imports))


if __name__ == "__main__":
    unittest.main()
