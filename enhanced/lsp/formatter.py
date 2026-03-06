"""
Enhanced LSP — Code Formatter.
Produces clean Enhanced style: one statement per line, trailing periods,
consistent spacing, indented blocks.
"""
import re


class Formatter:
    def format(self, source):
        """Format Enhanced source code, return list of TextEdit objects."""
        formatted = self._format_source(source)
        if formatted == source:
            return []
        # Return a single full-document replacement
        lines = source.split('\n')
        return [{
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': len(lines), 'character': 0}
            },
            'newText': formatted
        }]

    def _format_source(self, source):
        lines = source.split('\n')
        result = []
        in_block = False
        prev_was_blank = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_was_blank and result:
                    result.append('')
                    prev_was_blank = True
                continue

            prev_was_blank = False

            # Detect block entry (for, if)
            is_block_header = (stripped.lower().startswith('for each') or
                               stripped.lower().startswith('if '))

            # Normalize spacing: collapse multiple spaces to single
            normalized = re.sub(r'\s+', ' ', stripped)

            # Ensure trailing period
            if not normalized.endswith('.'):
                normalized += '.'

            # Apply indentation
            if in_block and not is_block_header:
                normalized = '    ' + normalized
            elif is_block_header:
                in_block = True

            # Detect block exit (next non-indented line after block header)
            if in_block and not is_block_header:
                # Simple heuristic: after one body statement, exit block
                in_block = False

            result.append(normalized)

        # Remove trailing blank lines
        while result and result[-1] == '':
            result.pop()

        # Add final newline
        return '\n'.join(result) + '\n'
