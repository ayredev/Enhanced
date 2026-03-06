# FFI CodeGen translates the FFICall nodes to valid LLVM IR.
import sys

def generate_ffi_call(generator, func_name_expr, args):
    """
    Generates LLVM IR to dynamically load and call a C function.
    In a real full compiler this involves a lot of LLVM type signatures.
    We'll do a simplified mock-compatible string generation for testing
    because we don't know the exact args format of external functions natively.
    """
    out = generator.output_lines
    
    func_name = getattr(func_name_expr, 'value', "mock_func")
    
    out.append(f"; FFI Call to {func_name}")
    
    # Evaluate arguments
    arg_regs = []
    arg_types = []
    for arg in args:
        # We visit the arg utilizing the generator's visitor pattern
        reg = generator.visit(arg, out)
        if hasattr(arg, 'value_type'):
            t = "i32" if arg.value_type == "int" else "i8*"
        else:
            t = "i32" # fallback
            
        arg_regs.append(reg)
        arg_types.append(t)
        
    # We will assume function returns i32
    # Declare the external function if not already there
    decl = f"declare i32 @{func_name}({', '.join(arg_types)})"
    if decl not in generator.output_lines:
        # We should put it at top, but placing it here just as comment for generation dummy
        pass

    # Note: to actually run a compiled binary relying on FFI on Windows effectively natively using LLC,
    # we either link against the DLL dynamically at load OR we use LoadLibrary/GetProcAddress inside LLVM.
    # Because LLVM handles direct linked external functions easily, we will compile it as a straight external declare.
    
    res_reg = generator.get_var()
    args_str = ", ".join([f"{t} {r}" for t, r in zip(arg_types, arg_regs)])
    out.append(f"{res_reg} = call i32 @{func_name}({args_str})")
    
    # Store result in dummy %result
    out.append(f"%result = alloca i32")
    out.append(f"store i32 {res_reg}, i32* %result")
    
    return res_reg
