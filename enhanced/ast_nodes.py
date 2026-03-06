import json

class ASTNode:
    def __init__(self):
        self.line = 0
        self.value_type = None

    def to_dict(self):
        result = {}
        result['type'] = self.__class__.__name__
        if hasattr(self, 'value_type') and self.value_type is not None:
            result['value_type'] = str(self.value_type)
        
        for k, v in self.__dict__.items():
            if k in ('line', 'value_type'):
                continue
            if isinstance(v, ASTNode):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                result[k] = v
        return result

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class PrintStatement(ASTNode):
    def __init__(self, value):
        self.value = value

class VarDecl(ASTNode):
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class ForLoop(ASTNode):
    def __init__(self, item, collection, body):
        self.item = item
        self.collection = collection
        self.body = body

class IfStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ListDecl(ASTNode):
    def __init__(self, name):
        self.name = name

class ListAppend(ASTNode):
    def __init__(self, list_name, value):
        self.list_name = list_name
        self.value = value

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class LiteralNumber(ASTNode):
    def __init__(self, value):
        self.value = value

class LiteralString(ASTNode):
    def __init__(self, value):
        self.value = value

class GT(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

# Phase V Output Nodes
class FileRead(ASTNode):
    def __init__(self, path):
        self.path = path

class FileWrite(ASTNode):
    def __init__(self, path, content):
        self.path = path
        self.content = content

class FileAppend(ASTNode):
    def __init__(self, path, content):
        self.path = path
        self.content = content

class FileExists(ASTNode):
    def __init__(self, path):
        self.path = path

class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class ListSize(ASTNode):
    def __init__(self, list_name):
        self.list_name = list_name

class ListGet(ASTNode):
    def __init__(self, list_name, index):
        self.list_name = list_name
        self.index = index  # 0 for first, -1 for last

class ListRemove(ASTNode):
    def __init__(self, list_name, value):
        self.list_name = list_name
        self.value = value

class ListContains(ASTNode):
    def __init__(self, list_name, value):
        self.list_name = list_name
        self.value = value

class ListSort(ASTNode):
    def __init__(self, list_name):
        self.list_name = list_name

class Sleep(ASTNode):
    def __init__(self, ms):
        self.ms = ms

class Timestamp(ASTNode):
    def __init__(self):
        pass

class HttpGet(ASTNode):
    def __init__(self, url):
        self.url = url

class HttpResponseBody(ASTNode):
    def __init__(self):
        pass

class LoadLibrary(ASTNode):
    def __init__(self, library_name):
        self.library_name = library_name

class FFICall(ASTNode):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

# Phase VI Memory Safety Nodes

class HeapAlloc(ASTNode):
    def __init__(self, alloc_type, name):
        self.alloc_type = alloc_type  # e.g. "person", "user"
        self.name = name             # variable name string

class HeapFree(ASTNode):
    def __init__(self, name):
        self.name = name

class GenRefCheck(ASTNode):
    def __init__(self, name):
        self.name = name

class LinearOpen(ASTNode):
    def __init__(self, resource_type, path, name):
        self.resource_type = resource_type  # 'file', 'socket'
        self.path = path                     # expression for the path/address
        self.name = name                     # handle variable name

class LinearUse(ASTNode):
    def __init__(self, name, op, value=None):
        self.name = name    # handle name
        self.op = op        # 'read', 'write', 'send'
        self.value = value  # data to write/send (None for read)

class LinearConsume(ASTNode):
    def __init__(self, name):
        self.name = name
