from ast_nodes import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        tok = self.peek()
        if tok:
            self.pos += 1
        return tok

    def match_type(self, token_type):
        tok = self.peek()
        if tok and tok.type == token_type:
            return self.consume()
        return None

    def match_val(self, token_type, value):
        tok = self.peek()
        if tok and tok.type == token_type and tok.value == value:
            return self.consume()
        return None

    def expect_type(self, token_type, msg):
        tok = self.match_type(token_type)
        if not tok:
            actual = self.peek()
            actual_str = f"{actual.type}('{actual.value}')" if actual else "EOF"
            raise ParserError(f"{msg}. Got {actual_str}")
        return tok

    def expect_val(self, token_type, value, msg):
        tok = self.match_val(token_type, value)
        if not tok:
            actual = self.peek()
            actual_str = f"{actual.type}('{actual.value}')" if actual else "EOF"
            raise ParserError(f"{msg}. Got {actual_str}")
        return tok

    def parse(self):
        statements = []
        while self.peek():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            while self.match_val("PUNCTUATION", ".") or self.match_val("CONNECTOR", "then"):
                pass
            while self.match_val("PUNCTUATION", ","):
                pass
        return Program(statements)

    def parse_statement(self):
        tok = self.peek()
        if not tok:
            return None
        line = tok.line
        stmt = self._parse_statement_inner()
        if stmt:
            stmt.line = line
        return stmt

    def _parse_statement_inner(self):
        tok = self.peek()
        if not tok:
            return None

        if self.match_val("VERB", "say"):
            expr = self.parse_expression()
            return PrintStatement(expr)

        elif self.match_val("KEYWORD", "the"):
            noun = self.expect_type("NOUN", "Expected noun after 'the'")
            if noun.value in ("number", "text"):
                name_tok = self.expect_type("IDENTIFIER", f"Expected name after {noun.value}")
                self.expect_val("VERB", "is", f"Expected 'is' after variable name")
                val = self.parse_expression()
                var_type = "int" if noun.value == "number" else "str"
                return VarDecl(var_type, Identifier(name_tok.value), val)
            else:
                raise ParserError(f"I don't understand 'the {noun.value}' as a declaration.")

        elif self.match_val("VERB", "add"):
            left = self.parse_expression()
            if self.match_val("CONNECTOR", "and"):
                right = self.parse_expression()
                return BinaryOp("+", left, right)
            elif self.match_val("CONNECTOR", "to"):
                list_name = self.expect_type("IDENTIFIER", "Expected list name after 'to'")
                return ListAppend(Identifier(list_name.value), left)
            else:
                raise ParserError("Expected 'and' or 'to' after 'add X'")

        elif self.match_val("VERB", "subtract"):
            left = self.parse_expression()
            self.expect_val("CONNECTOR", "from", "Expected 'from' after subtract X")
            right = self.parse_expression()
            return BinaryOp("-", right, left)

        elif self.match_val("KEYWORD", "for"):
            self.expect_val("KEYWORD", "each", "Expected 'each' after 'for'")
            item_name = self.expect_type("IDENTIFIER", "Expected identifier after 'for each'")
            self.expect_val("KEYWORD", "in", "Expected 'in' after 'for each Z'")
            collection = self.parse_expression()
            body_stmt = self.parse_statement()
            return ForLoop(Identifier(item_name.value), collection, [body_stmt])

        elif self.match_val("KEYWORD", "if"):
            left = self.parse_expression()
            self.expect_val("VERB", "is", "Expected 'is' after if condition left")
            self.expect_val("KEYWORD", "greater", "Expected 'greater'")
            self.expect_val("KEYWORD", "than", "Expected 'than'")
            right = self.parse_expression()
            body_stmt = self.parse_statement()
            return IfStatement(GT(left, right), [body_stmt])
        
        elif self.match_val("VERB", "create"):
            article = self.expect_type("KEYWORD", "Expected article after 'create'")
            if article.value not in ("a", "an"):
                raise ParserError(f"Expected 'a' or 'an', got {article.value}")
            # Check for 'new' → HeapAlloc, otherwise list
            if self.match_val("KEYWORD", "new"):
                type_tok = self.expect_type("NOUN", "Expected type name after 'new'")
                self.expect_val("VERB", "called", "Expected 'called'")
                name_tok = self.expect_type("IDENTIFIER", "Expected variable name")
                return HeapAlloc(type_tok.value, name_tok.value)
            self.expect_val("NOUN", "list", "Expected 'list'")
            if self.match_val("CONNECTOR", "of"):
                self.expect_type("NOUN", "Expected noun after 'of'")
            self.expect_val("VERB", "called", "Expected 'called'")
            name_tok = self.expect_type("IDENTIFIER", "Expected list name")
            return ListDecl(Identifier(name_tok.value))

        # Stdlib & FFI additions
        elif self.match_val("VERB", "read"):
            # Could be 'read the file X' (FileRead) or 'read from X' (LinearUse)
            if self.peek() and self.peek().value == "from":
                self.consume()  # consume 'from'
                handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'read from'")
                return LinearUse(handle_tok.value, 'read')
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            self.expect_val("NOUN", "file", "Expected 'file'")
            path = self.parse_expression()
            return FileRead(path)

        elif self.match_val("VERB", "write"):
            content = self.parse_expression()
            self.expect_val("CONNECTOR", "to", "Expected 'to'")
            # Check: 'the file X' (FileWrite) vs identifier (LinearUse write)
            if self.peek() and self.peek().value == "the":
                self.consume()
                self.expect_val("NOUN", "file", "Expected 'file'")
                path = self.parse_expression()
                return FileWrite(path, content)
            else:
                handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'write X to'")
                return LinearUse(handle_tok.value, 'write', content)

        elif self.match_val("VERB", "append"):
            content = self.parse_expression()
            self.expect_val("CONNECTOR", "to", "Expected 'to'")
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            self.expect_val("NOUN", "file", "Expected 'file'")
            path = self.parse_expression()
            return FileAppend(path, content)

        elif self.match_val("VERB", "check"):
            self.expect_val("KEYWORD", "if", "Expected 'if'")
            # 'check if X is still valid' → GenRefCheck
            # 'check if the file X exists' → FileExists
            # 'check if X is in Y' → ListContains
            if self.peek() and self.peek().value == "the" and self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].value == "file":
                self.consume()
                self.consume()
                path = self.parse_expression()
                self.expect_val("VERB", "exists", "Expected 'exists'")
                return FileExists(path)
            else:
                name_tok = self.peek()
                # Try GenRefCheck: 'check if X is still valid'
                if name_tok and name_tok.type == "IDENTIFIER":
                    saved_pos = self.pos
                    self.consume()
                    if self.match_val("VERB", "is") and self.match_val("KEYWORD", "still") and self.match_val("KEYWORD", "valid"):
                        return GenRefCheck(name_tok.value)
                    # Not a GenRefCheck, backtrack
                    self.pos = saved_pos
                # ListContains: 'check if X is in Y'
                val = self.parse_expression()
                self.expect_val("VERB", "is", "Expected 'is'")
                self.expect_val("KEYWORD", "in", "Expected 'in'")
                list_expr = self.parse_expression()
                return ListContains(list_expr, val)

        elif self.match_val("VERB", "multiply"):
            left = self.parse_expression()
            self.expect_val("CONNECTOR", "and", "Expected 'and'")
            right = self.parse_expression()
            return BinaryOp("*", left, right)

        elif self.match_val("VERB", "divide"):
            left = self.parse_expression()
            self.expect_val("CONNECTOR", "by", "Expected 'by'")
            right = self.parse_expression()
            return BinaryOp("/", left, right)

        elif self.match_val("VERB", "remove"):
            val = self.parse_expression()
            self.expect_val("CONNECTOR", "from", "Expected 'from'")
            list_expr = self.parse_expression()
            return ListRemove(list_expr, val)

        elif self.match_val("VERB", "sort"):
            list_expr = self.parse_expression()
            return ListSort(list_expr)

        elif self.match_val("VERB", "wait"):
            ms_expr = self.parse_expression()
            self.expect_val("NOUN", "seconds", "Expected 'seconds'")
            return Sleep(ms_expr)

        elif self.match_val("VERB", "get"):
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            self.expect_val("NOUN", "url", "Expected 'url'")
            url = self.parse_expression()
            return HttpGet(url)

        elif self.match_val("VERB", "load"):
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            self.expect_val("NOUN", "library", "Expected 'library'")
            name = self.parse_expression()
            return LoadLibrary(name)
            
        elif self.match_val("VERB", "call"):
            func = self.parse_expression()
            self.expect_val("CONNECTOR", "with", "Expected 'with'")
            args = [self.parse_expression()]
            while self.match_val("CONNECTOR", "and"):
                args.append(self.parse_expression())
            return FFICall(func, args)
            
        # specifically "set the presence state to X"
        elif self.match_val("VERB", "set"):
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            # we can parse identifier until "to"
            # It's an assignment or special mapping. In Phase V prompt:
            # "set the presence state to 'Coding in Enhanced'."
            # This is essentially assigning variables: "presence_state" = 'Coding in Enhanced'.
            # Or translating "presence state" into a variable name to pass to Discord_UpdatePresence?
            # Wait, the prompt says:
            # call "Discord_UpdatePresence" with the presence.
            # So "the presence" represents the object. We can just compile 'set the X to Y' as setting a variable.
            var_parts = []
            while self.peek() and self.peek().value != "to":
                var_parts.append(self.consume().value)
            self.expect_val("CONNECTOR", "to", "Expected 'to'")
            val = self.parse_expression()
            var_name = "_".join(var_parts)
            return VarDecl("any", Identifier(var_name), val)
        # Phase VI: Memory safety verbs
        elif self.match_val("VERB", "free"):
            name_tok = self.expect_type("IDENTIFIER", "Expected variable name after 'free'")
            return HeapFree(name_tok.value)

        elif self.match_val("VERB", "open"):
            self.expect_val("KEYWORD", "the", "Expected 'the'")
            resource_tok = self.peek()
            if resource_tok and resource_tok.value == "file":
                self.consume()
                path = self.parse_expression()
                self.expect_val("KEYWORD", "as", "Expected 'as'")
                handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'as'")
                return LinearOpen('file', path, handle_tok.value)
            elif resource_tok and resource_tok.value == "connection":
                self.consume()
                self.expect_val("CONNECTOR", "to", "Expected 'to'")
                addr = self.parse_expression()
                self.expect_val("KEYWORD", "as", "Expected 'as'")
                handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'as'")
                return LinearOpen('socket', addr, handle_tok.value)
            else:
                raise ParserError("Expected 'file' or 'connection' after 'open the'")

        elif self.match_val("VERB", "close"):
            handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'close'")
            return LinearConsume(handle_tok.value)

        elif self.match_val("VERB", "send"):
            data = self.parse_expression()
            self.expect_val("CONNECTOR", "through", "Expected 'through'")
            handle_tok = self.expect_type("IDENTIFIER", "Expected handle name after 'through'")
            return LinearUse(handle_tok.value, 'send', data)

        raise ParserError(f"I don't understand '{tok.value}' \u2014 did you mean something else?")

    def parse_expression(self):
        tok = self.peek()
        if not tok:
            raise ParserError("Expected expression but found end of file")
        line = tok.line
        expr = self._parse_primary()
        if expr:
            expr.line = line

        while self.peek() and self.peek().type == "CONNECTOR" and self.peek().value == "to":
            if self.pos + 3 < len(self.tokens) and \
               self.tokens[self.pos+1].value == "the" and \
               self.tokens[self.pos+2].value == "power" and \
               self.tokens[self.pos+3].value == "of":
                self.consume()
                self.consume()
                self.consume()
                self.consume()
                right = self._parse_primary()
                expr = BinaryOp("pow", expr, right)
                expr.line = line
            else:
                break
        return expr

    def _parse_primary(self):
        tok = self.peek()
        if not tok:
            raise ParserError("Expected expression but found end of file")

        if tok.type == "LITERAL_NUMBER":
            self.consume()
            return LiteralNumber(int(tok.value))
        elif tok.type == "LITERAL_STRING":
            self.consume()
            return LiteralString(tok.value)
        elif tok.type == "KEYWORD" and tok.value == "the":
            self.consume()
            if self.match_val("NOUN", "remainder"):
                self.expect_val("CONNECTOR", "of", "Expected 'of'")
                left = self.parse_expression()
                self.expect_val("VERB", "divided", "Expected 'divided'")
                self.expect_val("CONNECTOR", "by", "Expected 'by'")
                right = self.parse_expression()
                return BinaryOp("%", left, right)
            
            elif self.match_val("NOUN", "absolute"):
                self.expect_val("NOUN", "value", "Expected 'value'")
                self.expect_val("CONNECTOR", "of", "Expected 'of'")
                val = self.parse_expression()
                return UnaryOp("abs", val)

            elif self.match_val("NOUN", "size"):
                self.expect_val("CONNECTOR", "of", "Expected 'of'")
                list_expr = self.parse_expression()
                return ListSize(list_expr)

            elif self.match_val("KEYWORD", "first"):
                self.expect_val("NOUN", "item", "Expected 'item'")
                self.expect_val("KEYWORD", "in", "Expected 'in'")
                list_expr = self.parse_expression()
                return ListGet(list_expr, 0)

            elif self.match_val("KEYWORD", "last"):
                self.expect_val("NOUN", "item", "Expected 'item'")
                self.expect_val("KEYWORD", "in", "Expected 'in'")
                list_expr = self.parse_expression()
                return ListGet(list_expr, -1)
            
            elif self.match_val("KEYWORD", "current"):
                self.expect_val("NOUN", "timestamp", "Expected 'timestamp'")
                return Timestamp()
            
            elif self.match_val("NOUN", "response"):
                self.expect_val("NOUN", "body", "Expected 'body'")
                return HttpResponseBody()

            else:
                noun = self.expect_type("NOUN", "Expected noun after 'the'")
                return Identifier(noun.value)
        elif tok.type == "KEYWORD" and tok.value == "null":
            self.consume()
            return LiteralNumber(0)
        elif tok.type == "IDENTIFIER":
            self.consume()
            return Identifier(tok.value)
        elif tok.type == "NOUN":
            self.consume()
            return Identifier(tok.value)
            
        raise ParserError(f"Expected expression, got {tok.type} '{tok.value}'")
