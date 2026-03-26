# -*- coding: utf-8 -*-
"""
對 Orig/main.js、Orig/renderer.js 與 Temp/UserTemp.zh 做 10 道獨立檢查（通過後再跑 apply 較安全）。

用法：在專案根目錄
  python scripts/validate_orig.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# 與 apply_zh_patch 一致
DELIM = ">*.*<"

ROOT = Path(__file__).resolve().parent.parent
ORIG_MAIN = ROOT / "Orig" / "main.js"
ORIG_RENDERER = ROOT / "Orig" / "renderer.js"
MAP_PATH = ROOT / "Temp" / "UserTemp.zh"


def _parse_zh_line(line: str) -> tuple[str, str, str, str] | None:
    i = line.find(DELIM)
    if i < 0:
        return None
    source = line[:i]
    rest = line[i + len(DELIM) :]
    tail = rest.split(DELIM, 2)
    if len(tail) != 3:
        return None
    return source, tail[0], tail[1], tail[2]


def _load_mapping() -> tuple[list[tuple[str, str, str, str]], list[tuple[str, str, str, str]]]:
    main_rows: list[tuple[str, str, str, str]] = []
    renderer_rows: list[tuple[str, str, str, str]] = []
    for raw in MAP_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or DELIM not in line:
            continue
        p = _parse_zh_line(line)
        if not p:
            raise ValueError(f"無法解析列: {line[:80]}")
        src, tgt, cat, fn = p
        fn = fn.strip()
        row = (src, tgt, cat, fn)
        if fn == "main.js":
            main_rows.append(row)
        elif fn == "renderer.js":
            renderer_rows.append(row)
        else:
            raise ValueError(f"未知檔名: {fn!r}")
    return main_rows, renderer_rows


def _apply_in_memory(text: str, pairs: list[tuple[str, str]]) -> str:
    for src, dst in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if src in text:
            text = text.replace(src, dst)
    return text


def main() -> int:
    errors: list[str] = []
    warns: list[str] = []

    # --- [1/10] 檔案存在 ---
    for p, name in [(ORIG_MAIN, "Orig/main.js"), (ORIG_RENDERER, "Orig/renderer.js"), (MAP_PATH, "Temp/UserTemp.zh")]:
        if not p.is_file():
            errors.append(f"[1/10] 缺少 {name}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("[1/10] 必要檔案存在 … OK")

    # --- [2/10] 體積與非空 ---
    if ORIG_MAIN.stat().st_size < 50000 or ORIG_RENDERER.stat().st_size < 500000:
        errors.append("[2/10] Orig 檔案異常小，可能不是完整 bundle")
    else:
        print("[2/10] 檔案大小合理 … OK")

    # --- [3/10] UTF-8 與無 NUL ---
    try:
        m_text = ORIG_MAIN.read_text(encoding="utf-8")
        r_text = ORIG_RENDERER.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        errors.append(f"[3/10] UTF-8 解碼失敗: {e}")
        m_text = r_text = ""
    else:
        if "\x00" in m_text or "\x00" in r_text:
            errors.append("[3/10] 內容含 NUL 位元組")
        else:
            print("[3/10] UTF-8、無 NUL … OK")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    # --- [4/10] Webpack 標頭 ---
    if not (m_text.startswith("/*!") and "main.js" in m_text[:80] and "(()=>{" in m_text[:200]):
        errors.append("[4/10] main.js 開頭不像 GitHub Desktop bundle")
    if not (r_text.startswith("/*!") and "renderer.js" in r_text[:80]):
        errors.append("[4/10] renderer.js 開頭不像 GitHub Desktop bundle")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("[4/10] Bundle 標頭 … OK")

    # --- [5/10] 對照表可載入 ---
    try:
        main_rows, renderer_rows = _load_mapping()
    except ValueError as e:
        print(f"[5/10] FAIL: {e}", file=sys.stderr)
        return 1
    print(f"[5/10] UserTemp.zh 解析 … OK（main {len(main_rows)} 列、renderer {len(renderer_rows)} 列）")

    # --- [6/10] 每條來源在對應 Orig 內至少出現 1 次 ---
    missing_main: list[str] = []
    missing_renderer: list[str] = []
    for src, _t, _c, _f in main_rows:
        if src not in m_text:
            missing_main.append(src[:70] + ("…" if len(src) > 70 else ""))
    for src, _t, _c, _f in renderer_rows:
        if src not in r_text:
            missing_renderer.append(src[:70] + ("…" if len(src) > 70 else ""))
    if missing_main or missing_renderer:
        print("[6/10] 有來源在 Orig 找不到:", file=sys.stderr)
        for s in missing_main[:12]:
            print(f"  main: {s!r}", file=sys.stderr)
        for s in missing_renderer[:12]:
            print(f"  renderer: {s!r}", file=sys.stderr)
        if len(missing_main) + len(missing_renderer) > 24:
            print("  …", file=sys.stderr)
        return 1
    print("[6/10] 所有來源字串皆出現在對應 Orig … OK")

    # --- [7/10] 出現次數 >1 的風險提示（不視為失敗）---
    for src, _t, _c, _f in main_rows:
        n = m_text.count(src)
        if n > 1:
            warns.append(f"main: {n}× {src[:50]!r}")
    for src, _t, _c, _f in renderer_rows:
        n = r_text.count(src)
        if n > 1:
            warns.append(f"renderer: {n}× {src[:50]!r}")
    if warns:
        print(f"[7/10] 警告：以下來源出現多次（仍會全部替換）共 {len(warns)} 條")
        for w in warns[:20]:
            print(f"  {w}")
        if len(warns) > 20:
            print(f"  … 其餘 {len(warns) - 20} 條略")
    else:
        print("[7/10] 所有來源在 Orig 內均只出現 1 次 … OK")

    # --- [8/10] 套用後須保留的程式哨兵（避免再誤換程式碼）---
    sentinels = [
        ("renderer", "super(`The remote \\'${t.name}\\' already exists`)"),
        ("renderer", "The remote '${t.name}' already exists"),
    ]

    main_pairs = [(a, b) for a, b, _, _ in main_rows]
    renderer_pairs = [(a, b) for a, b, _, _ in renderer_rows]
    m_patched = _apply_in_memory(m_text, main_pairs)
    r_patched = _apply_in_memory(r_text, renderer_pairs)

    for label, needle in sentinels:
        if label == "renderer" and needle not in r_patched and needle.replace("\\", "") not in r_patched:
            # 允許兩種跳脫
            alt = needle.replace("\\'", "'")
            if alt not in r_patched:
                errors.append(f"[8/10] 套用後 renderer 缺少哨兵（程式可能被誤換）: {needle[:50]}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("[8/10] 套用後仍保留遠端 Error 類別模板字串 … OK")

    # --- [9/10] 結構計數：僅應替換字串，不應增刪程式骨架 ---
    if r_text.count("createElement") != r_patched.count("createElement"):
        errors.append(
            f"[9/10] renderer createElement 次數變化: {r_text.count('createElement')} → {r_patched.count('createElement')}"
        )
    if m_text.count("=>{") != m_patched.count("=>{"):
        errors.append(
            f"[9/10] main.js =>{{ 次數變化: {m_text.count('=>{')} → {m_patched.count('=>{')}"
        )
    for name, orig, patched in [
        ("main.js", m_text, m_patched),
        ("renderer.js", r_text, r_patched),
    ]:
        for ch, label in [("`", "反引號"), ("{", "{"), ("}", "}")]:
            o, p = orig.count(ch), patched.count(ch)
            if p < o - 5 or p > o + 5:
                warns.append(f"[9/10] {name} {label} 數量變化過大: {o} → {p}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    if any("[9/10]" in w for w in warns):
        for w in warns:
            if "[9/10]" in w:
                print(w)
    else:
        print("[9/10] createElement / 箭頭函式骨架與反引號、大括號 … OK")

    # --- [10/10] 第二次套用不應再改動（對照表對已譯內容應 0 命中）---
    m2 = _apply_in_memory(m_patched, main_pairs)
    r2 = _apply_in_memory(r_patched, renderer_pairs)
    if m2 != m_patched or r2 != r_patched:
        errors.append("[10/10] 第二次套用仍改變內容（對照表來源可能與譯文衝突）")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("[10/10] 套用具 idempotence（連續套用不再變） … OK")

    print("\n全部 10 項檢查通過。可執行: python scripts/apply_zh_patch.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
