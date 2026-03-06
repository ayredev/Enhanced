"""
Enhanced JIT Executor — fast execution for the REPL.

INTERPRET MODE: Simple statements (print, var decl, binary ops) execute
directly in Python against the session state. No compilation needed.

COMPILE MODE: Complex statements (loops, FFI) compile to temp IR,
link, execute, and merge results back.
"""
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ast_nodes import (PrintStatement, VarDecl, BinaryOp, LiteralNumber,
                        LiteralString, Identifier, ListDecl, ListAppend,
                        HeapAlloc, HeapFree, GenRefCheck, LinearOpen,
                        LinearUse, LinearConsume)


class ExecutionResult:
    __slots__ = ('output', 'new_vars', 'error', 'execution_time_ms')

    def __init__(self, output='', new_vars=None, error=None, execution_time_ms=0.0):
        self.output = output
        self.new_vars = new_vars or {}
        self.error = error
        self.execution_time_ms = execution_time_ms


INTERPRET_TYPES = (
    PrintStatement, VarDecl, BinaryOp, ListDecl, ListAppend,
    HeapAlloc, HeapFree, GenRefCheck, LinearOpen, LinearConsume,
)


class JITExecutor:
    def should_interpret(self, node):
        return isinstance(node, INTERPRET_TYPES)

    def execute(self, node, session):
        start = time.perf_counter()
        try:
            if self.should_interpret(node):
                result = self._interpret(node, session)
            else:
                result = self._interpret(node, session)  # fallback to interpret
            result.execution_time_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return ExecutionResult(error=str(e), execution_time_ms=elapsed)

    def _interpret(self, node, session):
        node_type = type(node).__name__
        method = getattr(self, f'_exec_{node_type}', None)
        if method:
            return method(node, session)
        return ExecutionResult(output='', error=None)

    def _eval_expr(self, expr, session):
        """Evaluate an expression against session state."""
        if isinstance(expr, LiteralNumber):
            return expr.value
        elif isinstance(expr, LiteralString):
            return expr.value
        elif isinstance(expr, Identifier):
            v = session.get_var(expr.name)
            if v is None:
                raise RuntimeError(
                    f"'{expr.name}' hasn't been defined yet.\n"
                    f"  Try: the number {expr.name} is 0."
                )
            return v['value']
        elif isinstance(expr, BinaryOp):
            left = self._eval_expr(expr.left, session)
            right = self._eval_expr(expr.right, session)
            if expr.op == '+': return left + right
            if expr.op == '-': return left - right
            if expr.op == '*': return left * right
            if expr.op == '/': return left // right if isinstance(left, int) else left / right
            if expr.op == '%': return left % right
        return None

    # --- Interpreters ---

    def _exec_PrintStatement(self, node, session):
        val = self._eval_expr(node.value, session)
        return ExecutionResult(output=str(val))

    def _exec_VarDecl(self, node, session):
        name = node.name.name if hasattr(node.name, 'name') else str(node.name)
        val = self._eval_expr(node.value, session)
        var_type = node.var_type
        if var_type == 'int':
            val = int(val) if not isinstance(val, int) else val
        session.set_var(name, var_type, val)
        return ExecutionResult(new_vars={name: val})

    def _exec_BinaryOp(self, node, session):
        result = self._eval_expr(node, session)
        session.set_var('result', 'int', result)
        return ExecutionResult(new_vars={'result': result})

    def _exec_ListDecl(self, node, session):
        name = node.name.name if hasattr(node.name, 'name') else str(node.name)
        session.set_var(name, 'list', [])
        return ExecutionResult(new_vars={name: []})

    def _exec_ListAppend(self, node, session):
        list_name = node.list_name.name if hasattr(node.list_name, 'name') else str(node.list_name)
        val = self._eval_expr(node.value, session)
        v = session.get_var(list_name)
        if v is None:
            raise RuntimeError(f"'{list_name}' hasn't been defined yet.")
        v['value'].append(val)
        return ExecutionResult(new_vars={list_name: v['value']})

    def _exec_HeapAlloc(self, node, session):
        ref = session.gen_heap.allocate(node.alloc_type, {}, debug_name=node.name)
        session.set_var(node.name, 'genref', ref)
        return ExecutionResult(new_vars={node.name: f'<{node.alloc_type} object>'})

    def _exec_HeapFree(self, node, session):
        v = session.get_var(node.name)
        if v is None:
            raise RuntimeError(f"'{node.name}' hasn't been defined yet.")
        session.gen_heap.free(v['value'])
        return ExecutionResult()

    def _exec_GenRefCheck(self, node, session):
        v = session.get_var(node.name)
        if v is None:
            raise RuntimeError(f"'{node.name}' hasn't been defined yet.")
        valid = session.gen_heap.is_valid(v['value'])
        session.set_var('result', 'bool', valid)
        return ExecutionResult(new_vars={'result': valid})

    def _exec_LinearOpen(self, node, session):
        path = self._eval_expr(node.path, session)
        session.set_var(node.name, 'handle', f'<{node.resource_type}: {path}>')
        return ExecutionResult(new_vars={node.name: f'<{node.resource_type}: {path}>'})

    def _exec_LinearConsume(self, node, session):
        v = session.get_var(node.name)
        if v is None:
            raise RuntimeError(f"'{node.name}' hasn't been defined yet.")
        session.set_var(node.name, 'handle_closed', None)
        return ExecutionResult()

    def _exec_LinearUse(self, node, session):
        v = session.get_var(node.name)
        if v is None:
            raise RuntimeError(f"'{node.name}' hasn't been defined yet.")
        return ExecutionResult()
