#include <stdio.h>
#include <string.h>

void enhanced_say_str(char *s) { puts(s); }

void enhanced_say_int(int n) { printf("%d\n", n); }

void enhanced_say_bool(int b) { printf("%s\n", b ? "true" : "false"); }

int enhanced_add(int a, int b) { return a + b; }

int enhanced_subtract(int a, int b) { return a - b; }

// v2 Hashtable map implementation
#include <stdlib.h>
typedef struct KV {
  char *key;
  void *value;
  struct KV *next;
} KV;

typedef struct {
  KV **buckets;
  int capacity;
  int size;
} EnhancedMap;

static int hash_str(char *str, int capacity) {
  unsigned long hash = 5381;
  int c;
  while ((c = *str++))
    hash = ((hash << 5) + hash) + c;
  return hash % capacity;
}

EnhancedMap *enhanced_map_create() {
  EnhancedMap *m = (EnhancedMap *)malloc(sizeof(EnhancedMap));
  m->capacity = 16;
  m->size = 0;
  m->buckets = (KV **)calloc(m->capacity, sizeof(KV *));
  return m;
}

void enhanced_map_set(EnhancedMap *m, char *key, void *value) {
  int idx = hash_str(key, m->capacity);
  KV *curr = m->buckets[idx];
  while (curr) {
    if (strcmp(curr->key, key) == 0) {
      curr->value = value;
      return;
    }
    curr = curr->next;
  }
  KV *new_kv = (KV *)malloc(sizeof(KV));
  new_kv->key = strdup(key);
  new_kv->value = value;
  new_kv->next = m->buckets[idx];
  m->buckets[idx] = new_kv;
  m->size++;
}

void *enhanced_map_get(EnhancedMap *m, char *key) {
  int idx = hash_str(key, m->capacity);
  KV *curr = m->buckets[idx];
  while (curr) {
    if (strcmp(curr->key, key) == 0)
      return curr->value;
    curr = curr->next;
  }
  return NULL;
}

int enhanced_map_contains(EnhancedMap *m, char *key) {
  return enhanced_map_get(m, key) != NULL;
}

int enhanced_map_size(EnhancedMap *m) { return m->size; }

// v2 Optionals
typedef struct {
  int has_value;
  void *value;
} EnhancedOptional;

EnhancedOptional *enhanced_optional_create() {
  EnhancedOptional *opt = (EnhancedOptional *)malloc(sizeof(EnhancedOptional));
  opt->has_value = 0;
  opt->value = NULL;
  return opt;
}
