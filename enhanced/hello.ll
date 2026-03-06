; LLVM IR for Enhanced Language

declare i32 @printf(i8*, ...)
declare i32 @puts(i8*)
@str_1 = private unnamed_addr constant [13 x i8] c"Hello, World\00", align 1

define i32 @main() {
entry:
    call i32 @puts(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @str_1, i32 0, i32 0))
    ret i32 0
}
