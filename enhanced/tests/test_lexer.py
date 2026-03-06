import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer, Token

class TestLexer(unittest.TestCase):
    def test_program_1(self):
        code = 'say "Hello, World"'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token('VERB', 'say'),
            Token('LITERAL_STRING', 'Hello, World')
        ])

    def test_program_2(self):
        code = '''the number x is 5.
the number y is 10.
add x and y then say the result.'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token('KEYWORD', 'the'), Token('NOUN', 'number'), Token('IDENTIFIER', 'x'), Token('VERB', 'is'), Token('LITERAL_NUMBER', '5'), Token('PUNCTUATION', '.'),
            Token('KEYWORD', 'the'), Token('NOUN', 'number'), Token('IDENTIFIER', 'y'), Token('VERB', 'is'), Token('LITERAL_NUMBER', '10'), Token('PUNCTUATION', '.'),
            Token('VERB', 'add'), Token('IDENTIFIER', 'x'), Token('CONNECTOR', 'and'), Token('IDENTIFIER', 'y'), Token('CONNECTOR', 'then'), Token('VERB', 'say'), Token('KEYWORD', 'the'), Token('NOUN', 'result'), Token('PUNCTUATION', '.')
        ])

    def test_program_3(self):
        code = '''create a list of names called team.
add "Alice" to team.
add "Bob" to team.
for each name in team say name.'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token('VERB', 'create'), Token('KEYWORD', 'a'), Token('NOUN', 'list'), Token('CONNECTOR', 'of'), Token('NOUN', 'names'), Token('VERB', 'called'), Token('IDENTIFIER', 'team'), Token('PUNCTUATION', '.'),
            Token('VERB', 'add'), Token('LITERAL_STRING', 'Alice'), Token('CONNECTOR', 'to'), Token('IDENTIFIER', 'team'), Token('PUNCTUATION', '.'),
            Token('VERB', 'add'), Token('LITERAL_STRING', 'Bob'), Token('CONNECTOR', 'to'), Token('IDENTIFIER', 'team'), Token('PUNCTUATION', '.'),
            Token('KEYWORD', 'for'), Token('KEYWORD', 'each'), Token('IDENTIFIER', 'name'), Token('KEYWORD', 'in'), Token('IDENTIFIER', 'team'), Token('VERB', 'say'), Token('IDENTIFIER', 'name'), Token('PUNCTUATION', '.')
        ])

if __name__ == '__main__':
    unittest.main()
