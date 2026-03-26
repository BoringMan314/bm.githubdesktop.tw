# -*- coding: utf-8 -*-
"""List UserTemp renderer sources: count in Orig, flag risky short strings."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from apply_zh_patch import parse_mapping  # noqa: E402

DELIM = ">*.*<"


def main() -> None:
    main_pairs, renderer_pairs = parse_mapping(ROOT / "Temp" / "UserTemp.zh")
    r = (ROOT / "Orig" / "renderer.js").read_text(encoding="utf-8")

    rows = []
    for src, dst in renderer_pairs:
        n = r.count(src)
        rows.append((n, len(src), src[:90], dst[:40]))

    rows.sort(key=lambda x: (x[0], x[1]))

    print("renderer mappings sorted by (occurrence count, then source length):\n")
    for n, ln, s, d in rows:
        flag = " ***" if n != 1 or ln < 12 else ""
        print(f"  {n:2}x  len={ln:3}  {s!r} -> {d!r}{flag}")

    print(f"\nTotal renderer pairs: {len(renderer_pairs)}")


if __name__ == "__main__":
    main()
