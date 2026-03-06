import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer
from parser import Parser
from printer import ast_to_json

class TestParser(unittest.TestCase):
    def test_program_1(self):
        code = 'say "Hello, World"'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(ast.statements[0].__class__.__name__, 'PrintStatement')
        self.assertEqual(ast.statements[0].value.__class__.__name__, 'LiteralString')
        self.assertEqual(ast.statements[0].value.value, 'Hello, World')
        
        print("\n--- Program 1 AST ---")
        print(ast_to_json(ast))

    def test_program_2(self):
        code = '''the number x is 5.
the number y is 10.
add x and y then say the result.'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.statements), 4)
        self.assertEqual(ast.statements[0].__class__.__name__, 'VarDecl')
        self.assertEqual(ast.statements[1].__class__.__name__, 'VarDecl')
        self.assertEqual(ast.statements[2].__class__.__name__, 'BinaryOp')
        self.assertEqual(ast.statements[3].__class__.__name__, 'PrintStatement')
        
        print("\n--- Program 2 AST ---")
        print(ast_to_json(ast))

    def test_program_3(self):
        code = '''create a list of names called team.
add "Alice" to team.
add "Bob" to team.
for each name in team say name.'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.statements), 4)
        self.assertEqual(ast.statements[0].__class__.__name__, 'ListDecl')
        self.assertEqual(ast.statements[1].__class__.__name__, 'ListAppend')
        self.assertEqual(ast.statements[2].__class__.__name__, 'ListAppend')
        self.assertEqual(ast.statements[3].__class__.__name__, 'ForLoop')
        
        print("\n--- Program 3 AST ---")
        print(ast_to_json(ast))

if __name__ == '__main__':
    unittest.main()
