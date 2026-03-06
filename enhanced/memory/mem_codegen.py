"""
Memory-Safe IR Generation — extends codegen with heap safety primitives.

Emits LLVM IR that calls enhanced_alloc, enhanced_free, enhanced_deref,
and enhanced_is_valid from the C runtime.
"""


def emit_heap_alloc(out, var_name, type_size=8):
    """Emit IR for creating a new heap object via generational reference."""
    out.append(f"; HeapAlloc '{var_name}'")
    out.append(f"%{var_name}_ref = call {{i64, i64}} @enhanced_alloc(i64 {type_size})")
    out.append(f"%{var_name}_ref_ptr = alloca {{i64, i64}}")
    out.append(f"store {{i64, i64}} %{var_name}_ref, {{i64, i64}}* %{var_name}_ref_ptr")


def emit_heap_free(out, var_name):
    """Emit IR for freeing a heap object, incrementing its generation."""
    out.append(f"; HeapFree '{var_name}'")
    out.append(f"%{var_name}_ref_load = load {{i64, i64}}, {{i64, i64}}* %{var_name}_ref_ptr")
    out.append(f"call void @enhanced_free({{i64, i64}} %{var_name}_ref_load)")


def emit_heap_deref(out, var_name, dest_reg):
    """Emit IR for dereferencing a heap object with gen validation."""
    out.append(f"; HeapDeref '{var_name}' (gen-checked)")
    out.append(f"%{var_name}_ref_val = load {{i64, i64}}, {{i64, i64}}* %{var_name}_ref_ptr")
    out.append(f"{dest_reg} = call i8* @enhanced_deref({{i64, i64}} %{var_name}_ref_val)")


def emit_gen_check(out, var_name, dest_reg):
    """Emit IR for checking if a GenRef is still valid."""
    out.append(f"; GenRefCheck '{var_name}'")
    out.append(f"%{var_name}_ref_chk = load {{i64, i64}}, {{i64, i64}}* %{var_name}_ref_ptr")
    out.append(f"{dest_reg} = call i32 @enhanced_is_valid({{i64, i64}} %{var_name}_ref_chk)")


def emit_linear_open_file(out, path_arg, handle_name):
    """Emit IR for opening a file as a linear resource."""
    out.append(f"; LinearOpen file '{handle_name}'")
    out.append(f"%{handle_name}_ptr = call i8* @enhanced_open_file(i8* {path_arg})")
    out.append(f"%{handle_name} = alloca i8*")
    out.append(f"store i8* %{handle_name}_ptr, i8** %{handle_name}")


def emit_linear_close(out, handle_name):
    """Emit IR for closing a linear resource."""
    out.append(f"; LinearConsume '{handle_name}'")
    out.append(f"%{handle_name}_lv = load i8*, i8** %{handle_name}")
    out.append(f"call void @enhanced_close_file(i8* %{handle_name}_lv)")


def emit_linear_write(out, handle_name, data_arg):
    """Emit IR for writing to a linear file handle."""
    out.append(f"; LinearUse write '{handle_name}'")
    out.append(f"%{handle_name}_wh = load i8*, i8** %{handle_name}")
    out.append(f"call void @enhanced_write_handle(i8* %{handle_name}_wh, i8* {data_arg})")


def emit_linear_read(out, handle_name, dest_reg):
    """Emit IR for reading from a linear file handle."""
    out.append(f"; LinearUse read '{handle_name}'")
    out.append(f"%{handle_name}_rh = load i8*, i8** %{handle_name}")
    out.append(f"{dest_reg} = call i8* @enhanced_read_handle(i8* %{handle_name}_rh)")


# Declarations for the memory-safe runtime functions
MEMORY_DECLARATIONS = [
    "declare {i64, i64} @enhanced_alloc(i64)",
    "declare void @enhanced_free({i64, i64})",
    "declare i8* @enhanced_deref({i64, i64})",
    "declare i32 @enhanced_is_valid({i64, i64})",
    "declare i8* @enhanced_open_file(i8*)",
    "declare void @enhanced_close_file(i8*)",
    "declare void @enhanced_write_handle(i8*, i8*)",
    "declare i8* @enhanced_read_handle(i8*)",
]
