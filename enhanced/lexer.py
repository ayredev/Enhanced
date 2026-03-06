import re

class Token:
    def __init__(self, type_, value, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value

class Lexer:
    KEYWORDS = {"a", "an", "the", "for", "each", "in", "if", "greater", "than", "first", "last", "current", "null", "new", "still", "valid", "as"}
    CONNECTORS = {"and", "then", "with", "to", "from", "of", "by", "through"}
    VERBS = {"say", "create", "add", "set", "subtract", "is", "called", "read", "write", "append", "multiply", "divide", "divided", "remove", "sort", "wait", "get", "load", "call", "check", "exists", "open", "close", "send", "free"}
    NOUNS = {"number", "text", "list", "names", "result", "file", "remainder", "absolute", "value", "power", "size", "item", "seconds", "timestamp", "url", "response", "body", "library", "person", "user", "connection"}

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char == '\n':
                self.line += 1
                self.pos += 1
                continue

            if char.isspace():
                self.pos += 1
                continue

            if char in {'.', ','}:
                tokens.append(Token("PUNCTUATION", char, self.line))
                self.pos += 1
                continue

            if char.isdigit():
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1
                tokens.append(Token("LITERAL_NUMBER", self.text[start:self.pos], self.line))
                continue

            if char == '"':
                self.pos += 1
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos] != '"':
                    if self.text[self.pos] == '\n':
                        self.line += 1
                    self.pos += 1
                tokens.append(Token("LITERAL_STRING", self.text[start:self.pos], self.line))
                if self.pos < len(self.text) and self.text[self.pos] == '"':
                    self.pos += 1 # consume closing quote
                continue

            if char.isalpha():
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                word = self.text[start:self.pos]
                
                if word in Lexer.KEYWORDS:
                    tokens.append(Token("KEYWORD", word, self.line))
                elif word in Lexer.CONNECTORS:
                    tokens.append(Token("CONNECTOR", word, self.line))
                elif word in Lexer.VERBS:
                    tokens.append(Token("VERB", word, self.line))
                elif word in Lexer.NOUNS:
                    tokens.append(Token("NOUN", word, self.line))
                else:
                    tokens.append(Token("IDENTIFIER", word, self.line))
                continue
            
            raise Exception(f"Unexpected character: {char}")

        return tokens
