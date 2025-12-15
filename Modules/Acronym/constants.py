import re

# Remove comments (everything after %) but keep escaped \%
COMMENT_RE = re.compile(r"(?<!\\)%.*")

# Find acronyms in parentheses: (XAI), (API), (ANN2) ...
ACRONYM_PAREN_RE = re.compile(r"\((?P<acr>[A-Z][A-Z0-9]{1,19})\)")  # allow up to 20 chars

MAX_CHAR_PER_WORD = 30