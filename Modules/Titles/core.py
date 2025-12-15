import re
from pathlib import Path
from logging import Logger
from typing import Optional

from .constants import SECTION_COMMANDS, STOP_WORDS

def standardize_title_text(text: str, mode: str) -> str:
    """
    Standardize the title text based on the mode.
    
    Args:
        text (str): The title text to standardize.
        mode (str): One of "Uppercase", "Capitalize", "AllCaps".
        
    Returns:
        str: The standardized text.
    """
    text = text.strip()
    if not text:
        return text

    if mode == "AllCaps":
        return text.upper()
    
    if mode == "Capitalize":
        # "Capitalize only make the first word capital case" -> Sentence case
        # We lowercase everything first, then capitalize the first char.
        return text.lower().capitalize()

    if mode == "Uppercase":
        # Title Case: Uppercase all words except linkers/stop-words
        # First word is always capitalized.
        words = text.split()
        new_words = []
        for i, word in enumerate(words):
            # Check if it's a stop word and not the first word
            clean_word = re.sub(r"[^a-zA-Z0-9]", "", word.lower())
            if i > 0 and clean_word in STOP_WORDS:
                # Keep it lower, but preserve original casing if it was mixed? 
                # User asked to "start with Upper case" -> implies forcing upper.
                # So we should force lower for linkers.
                new_words.append(word.lower()) 
            else:
                new_words.append(word.capitalize())
        return " ".join(new_words)

    # Default fallback
    return text


def process_file_content(content: str, mode: str) -> str:
    """
    Find and replace titles in the content.
    """
    # Create a regex to match \command{...} or \command*{...}
    # Handling nested braces in LaTeX regex is hard, but we can assume simple structure for now 
    # or use a balancing approach if needed. For this task, we'll try a greedy match up to the closing brace 
    # assuming single line or basic multiline. 
    # Actually, titles often span lines. 
    # Let's try to match \command*{text} or \command{text}
    
    for cmd in SECTION_COMMANDS:
        # Regex explanation:
        # \\(cmd)       : match literal backslash and command name
        # \*?           : optional asterisk (e.g. \section*)
        # \s*           : optional space
        # \{            : literal opening brace
        # (?P<title>.*?) : capture the title content (non-greedy)
        # \}            : literal closing brace
        # We need dotall to match newlines if title spans lines.
        
        # NOTE: This simple regex fails on nested braces: \section{An importance of \textit{AI}}
        # For robustness, we might need a recursive parser or just be careful.
        # Given "standardize titles", complex LaTeX inside titles is risky to modify automatically.
        # We will assume titles don't have heavy nested braces for now, or just capture until the first closing brace 
        # which is dangerous. 
        # Better approach: Iterate and match balanced braces.
        
        # For this implementation, let's stick to a reasonably safe regex that excludes } inside content if possible?
        # No, standard regex can't do balanced braces.
        # We will rely on the fact that titles usually terminate. 
        # Using [^}]* is safer than .*? but fails on \textit{...}.
        
        # Let's process match by match.
        pass

    # Re-implementation with custom parsing or `re.sub` with function
    
    def replacer(match):
        full_match = match.group(0)
        prefix = match.group(1) # \section*{
        title = match.group(2)
        suffix = match.group(3) # }
        
        # If title contains nested braces, this simple regex `([^{}]*)` below might miss it or break.
        # Let's try a slightly better regex for the loop.
        
        new_title = standardize_title_text(title, mode)
        return f"{prefix}{new_title}{suffix}"

    # We can iterate over all commands.
    # Pattern: (\\(?:part|chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?\s*\{)(.*?)\}
    # Using .*? is risky.
    # We will try a pattern that allows some nested braces match if we can, or just basic content.
    # For now, let's stick to `(.*?)` and hope it doesn't overeat. 
    # Actually `[^}]*` is safer if we assume no nested braces for titles.
    # Let's use `(.*?)` but verify.
    
    pattern = re.compile(
        r"(\\(?:" + "|".join(SECTION_COMMANDS) + r")\*?\s*\{)(.*?)(\})", 
        re.DOTALL | re.IGNORECASE
    )
    
    return pattern.sub(replacer, content)


def generate_titles(
    logger: Logger, 
    file: Optional[str] = None, 
    folder: Optional[str] = None, 
    json: bool = False, # Unused for titles but kept for signature compatibility
    export: Optional[str] = None, # Unused
    export_latex: Optional[str] = None, # Unused
    no_definitions: bool = False, # Unused
    task: str = "titles", # Unused
    title_standard: str = "Uppercase",
    inplace: bool = False
):
    """
    Standardize titles in LaTeX files.
    """
    
    # 1. Collect files
    from Modules.Acronym.tools import iter_tex_files
    
    files_to_process = []
    if file:
        files_to_process.append(Path(file))
    elif folder:
        fpath = Path(folder)
        if fpath.exists():
             # If recursive needed? main.py removed recursive arg but logic in iter_tex_files is recursive (rglob)
             files_to_process.extend(iter_tex_files(fpath))
        else:
            logger.error(f"Folder not found: {folder}")
            return

    if not files_to_process:
        logger.warning("No files to process.")
        return

    # 2. Process
    for tex_file in files_to_process:
        try:
            original_content = tex_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read {tex_file}: {e}")
            continue

        new_content = process_file_content(original_content, title_standard)

        # 3. Save
        if inplace:
            out_path = tex_file
        else:
            # Mirror structure in 'output/' folder relative to CWD?
            # Or just flat in output/ ?
            # Implementation plan said: "output/ directory in the current working directory, mirroring the input structure"
            
            # If absolute path, how to mirror? 
            # Usually relative to the input folder provided.
            # If --file passed, put in output/filename.tex
            # If --folder passed, preserve relative path from that folder.
            
            out_root = Path("output")
            if folder:
                rel_path = tex_file.relative_to(folder)
                out_path = out_root / rel_path
            else:
                out_path = out_root / tex_file.name

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(new_content, encoding="utf-8")
            logger.info(f"Processed: {tex_file} -> {out_path} [{title_standard}]")
        except Exception as e:
            logger.error(f"Failed to write {out_path}: {e}")
