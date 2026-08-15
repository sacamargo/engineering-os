# Context Engineering (EOS-native)

**Status:** `experimental`  
**Provenance:** Engineering OS adaptation for Cursor / vendor-neutral runtimes.

Not a copy of Claude-specific Context Engineering implementations.

## Invariants

- More context ≠ better context
- Never dump the entire repository
- Provenance required for included items
- Irrelevant and stale context must be excludable/invalidatable
- Not a universal routing shortcut
- Cannot grant tools or permissions

Runtime: `skillpacks/context_engineering.py`
