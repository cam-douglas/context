"""Main-process DawDreamer render worker. JUCE must not run inside the HTTP thread."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(json.dumps({"ok": False, "error": "usage", "detail": "arrangement.json dest.wav"}))
        return 2
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dest = Path(sys.argv[2])
    from context_sidecar.dsp import _render_arrangement_inline

    result = _render_arrangement_inline(plan, dest)
    print(json.dumps(result))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
