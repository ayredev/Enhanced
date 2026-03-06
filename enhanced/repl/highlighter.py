"""
Enhanced REPL Syntax Highlighter — ANSI escape codes only, no external libs.
"""

# ANSI color codes
BLUE    = '\033[94m'
CYAN    = '\033[96m'
GREEN   = '\033[92m'
YELLOW  = '\033[93m'
GRAY    = '\033[90m'
RED     = '\033[91m'
BOLD    = '\033[1m'
RESET   = '\033[0m'

VERBS = {"say", "create", "add", "set", "subtract", "is", "called", "read",
         "write", "append", "multiply", "divide", "divided", "remove", "sort",
         "wait", "get", "load", "call", "check", "exists", "open", "close",
         "send", "free"}

KEYWORDS = {"a", "an", "the", "for", "each", "in", "if", "greater", "than",
            "first", "last", "current", "null", "new", "still", "valid", "as"}

TYPE_NOUNS = {"number", "text", "list", "file", "person", "user", "connection"}

STRUCTURE = {"and", "then", "with", "to", "from", "of", "by", "through"}


def highlight_line(line):
    """Return ANSI-highlighted version of an Enhanced source line."""
    result = []
    i = 0
    while i < len(line):
        ch = line[i]

        # String literal
        if ch == '"':
            j = i + 1
            while j < len(line) and line[j] != '"':
                j += 1
            j = min(j + 1, len(line))
            result.append(GREEN + line[i:j] + RESET)
            i = j
            continue

        # Number literal
        if ch.isdigit():
            j = i
            while j < len(line) and line[j].isdigit():
                j += 1
            result.append(YELLOW + line[i:j] + RESET)
            i = j
            continue

        # Word
        if ch.isalpha() or ch == '_':
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                j += 1
            word = line[i:j]
            wl = word.lower()
            if wl in VERBS:
                result.append(BLUE + word + RESET)
            elif wl in TYPE_NOUNS:
                result.append(CYAN + word + RESET)
            elif wl in KEYWORDS:
                result.append(GRAY + word + RESET)
            elif wl in STRUCTURE:
                result.append(GRAY + word + RESET)
            else:
                result.append(word)
            i = j
            continue

        result.append(ch)
        i += 1

    return ''.join(result)


def error_text(msg):
    """Format an error message in red."""
    return RED + msg + RESET


def success_text(msg):
    """Format a success message in green."""
    return GREEN + msg + RESET


def prompt_text():
    """The REPL prompt."""
    return BLUE + BOLD + '> ' + RESET


def continuation_prompt():
    """Multi-line continuation prompt."""
    return GRAY + '... ' + RESET


def format_var_entry(name, var_type, value):
    """Format a variable for the vars command."""
    return f"  {name}: {CYAN}{var_type}{RESET} = {GREEN}{value}{RESET}"
