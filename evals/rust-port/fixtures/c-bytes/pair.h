#ifndef PAIR_H
#define PAIR_H
#include <stddef.h>
#include <stdint.h>
/* 0: success, -1: invalid format, -2: overflow. Outputs unchanged on error.
 * A key is any byte. Input is a byte sequence, not a NUL-terminated string. */
int parse_pair(const uint8_t *input, size_t len, uint8_t *key, uint16_t *value);
#endif
