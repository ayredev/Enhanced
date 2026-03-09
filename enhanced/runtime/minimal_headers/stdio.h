#ifndef MINIMAL_STDIO_H
#define MINIMAL_STDIO_H

#include <stddef.h>

typedef struct _iobuf {
  void *_Placeholder;
} FILE;

extern FILE *stderr;

int printf(const char *format, ...);
int puts(const char *s);
int sprintf(char *str, const char *format, ...);
int fprintf(FILE *stream, const char *format, ...);
int fseek(FILE *stream, long offset, int whence);
long ftell(FILE *stream);
size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream);
FILE *fopen(const char *filename, const char *mode);
int fclose(FILE *stream);
int fflush(FILE *stream);

#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2

#endif
