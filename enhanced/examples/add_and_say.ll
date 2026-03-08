; LLVM IR for Enhanced Language

declare i32 @printf(i8*, ...)
declare i32 @puts(i8*)
declare i8* @enhanced_read_file(i8*)
declare void @enhanced_write_file(i8*, i8*)
declare void @enhanced_append_file(i8*, i8*)
declare i32 @enhanced_file_exists(i8*)
declare i32 @enhanced_list_size(i8*)
declare i32 @enhanced_pow(i32, i32)
declare void @enhanced_sleep(i32)
declare i32 @enhanced_timestamp()
declare i8* @enhanced_http_get(i8*)
declare {i64, i64} @enhanced_alloc(i64)
declare void @enhanced_free({i64, i64})
declare i8* @enhanced_deref({i64, i64})
declare i32 @enhanced_is_valid({i64, i64})
declare i8* @enhanced_open_file(i8*)
declare void @enhanced_close_file(i8*)
declare void @enhanced_write_handle(i8*, i8*)
declare i8* @enhanced_read_handle(i8*)
declare void @enhanced_server_start(i32)
declare void @enhanced_server_stop()
declare void @enhanced_server_route(i8*, i8*, void()*)
declare void @enhanced_send_response(i32, i8*)
declare i8* @enhanced_get_request_body()
declare i8* @enhanced_get_url_param(i8*)
declare i8* @enhanced_json_parse(i8*)
declare i8* @enhanced_json_serialize(i8*)
declare i8* @enhanced_db_open(i8*)
declare void @enhanced_db_close(i8*)
declare void @enhanced_db_exec(i8*, i8*)
declare i8* @enhanced_db_query(i8*, i8*, i8*)
declare void @enhanced_add_middleware(i8*, void()*)
declare void @enhanced_stop_middleware()
declare i8* @enhanced_get_query_param(i8*)
declare i8* @enhanced_get_request_header(i8*)
declare i8* @enhanced_get_env(i8*)

define i32 @main() {
entry:
    %x = alloca i32
    store i32 5, i32* %x
    %y = alloca i32
    store i32 10, i32* %y
    %v3 = load i32, i32* %x
    %v4 = load i32, i32* %y
    %v1 = load i32, i32* %x
    %v2 = load i32, i32* %y
    %v5 = add i32 %v1, %v2
    %result = alloca i32
    store i32 %v5, i32* %result
    %v6 = load i32, i32* %result
    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @fmt_int, i32 0, i32 0), i32 %v6)
    ret i32 0
}