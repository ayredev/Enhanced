"""
Memory Analysis Pass — runs after semantic analysis, before codegen.

1. Runs the LinearTypeChecker to catch resource violations at compile time.
2. Annotates HeapAlloc nodes with gen_ref metadata.
3. Annotates heap dereference nodes with requires_gen_check.
4. Annotates HeapFree nodes with increments_gen.
"""

from memory.linear_types import LinearTypeChecker, LinearTypeError


class MemoryAnalysisError(Exception):
    """Raised when one or more memory safety violations are found."""
    pass


class MemoryAnalyzer:
    def __init__(self):
        self.gen_ref_counter = 0
        self.heap_vars = set()  # variable names that are heap-allocated

    def analyze(self, typed_ast, symbol_table=None):
        """
        Run both linear type checking and generational reference annotation.
        Returns the annotated AST. Raises MemoryAnalysisError on violations.
        """
        # --- Layer 2: Linear Type Checking (compile time) ---
        checker = LinearTypeChecker()
        errors = checker.check(typed_ast)
        if errors:
            msg = "I found some memory safety problems:\n\n"
            for i, e in enumerate(errors, 1):
                msg += f"  Problem {i}: {e}\n\n"
            raise MemoryAnalysisError(msg)

        # --- Layer 1: GenRef Annotations (for codegen) ---
        for stmt in typed_ast.statements:
            self._annotate(stmt)

        return typed_ast

    def _annotate(self, node):
        """Walk AST and annotate heap-related nodes."""
        node_type = type(node).__name__

        if node_type == 'HeapAlloc':
            self.gen_ref_counter += 1
            node.gen_ref_id = self.gen_ref_counter
            node.initial_gen = 0
            self.heap_vars.add(node.name)

        elif node_type == 'HeapFree':
            node.increments_gen = True

        elif node_type == 'GenRefCheck':
            pass  # no annotation needed, codegen handles it

        elif node_type == 'PrintStatement':
            # Check if the print references a heap variable
            if hasattr(node.value, 'name') and node.value.name in self.heap_vars:
                node.requires_gen_check = True

        elif node_type == 'VarDecl':
            # If value references a heap var, mark it
            if hasattr(node.value, 'name') and node.value.name in self.heap_vars:
                node.requires_gen_check = True

        # Recurse into bodies/children
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                self._annotate(child)
        if hasattr(node, 'statements') and isinstance(node.statements, list):
            for child in node.statements:
                self._annotate(child)
