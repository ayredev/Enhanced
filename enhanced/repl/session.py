"""
Enhanced REPL Session — persistent state across inputs.
Maintains live symbol table, heap, linear environment, and history.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from symbol_table import SymbolTable
from memory.gen_ref import GenerationalHeap


class ReplSession:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.gen_heap = GenerationalHeap()
        self.history = []
        self.variables = {}  # name -> {'type': ..., 'value': ...}
        self.line_counter = 0

    def record(self, source):
        """Record a valid input line in history."""
        self.history.append(source)

    def set_var(self, name, var_type, value):
        self.variables[name] = {'type': var_type, 'value': value}

    def get_var(self, name):
        return self.variables.get(name)

    def get_all_vars(self):
        return dict(self.variables)

    def get_var_names(self):
        return list(self.variables.keys())

    def reset(self):
        self.symbol_table = SymbolTable()
        self.gen_heap = GenerationalHeap()
        self.history = []
        self.variables = {}
        self.line_counter = 0

    def save(self, path):
        """Save entire session history as a .en file."""
        with open(path, 'w', encoding='utf-8') as f:
            for line in self.history:
                f.write(line + '\n')

    def get_history(self, count=20):
        return self.history[-count:]

    def next_line(self):
        self.line_counter += 1
        return self.line_counter
