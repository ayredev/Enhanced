"""
Test Memory Safety — Generational References + Linear Types
"""
import unittest
import os
import sys
import time

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory.gen_ref import GenerationalHeap, GenRef, SafetyError
from memory.linear_types import LinearTypeChecker, LinearTypeError, UNCONSUMED, CONSUMED
from memory.mem_analyzer import MemoryAnalyzer, MemoryAnalysisError

# We also need the compiler pipeline for full-program tests
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer


class TestGenRef(unittest.TestCase):
    """Tests for the Generational Reference heap simulator."""

    def setUp(self):
        self.heap = GenerationalHeap()

    def test_allocate_read_free(self):
        ref = self.heap.allocate('person', {'name': 'Alice', 'age': 30}, debug_name='alice')
        self.assertEqual(ref.gen, 0)
        val = self.heap.deref(ref)
        self.assertEqual(val['name'], 'Alice')
        self.heap.free(ref)
        # gen should have incremented
        slot = self.heap.slots[ref.addr]
        self.assertEqual(slot.gen, 1)
        self.assertTrue(slot.is_free)

    def test_use_after_free_raises(self):
        ref = self.heap.allocate('person', {'name': 'Bob'}, debug_name='bob')
        self.heap.free(ref)
        with self.assertRaises(SafetyError) as ctx:
            self.heap.deref(ref)
        self.assertIn("bob", str(ctx.exception))
        self.assertIn("already freed", str(ctx.exception))

    def test_is_valid_after_free(self):
        ref = self.heap.allocate('user', 'data', debug_name='u')
        self.assertTrue(self.heap.is_valid(ref))
        self.heap.free(ref)
        self.assertFalse(self.heap.is_valid(ref))

    def test_double_free_raises(self):
        ref = self.heap.allocate('person', 42, debug_name='x')
        self.heap.free(ref)
        with self.assertRaises(SafetyError):
            self.heap.free(ref)


class TestLinearTypes(unittest.TestCase):
    """Tests for the LinearTypeChecker — compile-time resource safety."""

    def _make_ast(self, statements):
        """Helper: build a minimal Program-like object."""
        class FakeProgram:
            pass
        p = FakeProgram()
        p.statements = statements
        return p

    def _make_node(self, cls_name, **kwargs):
        """Helper: build a minimal AST node."""
        class FakeNode:
            pass
        n = FakeNode()
        n.__class__ = type(cls_name, (), {})
        for k, v in kwargs.items():
            setattr(n, k, v)
        return n

    def test_open_and_close_clean(self):
        from ast_nodes import LinearOpen, LinearConsume, LiteralString
        stmts = [
            LinearOpen('file', LiteralString("test.txt"), 'my_file'),
            LinearConsume('my_file'),
        ]
        stmts[0].line = 1
        stmts[1].line = 2
        checker = LinearTypeChecker()
        errors = checker.check(self._make_ast(stmts))
        self.assertEqual(errors, [])

    def test_forgot_to_close(self):
        from ast_nodes import LinearOpen, LiteralString
        stmts = [
            LinearOpen('file', LiteralString("test.txt"), 'log_file'),
        ]
        stmts[0].line = 1
        checker = LinearTypeChecker()
        errors = checker.check(self._make_ast(stmts))
        self.assertEqual(len(errors), 1)
        self.assertIn("never closed", errors[0])
        self.assertIn("log_file", errors[0])

    def test_use_after_close(self):
        from ast_nodes import LinearOpen, LinearConsume, LinearUse, LiteralString
        stmts = [
            LinearOpen('file', LiteralString("data.txt"), 'f'),
            LinearConsume('f'),
            LinearUse('f', 'read'),
        ]
        stmts[0].line = 1
        stmts[1].line = 2
        stmts[2].line = 3
        checker = LinearTypeChecker()
        errors = checker.check(self._make_ast(stmts))
        self.assertEqual(len(errors), 1)
        self.assertIn("already closed", errors[0])

    def test_double_assignment_error(self):
        from ast_nodes import LinearOpen, VarDecl, Identifier, LiteralString
        stmts = [
            LinearOpen('file', LiteralString("data.txt"), 'my_file'),
            VarDecl('handle', Identifier('other_file'), Identifier('my_file')),
        ]
        stmts[0].line = 1
        stmts[1].line = 2
        checker = LinearTypeChecker()
        errors = checker.check(self._make_ast(stmts))
        # Should flag: can't copy a file handle
        has_copy_err = any("copy" in e.lower() for e in errors)
        # Also should flag: my_file never closed
        has_close_err = any("never closed" in e for e in errors)
        self.assertTrue(has_copy_err, f"Expected copy error, got: {errors}")


class TestMemoryAnalyzer(unittest.TestCase):
    """Tests for the MemoryAnalyzer pass (linear + genref)."""

    def _make_ast(self, statements):
        class FakeProgram:
            pass
        p = FakeProgram()
        p.statements = statements
        return p

    def test_unclosed_resource_raises_analysis_error(self):
        from ast_nodes import LinearOpen, LiteralString
        stmts = [
            LinearOpen('file', LiteralString("data.txt"), 'log_file'),
        ]
        stmts[0].line = 2
        analyzer = MemoryAnalyzer()
        with self.assertRaises(MemoryAnalysisError) as ctx:
            analyzer.analyze(self._make_ast(stmts))
        self.assertIn("memory safety", str(ctx.exception).lower())


class TestFullPipeline(unittest.TestCase):
    """Tests that .en programs compile through the memory analysis pass."""

    def setUp(self):
        self.enhc_path = os.path.join(os.path.dirname(__file__), '..', 'enhc.py')

    def test_memory_safe_compiles_ir(self):
        import subprocess
        example_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'memory_safe.en')
        result = subprocess.run(['python', self.enhc_path, example_path, '--ir'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Error: {result.stdout} {result.stderr}")
        self.assertIn("HeapAlloc", result.stdout)
        self.assertIn("HeapFree", result.stdout)
        self.assertIn("GenRefCheck", result.stdout)
        self.assertIn("@enhanced_alloc", result.stdout)
        self.assertIn("@enhanced_free", result.stdout)
        self.assertIn("@enhanced_is_valid", result.stdout)

    def test_linear_file_compiles_ir(self):
        import subprocess
        example_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'linear_file.en')
        result = subprocess.run(['python', self.enhc_path, example_path, '--ir'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Error: {result.stdout} {result.stderr}")
        self.assertIn("LinearOpen", result.stdout)
        self.assertIn("LinearConsume", result.stdout)
        self.assertIn("@enhanced_open_file", result.stdout)
        self.assertIn("@enhanced_close_file", result.stdout)


class TestBenchmark(unittest.TestCase):
    """Verify that generational reference ops are lightweight."""

    def test_genref_overhead(self):
        heap = GenerationalHeap()
        N = 10000
        start = time.perf_counter()
        refs = []
        for i in range(N):
            refs.append(heap.allocate('obj', i, debug_name=f'o{i}'))
        for ref in refs:
            heap.deref(ref)
        for ref in refs:
            heap.free(ref)
        elapsed = time.perf_counter() - start
        # 10K alloc+deref+free in under 1 second should be trivial in Python
        self.assertLess(elapsed, 1.0, f"GenRef ops took {elapsed:.3f}s for {N} objects, too slow")


if __name__ == '__main__':
    unittest.main()
