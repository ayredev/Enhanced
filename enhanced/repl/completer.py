"""
Enhanced REPL Tab Completer — uses readline when available.
Degrades gracefully on Windows if readline is missing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

ENHANCED_KEYWORDS = [
    "say", "the number", "the text", "create a list", "create a new",
    "add", "subtract", "multiply", "divide", "for each",
    "if", "check if", "open the file", "read from", "write",
    "close", "free", "wait", "get the url", "load the library",
    "call", "set the", "send", "append", "sort", "remove",
    "check if the file", "the size of", "the first item in",
    "the last item in", "the current timestamp",
    "the absolute value of", "the remainder of",
]


class EnhancedCompleter:
    def __init__(self, session=None):
        self.session = session
        self._matches = []

    def complete(self, text, state):
        if state == 0:
            self._matches = self._get_matches(text)
        if state < len(self._matches):
            return self._matches[state]
        return None

    def _get_matches(self, text):
        matches = []
        text_lower = text.lower()

        # Match keywords
        for kw in ENHANCED_KEYWORDS:
            if kw.lower().startswith(text_lower):
                matches.append(kw + ' ')

        # Match session variables
        if self.session:
            for name in self.session.get_var_names():
                if name.lower().startswith(text_lower):
                    matches.append(name)

        return matches


def setup_readline(completer):
    """Install tab completion via readline. No-op if not available."""
    try:
        import readline
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' \t\n')
        return True
    except ImportError:
        return False
