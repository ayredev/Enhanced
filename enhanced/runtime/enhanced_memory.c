/*
 * Enhanced Memory Runtime — Generational Heap + Linear Resource Handles
 * Pure C99.  Never segfaults — every bad access produces a plain English
 * message and exits cleanly.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/* ---------------------------------------------------------------
   Layer 1 — Generational Heap
   --------------------------------------------------------------- */

#define ENHANCED_HEAP_SLOTS 131072 /* ~1 MB worth of slots */

typedef struct {
  void *data;
  uint64_t gen;
  size_t size;
  int is_free;
} HeapSlot;

typedef struct {
  uint64_t addr;
  uint64_t expected_gen;
} GenRef;

static HeapSlot g_heap[ENHANCED_HEAP_SLOTS];
static int g_heap_init = 0;

static void heap_init(void) {
  if (g_heap_init)
    return;
  for (int i = 0; i < ENHANCED_HEAP_SLOTS; i++) {
    g_heap[i].data = NULL;
    g_heap[i].gen = 0;
    g_heap[i].size = 0;
    g_heap[i].is_free = 1;
  }
  g_heap_init = 1;
}

GenRef enhanced_alloc(uint64_t size) {
  heap_init();
  GenRef ref;
  for (int i = 0; i < ENHANCED_HEAP_SLOTS; i++) {
    if (g_heap[i].is_free) {
      g_heap[i].data = calloc(1, (size_t)size);
      g_heap[i].size = (size_t)size;
      g_heap[i].is_free = 0;
      /* gen stays as-is (incremented on free) */
      ref.addr = (uint64_t)i;
      ref.expected_gen = g_heap[i].gen;
      return ref;
    }
  }
  fprintf(stderr, "I ran out of heap space.\n"
                  "Your program tried to allocate too many objects.\n");
  exit(1);
}

void enhanced_free(GenRef ref) {
  heap_init();
  uint64_t a = ref.addr;
  if (a >= ENHANCED_HEAP_SLOTS) {
    fprintf(
        stderr,
        "I found a problem: you tried to free something that doesn't exist.\n");
    exit(1);
  }
  HeapSlot *slot = &g_heap[a];
  if (slot->is_free || slot->gen != ref.expected_gen) {
    fprintf(stderr, "You tried to free something that was already freed.\n"
                    "Once you free something, you can't free it again.\n");
    exit(1);
  }
  free(slot->data);
  slot->data = NULL;
  slot->gen += 1;
  slot->is_free = 1;
}

void *enhanced_deref(GenRef ref) {
  heap_init();
  uint64_t a = ref.addr;
  if (a >= ENHANCED_HEAP_SLOTS) {
    fprintf(
        stderr,
        "I found a problem: you tried to read from an invalid reference.\n");
    exit(1);
  }
  HeapSlot *slot = &g_heap[a];
  if (slot->is_free || slot->gen != ref.expected_gen) {
    fprintf(stderr, "You tried to use something after it was already freed.\n"
                    "Once you free something, you can't use it anymore.\n");
    exit(1);
  }
  return slot->data;
}

int enhanced_is_valid(GenRef ref) {
  heap_init();
  uint64_t a = ref.addr;
  if (a >= ENHANCED_HEAP_SLOTS)
    return 0;
  HeapSlot *slot = &g_heap[a];
  return (!slot->is_free && slot->gen == ref.expected_gen) ? 1 : 0;
}

/* ---------------------------------------------------------------
   Layer 2 — Linear Resource Handles (file I/O wrappers)
   --------------------------------------------------------------- */

void *enhanced_open_file(const char *path) {
  if (!path) {
    fprintf(stderr, "You tried to open a file but didn't provide a name.\n");
    exit(1);
  }
  FILE *f = fopen(path, "w+");
  if (!f) {
    fprintf(stderr,
            "I couldn't open the file '%s'. Check that the path is correct "
            "and you have permission to access it.\n",
            path);
    exit(1);
  }
  return (void *)f;
}

void enhanced_close_file(void *handle) {
  if (!handle) {
    fprintf(stderr, "You tried to close a file that was never opened.\n");
    exit(1);
  }
  fclose((FILE *)handle);
}

void enhanced_write_handle(void *handle, const char *data) {
  if (!handle) {
    fprintf(stderr, "You tried to write to a file that was never opened.\n");
    exit(1);
  }
  fprintf((FILE *)handle, "%s", data);
  fflush((FILE *)handle);
}

void *enhanced_read_handle(void *handle) {
  if (!handle) {
    fprintf(stderr, "You tried to read from a file that was never opened.\n");
    exit(1);
  }
  FILE *f = (FILE *)handle;
  fseek(f, 0, SEEK_END);
  long len = ftell(f);
  fseek(f, 0, SEEK_SET);
  if (len <= 0) {
    char *empty = (char *)calloc(1, 1);
    return (void *)empty;
  }
  char *buf = (char *)calloc(1, (size_t)len + 1);
  fread(buf, 1, (size_t)len, f);
  return (void *)buf;
}
