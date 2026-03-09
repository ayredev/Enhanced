#ifndef MINIMAL_STDLIB_H
#define MINIMAL_STDLIB_H

#include <stddef.h>

void *malloc(size_t size);
void *calloc(size_t nmemb, size_t size);
void free(void *ptr);
void exit(int status);

#endif
