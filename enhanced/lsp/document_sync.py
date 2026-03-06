"""
Enhanced LSP — Document Sync.
Tracks open .en documents in memory with incremental updates.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexer import Lexer
from parser import Parser, ParserError
from analyzer import SemanticAnalyzer, SemanticError
from memory.mem_analyzer import MemoryAnalyzer, MemoryAnalysisError


class DocumentState:
    __slots__ = ('uri', 'content', 'version', 'tokens', 'ast',
                 'typed_ast', 'diagnostics', 'symbol_table',
                 'definitions')

    def __init__(self, uri, content, version=0):
        self.uri = uri
        self.content = content
        self.version = version
        self.tokens = []
        self.ast = None
        self.typed_ast = None
        self.diagnostics = []
        self.symbol_table = None
        self.definitions = {}  # name -> {'line': int, 'col': int, 'type': str}


class DocumentStore:
    def __init__(self):
        self.documents = {}  # uri -> DocumentState

    def open(self, uri, content, version=0):
        doc = DocumentState(uri, content, version)
        self.documents[uri] = doc
        self._analyze(doc)
        return doc

    def change(self, uri, changes, version=None):
        doc = self.documents.get(uri)
        if not doc:
            return None
        for change in changes:
            if 'range' in change:
                doc.content = self._apply_change(doc.content, change)
            else:
                doc.content = change.get('text', doc.content)
        if version is not None:
            doc.version = version
        self._analyze(doc)
        return doc

    def close(self, uri):
        self.documents.pop(uri, None)

    def get(self, uri):
        return self.documents.get(uri)

    def _apply_change(self, content, change):
        """Apply an incremental text change."""
        rng = change['range']
        start = rng['start']
        end = rng['end']
        new_text = change.get('text', '')

        lines = content.split('\n')
        start_line = start['line']
        start_char = start['character']
        end_line = end['line']
        end_char = end['character']

        # Build prefix
        if start_line < len(lines):
            prefix = lines[start_line][:start_char]
        else:
            prefix = ''

        # Build suffix
        if end_line < len(lines):
            suffix = lines[end_line][end_char:]
        else:
            suffix = ''

        # Replace
        new_lines = (prefix + new_text + suffix).split('\n')
        result_lines = lines[:start_line] + new_lines + lines[end_line + 1:]
        return '\n'.join(result_lines)

    def _analyze(self, doc):
        """Re-lex, parse, analyze the document. Collect diagnostics."""
        doc.diagnostics = []
        doc.tokens = []
        doc.ast = None
        doc.typed_ast = None
        doc.symbol_table = None
        doc.definitions = {}

        source = doc.content

        # Stage 1: Lex
        try:
            lexer = Lexer(source)
            doc.tokens = lexer.tokenize()
        except Exception as e:
            doc.diagnostics.append(_make_diag(0, 0, str(e), 1))
            return

        # Stage 2: Parse
        try:
            parser = Parser(doc.tokens)
            doc.ast = parser.parse()
        except ParserError as e:
            line = _extract_line(str(e))
            doc.diagnostics.append(_make_diag(line, 0, str(e), 1))
            return
        except Exception as e:
            doc.diagnostics.append(_make_diag(0, 0, str(e), 1))
            return

        # Stage 3: Semantic Analysis
        try:
            analyzer = SemanticAnalyzer()
            doc.typed_ast = analyzer.analyze(doc.ast)
            doc.symbol_table = analyzer.symtab
            # Build definitions map from symbol table scopes
            if hasattr(analyzer.symtab, 'scopes'):
                for scope in analyzer.symtab.scopes:
                    for name, entry in scope.items():
                        if isinstance(entry, dict):
                            doc.definitions[name] = {
                                'line': entry.get('line', 0),
                                'col': 0,
                                'type': entry.get('type', 'unknown')
                            }
        except SemanticError as e:
            line = _extract_line(str(e))
            doc.diagnostics.append(_make_diag(line, 0, str(e), 1))
            return
        except Exception as e:
            doc.diagnostics.append(_make_diag(0, 0, str(e), 1))
            return

        # Stage 4: Memory Analysis
        try:
            mem = MemoryAnalyzer()
            doc.typed_ast = mem.analyze(doc.typed_ast, doc.symbol_table)
        except MemoryAnalysisError as e:
            line = _extract_line(str(e))
            doc.diagnostics.append(_make_diag(line, 0, str(e), 2))
        except Exception:
            pass  # non-fatal for LSP


def _make_diag(line, col, message, severity):
    """Create an LSP-compatible diagnostic dict."""
    return {
        'range': {
            'start': {'line': max(0, line - 1), 'character': col},
            'end': {'line': max(0, line - 1), 'character': col + 80}
        },
        'severity': severity,
        'message': message,
        'source': 'enhanced'
    }


def _extract_line(msg):
    """Try to extract a line number from an error message."""
    import re
    m = re.search(r'line\s+(\d+)', msg, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 1
