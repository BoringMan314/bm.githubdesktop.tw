# -*- coding: utf-8 -*-
"""掃描套用 UserTemp 後，renderer 內「像 UI 的英文」雙引號字串（長度有上限，避免誤判）。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DELIM = ">*.*<"
MAX_LEN = 220
MIN_LEN = 12


def parse_pairs(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    main_p, ren_p = [], []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or DELIM not in line:
            continue
        i = line.find(DELIM)
        src = line[:i]
        rest = line[i + len(DELIM) :]
        parts = rest.split(DELIM, 2)
        if len(parts) != 3:
            continue
        tgt, _, fn = parts
        fn = fn.strip()
        if fn == "main.js":
            main_p.append((src, tgt))
        elif fn == "renderer.js":
            ren_p.append((src, tgt))
    return main_p, ren_p


def apply_all(text: str, pairs: list[tuple[str, str]]) -> str:
    for src, dst in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if src:
            text = text.replace(src, dst)
    return text


def iter_quoted_strings(s: str):
    i = 0
    n = len(s)
    while i < n:
        if s[i] != '"':
            i += 1
            continue
        i += 1
        start = i
        buf: list[str] = []
        while i < n:
            c = s[i]
            if c == "\\":
                if i + 1 < n:
                    buf.append(s[i : i + 2])
                    i += 2
                else:
                    i += 1
                continue
            if c == '"':
                yield "".join(buf), start
                i += 1
                break
            buf.append(c)
            i += 1
        else:
            break


SKIP_SUBSTR = (
    "http://",
    "https://",
    "github.com",
    "atom://",
    "data:",
    "webpack",
    "${",
    "\\n",
    "rgba(",
    "translate3d",
    "SourceMap",
    "Error.stack",
    "process.",
    "require(",
    "Object.",
    "function",
    "return ",
    "var ",
    "const ",
    "prototype",
)


def looks_like_ui_english(t: str) -> bool:
    if len(t) < MIN_LEN or len(t) > MAX_LEN:
        return False
    if not any(c.isalpha() for c in t):
        return False
    non_ascii = sum(1 for c in t if ord(c) > 127)
    if non_ascii > max(3, len(t) // 8):
        return False
    if not re.search(r"[A-Za-z]{3,}", t):
        return False
    for sub in SKIP_SUBSTR:
        if sub in t:
            return False
    # 排除全是 camelCase 單詞片段
    if re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_.-]+", t):
        return False
    if " " not in t and "…" not in t and not t.endswith("?"):
        return False
    return True


def main() -> int:
    map_path = ROOT / "Temp" / "UserTemp.zh"
    ren_js = (ROOT / "Orig" / "renderer.js").read_text(encoding="utf-8")
    _, rp = parse_pairs(map_path)
    r2 = apply_all(ren_js, rp)

    seen: set[str] = set()
    hits: list[str] = []
    for q, _ in iter_quoted_strings(r2):
        if q in seen or not looks_like_ui_english(q):
            continue
        seen.add(q)
        hits.append(q)
    hits.sort(key=lambda x: (-len(x), x.lower()))
    print(f"renderer.js 套用後仍像英文 UI 的雙引號字串（{len(hits)} 條，長度 {MIN_LEN}–{MAX_LEN}）：\n")
    for h in hits:
        print(h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
