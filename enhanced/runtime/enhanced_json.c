#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Basic JSON value types
typedef enum {
    JSON_NULL,
    JSON_BOOL,
    JSON_NUMBER,
    JSON_STRING,
    JSON_ARRAY,
    JSON_OBJECT
} JsonType;

// Forward declare for self-reference
struct JsonValue;

// Key-value pair for objects
typedef struct {
    char* key;
    struct JsonValue* value;
} JsonPair;

// The main JSON value structure
typedef struct JsonValue {
    JsonType type;
    union {
        int bool_val;
        double num_val;
        char* str_val;
        struct {
            struct JsonValue** elements;
            int count;
        } arr_val;
        struct {
            JsonPair* members;
            int count;
        } obj_val;
    } as;
} JsonValue;

// Mock parser: For simplicity, this will be a very basic parser
// that only handles a flat object with string values.
JsonValue* enhanced_json_parse(char* text) {
    // This is a placeholder for a real parser.
    // It will just create a dummy object.
    JsonValue* val = (JsonValue*)malloc(sizeof(JsonValue));
    val->type = JSON_OBJECT;
    val->as.obj_val.count = 1;
    val->as.obj_val.members = (JsonPair*)malloc(sizeof(JsonPair));
    
    val->as.obj_val.members[0].key = strdup("mock_key");
    
    JsonValue* inner_val = (JsonValue*)malloc(sizeof(JsonValue));
    inner_val->type = JSON_STRING;
    inner_val->as.str_val = strdup("mock_value");
    
    val->as.obj_val.members[0].value = inner_val;
    
    return val;
}

// Mock serializer
char* enhanced_json_serialize(JsonValue* val) {
    if (!val) {
        return strdup("null");
    }
    // This is a placeholder for a real serializer.
    switch (val->type) {
        case JSON_OBJECT:
            // very simple case for one key-value pair
            if (val->as.obj_val.count > 0) {
                char buffer[256];
                JsonPair pair = val->as.obj_val.members[0];
                char* inner_val_str = enhanced_json_serialize(pair.value);
                sprintf(buffer, "{\""%s\"": %s}", pair.key, inner_val_str);
                free(inner_val_str);
                return strdup(buffer);
            }
            return strdup("{}");
        case JSON_STRING:
            {
                char buffer[256];
                sprintf(buffer, "\"%s\"", val->as.str_val);
                return strdup(buffer);
            }
        case JSON_NUMBER:
             {
                char buffer[256];
                sprintf(buffer, "%f", val->as.num_val);
                return strdup(buffer);
            }
        case JSON_BOOL:
            return strdup(val->as.bool_val ? "true" : "false");
        default:
            return strdup("null");
    }
}
