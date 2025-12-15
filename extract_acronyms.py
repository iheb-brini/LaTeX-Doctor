#!/usr/bin/env python3
"""
Extract acronyms written in parentheses from a LaTeX .tex file.

Examples it catches:
- explainable artificial intelligence (XAI)  -> XAI
- self-supervised learning (SSL)            -> SSL

It ignores:
- (see Figure 2)
- (2024)
- (x)  # too short / not uppercase-ish
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Iterable, List, Set
from pathlib import Path


# Heuristic: acronym inside parentheses:
# - 2..10 chars
# - starts with A-Z
# - contains only A-Z, digits, hyphen (optional), slash (optional)
#   (you can tighten/loosen this later)
ACRONYM_PAREN_RE = re.compile(
    r"\((?P<acr>[A-Z][A-Z0-9]*(?:[A-Z0-9]|[-/][A-Z0-9]+)*)\)"
)

# Optional: remove comments (everything after %), but keep escaped \%
COMMENT_RE = re.compile(r"(?<!\\)%.*")


def strip_latex_comments(tex: str) -> str:
    """Remove LaTeX comments while preserving escaped percent signs."""
    return "\n".join(COMMENT_RE.sub("", line) for line in tex.splitlines())


def extract_acronyms_from_tex_content(tex: str) -> List[str]:
    """
    Return a sorted list of unique acronyms found in parentheses.
    """
    tex = strip_latex_comments(tex)

    found: Set[str] = set()
    for m in ACRONYM_PAREN_RE.finditer(tex):
        acr = m.group("acr").strip()
        # final sanity checks (avoid single letters, avoid very long tokens)
        if 2 <= len(acr) <= 10:
            found.add(acr)

    return sorted(found)


def extract_acronyms_from_file(path: str | Path) -> List[str]:
    p = Path(path)
    content = p.read_text(encoding="utf-8", errors="replace")
    return extract_acronyms_from_tex_content(content)


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Extract acronyms in parentheses from a .tex file.")
    parser.add_argument("--file", "-f", help="Path to the .tex file")
    parser.add_argument("--folder", "-F", help="Folder to search for .tex files")
    parser.add_argument("--json", action="store_true", help="Output as JSON array")
    parser.add_argument("--export", help="Export acronyms to a file")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.file and not args.folder:
        parser.error("At least one of --file or --folder must be specified")

    if args.file:
        tex_files = [Path(args.file)]

    elif args.folder:
        tex_files = Path(args.folder).glob("*.tex")
    else:
        parser.error("At least one of --file or --folder must be specified")

    acronyms = []
    for tex_file in tex_files:
        acronyms.extend(extract_acronyms_from_file(tex_file))

    # Remove duplicates.
    acronyms = list(set(acronyms))
    acronyms = sorted(acronyms)

    if args.json:
        import json
        print(json.dumps(acronyms, indent=2))
    else:
        for a in acronyms:
            print(a)

    if args.export:
        output_dir = Path(args.export).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(args.export, "w") as f:
            for a in acronyms:
                f.write(a + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
