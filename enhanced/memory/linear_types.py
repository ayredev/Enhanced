"""
Linear Types — Layer 2 of Enhanced Memory Safety.

Linear resources (file handles, sockets, FFI handles) must be used
exactly once: opened, used, then closed. The compiler catches violations
at compile time with plain English error messages.
"""


class LinearTypeError(Exception):
    """Raised at compile time when a linear resource rule is violated."""
    pass


# Resource states
UNCONSUMED = 'UNCONSUMED'   # resource is open, not yet closed
CONSUMED   = 'CONSUMED'     # resource has been closed
MOVED      = 'MOVED'        # resource was moved to another variable


class LinearResource:
    """Tracks a single linear resource's lifecycle."""
    __slots__ = ('name', 'resource_type', 'state', 'open_line', 'consume_line', 'moved_to')

    def __init__(self, name, resource_type, open_line):
        self.name = name
        self.resource_type = resource_type  # 'file', 'socket', 'ffi_handle'
        self.state = UNCONSUMED
        self.open_line = open_line
        self.consume_line = None
        self.moved_to = None


class LinearTypeChecker:
    """
    Walks the Typed AST after semantic analysis and tracks all linear resources.
    Errors are collected and returned as a list of plain English messages.
    """

    def __init__(self):
        self.resources = {}   # name → LinearResource
        self.errors = []

    def check(self, typed_ast):
        """Run the linear type check on the full AST. Returns list of error strings."""
        self.resources = {}
        self.errors = []
        for stmt in typed_ast.statements:
            self._visit(stmt)
        # After all statements: check for unclosed resources
        for name, res in self.resources.items():
            if res.state == UNCONSUMED:
                self.errors.append(
                    f"You opened '{name}' on line {res.open_line} but never closed it.\n"
                    f"Add 'close {name}' before the program ends."
                )
        return self.errors

    def _visit(self, node):
        node_type = type(node).__name__
        method = getattr(self, f'_visit_{node_type}', None)
        if method:
            method(node)

    # --- Linear resource open ---
    def _visit_LinearOpen(self, node):
        name = node.name
        line = getattr(node, 'line', 0)
        if name in self.resources and self.resources[name].state == UNCONSUMED:
            self.errors.append(
                f"You tried to open '{name}' on line {line}, but it's already open "
                f"from line {self.resources[name].open_line}.\n"
                f"Close it first before opening again."
            )
            return
        self.resources[name] = LinearResource(name, node.resource_type, line)

    # --- Linear resource use ---
    def _visit_LinearUse(self, node):
        name = node.name
        line = getattr(node, 'line', 0)
        if name not in self.resources:
            self.errors.append(
                f"You tried to use '{name}' on line {line}, but it was never opened.\n"
                f"Open it first with 'open the file ... as {name}'."
            )
            return
        res = self.resources[name]
        if res.state == CONSUMED:
            self.errors.append(
                f"You already closed '{name}' on line {res.consume_line}.\n"
                f"You can't use it anymore after closing."
            )
        elif res.state == MOVED:
            self.errors.append(
                f"'{name}' was moved to '{res.moved_to}' and can no longer be used directly."
            )

    # --- Linear resource close ---
    def _visit_LinearConsume(self, node):
        name = node.name
        line = getattr(node, 'line', 0)
        if name not in self.resources:
            self.errors.append(
                f"You tried to close '{name}' on line {line}, but it was never opened."
            )
            return
        res = self.resources[name]
        if res.state == CONSUMED:
            self.errors.append(
                f"You already closed '{name}' on line {res.consume_line}.\n"
                f"You can't close it twice."
            )
            return
        res.state = CONSUMED
        res.consume_line = line

    # --- HeapAlloc / HeapFree / GenRefCheck are not linear, skip them ---
    def _visit_HeapAlloc(self, node):
        pass

    def _visit_HeapFree(self, node):
        pass

    def _visit_GenRefCheck(self, node):
        pass

    # --- Assignment of a linear resource to a new variable ---
    def _visit_VarDecl(self, node):
        # If the value being assigned IS a linear resource identifier, mark it as moved
        if hasattr(node.value, 'name') and node.value.name in self.resources:
            src = node.value.name
            dst = node.name.name if hasattr(node.name, 'name') else str(node.name)
            res = self.resources[src]
            if res.state == UNCONSUMED:
                line = getattr(node, 'line', 0)
                self.errors.append(
                    f"You can't copy a {res.resource_type} handle.\n"
                    f"'{dst}' would be the same {res.resource_type} as '{src}'.\n"
                    f"Use one name for it."
                )
