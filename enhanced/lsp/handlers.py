"""
Enhanced LSP — Request Handlers.
Implements every LSP method the server supports.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lsp.document_sync import DocumentStore
from lsp.diagnostics import DiagnosticsEngine
from lsp.completion import CompletionEngine
from lsp.hover import HoverEngine
from lsp.definition import DefinitionEngine
from lsp.formatter import Formatter

VERSION = "0.1.0"


class LSPHandlers:
    def __init__(self, send_notification):
        self.doc_store = DocumentStore()
        self.completion = CompletionEngine()
        self.hover_engine = HoverEngine()
        self.definition_engine = DefinitionEngine()
        self.formatter = Formatter()
        self.send_notification = send_notification
        self.diag_engine = DiagnosticsEngine(self._publish_diagnostics)
        self._initialized = False

    def _publish_diagnostics(self, uri, diagnostics):
        self.send_notification('textDocument/publishDiagnostics', {
            'uri': uri,
            'diagnostics': diagnostics
        })

    # ---- Lifecycle ----

    def handle_initialize(self, params):
        self._initialized = True
        return {
            'capabilities': {
                'textDocumentSync': {
                    'openClose': True,
                    'change': 2,  # Incremental
                    'save': {'includeText': True}
                },
                'completionProvider': {
                    'triggerCharacters': [' '],
                    'resolveProvider': False
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'documentFormattingProvider': True,
            },
            'serverInfo': {
                'name': 'enhanced-lsp',
                'version': VERSION
            }
        }

    def handle_initialized(self, params):
        return None

    def handle_shutdown(self, params):
        self._initialized = False
        return None

    def handle_exit(self, params):
        sys.exit(0)

    # ---- Document Sync ----

    def handle_textDocument_didOpen(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        text = td.get('text', '')
        version = td.get('version', 0)
        doc = self.doc_store.open(uri, text, version)
        self._publish_diagnostics(uri, doc.diagnostics)
        return None

    def handle_textDocument_didChange(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        version = td.get('version')
        changes = params.get('contentChanges', [])
        self.doc_store.change(uri, changes, version)
        self.diag_engine.schedule(uri, self.doc_store)
        return None

    def handle_textDocument_didSave(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        text = params.get('text')
        if text is not None:
            self.doc_store.change(uri, [{'text': text}])
        doc = self.doc_store.get(uri)
        if doc:
            self._publish_diagnostics(uri, doc.diagnostics)
        return None

    def handle_textDocument_didClose(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        self.doc_store.close(uri)
        return None

    # ---- Features ----

    def handle_textDocument_completion(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        position = params.get('position', {'line': 0, 'character': 0})
        doc = self.doc_store.get(uri)
        if not doc:
            return {'isIncomplete': False, 'items': []}
        items = self.completion.complete(doc, position)
        return {'isIncomplete': False, 'items': items}

    def handle_textDocument_hover(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        position = params.get('position', {'line': 0, 'character': 0})
        doc = self.doc_store.get(uri)
        if not doc:
            return None
        return self.hover_engine.hover(doc, position)

    def handle_textDocument_definition(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        position = params.get('position', {'line': 0, 'character': 0})
        doc = self.doc_store.get(uri)
        if not doc:
            return None
        return self.definition_engine.definition(doc, position)

    def handle_textDocument_formatting(self, params):
        td = params.get('textDocument', {})
        uri = td.get('uri', '')
        doc = self.doc_store.get(uri)
        if not doc:
            return []
        return self.formatter.format(doc.content)

    def dispatch(self, method, params):
        """Dispatch an LSP method to the correct handler."""
        handler_name = 'handle_' + method.replace('/', '_')
        handler = getattr(self, handler_name, None)
        if handler:
            return handler(params or {})
        return None
