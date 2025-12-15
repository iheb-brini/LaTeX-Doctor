
from pathlib import Path
from typing import List
import re
from .constants import COMMENT_RE

def strip_latex_comments(tex: str) -> str:
    """Remove LaTeX comments while preserving escaped percent signs."""
    return "\n".join(COMMENT_RE.sub("", line) for line in tex.splitlines())


def _strip_basic_latex_noise(s: str) -> str:
    """
    Remove common LaTeX commands so the char-window isn't polluted.
    Conservative on purpose (v2).
    """
    # Replace \command{...} -> ...
    s = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", s)
    # Remove remaining commands like \LaTeX, \emph, etc.
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    # Remove braces
    s = s.replace("{", " ").replace("}", " ")
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

def Capitalize_words(word:str) -> str:
    return " ".join([w.capitalize() for w in word.split(" ")])

def iter_tex_files(folder: Path) -> List[Path]:
    return sorted(p for p in folder.rglob("*.tex") if p.is_file())


def read_files_concat(tex_files: List[Path]) -> str:
    chunks: List[str] = []
    for p in tex_files:
        chunks.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)
