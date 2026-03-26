# -*- coding: utf-8 -*-
"""Structural compare Orig vs Windows bundles (no unicode print)."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent

def stats(label: str, text: str) -> None:
    markers = [
        "createElement",
        "function ",
        "=>{",
        "exports.",
        "webpackChunk",
    ]
    print(label)
    for m in markers:
        print(f"  {m}: {text.count(m)}")

for name in ["renderer.js", "main.js"]:
    o = (root / "Orig" / name).read_text(encoding="utf-8")
    w = (root / "Windows" / name).read_text(encoding="utf-8")
    print("===", name, "===")
    stats("  orig", o)
    stats("  win ", w)
    print("  len delta:", len(w) - len(o))

# renderer: must keep error constructor
w = (root / "Windows" / "renderer.js").read_text(encoding="utf-8")
ok = "already exists" in w and "The remote" in w and "super(`" in w
print("=== remote error snippet present:", ok)
