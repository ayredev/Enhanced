from ast_nodes import *
from codegen import IRGenerator

class WasmGenerator(IRGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, ast):
        self.output_lines.append("; LLVM IR for Enhanced Language (WebAssembly Target)")
        self.output_lines.append("target datalayout = \"e-m:e-p:32:32-i64:64-n32:64-S128\"")
        self.output_lines.append("target triple = \"wasm32-unknown-unknown\"")
        self.output_lines.append("")
        
        # WASM-specific Imports
        self.output_lines.append("declare void @enhanced_print_str(i8*)")
        self.output_lines.append("declare void @enhanced_print_int(i32)")
        self.output_lines.append("declare void @enhanced_print_bool(i32)")
        
        # Memory Safety Declarations (WASM compatible)
        self.output_lines.append("declare {i64, i64} @enhanced_alloc(i64)")
        self.output_lines.append("declare void @enhanced_free({i64, i64})")
        self.output_lines.append("declare i8* @enhanced_deref({i64, i64})")
        self.output_lines.append("declare i32 @enhanced_is_valid({i64, i64})")

        main_body = []
        for stmt in ast.statements:
            self.visit(stmt, main_body)

        # Output strings
        for name, value in self.string_constants.items():
            val_len = len(value) + 1
            self.output_lines.append(f"@{name} = private unnamed_addr constant [{val_len} x i8] c\"{value}\\00\", align 1")
            
        self.output_lines.extend(self.global_lines)

        self.output_lines.append("\ndefine i32 @main() {")
        self.output_lines.append("entry:")
        self.output_lines.extend(["    " + line for line in main_body])
        self.output_lines.append("    ret i32 0")
        self.output_lines.append("}")
        return "\n".join(self.output_lines)

    def visit_PrintStatement(self, node, out):
        if hasattr(node.value, 'value_type') and node.value.value_type == 'str':
            if isinstance(node.value, LiteralString):
                str_id = f"str_{self.var_count}"
                self.var_count += 1
                self.string_constants[str_id] = node.value.value
                val_len = len(node.value.value) + 1
                out.append(f"call void @enhanced_print_str(i8* getelementptr inbounds ([{val_len} x i8], [{val_len} x i8]* @{str_id}, i32 0, i32 0))")
                return ""
            elif isinstance(node.value, Identifier):
                reg = self.get_var()
                out.append(f"{reg} = load i8*, i8** %{node.value.name}")
                out.append(f"call void @enhanced_print_str(i8* {reg})")
        elif hasattr(node.value, 'value_type') and node.value.value_type == 'bool':
             val = self.visit(node.value, out)
             out.append(f"call void @enhanced_print_bool(i32 {val})")
        else: # int
            if isinstance(node.value, LiteralNumber):
                out.append(f"call void @enhanced_print_int(i32 {node.value.value})")
            elif isinstance(node.value, Identifier):
                reg = self.get_var()
                out.append(f"{reg} = load i32, i32* %{node.value.name}")
                out.append(f"call void @enhanced_print_int(i32 {reg})")
            else:
                val = self.visit(node.value, out)
                out.append(f"call void @enhanced_print_int(i32 {val})")
        return ""
