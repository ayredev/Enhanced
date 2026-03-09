#ifndef MINIMAL_STRING_H
#define MINIMAL_STRING_H

#include <stddef.h>

size_t strlen(const char *s);
int strcmp(const char *s1, const char *s2);
char *strdup(const char *s);
void *memcpy(void *dest, const void *src, size_t n);

#endif
