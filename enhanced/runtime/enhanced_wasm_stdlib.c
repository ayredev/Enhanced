#include <stdint.h>

// WebAssembly Imports from JS
extern void enhanced_print_str(const char* s);
extern void enhanced_print_int(int32_t n);
extern void enhanced_print_bool(int32_t b);

// Standard Library functions for WASM target
void say_str(const char* s) {
    enhanced_print_str(s);
}

void say_int(int32_t n) {
    enhanced_print_int(n);
}

void say_bool(int32_t b) {
    enhanced_print_bool(b);
}

// Memory safety stubs for WASM
typedef struct {
    uint64_t low;
    uint64_t high;
} gen_ref_t;

gen_ref_t enhanced_alloc(uint64_t size) {
    gen_ref_t ref = {0, 0};
    return ref;
}

void enhanced_free(gen_ref_t ref) {}

void* enhanced_deref(gen_ref_t ref) {
    return (void*)0;
}

int32_t enhanced_is_valid(gen_ref_t ref) {
    return 1;
}
