import json
from ast_nodes import ASTNode

def ast_to_json(node_or_nodes):
    if isinstance(node_or_nodes, ASTNode):
        return json.dumps(node_or_nodes.to_dict(), indent=2)
    elif isinstance(node_or_nodes, list):
        return json.dumps([n.to_dict() for n in node_or_nodes], indent=2)
    return str(node_or_nodes)

def print_ast(node_or_nodes):
    print(ast_to_json(node_or_nodes))
