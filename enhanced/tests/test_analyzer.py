import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer, SemanticError

class TestAnalyzer(unittest.TestCase):
    def run_analyzer(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        return analyzer.analyze(ast)

    def test_valid_program_1(self):
        code = 'say "Hello, World"'
        ast = self.run_analyzer(code)
        self.assertEqual(ast.statements[0].value.value_type, "str")

    def test_valid_program_2(self):
        code = '''the number x is 5.
the number y is 10.
add x and y then say the result.'''
        ast = self.run_analyzer(code)
        # Checking that variable nodes get typed
        self.assertEqual(ast.statements[0].value_type, "int")
        self.assertEqual(ast.statements[2].value_type, "int")

    def test_valid_program_3(self):
        code = '''create a list of names called team.
add "Alice" to team.
add "Bob" to team.
for each name in team say name.'''
        ast = self.run_analyzer(code)
        self.assertEqual(ast.statements[0].value_type, "list")

    def test_error_undefined_variable(self):
        code = 'say result.'
        with self.assertRaises(SemanticError) as context:
            self.run_analyzer(code)
        self.assertIn("I found a problem on line 1: 'result' hasn't been defined yet.", str(context.exception))

    def test_error_type_mismatch(self):
        code = '''the number x is 5.
the text y is "hello".
add x and y then say the result.'''
        with self.assertRaises(SemanticError) as context:
            self.run_analyzer(code)
        self.assertIn("You can't add a number and a text together.", str(context.exception))

    def test_error_append_wrong_type(self):
        code = '''create a list called scores.
add "Alice" to scores.
add 99 to scores.'''
        with self.assertRaises(SemanticError) as context:
            self.run_analyzer(code)
        self.assertIn("'scores' holds a texts, but you're trying to add a number.", str(context.exception))

if __name__ == '__main__':
    unittest.main()
