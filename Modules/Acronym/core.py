#!/usr/bin/env python3
"""
LaTeXDoctor - Acronym extractor

Extract acronyms written in parentheses like:
  explainable artificial intelligence (XAI)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


from .constants import ACRONYM_PAREN_RE,MAX_CHAR_PER_WORD
from .tools import _strip_basic_latex_noise, Capitalize_words,strip_latex_comments, read_files_concat, iter_tex_files



def derive_definition_from_window(prefix: str, acr: str) -> str:
    """
    Apply the requested heuristic:
    - N = len(acr)
    - take last N*MAX_CHAR_PER_WORD chars of prefix
    - remove special chars (including '-')
    - split by space
    - take last N words
    """
    N = len(acr)
    window_len = N * MAX_CHAR_PER_WORD
    window = prefix[-window_len:] if window_len > 0 else prefix

    # Optional: strip latex noise first (helps a lot)
    window = _strip_basic_latex_noise(window)

    # Remove special characters (including '-'), keep letters/spaces only
    # (digits removed from long-form; acr itself may have digits but definition typically doesn't)
    window = re.sub(r"[^A-Za-z\s]", " ", window)  # '-' and punctuation become spaces
    window = re.sub(r"\s+", " ", window).strip()

    words = window.split(" ") if window else []
    if not words:
        return ""

    # Take last N words (if fewer than N, take all)
    take = words[-N:] if len(words) >= N else words
    definition = " ".join(take).lower().strip()
    return Capitalize_words(definition)


def extract_acronyms_with_definitions(tex: str) -> Dict[str, str]:
    """
    Return {ACR: definition} using the N*10 char window rule.
    First occurrence wins.
    """
    tex = strip_latex_comments(tex)
    mapping: Dict[str, str] = {}

    for m in ACRONYM_PAREN_RE.finditer(tex):
        acr = m.group("acr").strip()

        # Basic sanity checks (avoid (A), avoid very long)
        if not (2 <= len(acr) <= 20):
            continue

        # Text before '('
        prefix = tex[: m.start()]

        definition = derive_definition_from_window(prefix, acr)

        # Optional: require at least 1 word (or 2 words if you want stricter)
        if not definition:
            continue

        mapping.setdefault(acr, definition)

    return dict(sorted(mapping.items(), key=lambda kv: kv[0]))


def extract_acronyms_only(tex: str) -> List[str]:
    """Return a sorted list of unique acronyms found in parentheses (no definitions)."""
    tex = strip_latex_comments(tex)
    found: Set[str] = set()
    
    for m in ACRONYM_PAREN_RE.finditer(tex):
        acr = m.group("acr").strip()
        if 2 <= len(acr) <= 20:
            found.add(acr)

    return sorted(found)


def export_acronyms_to_latex(acronyms: Dict[str, str]) -> str:
    lines: List[str] = []
    lines.append(r"\chapter{Acronyms}\label{cha:acronyme}")
    lines.append(r"\begin{itemize}")

    for acr, definition in acronyms.items():
        if definition != "":
            lines.append(rf"\item \textbf{{{acr}:}} {definition}")
        else:
            lines.append(rf"\item \textbf{{{acr}}}")

    lines.append(r"\end{itemize}")
    return "\n".join(lines) + "\n"


def generate_acronyms(logger: Logger, file: Optional[str] = None, folder: Optional[str] = None, json: bool = False, export: Optional[str] = None, export_latex: Optional[str] = None, no_definitions: bool = False):
    """
    Generate acronyms from a LaTeX file or folder.

    Args:
        file (str): Path to a single .tex file
        folder (str): Folder containing .tex files
        json (bool): Print JSON (list or dict)
        export (str): Export acronyms (plain list) to a file
        export_latex (str): Export LaTeX Acronyms chapter to a file
        no_definitions (bool): Only extract acronyms in parentheses (ignore definitions)
    """
    if not file and not folder:
        logger.error("At least one of --file or --folder must be specified")

    if file:
        tex_files = [Path(file)]
    else:
        folder = Path(folder)
        if not folder.exists():
            logger.error(f"Folder not found: {folder}")
        tex_files = iter_tex_files(folder)

    if not tex_files:
        logger.error("No .tex files found.")

    full_tex = read_files_concat(tex_files)
    if no_definitions:
        acr_list = extract_acronyms_only(full_tex)
        acr_dict: Dict[str, str] = {}
    else:
        acr_dict = extract_acronyms_with_definitions(full_tex)
        acr_list = sorted(acr_dict.keys()) if acr_dict else extract_acronyms_only(full_tex)

    # Print
    if json:
        if no_definitions:
            print(json.dumps(acr_list, indent=2))
        else:
            print(json.dumps(acr_dict if acr_dict else acr_list, indent=2, ensure_ascii=False))
    else:
        if acr_dict:
            for k, v in acr_dict.items():
                logger.info(f"{k}: {v}")
        else:
            for a in acr_list:
                logger.info(a)

    # Export plain list
    if export:
        with open(export, "w", encoding="utf-8") as f:
            for a in acr_list:
                f.write(a + "\n")

    # Export LaTeX chapter
    if export_latex:
        output_dir = Path(export_latex).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        if not acr_dict:
            acr_dict = {a: "" for a in acr_list}
        latex_block = export_acronyms_to_latex(acr_dict)
        with open(export_latex, "w", encoding="utf-8") as f:
            f.write(latex_block)