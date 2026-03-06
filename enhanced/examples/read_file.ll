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
@str_hello = private unnamed_addr constant [34 x i8] c"Hello from Enhanced Lang Phase V!\00", align 1
@str_0 = private unnamed_addr constant [38 x i8] c"Wrote to file. Now reading it back...\00", align 1

define i32 @main() {
entry:
    %hello = alloca i8*
    store i8* getelementptr inbounds ([34 x i8], [34 x i8]* @str_hello, i32 0, i32 0), i8** %hello
    ; FileWrite
    call i32 @puts(i8* getelementptr inbounds ([38 x i8], [38 x i8]* @str_0, i32 0, i32 0))
    ; FileRead
    ; Print statement for string variable result
    call i32 @puts(i8* %result)
    ; FileExists
    %v2 = load i32, i32* %result
    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @fmt_int, i32 0, i32 0), i32 %v2)
    ret i32 0
}