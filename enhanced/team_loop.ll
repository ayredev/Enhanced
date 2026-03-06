; LLVM IR for Enhanced Language

declare i32 @printf(i8*, ...)
declare i32 @puts(i8*)
@str_Alice = private unnamed_addr constant [6 x i8] c"Alice\00", align 1
@str_Bob = private unnamed_addr constant [4 x i8] c"Bob\00", align 1

define i32 @main() {
entry:
    ; Declaring list team
    ; Appending to list team
    ; Appending to list team
    ; ForLoop start
    br label %loop_entry
loop_entry:
    ; ... loop condition dummy ...
    br i1 1, label %loop_body, label %loop_exit
loop_body:
    ; Print statement for string variable name
    call i32 @puts(i8* %name)
    br label %loop_entry
loop_exit:
    ret i32 0
}
