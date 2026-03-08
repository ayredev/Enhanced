from ast_nodes import *

class WasmCompatibilityChecker:
    def check(self, ast):
        for stmt in ast.statements:
            self.visit(stmt)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Recursively visit children if they exist and are AST nodes
        for attr in dir(node):
            if attr.startswith('_'): continue
            val = getattr(node, attr)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        self.visit(item)
            elif isinstance(val, ASTNode):
                self.visit(val)

    def visit_FileRead(self, node):
        raise Exception("File I/O operations (read) are not supported in the WebAssembly target.")

    def visit_FileWrite(self, node):
        raise Exception("File I/O operations (write) are not supported in the WebAssembly target.")

    def visit_FileAppend(self, node):
        raise Exception("File I/O operations (append) are not supported in the WebAssembly target.")

    def visit_FileExists(self, node):
        raise Exception("File I/O operations (exists) are not supported in the WebAssembly target.")

    def visit_HttpGet(self, node):
        raise Exception("HTTP operations are not supported in the WebAssembly target.")

    def visit_ServerStart(self, node):
        raise Exception("Server operations are not supported in the WebAssembly target.")

    def visit_RouteHandler(self, node):
        raise Exception("Server operations are not supported in the WebAssembly target.")

    def visit_OpenDatabase(self, node):
        raise Exception("Database operations are not supported in the WebAssembly target.")

    def visit_DbExec(self, node):
        raise Exception("Database operations are not supported in the WebAssembly target.")

    def visit_DbQuery(self, node):
        raise Exception("Database operations are not supported in the WebAssembly target.")
