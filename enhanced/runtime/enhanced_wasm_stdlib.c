#include <stdint.h>

// UI Functions
extern int32_t enhanced_ui_create_element(const char* type);
extern void enhanced_ui_set_property(int32_t id, const char* prop, const char* value);
extern void enhanced_ui_add_to_screen(int32_t id);
extern void enhanced_ui_set_event_handler(int32_t id, const char* event, void (*handler)(void));

// Map Functions
extern const char* enhanced_map_get(const char* map_ptr, const char* key);
extern void enhanced_map_set(const char* map_ptr, const char* key, const char* value);

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
