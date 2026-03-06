import os
import subprocess
from lexer import Lexer
from parser import Parser, ParserError
from analyzer import SemanticAnalyzer, SemanticError
from codegen import IRGenerator
from memory.mem_analyzer import MemoryAnalyzer, MemoryAnalysisError

class PipelineError(Exception):
    pass

class Pipeline:
    def __init__(self, keep_ll=False):
        self.keep_ll = keep_ll

    def run(self, source_path):
        if not os.path.exists(source_path):
            raise PipelineError(f"I couldn't find the file '{source_path}'")
        
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # 1. Lexing
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # 2. Parsing
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 3. Type Checking & Semantic Analysis
            analyzer = SemanticAnalyzer()
            typed_ast = analyzer.analyze(ast)
            
            # 3.5. Memory Safety Analysis
            mem_analyzer = MemoryAnalyzer()
            typed_ast = mem_analyzer.analyze(typed_ast, analyzer.symtab)
            
            # 4. IR Generation
            generator = IRGenerator()
            ir_str = generator.generate(typed_ast)
            
            # 5. Native Compilation
            basename = os.path.splitext(os.path.basename(source_path))[0]
            dir_path = os.path.dirname(os.path.abspath(source_path))
            ll_path = os.path.join(dir_path, f"{basename}.ll")
            obj_path = os.path.join(dir_path, f"{basename}.o")
            exe_name = f"{basename}.exe" if os.name == 'nt' else basename
            exe_path = os.path.join(dir_path, exe_name)
            
            with open(ll_path, 'w', encoding='utf-8') as f:
                f.write(ir_str)
                
            # Compile LLVM IR to object via clang directly if llc is missing, or llc if preferred.
            try:
                # Use clang directly for .ll to .o which acts standard generally vs naked llc on windows
                subprocess.run(["clang", "-c", ll_path, "-o", obj_path], check=True, capture_output=True, text=True)
            except FileNotFoundError:
                 raise PipelineError("I couldn't find 'clang' installed on your system. Please install LLVM compiler infrastructure.")
            except subprocess.CalledProcessError as e:
                 raise PipelineError(f"There was a problem compiling the IR code into a native object:\\n{e.stderr}")
            
            # 6. Linking
            runtime_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime", "enhanced_runtime.o")
            stdlib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime", "enhanced_stdlib.o")
            memory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime", "enhanced_memory.o")
            for rp in [runtime_path, stdlib_path, memory_path]:
                if not os.path.exists(rp):
                    raise PipelineError(f"I couldn't find the compiled runtime at {rp}. Make sure 'make build' was run.")
                
            try:
                 subprocess.run(["clang", obj_path, runtime_path, stdlib_path, memory_path, "-o", exe_path], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                 raise PipelineError(f"There was a problem linking the final executable:\\n{e.stderr}")
            
            if not self.keep_ll:
                if os.path.exists(ll_path): os.remove(ll_path)
                if os.path.exists(obj_path): os.remove(obj_path)
                
            stats = {
                "tokens": len(tokens),
                "statements": len(ast.statements),
                "ll_path": ll_path,
                "obj_path": obj_path,
                "exe_path": exe_path
            }
            return exe_path, stats
            
        except (ParserError, SemanticError, MemoryAnalysisError) as e:
             raise PipelineError(str(e))
        except Exception as e:
             raise PipelineError(f"An unexpected error occurred: {str(e)}")
