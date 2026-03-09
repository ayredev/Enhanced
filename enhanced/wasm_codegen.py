from ast_nodes import *
from codegen import IRGenerator

class WasmGenerator(IRGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, ast, emit_main=True):
        self.output_lines.append("; LLVM IR for Enhanced Language (WebAssembly Target)")
        self.output_lines.append("target datalayout = \"e-m:e-p:32:32-i64:64-n32:64-S128\"")
        self.output_lines.append("target triple = \"wasm32-unknown-unknown\"")
        self.output_lines.append("")
        
        # WASM-specific Imports
        self.output_lines.append("declare void @enhanced_print_str(i8*)")
        self.output_lines.append("declare void @enhanced_print_int(i32)")
        self.output_lines.append("declare void @enhanced_print_bool(i32)")
        
        # UI Imports
        self.output_lines.append("declare i32 @enhanced_ui_create_element(i8*)")
        self.output_lines.append("declare void @enhanced_ui_set_property(i32, i8*, i8*)")
        self.output_lines.append("declare void @enhanced_ui_add_to_screen(i32)")
        self.output_lines.append("declare void @enhanced_ui_set_event_handler(i32, i8*, void()*)")

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

        if emit_main:
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

    def visit_UICreateElement(self, node, out):
        type_str = node.element_type
        str_id = f"str_{self.var_count}"
        self.var_count += 1
        self.string_constants[str_id] = type_str
        val_len = len(type_str) + 1
        
        reg = self.get_var()
        out.append(f"{reg} = call i32 @enhanced_ui_create_element(i8* getelementptr inbounds ([{val_len} x i8], [{val_len} x i8]* @{str_id}, i32 0, i32 0))")
        out.append(f"%{node.name} = alloca i32")
        out.append(f"store i32 {reg}, i32* %{node.name}")
        return reg

    def visit_UISetProperty(self, node, out):
        elem_reg = self.get_var()
        out.append(f"{elem_reg} = load i32, i32* %{node.element_name}")
        
        prop_str = node.property_name
        prop_id = f"str_{self.var_count}"
        self.var_count += 1
        self.string_constants[prop_id] = prop_str
        prop_len = len(prop_str) + 1
        
        val_arg = self._eval_arg(node.value, out, 'i8*')
        
        out.append(f"call void @enhanced_ui_set_property(i32 {elem_reg}, i8* getelementptr inbounds ([{prop_len} x i8], [{prop_len} x i8]* @{prop_id}, i32 0, i32 0), i8* {val_arg})")

    def visit_UIAddToScreen(self, node, out):
        elem_reg = self.get_var()
        out.append(f"{elem_reg} = load i32, i32* %{node.element_name}")
        out.append(f"call void @enhanced_ui_add_to_screen(i32 {elem_reg})")

    def visit_UIEventHandler(self, node, out):
        handler_name = f"handler_{node.element_name}_{node.event_type}_{self.block_count}"
        self.block_count += 1
        
        # Define handler function
        handler_lines = [f"define void @{handler_name}() {{", "entry:"]
        for stmt in node.body:
            self.visit(stmt, handler_lines)
        handler_lines.append("    ret void")
        handler_lines.append("}")
        self.global_lines.extend(handler_lines)
        
        # Register handler
        elem_reg = self.get_var()
        out.append(f"{elem_reg} = load i32, i32* %{node.element_name}")
        
        event_str = node.event_type
        event_id = f"str_{self.var_count}"
        self.var_count += 1
        self.string_constants[event_id] = event_str
        event_len = len(event_str) + 1
        
        out.append(f"call void @enhanced_ui_set_event_handler(i32 {elem_reg}, i8* getelementptr inbounds ([{event_len} x i8], [{event_len} x i8]* @{event_id}, i32 0, i32 0), void()* @{handler_name})")

    def visit_MapGet(self, node, out):
        out.append(f"; MapGet {node.map_name}")
        key_arg = self._eval_arg(node.key, out, 'i8*')
        map_reg = self.get_var()
        out.append(f"{map_reg} = load i8*, i8** %{node.map_name}")
        res_reg = self.get_var()
        out.append(f"{res_reg} = call i8* @enhanced_map_get(i8* {map_reg}, i8* {key_arg})")
        return res_reg

    def visit_MapSet(self, node, out):
        out.append(f"; MapSet {node.map_name}")
        key_arg = self._eval_arg(node.key, out, 'i8*')
        val_arg = self._eval_arg(node.value, out, 'i8*')
        map_reg = self.get_var()
        out.append(f"{map_reg} = load i8*, i8** %{node.map_name}")
        out.append(f"call void @enhanced_map_set(i8* {map_reg}, i8* {key_arg}, i8* {val_arg})")
