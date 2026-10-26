#include "pair.h"
int parse_pair(const uint8_t *input, size_t len, uint8_t *key, uint16_t *value) {
    if (input == NULL || key == NULL || value == NULL || len < 3 || input[1] != '=') return -1;
    uint32_t number = 0;
    for (size_t i = 2; i < len; ++i) {
        if (input[i] < '0' || input[i] > '9') return -1;
        number = number * 10 + (input[i] - '0');
        if (number > UINT16_MAX) return -2;
    }
    *key = input[0];
    *value = (uint16_t)number;
    return 0;
}
