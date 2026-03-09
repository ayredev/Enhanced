; LLVM IR for Enhanced Language (WebAssembly Target)
target datalayout = "e-m:e-p:32:32-i64:64-n32:64-S128"
target triple = "wasm32-unknown-unknown"

declare void @enhanced_print_str(i8*)
declare void @enhanced_print_int(i32)
declare void @enhanced_print_bool(i32)
declare i32 @enhanced_ui_create_element(i8*)
declare void @enhanced_ui_set_property(i32, i8*, i8*)
declare void @enhanced_ui_add_to_screen(i32)
declare void @enhanced_ui_set_event_handler(i32, i8*, void()*)
declare {i64, i64} @enhanced_alloc(i64)
declare void @enhanced_free({i64, i64})
declare i8* @enhanced_deref({i64, i64})
declare i32 @enhanced_is_valid({i64, i64})
@str_0 = private unnamed_addr constant [12 x i8] c"Answer is: \00", align 1

define i32 @main() {
entry:
    ; UsePackage math_lib
    %x = alloca i32
    ; Assigning expression to int
    call void @enhanced_print_str(i8* getelementptr inbounds ([12 x i8], [12 x i8]* @str_0, i32 0, i32 0))
    %v2 = load i32, i32* %x
    ret i32 0
}