#!/usr/bin/env python3
"""
LaTeXDoctor - Acronym extractor (v2)

Extract acronyms written in parentheses like:
  explainable artificial intelligence (XAI)

Definition rule (as requested):
- Let N = number of characters in acronym
- Take the N*10 characters immediately before '('
- Remove special characters (including '-')
- Split by spaces, take last N words => definition

Outputs:
- JSON (--json)
- Plain list export (--export)
- LaTeX chapter export (--export-latex)

Examples:
  python extract_acronyms.py --file main.tex --export-latex acronyms.tex
  python extract_acronyms.py --folder chapters --recursive --export-latex acronyms.tex
"""

from pathlib import Path
from typing import Optional, Iterable, Dict
from Modules.Acronym.core import generate_acronyms
from logging import basicConfig, getLogger, Logger


def setup_logger() -> Logger:
    basicConfig(level="INFO")
    logger = getLogger("> ")
    return logger



def main(argv: Optional[Iterable[str]] = None) -> int:
    import argparse
    import json

    logger = setup_logger()

    parser = argparse.ArgumentParser(description="Extract acronyms from LaTeX .tex files.")
    parser.add_argument("--file", "-f", help="Path to a single .tex file")
    parser.add_argument("--folder", "-F", help="Folder containing .tex files")
    parser.add_argument("--json", action="store_true", help="Print JSON (list or dict)")
    parser.add_argument("--export", help="Export acronyms (plain list) to a file")
    parser.add_argument("--export-latex", help="Export LaTeX Acronyms chapter to a file")
    parser.add_argument(
        "--no-definitions",
        action="store_true",
        help="Only extract acronyms in parentheses (ignore definitions)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    generate_acronyms(logger, args.file, args.folder, args.json, args.export, args.export_latex, args.no_definitions)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())