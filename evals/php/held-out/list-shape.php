<?php

require $argv[1];

function same(string $expected, string $actual): void
{
    if ($expected !== $actual) {
        throw new RuntimeException('Unexpected JSON: ' . $actual);
    }
}

same('[]', enabledNamesJson([]));
same('[]', enabledNamesJson([['name' => 'x', 'enabled' => false]]));
same('["0","","0"]', enabledNamesJson([
    ['name' => 'skip', 'enabled' => false],
    ['name' => '0', 'enabled' => true],
    ['name' => '', 'enabled' => true],
    ['name' => '0', 'enabled' => true],
]));
same('["a","b"]', enabledNamesJson([
    5 => ['name' => 'a', 'enabled' => true],
    9 => ['name' => 'b', 'enabled' => true],
]));
try {
    enabledNamesJson([['name' => "\xff", 'enabled' => true]]);
} catch (JsonException $error) {
    echo "list-shape: passed\n";
    exit(0);
}
throw new RuntimeException('Invalid UTF-8 did not throw JsonException');
