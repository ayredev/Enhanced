#include <stdio.h>
#include <string.h>

void enhanced_say_str(char* s) {
    puts(s);
}

void enhanced_say_int(int n) {
    printf("%d\n", n);
}

void enhanced_say_bool(int b) {
    printf("%s\n", b ? "true" : "false");
}

int enhanced_add(int a, int b) {
    return a + b;
}

int enhanced_subtract(int a, int b) {
    return a - b;
}
