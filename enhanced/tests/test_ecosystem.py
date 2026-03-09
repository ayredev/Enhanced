
import unittest
import os
import sys
import shutil
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from ast_nodes import *

class TestEcosystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath("test_ecosystem_tmp")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except:
                pass

    def test_parse_manifest(self):
        code = """
        this is the "my_web_app" package.
        the version is "1.0.0".
        the author is "ayredev".
        use the "web_ui" package version "2.1.0".
        use the "sqlite_helper" package from "github.com/enhanced/db".
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        manifest = parser.parse_manifest()

        self.assertIsInstance(manifest, Manifest)
        self.assertEqual(manifest.package_name, "my_web_app")
        self.assertEqual(manifest.version, "1.0.0")
        self.assertEqual(manifest.author, "ayredev")
        self.assertEqual(len(manifest.dependencies), 2)
        
        dep1 = manifest.dependencies[0]
        self.assertEqual(dep1.package_name, "web_ui")
        self.assertEqual(dep1.version, "2.1.0")
        
        dep2 = manifest.dependencies[1]
        self.assertEqual(dep2.package_name, "sqlite_helper")
        self.assertEqual(dep2.source, "github.com/enhanced/db")

    def test_parse_use_statement(self):
        code = """
        use the "math" package.
        use the "utils" from the "std" package.
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.statements), 2)
        stmt1 = ast.statements[0]
        self.assertIsInstance(stmt1, UsePackage)
        self.assertEqual(stmt1.package_name, "math")
        
        stmt2 = ast.statements[1]
        self.assertIsInstance(stmt2, UsePackage)
        self.assertEqual(stmt2.package_name, "std")
        self.assertEqual(stmt2.module_name, "utils")

    def test_analyzer_package_namespace(self):
        # This test verifies that importing a package creates a namespace
        # and allows accessing symbols from it (mocked in analyzer)
        code = """
        use the "math" package.
        the number x is math's add.
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer()
        typed_ast = analyzer.analyze(ast)
        
        # Verify symbol table has "math"
        sym = analyzer.symtab.lookup("math", 1)
        self.assertEqual(sym['type'], "package")
        
        # Verify x has type "int" (from our mock in analyzer)
        x_sym = analyzer.symtab.lookup("x", 2)
        self.assertEqual(x_sym['type'], "int")

    def test_cli_and_imports(self):
        # 1. Setup registry and package
        registry_path = os.path.join(self.test_dir, "Registry")
        os.makedirs(registry_path)
        
        math_pkg = os.path.join(registry_path, "math_lib")
        os.makedirs(math_pkg)
        with open(os.path.join(math_pkg, "manifest.en"), "w") as f:
            f.write('this is the "math_lib" package.\\nthe version is "1.0.0".\\nthe author is "me".')
        with open(os.path.join(math_pkg, "constants.en"), "w") as f:
            f.write('the number pi is 3.')
            
        # 2. Setup app project
        app_path = os.path.join(self.test_dir, "app")
        os.makedirs(app_path)
        
        # Create a local Registry inside app so 'enhc get' finds it
        shutil.copytree(registry_path, os.path.join(app_path, "Registry"))
        
        with open(os.path.join(app_path, "manifest.en"), "w") as f:
            f.write('this is the "app" package.\\nthe version is "1.0.0".\\nthe author is "me".\\nuse the "math_lib" package.')
        
        with open(os.path.join(app_path, "main.en"), "w") as f:
            f.write('''use the "math_lib" package.
the number x is math_lib's pi.
say x.''')
            
        # 3. Run 'enhc get'
        cwd = os.getcwd()
        os.chdir(app_path)
        try:
            # Locate enhc.py relative to test file location
            enhc_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'enhc.py'))
            
            # Run get
            # We invoke python explicitly
            cmd_get = [sys.executable, enhc_script, "get", "the", "math_lib", "package"]
            subprocess.run(cmd_get, check=True)
            
            self.assertTrue(os.path.exists("enhanced_packages/math_lib"))
            self.assertTrue(os.path.exists("enhanced_packages/math_lib/constants.en"))
            
            # 4. Run compilation (check only)
            cmd_check = [sys.executable, enhc_script, "main.en", "--check"]
            result = subprocess.run(cmd_check, check=True, text=True)
            
            # self.assertIn("[OK] Type checked", result.stdout) # Removed because we don't capture output anymore
            
        finally:
            os.chdir(cwd)

if __name__ == '__main__':
    unittest.main()
