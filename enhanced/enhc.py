#!/usr/bin/env python3
import argparse
import sys
import os
import json

from lexer import Lexer
from parser import Parser
from printer import ast_to_json
from analyzer import SemanticAnalyzer
from codegen import IRGenerator
from pipeline import Pipeline, PipelineError
from memory.mem_analyzer import MemoryAnalyzer, MemoryAnalysisError

VERSION = "0.1.0"

def main():
    parser = argparse.ArgumentParser(description="Enhanced Language Compiler", add_help=False)
    parser.add_argument("file", nargs="?", help="The .en file to compile")
    parser.add_argument("--run", action="store_true", help="Compile and run immediately")
    parser.add_argument("--ir", action="store_true", help="Stop after IR generation and show .ll")
    parser.add_argument("--ast", action="store_true", help="Stop after parsing and show AST JSON")
    parser.add_argument("--check", action="store_true", help="Run semantic analysis only")
    parser.add_argument("--lsp", action="store_true", help="Start the Language Server (LSP)")
    parser.add_argument("--version", action="store_true", help="Print compiler version")
    parser.add_argument("--help", action="store_true", help="Print this help message")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Enhanced {VERSION}")
        sys.exit(0)

    if args.lsp:
        from lsp.server import LSPServer
        LSPServer().run()
        sys.exit(0)
        
    if args.help or not args.file:
        print(f"Enhanced Compiler {VERSION}")
        print("Usage:")
        print("  enhc <file.en>              -> compile and produce executable")
        print("  enhc <file.en> --run        -> compile and immediately run it")
        print("  enhc <file.en> --ir         -> stop after IR generation, show the .ll file")
        print("  enhc <file.en> --ast        -> stop after parsing, show the AST JSON")
        print("  enhc <file.en> --check      -> run semantic analysis only, report errors")
        print("  enhc --lsp                  -> start the Language Server")
        print("  enhc --version              -> print version")
        print("  enhc --help                 -> print this message")
        sys.exit(0)

    source_path = args.file
    if not os.path.exists(source_path):
        print(f"[Error] I couldn't find the file '{source_path}'")
        sys.exit(1)
        
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        ast_parser = Parser(tokens)
        ast = ast_parser.parse()
        
        if args.ast:
            print(ast_to_json(ast))
            sys.exit(0)
            
        analyzer = SemanticAnalyzer()
        typed_ast = analyzer.analyze(ast)
        
        if args.check:
            print("[OK] Type checked -- no errors")
            sys.exit(0)

        # Memory Safety Analysis
        mem_analyzer = MemoryAnalyzer()
        typed_ast = mem_analyzer.analyze(typed_ast, analyzer.symtab)
            
        generator = IRGenerator()
        ir_str = generator.generate(typed_ast)
        
        if args.ir:
            print(ir_str)
            sys.exit(0)
            
        pipe = Pipeline(keep_ll=True)
        exe_path, stats = pipe.run(source_path)
        
        print(f"[OK] Lexed {stats['tokens']} tokens")
        print(f"[OK] Parsed {stats['statements']} statements")
        print(f"[OK] Type checked — no errors")
        ll_name = os.path.basename(stats['ll_path'])
        obj_name = os.path.basename(stats['obj_path'])
        exe_name = os.path.basename(stats['exe_path'])
        print(f"[OK] Generated LLVM IR ({ll_name})")
        print(f"[OK] Compiled to object ({obj_name})")
        print(f"[OK] Linked executable ({exe_name})")
        
        if args.run:
            print(f"→ Running {exe_name}...")
            os.system(exe_path)
        else:
            print(f"→ Run it with: {exe_path}")
            
    except (PipelineError, MemoryAnalysisError) as e:
        print(f"[Error] {str(e)}")
        sys.exit(1)
    except Exception as e:
         print(f"[Error] {str(e)}")
         sys.exit(1)

if __name__ == "__main__":
    main()
