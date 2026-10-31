<?php

// Return a JSON list of enabled names, in input order, including duplicates.
function enabledNamesJson(array $rows): string
{
    $enabled = array_filter($rows, static function (array $row): bool {
        return $row['enabled'] === true;
    });
    return json_encode(array_map(static function (array $row): string {
        return $row['name'];
    }, $enabled), JSON_THROW_ON_ERROR);
}
