#include "pair.h"
#include <assert.h>
int main(void) {
    uint8_t key = 42;
    uint16_t value = 43;
    const uint8_t raw[] = {0xff, '=', '9'};
    assert(parse_pair(raw, sizeof raw, &key, &value) == 0 && key == 0xff && value == 9);
    assert(parse_pair((const uint8_t *)"a=00", 4, &key, &value) == 0 && value == 0);
    assert(parse_pair((const uint8_t *)"a=65535", 7, &key, &value) == 0 && value == UINT16_MAX);
    assert(parse_pair(NULL, 3, &key, &value) == -1);
    assert(parse_pair((const uint8_t *)"a=", 2, &key, &value) == -1);
    assert(parse_pair((const uint8_t *)"a=1x", 4, &key, &value) == -1);
    assert(parse_pair((const uint8_t *)"a=65536", 7, &key, &value) == -2);
    assert(parse_pair((const uint8_t *)"a=655360x", 9, &key, &value) == -2);
    assert(key == 'a' && value == UINT16_MAX);
    return 0;
}
