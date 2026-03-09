import os
import subprocess
import shutil
from lexer import Lexer
from parser import Parser, ParserError
from analyzer import SemanticAnalyzer, SemanticError
from codegen import IRGenerator
from wasm_codegen import WasmGenerator
from wasm_compat import WasmCompatibilityChecker
from memory.mem_analyzer import MemoryAnalyzer, MemoryAnalysisError

class PipelineError(Exception):
    pass

class Pipeline:
    def __init__(self, keep_ll=False, target="native"):
        self.keep_ll = keep_ll
        self.target = target

    def run(self, source_path):
        if not os.path.exists(source_path):
            raise PipelineError(f"I couldn't find the file '{source_path}'")
        
        # 0. Manifest Check & Dependency Resolution
        project_root = os.path.dirname(os.path.abspath(source_path))
        manifest_path = os.path.join(project_root, "manifest.en")
        package_paths = {}
        
        if os.path.exists(manifest_path):
            print(f"→ Reading manifest.en...")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                m_source = f.read()
            m_lexer = Lexer(m_source)
            m_tokens = m_lexer.tokenize()
            m_parser = Parser(m_tokens)
            manifest_ast = m_parser.parse_manifest()
            
            # Resolve dependencies
            from dependency_resolver import DependencyResolver
            registry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Registry")
            resolver = DependencyResolver(registry_path)
            resolver.resolve(project_root, manifest_ast)
            
            enhanced_packages_dir = os.path.join(project_root, "enhanced_packages")
            for dep in manifest_ast.dependencies:
                pkg_name = dep.package_name
                pkg_path = os.path.join(enhanced_packages_dir, pkg_name)
                local_path = os.path.join(project_root, pkg_name)

                if os.path.exists(pkg_path):
                    package_paths[pkg_name] = pkg_path
                elif os.path.exists(local_path):
                    package_paths[pkg_name] = local_path

        # 4. Target Compilation
        try:
            basename = os.path.splitext(os.path.basename(source_path))[0]
            dir_path = os.path.dirname(os.path.abspath(source_path))
            ll_path = os.path.join(dir_path, f"{basename}.ll")
            
            # 4.1 Compile Main File IR
            try:
                with open(source_path, 'r', encoding='utf-8-sig') as f:
                    source = f.read()
            except UnicodeDecodeError:
                with open(source_path, 'r', encoding='utf-16') as f:
                    source = f.read()
            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()
            
            # Semantic Analysis
            analyzer = SemanticAnalyzer()
            self._load_package_symbols(analyzer, package_paths)
            analyzer.analyze(ast)
            
            # Memory Analysis
            mem_analyzer = MemoryAnalyzer()
            mem_analyzer.analyze(ast)
            
            # Code Generation
            if self.target == "web":
                compat_checker = WasmCompatibilityChecker()
                compat_checker.check(ast)
                ir = WasmGenerator().generate(ast)
            else:
                ir = IRGenerator().generate(ast)
                
            with open(ll_path, 'w', encoding='utf-8') as f:
                f.write(ir)

            # 4.2 Clang Discovery
            clang_cmd = "clang"
            if not shutil.which("clang") and os.name == 'nt':
                alt_path = r"C:\Program Files\LLVM\bin\clang.exe"
                if os.path.exists(alt_path): clang_cmd = alt_path

            # 4.3 Package Compilation
            package_objs = []
            for pkg_name, pkg_path in package_paths.items():
                for root, _, files in os.walk(pkg_path):
                    for file in files:
                        if file.endswith(".en") and file != 'manifest.en':
                            pkg_src = os.path.join(root, file)
                            p_base = os.path.splitext(file)[0]
                            p_ll = os.path.join(dir_path, f"pkg_{pkg_name}_{p_base}.ll")
                            p_obj = os.path.join(dir_path, f"pkg_{pkg_name}_{p_base}.o")
                            
                            try:
                                try:
                                    with open(pkg_src, 'r', encoding='utf-8-sig') as f:
                                        p_src = f.read()
                                except UnicodeDecodeError:
                                    with open(pkg_src, 'r', encoding='utf-16') as f:
                                        p_src = f.read()
                                p_toks = Lexer(p_src).tokenize()
                                p_ast = Parser(p_toks).parse()
                                
                                if self.target == "web":
                                    p_ir = WasmGenerator().generate(p_ast, emit_main=False)
                                    c_args = ["--target=wasm32", "-nostdlib", "-c"]
                                else:
                                    p_ir = IRGenerator().generate(p_ast, emit_main=False)
                                    c_args = ["-c"]
                                    
                                with open(p_ll, 'w', encoding='utf-8') as f: f.write(p_ir)
                                subprocess.run([clang_cmd] + c_args + [p_ll, "-o", p_obj], check=True, capture_output=True, text=True)
                                package_objs.append(p_obj)
                            except Exception as e:
                                print(f"[Warning] Failed to compile package file {pkg_src}: {e}")

            stats = {
                "tokens": len(tokens),
                "statements": len(ast.statements),
                "ll_path": ll_path,
                "package_files": len(package_objs)
            }

            if self.target == "web":
                # WASM Link
                wasm_path = os.path.join(dir_path, f"{basename}.wasm")
                html_path = os.path.join(dir_path, f"{basename}.html")
                runtime_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime")
                stdlib_wasm_c = os.path.join(runtime_dir, "enhanced_wasm_stdlib.c")
                
                cmd = [
                    clang_cmd, "--target=wasm32", "-nostdlib",
                    "-Wl,--no-entry", "-Wl,--export-all", "-Wl,--allow-undefined",
                    "-o", wasm_path, ll_path, stdlib_wasm_c
                ] + package_objs
                
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                self.generate_html_shell(html_path, f"{basename}.wasm", basename)
                
                stats.update({"obj_path": wasm_path, "exe_path": html_path})
                return html_path, stats

            else:
                # Native Link
                obj_path = os.path.join(dir_path, f"{basename}.o")
                exe_name = f"{basename}.exe" if os.name == 'nt' else basename
                exe_path = os.path.join(dir_path, exe_name)
                
                subprocess.run([clang_cmd, "-c", ll_path, "-o", obj_path], check=True, capture_output=True, text=True)
                
                runtime_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime")
                runtime_objs = [
                    os.path.join(runtime_dir, "enhanced_runtime.o"),
                    os.path.join(runtime_dir, "enhanced_stdlib.o"),
                    os.path.join(runtime_dir, "enhanced_memory.o")
                ]
                
                link_cmd = [clang_cmd, obj_path] + package_objs + runtime_objs + ["-o", exe_path]
                res = subprocess.run(link_cmd, capture_output=True, text=True)
                
                if res.returncode != 0 and os.name == 'nt' and ("libcmt.lib" in res.stderr or "msvcrt.lib" in res.stderr):
                    # Fallback for missing Windows SDK
                    fallback = link_cmd + ["-Wl,/nodefaultlib:libcmt", "-lmsvcrt"]
                    res = subprocess.run(fallback, capture_output=True, text=True)
                
                if res.returncode != 0:
                    raise PipelineError(f"Native Linking Error: {res.stderr}")
                
                if not self.keep_ll:
                    if os.path.exists(ll_path): os.remove(ll_path)
                    if os.path.exists(obj_path): os.remove(obj_path)
                    for p_obj in package_objs:
                        if os.path.exists(p_obj): os.remove(p_obj)
                        p_ll = p_obj.replace(".o", ".ll")
                        if os.path.exists(p_ll): os.remove(p_ll)

                stats.update({"obj_path": obj_path, "exe_path": exe_path})
                return exe_path, stats
            
        except (ParserError, SemanticError, MemoryAnalysisError) as e:
             raise PipelineError(str(e))
        except Exception as e:
             raise PipelineError(f"An unexpected error occurred: {str(e)}")

    def _load_package_symbols(self, analyzer, package_paths):
        """Loads symbols from all resolved packages and standard library."""
        # 1. Standard Library
        stdlib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stdlib")
        if os.path.exists(stdlib_path):
             self._scan_and_register("stdlib", stdlib_path, analyzer)

        # 2. External and Local Packages
        for pkg_name, pkg_path in package_paths.items():
             self._scan_and_register(pkg_name, pkg_path, analyzer)

    def _scan_and_register(self, pkg_name, pkg_path, analyzer):
        import re
        symbols = {}
        # Scan for .en files
        for root, _, files in os.walk(pkg_path):
            for file in files:
                if file.endswith(".en") and file != 'manifest.en':
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Find functions: "to [verb] [type] [name]..."
                            # Simple pattern for simulation
                            matches = re.findall(r'to (\w+) ', content)
                            for m in matches:
                                symbols[m] = {'type': 'int', 'kind': 'function'}
                            
                            # Find structs: "define a [struct] as:"
                            matches = re.findall(r'define a (\w+) as', content)
                            for m in matches:
                                symbols[m] = {'type': m, 'kind': 'struct'}
                    except Exception:
                        continue
        analyzer.register_package_symbols(pkg_name, symbols)

    def generate_html_shell(self, path, wasm_filename, title):
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced - {title}</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            background-color: #0f0f0f;
            color: #e0e0e0;
            font-family: 'IBM Plex Mono', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            width: 80%;
            max-width: 800px;
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }}
        h1 {{
            color: #00ff88;
            margin-top: 0;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }}
        #enhanced-output {{
            white-space: pre-wrap;
            background-color: #000;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #222;
            min-height: 200px;
            color: #00ff00;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 0.8em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Enhanced WASM: {title}</h1>
        <div id="enhanced-output"></div>
        <div class="footer">Built with Enhanced Compiler v0.1.0</div>
    </div>
    <script src="browser/enhanced_browser.js"></script>
    <script>
        window.addEventListener('load', () => {{
            EnhancedRuntime.loadAndRun('{wasm_filename}');
        }});
    </script>
</body>
</html>
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
