"""
Enhanced LSP — Go-to-Definition.
Ctrl+Click or F12 on a variable name jumps to its declaration line.
"""


class DefinitionEngine:
    def definition(self, doc, position):
        """Return the definition location for the symbol at position."""
        line_num = position.get('line', 0)
        char_num = position.get('character', 0)

        lines = doc.content.split('\n')
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        word = self._word_at(line, char_num)
        if not word:
            return None

        # Look up in definitions
        if doc.definitions and word in doc.definitions:
            info = doc.definitions[word]
            def_line = max(0, info.get('line', 1) - 1)
            def_col = info.get('col', 0)

            # Find the actual column of the word on the definition line
            if def_line < len(lines):
                def_text = lines[def_line]
                idx = def_text.find(word)
                if idx >= 0:
                    def_col = idx

            return {
                'uri': doc.uri,
                'range': {
                    'start': {'line': def_line, 'character': def_col},
                    'end': {'line': def_line, 'character': def_col + len(word)}
                }
            }

        return None

    def _word_at(self, line, col):
        """Extract the word at column position."""
        if col >= len(line):
            col = max(0, len(line) - 1)
        if not line or not (line[col].isalnum() or line[col] == '_'):
            return None

        start = col
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        end = col
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        return line[start:end] if start < end else None
