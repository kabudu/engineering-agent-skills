<?php

// A patch key that is absent leaves the old value alone. Explicit null clears it.
function applyLabel(array $patch, ?string $current): ?string
{
    return $patch['label'] ?? $current;
}
