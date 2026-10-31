<?php

require $argv[1];

function same($expected, $actual): void
{
    if ($expected !== $actual) {
        throw new RuntimeException('Unexpected label: ' . var_export($actual, true));
    }
}

same('old', applyLabel([], 'old'));
same(null, applyLabel([], null));
same(null, applyLabel(['label' => null], 'old'));
foreach (['', '0', 'new', "\0", 'é'] as $value) {
    same($value, applyLabel(['label' => $value], 'old'));
}
foreach ([false, true, 0, 1, 1.5, [], new stdClass()] as $value) {
    try {
        applyLabel(['label' => $value], 'old');
    } catch (InvalidArgumentException $error) {
        continue;
    }
    throw new RuntimeException('Invalid value was accepted');
}
echo "presence: passed\n";
