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