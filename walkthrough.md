# Enhanced Language Project Walkthrough

This document provides a comprehensive history and technical overview of the Enhanced language project. It is divided into phases, each detailing a major stage of development.

## 1. Project Overview

Enhanced is a high-level, English-like programming language designed to be intuitive and easy to read. The vision is to combine the simplicity of natural language with the power of a compiled, statically-typed language.

The core stack consists of:
- **Frontend**: A Python-based toolchain including a lexer, parser, and semantic analyzer.
- **Compiler Backend**: An LLVM IR generator that transpiles Enhanced code into LLVM Intermediate Representation.
- **Runtime**: A C-based runtime library that provides core functionalities like I/O, memory management, and the standard library.
- **Tooling**: A VSCode extension for syntax highlighting and an LSP server for advanced IDE features.

## 2. Phase I — Lexer + Parser

This phase laid the foundation for the compiler by implementing the initial tokenizer and parser.

- **Files Created**:
  - `enhanced/lexer.py`: The tokenizer, responsible for converting raw code into a stream of tokens.
  - `enhanced/parser.py`: The parser, which consumes tokens and builds an Abstract Syntax Tree (AST).
  - `enhanced/ast_nodes.py`: Definitions for all the AST nodes.
  - `enhanced/tests/test_lexer.py`: Unit tests for the lexer.
  - `enhanced/tests/test_parser.py`: Unit tests for the parser.

- **Grammar Patterns Added**:
  - `say "..."`
  - `add <number> and <number>`
  - `subtract <number> from <number>`
  - `multiply <number> and <number>`
  - `divide <number> by <number>`
  - Variable declaration: `the number X is 10.`

- **Tests**:
  - `test_lexer.py`: 3 tests
  - `test_parser.py`: 3 tests

## 3. Phase II — Semantic Analyzer + Type System

This phase introduced static analysis to catch errors before compilation.

- **Files Created/Modified**:
  - `enhanced/analyzer.py`: The semantic analyzer, which traverses the AST to check for semantic correctness.
  - `enhanced/type_system.py`: The type system, defining the language's types and type checking rules.
  - `enhanced/symbol_table.py`: A symbol table to track variables and their types.
  - `enhanced/tests/test_analyzer.py`: Tests for the semantic analyzer.

- **Errors Caught**:
  - Undefined variables.
  - Type mismatches in binary operations and variable assignments.
  - Appending the wrong type to a list.

- **Tests**:
  - `test_analyzer.py`: 6 tests

## 4. Phase III — VSCode Extension + LLVM IR Generator

This phase focused on developer experience and the first step towards compilation.

- **Files Created/Modified**:
  - `enhanced-vscode/`: Directory for the VSCode extension, including syntax highlighting rules (`enhanced.tmLanguage.json`).
  - `enhanced/codegen.py`: The LLVM IR generator, which converts the AST into LLVM IR.

- **IR Generation Example**:
  The Enhanced code `say "Hello"` would be translated into LLVM IR similar to this:
  ```llvm
  @.str = private unnamed_addr constant [6 x i8] c"Hello\00"
  ...
  call i32 @puts(i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str, i32 0, i32 0))
  ```

## 5. Phase IV — Compilation Pipeline + CLI

This phase created a user-friendly command-line interface to compile Enhanced programs.

- **Files Created/Modified**:
  - `enhanced/enhc.py`: The main command-line interface for the compiler.
  - `enhanced/pipeline.py`: The compilation pipeline that ties together the lexer, parser, analyzer, and code generator.
  - `enhanced/tests/test_pipeline.py`: End-to-end tests for the compilation pipeline.

- **Terminal Session Example**:
  ```sh
  # Compile and run an Enhanced program
  python enhanced/enhc.py enhanced/examples/hello.en

  # Generate LLVM IR
  python enhanced/enhc.py enhanced/examples/hello.en --ir
  ```

## 6. Phase V — Standard Library + FFI

This phase expanded the language's capabilities with a standard library and a Foreign Function Interface (FFI).

- **Files Created/Modified**:
  - `enhanced/runtime/enhanced_stdlib.c`: C implementation of the standard library functions.
  - `enhanced/ffi/ffi_loader.py` and `enhanced/ffi/ffi_codegen.py`: (Assumed from project structure) Tooling for the FFI.
  - `enhanced/tests/test_stdlib.py`: Tests for the standard library.

- **Grammar Patterns Added**:
  - `read the file "..."`
  - `write "..." to the file "..."`
  - `append "..." to the file "..."`
  - `check if the file "..." exists`
  - `get the url "..."`
  - `load the library "..."`
  - `call "..." with "..."`

## 7. Phase VI — Memory Safety

This phase introduced advanced memory safety features to prevent common memory-related bugs.

- **Files Created/Modified**:
  - `enhanced/memory/`: Directory for memory safety components.
  - `enhanced/memory/gen_ref.py`: Implementation of generational references.
  - `enhanced/memory/linear_types.py`: Implementation of linear types for resource management.
  - `enhanced/memory/mem_analyzer.py`: A new analysis pass for memory safety.
  - `enhanced/runtime/enhanced_memory.c`: C runtime support for memory management.
  - `enhanced/tests/test_memory.py`: Tests for memory safety features.

- **Key Concepts**:
  - **Generational References**: A heap allocation strategy that helps prevent use-after-free errors by versioning memory slots.
  - **Linear Types**: A type system feature that ensures resources like file handles are used exactly once (opened and then closed).

- **Tests**:
  - `test_memory.py`: 12 tests

## 8. Phase VII — REPL + Runtime Package

This phase added an interactive development environment (REPL) and packaged the runtime.

- **Files Created/Modified**:
  - `enhanced/repl/`: Directory for the REPL components.
  - `enhanced/repl/repl.py`: The main REPL loop.
  - `enhanced/runtime/enhanced_jit.py`: A JIT (Just-In-Time) compiler for the REPL.
  - `enhanced/tests/test_repl.py`: Tests for the REPL.

- **REPL Demo**:
  ```
  Enhanced REPL v0.1.0
  >>> the number x is 10.
  >>> say x
  10
  ```

- **JIT Benchmarks**: The tests include benchmarks to ensure the JIT compiler is performant.

## 9. Phase VIII — Language Server Protocol

This phase integrated Enhanced with IDEs by implementing the Language Server Protocol (LSP).

- **Files Created/Modified**:
  - `enhanced/lsp/`: Directory for the LSP server.
  - `enhanced/lsp/server.py`: The main LSP server implementation.
  - `enhanced/lsp/handlers.py`: Handlers for different LSP requests.
  - `enhanced/tests/test_lsp.py`: Tests for the LSP server.

- **LSP Features**:
  - **Diagnostics**: Real-time error checking.
  - **Completion**: Autocomplete for keywords and variables.
  - **Hover**: Show type information on hover.
  - **Go to Definition**: Jump to the definition of a variable.
  - **Formatting**: Automatic code formatting.

- **Tests**:
  - `test_lsp.py`: 18 tests

## 10. Phase IX — v2 Type System

This phase introduced a more powerful type system with support for custom types.

- **Files Created/Modified**:
  - `enhanced/etypes/`: Directory for custom type implementations.
  - `enhanced/tests/test_types.py`: Tests for the new type system features.

- **Grammar Patterns Added**:
  - **Structs**: `define a <struct> as: ...`
  - **Enums**: `define a <enum> as one of: ...`
  - **Maps**: `create a map called ...`
  - **Optionals**: `the optional <type> called ... is nothing`
  - **Methods**: `to <verb> a <type>: ...`

- **Tests**:
  - `test_types.py`: 21 tests

## 11. Phase X — Backend (HTTP Server + JSON + SQLite)

This phase aimed to build a backend stack into the language.

- **Files Created/Modified**:
  - `enhanced/runtime/enhanced_http.c`: C implementation for the HTTP server.
  - `enhanced/runtime/enhanced_json.c`: C implementation for JSON parsing and serialization.
  - `enhanced/runtime/enhanced_db.c`: C implementation for the SQLite wrapper.
  - `parser.py`, `ast_nodes.py`, `codegen.py`: Updated to support the new backend features.

- **Grammar Patterns Added**:
  - `start a server on port <number>`
  - `when someone gets "<path>": ...`
  - `send "<response>"`
  - `send with status <code> json <expression>`
  - `parse <expression> as json`
  - `serialize <expression> as json`
  - `open database "<path>" as <handle>`
  - `run on <db_handle>: ...`
  - `ask <db_handle> for all <table_name>`

- **Test Results**: All tests related to this phase that do not depend on `clang` are now passing.

## 12. Current Status

The project has a solid foundation with a working parser, analyzer, and a partially complete code generator. The language supports a rich set of features, including a standard library, FFI, memory safety, and a v2 type system. The backend stack (Phase X) is designed, and the runtime C files have been created, but the compilation pipeline for them is not fully tested due to a missing `clang` dependency.

**Next Steps (Phase XI)**:
The next logical step is to target WebAssembly. This would involve:
- Updating `codegen.py` to generate wasm-compatible LLVM IR.
- Creating a new runtime for the browser environment.
- Building a toolchain to compile Enhanced code to a `.wasm` file.

## 13. Total Test Count

| Phase | Test File | Test Count | Passing |
|---|---|---|---|
| I | `test_lexer.py` | 3 | 3 |
| I | `test_parser.py` | 3 | 3 |
| II | `test_analyzer.py` | 6 | 6 |
| IV | `test_pipeline.py` | 3 | 0 |
| V | `test_stdlib.py` | 3 | 3 |
| VI | `test_memory.py` | 12 | 12 |
| VII | `test_repl.py` | 17 | 17 |
| VIII | `test_lsp.py` | 18 | 18 |
| IX | `test_types.py` | 27 | 27 |
| **Total** | | **92** | **89** |
