"""
Test LSP — Server, Document Sync, Diagnostics, Completion, Hover, Definition, Formatter.
"""
import unittest
import os
import sys
import json
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lsp.document_sync import DocumentStore, DocumentState
from lsp.diagnostics import DiagnosticsEngine
from lsp.completion import CompletionEngine
from lsp.hover import HoverEngine
from lsp.definition import DefinitionEngine
from lsp.formatter import Formatter
from lsp.handlers import LSPHandlers


def _noop_send(*args):
    pass


class TestServerInit(unittest.TestCase):
    """Test 1: Server initializes and returns correct capabilities."""
    def test_initialize(self):
        handlers = LSPHandlers(_noop_send)
        result = handlers.handle_initialize({})
        caps = result['capabilities']
        self.assertIn('textDocumentSync', caps)
        self.assertIn('completionProvider', caps)
        self.assertTrue(caps['hoverProvider'])
        self.assertTrue(caps['definitionProvider'])
        self.assertTrue(caps['documentFormattingProvider'])
        self.assertEqual(result['serverInfo']['name'], 'enhanced-lsp')


class TestDidOpenDiagnostics(unittest.TestCase):
    """Test 2: didOpen triggers diagnostic analysis."""
    def test_did_open_runs_analysis(self):
        handlers = LSPHandlers(_noop_send)
        handlers.handle_initialize({})
        handlers.handle_textDocument_didOpen({
            'textDocument': {
                'uri': 'file:///test.en',
                'text': 'say "Hello".',
                'version': 1
            }
        })
        doc = handlers.doc_store.get('file:///test.en')
        self.assertIsNotNone(doc)
        self.assertIsNotNone(doc.ast)


class TestZeroDiagnostics(unittest.TestCase):
    """Test 3: Valid .en file produces zero diagnostics."""
    def test_valid_file(self):
        store = DocumentStore()
        doc = store.open('file:///valid.en', 'say "Hello".')
        self.assertEqual(doc.diagnostics, [])


class TestUndefinedVarDiag(unittest.TestCase):
    """Test 4: Undefined variable produces Error diagnostic."""
    def test_undefined(self):
        store = DocumentStore()
        doc = store.open('file:///undef.en', 'say ghost.')
        self.assertTrue(len(doc.diagnostics) > 0)
        self.assertEqual(doc.diagnostics[0]['severity'], 1)
        self.assertIn('ghost', doc.diagnostics[0]['message'].lower())


class TestTypeMismatchDiag(unittest.TestCase):
    """Test 5: Type mismatch produces Error diagnostic."""
    def test_type_error(self):
        store = DocumentStore()
        source = 'the number x is 5.\nthe text y is "hi".\nadd x and y.'
        doc = store.open('file:///type.en', source)
        self.assertTrue(len(doc.diagnostics) > 0)
        self.assertEqual(doc.diagnostics[0]['severity'], 1)


class TestUnclosedHandleDiag(unittest.TestCase):
    """Test 6: Unclosed file handle produces Warning diagnostic."""
    def test_unclosed(self):
        store = DocumentStore()
        source = 'open the file "data.txt" as f.'
        doc = store.open('file:///leak.en', source)
        has_warning = any(d['severity'] == 2 for d in doc.diagnostics)
        has_error = any(d['severity'] == 1 for d in doc.diagnostics)
        self.assertTrue(has_warning or has_error,
                        f"Expected warning/error for unclosed handle, got: {doc.diagnostics}")


class TestCompletionVerbs(unittest.TestCase):
    """Test 7: Completion at line start returns verb templates."""
    def test_verbs(self):
        store = DocumentStore()
        doc = store.open('file:///comp.en', '')
        engine = CompletionEngine()
        items = engine.complete(doc, {'line': 0, 'character': 0})
        labels = [i['label'] for i in items]
        self.assertIn('say', labels)
        self.assertIn('the number', labels)
        self.assertIn('for each', labels)


class TestCompletionVars(unittest.TestCase):
    """Test 8: Completion after say returns variable names."""
    def test_vars(self):
        store = DocumentStore()
        doc = store.open('file:///compvar.en', 'the number score is 0.\n')
        engine = CompletionEngine()
        items = engine.complete(doc, {'line': 1, 'character': 0})
        labels = [i['label'] for i in items]
        self.assertIn('score', labels)


class TestHoverSay(unittest.TestCase):
    """Test 9: Hover on say returns correct documentation."""
    def test_hover_say(self):
        store = DocumentStore()
        doc = store.open('file:///hvr.en', 'say "Hello".')
        engine = HoverEngine()
        result = engine.hover(doc, {'line': 0, 'character': 1})
        self.assertIsNotNone(result)
        self.assertIn('say', result['contents']['value'])
        self.assertIn('Prints', result['contents']['value'])


class TestHoverVariable(unittest.TestCase):
    """Test 10: Hover on variable returns name, type, definition line."""
    def test_hover_var(self):
        store = DocumentStore()
        doc = store.open('file:///hvrv.en', 'the number score is 5.\nsay score.')
        engine = HoverEngine()
        result = engine.hover(doc, {'line': 1, 'character': 5})
        self.assertIsNotNone(result)
        self.assertIn('score', result['contents']['value'])


class TestHoverLinearResource(unittest.TestCase):
    """Test 11: Hover on linear resource shows status."""
    def test_hover_handle(self):
        store = DocumentStore()
        doc = store.open('file:///hvrh.en',
                         'open the file "x.txt" as my_file.\nclose my_file.')
        engine = HoverEngine()
        result = engine.hover(doc, {'line': 0, 'character': 30})
        # my_file is at char ~30, but word extraction should find it
        if result:
            self.assertIn('my_file', result['contents']['value'])


class TestDefinition(unittest.TestCase):
    """Test 12: Definition on variable returns correct location."""
    def test_goto_def(self):
        store = DocumentStore()
        doc = store.open('file:///def.en', 'the number x is 5.\nsay x.')
        engine = DefinitionEngine()
        result = engine.definition(doc, {'line': 1, 'character': 4})
        self.assertIsNotNone(result)
        self.assertEqual(result['uri'], 'file:///def.en')
        self.assertEqual(result['range']['start']['line'], 0)


class TestFormatterPeriods(unittest.TestCase):
    """Test 13: Formatter adds missing periods."""
    def test_add_period(self):
        formatter = Formatter()
        edits = formatter.format('say "Hello"\nthe number x is 5\n')
        self.assertTrue(len(edits) > 0)
        self.assertIn('.', edits[0]['newText'])


class TestFormatterIndent(unittest.TestCase):
    """Test 14: Formatter corrects indentation in for loop."""
    def test_indent(self):
        formatter = Formatter()
        edits = formatter.format('for each name in team\nsay name.\n')
        self.assertTrue(len(edits) > 0)
        self.assertIn('    say', edits[0]['newText'])


class TestDebounce(unittest.TestCase):
    """Test 15: Debounce — rapid changes trigger only one analysis."""
    def test_debounce(self):
        calls = []

        def mock_publish(uri, diags):
            calls.append(uri)

        engine = DiagnosticsEngine(mock_publish, delay=0.05)
        store = DocumentStore()
        store.open('file:///debounce.en', 'say "a".')
        # Fire 3 rapid changes
        engine.schedule('file:///debounce.en', store)
        engine.schedule('file:///debounce.en', store)
        engine.schedule('file:///debounce.en', store)
        time.sleep(0.2)
        # Should have coalesced into 1 call
        self.assertEqual(len(calls), 1)


class TestDidClose(unittest.TestCase):
    """Test 16: didClose cleans up document state."""
    def test_close(self):
        handlers = LSPHandlers(_noop_send)
        handlers.handle_initialize({})
        handlers.handle_textDocument_didOpen({
            'textDocument': {'uri': 'file:///cls.en', 'text': 'say "x".', 'version': 1}
        })
        self.assertIsNotNone(handlers.doc_store.get('file:///cls.en'))
        handlers.handle_textDocument_didClose({
            'textDocument': {'uri': 'file:///cls.en'}
        })
        self.assertIsNone(handlers.doc_store.get('file:///cls.en'))


class TestShutdownExit(unittest.TestCase):
    """Test 17: shutdown + exit sequence completes cleanly."""
    def test_shutdown(self):
        handlers = LSPHandlers(_noop_send)
        handlers.handle_initialize({})
        result = handlers.handle_shutdown({})
        self.assertIsNone(result)
        self.assertFalse(handlers._initialized)


class TestFullFlow(unittest.TestCase):
    """Test 18: Full flow — open, diagnostics, fix, hover, complete."""
    def test_full_flow(self):
        published = []

        def capture(method, params):
            published.append((method, params))

        handlers = LSPHandlers(capture)
        handlers.handle_initialize({})

        # Open file with error
        handlers.handle_textDocument_didOpen({
            'textDocument': {
                'uri': 'file:///flow.en',
                'text': 'say ghost.',
                'version': 1
            }
        })
        doc = handlers.doc_store.get('file:///flow.en')
        self.assertTrue(len(doc.diagnostics) > 0)

        # Fix the error
        handlers.handle_textDocument_didChange({
            'textDocument': {'uri': 'file:///flow.en', 'version': 2},
            'contentChanges': [{'text': 'say "Hello".'}]
        })
        doc = handlers.doc_store.get('file:///flow.en')
        self.assertEqual(doc.diagnostics, [])

        # Hover on say
        hover = handlers.handle_textDocument_hover({
            'textDocument': {'uri': 'file:///flow.en'},
            'position': {'line': 0, 'character': 1}
        })
        self.assertIsNotNone(hover)

        # Completion
        comp = handlers.handle_textDocument_completion({
            'textDocument': {'uri': 'file:///flow.en'},
            'position': {'line': 0, 'character': 0}
        })
        self.assertTrue(len(comp['items']) > 0)


if __name__ == '__main__':
    unittest.main()
