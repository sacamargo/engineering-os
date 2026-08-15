"""Allow `python3 -m codebase` to delegate to CLI."""

from codebase.cli import main

raise SystemExit(main())
