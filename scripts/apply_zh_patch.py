# -*- coding: utf-8 -*-
"""
依 Temp/UserTemp.zh 的對照表，將「英文原版」main.js / renderer.js 批次替換為譯文。

使用方式（在專案根目錄）：
  python scripts/apply_zh_patch.py

預設：讀取 Orig/main.js、Orig/renderer.js，寫入 Windows/main.js、Windows/renderer.js。

若你的 GitHub Desktop 版本與本專案 Orig 不同，請先從安裝目錄複製原版覆蓋 Orig/ 再執行本腳本。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


DELIM = ">*.*<"


def _parse_zh_line(line: str) -> tuple[str, str, str, str] | None:
    """
    解析一列對照：SOURCE>*.*<TARGET>*.*<CATEGORY>*.*<FILE
    SOURCE 為第一個「>*.*<」之前的全部字元（不含 >）。
    """
    i = line.find(DELIM)
    if i < 0:
        return None
    # `>` 一律為分隔符 `>*.*<` 的起頭，不可併入來源（否則 `...remote.">*.*<` 會誤把 `>` 吃進來源）。
    source = line[:i]
    rest = line[i + len(DELIM) :]
    tail = rest.split(DELIM, 2)
    if len(tail) != 3:
        return None
    target, category, target_file = tail
    return source, target, category, target_file


def parse_mapping(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    main_pairs: list[tuple[str, str]] = []
    renderer_pairs: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if DELIM not in line:
            continue
        parsed = _parse_zh_line(line)
        if not parsed:
            continue
        source, target, _category, target_file = parsed
        target_file = target_file.strip()
        if target_file == "main.js":
            main_pairs.append((source, target))
        elif target_file == "renderer.js":
            renderer_pairs.append((source, target))
        else:
            print(f"[skip] unknown file column: {target_file!r}", file=sys.stderr)
    return main_pairs, renderer_pairs


def apply_pairs(content: str, pairs: list[tuple[str, str]], label: str) -> str:
    # 先替換較長的來源字串，避免子字串先被換掉導致長字串對不到
    sorted_pairs = sorted(pairs, key=lambda x: len(x[0]), reverse=True)
    missing: list[str] = []
    for src, dst in sorted_pairs:
        if not src:
            continue
        if src not in content:
            missing.append(src[:80] + ("…" if len(src) > 80 else ""))
            continue
        content = content.replace(src, dst)
    if missing:
        print(f"[warn] {label}: {len(missing)} source string(s) not found (version mismatch?)", file=sys.stderr)
        for m in missing[:15]:
            print(f"  - {m!r}", file=sys.stderr)
        if len(missing) > 15:
            print(f"  ... and {len(missing) - 15} more", file=sys.stderr)
    return content


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Apply UserTemp.zh to main.js / renderer.js")
    p.add_argument(
        "--map",
        type=Path,
        default=root / "Temp" / "UserTemp.zh",
        help="Path to UserTemp.zh",
    )
    p.add_argument("--main-in", type=Path, default=root / "Orig" / "main.js")
    p.add_argument("--renderer-in", type=Path, default=root / "Orig" / "renderer.js")
    p.add_argument("--main-out", type=Path, default=root / "Windows" / "main.js")
    p.add_argument("--renderer-out", type=Path, default=root / "Windows" / "renderer.js")
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--main-only",
        action="store_true",
        help="只套用 main.js；renderer.js 輸出為原版（用於排查白屏是否來自 renderer）",
    )
    g.add_argument(
        "--renderer-only",
        action="store_true",
        help="只套用 renderer.js；main.js 輸出為原版（用於排查白屏是否來自 main）",
    )
    args = p.parse_args()

    if not args.map.is_file():
        print(f"Mapping not found: {args.map}", file=sys.stderr)
        return 1
    main_pairs, renderer_pairs = parse_mapping(args.map)
    if not main_pairs and not renderer_pairs:
        print("No mapping entries found.", file=sys.stderr)
        return 1

    if not args.main_in.is_file() or not args.renderer_in.is_file():
        print(
            "Input main.js or renderer.js missing. Copy them from GitHub Desktop:\n"
            "  %LOCALAPPDATA%\\GitHubDesktop\\app-*\\resources\\app\\\n"
            f"  Expected: {args.main_in}\n"
            f"            {args.renderer_in}",
            file=sys.stderr,
        )
        return 1

    main_js = args.main_in.read_text(encoding="utf-8")
    renderer_js = args.renderer_in.read_text(encoding="utf-8")

    if args.main_only:
        main_js = apply_pairs(main_js, main_pairs, "main.js")
        # renderer 維持英文原版，避免與已繁體的 main 混到舊檔
        renderer_js = args.renderer_in.read_text(encoding="utf-8")
    elif args.renderer_only:
        renderer_js = apply_pairs(renderer_js, renderer_pairs, "renderer.js")
        main_js = args.main_in.read_text(encoding="utf-8")
    else:
        main_js = apply_pairs(main_js, main_pairs, "main.js")
        renderer_js = apply_pairs(renderer_js, renderer_pairs, "renderer.js")

    args.main_out.parent.mkdir(parents=True, exist_ok=True)
    args.renderer_out.parent.mkdir(parents=True, exist_ok=True)
    # 與安裝目錄原版一致使用 LF（Windows 上 write_text 預設會把 \n 轉成 CRLF）
    for out_path, text in (
        (args.main_out, main_js),
        (args.renderer_out, renderer_js),
    ):
        with out_path.open("w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    print(f"Wrote {args.main_out}")
    print(f"Wrote {args.renderer_out}")
    if args.main_only:
        print("(mode: main-only — renderer 為未修改原版)")
    elif args.renderer_only:
        print("(mode: renderer-only — main 為未修改原版)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
