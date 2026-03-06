#!/usr/bin/env python3
"""
Enhanced REPL — Interactive Shell.
Type English to code. See results instantly.
"""
import sys
import os
import time

# Ensure the enhanced package root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from repl.session import ReplSession
from repl.highlighter import (highlight_line, error_text, success_text,
                               prompt_text, continuation_prompt,
                               format_var_entry, BLUE, CYAN, GRAY,
                               GREEN, YELLOW, RED, BOLD, RESET)
from repl.completer import EnhancedCompleter, setup_readline
from runtime.enhanced_jit import JITExecutor, ExecutionResult
from lexer import Lexer
from parser import Parser, ParserError
from analyzer import SemanticAnalyzer, SemanticError

VERSION = "0.1.0"

HELP_TEXT = f"""\
{BOLD}=================================================={RESET}
{BOLD}{BLUE}ENHANCED {VERSION} -- QUICK REFERENCE{RESET}
{BOLD}=================================================={RESET}

{BOLD}PRINT{RESET}
  {BLUE}say{RESET} {GREEN}"Hello"{RESET}
  {BLUE}say{RESET} my_variable

{BOLD}VARIABLES{RESET}
  {GRAY}the{RESET} {CYAN}number{RESET} x {BLUE}is{RESET} {YELLOW}5{RESET}
  {GRAY}the{RESET} {CYAN}text{RESET} name {BLUE}is{RESET} {GREEN}"Alice"{RESET}

{BOLD}MATH{RESET}
  {BLUE}add{RESET} x {GRAY}and{RESET} y
  {BLUE}subtract{RESET} x {GRAY}from{RESET} y
  {BLUE}multiply{RESET} x {GRAY}and{RESET} y
  {BLUE}divide{RESET} x {GRAY}by{RESET} y

{BOLD}LISTS{RESET}
  {BLUE}create{RESET} {GRAY}a{RESET} {CYAN}list{RESET} {BLUE}called{RESET} team
  {BLUE}add{RESET} {GREEN}"Alice"{RESET} {GRAY}to{RESET} team
  {GRAY}for each{RESET} name {GRAY}in{RESET} team {BLUE}say{RESET} name
  {GRAY}the{RESET} {CYAN}size{RESET} {GRAY}of{RESET} team

{BOLD}FILES{RESET}
  {BLUE}open{RESET} {GRAY}the{RESET} {CYAN}file{RESET} {GREEN}"data.txt"{RESET} {GRAY}as{RESET} f
  {BLUE}read{RESET} {GRAY}from{RESET} f
  {BLUE}write{RESET} {GREEN}"hello"{RESET} {GRAY}to{RESET} f
  {BLUE}close{RESET} f

{BOLD}MEMORY{RESET}
  {BLUE}create{RESET} {GRAY}a new{RESET} {CYAN}person{RESET} {BLUE}called{RESET} alice
  {BLUE}free{RESET} alice
  {BLUE}check{RESET} {GRAY}if{RESET} alice {GRAY}is still valid{RESET}

{BOLD}REPL COMMANDS{RESET}
  help      show this reference
  vars      show all variables
  clear     reset session
  history   show last 20 inputs
  save "x"  save session to file
  load "x"  run a .en file
  exit      quit
{BOLD}=================================================={RESET}
"""


def run_repl():
    session = ReplSession()
    jit = JITExecutor()
    completer = EnhancedCompleter(session)
    setup_readline(completer)

    # Banner
    print(f"\n{BOLD}{BLUE}Enhanced {VERSION}{RESET}")
    print(f"Type English to code. Type {BOLD}'help'{RESET} for commands. Type {BOLD}'exit'{RESET} to quit.")
    print(f"{GRAY}{'─' * 50}{RESET}")
    print()

    while True:
        try:
            line = input(prompt_text())
        except (EOFError, KeyboardInterrupt):
            print(f"\n{GRAY}Goodbye!{RESET}")
            break

        stripped = line.strip()
        if not stripped:
            continue

        # --- Meta-commands ---
        lower = stripped.lower()

        if lower in ('exit', 'quit'):
            print(f"{GRAY}Goodbye!{RESET}")
            break

        if lower == 'help':
            print(HELP_TEXT)
            continue

        if lower == 'vars':
            all_vars = session.get_all_vars()
            if not all_vars:
                print(f"  {GRAY}(no variables defined){RESET}")
            else:
                for name, info in all_vars.items():
                    print(format_var_entry(name, info['type'], info['value']))
            continue

        if lower == 'clear':
            session.reset()
            print(f"  {GREEN}Session cleared.{RESET}")
            continue

        if lower == 'history':
            hist = session.get_history()
            if not hist:
                print(f"  {GRAY}(no history yet){RESET}")
            else:
                for i, h in enumerate(hist, 1):
                    print(f"  {GRAY}{i:3d}{RESET}  {highlight_line(h)}")
            continue

        if lower.startswith('save '):
            path = stripped[5:].strip().strip('"').strip("'")
            try:
                session.save(path)
                print(f"  {GREEN}Session saved to {path}{RESET}")
            except Exception as e:
                print(f"  {error_text('Error saving:')} {e}")
            continue

        if lower.startswith('load '):
            path = stripped[5:].strip().strip('"').strip("'")
            if not os.path.exists(path):
                print(f"  {error_text('File not found:')} {path}")
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                # Execute each line
                for file_line in source.strip().split('\n'):
                    file_line = file_line.strip()
                    if file_line:
                        _execute_line(file_line, session, jit)
                        session.record(file_line)
                print(f"  {GREEN}Loaded {path}{RESET}")
            except Exception as e:
                print(f"  {error_text('Error loading:')} {e}")
            continue

        # --- Execute Enhanced code ---
        _execute_line(stripped, session, jit)
        session.record(stripped)


def _execute_line(source, session, jit):
    """Parse and execute a single Enhanced line."""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        # Analyze
        analyzer = SemanticAnalyzer()
        # Inject existing session variables into the symbol table
        for name, info in session.get_all_vars().items():
            try:
                analyzer.symtab.define(name, info['type'], 0)
            except Exception:
                pass
        typed_ast = analyzer.analyze(ast)

        # Execute each statement via JIT
        for stmt in typed_ast.statements:
            result = jit.execute(stmt, session)
            if result.error:
                print(f"  {RED}\u2717{RESET} {error_text(result.error)}")
            elif result.output:
                print(result.output)

    except ParserError as e:
        print(f"  {RED}\u2717{RESET} {error_text(str(e))}")
    except SemanticError as e:
        print(f"  {RED}\u2717{RESET} {error_text(str(e))}")
    except Exception as e:
        print(f"  {RED}\u2717{RESET} {error_text(str(e))}")


def main():
    run_repl()


if __name__ == '__main__':
    main()
