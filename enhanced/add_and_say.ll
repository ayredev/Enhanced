; LLVM IR for Enhanced Language

declare i32 @printf(i8*, ...)
declare i32 @puts(i8*)
@fmt_int = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1

define i32 @main() {
entry:
    %x = alloca i32
    store i32 5, i32* %x
    %y = alloca i32
    store i32 10, i32* %y
    %v1 = load i32, i32* %x
    %v2 = load i32, i32* %y
    %v3 = add i32 %v1, %v2
    %result = alloca i32
    store i32 %v3, i32* %result
    %v4 = load i32, i32* %result
    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @fmt_int, i32 0, i32 0), i32 %v4)
    ret i32 0
}
