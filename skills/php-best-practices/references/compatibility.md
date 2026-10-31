# PHP compatibility

Sources reviewed 2026-10-31. Verify current documentation when a task depends on a newer release; this file is not a frozen catalogue of language features.

## Establish evidence

Read root and relevant package Composer requirements, platform overrides, CI matrices, runtime images, deployment configuration, and analyser settings. Record supported versions separately from locally available versions. A broad constraint such as `^8.2` permits later PHP 8 releases; it is not evidence that only 8.2 matters. Do not derive the minimum from the developer's interpreter.

Composer's platform override affects dependency resolution, not the interpreter executing the code. A successful install on a simulated platform proves neither syntax compatibility nor production extension availability. Use `composer check-platform-reqs` in the actual runtime; select production versus development dependencies according to the deployment. Do not bypass checks with ignore-platform flags to make validation pass.

If configuration conflicts, determine whether it is stale or expresses separate consumer/deployment requirements. Ask only for a consequential unresolved target decision; do not silently choose the newest or lowest number. An unsupported upstream runtime may still be an explicit maintenance target. Report its support status and upgrade options without upgrading it as part of unrelated work.

## Make version-sensitive changes

Consult the official migration guide for each release crossed and the manual for the particular feature. Check additions, removals, changed coercion/error behaviour, deprecations, and extension dependencies. A guard cannot make newer syntax parse on an older interpreter. Conditional use of a new function must include a valid fallback where older runtimes are supported.

Separate the runtime required by development tools from the PHP versions supported by shipped code. Check the installed analyser and compatibility scanner's documented coverage before trusting their results. Configure PHPStan's target or range consistently with the project; verify configuration support in the installed tool version. Do not infer that running analysis on a modern interpreter makes the code compatible with an older one.

Public parameter names can be consumed by named arguments. Adding types, changing parameter names, changing visibility, or adding final/readonly can break callers, subclasses, proxy generation, or hydration. Compare against the actual compatibility promise, not merely whether the edited application tests pass.

## Primary sources

- [PHP migration guides and appendices](https://www.php.net/manual/en/appendices.php): release-specific additions and incompatibilities.
- [PHP supported versions](https://www.php.net/supported-versions.php): current upstream support windows; avoid copying dates into permanent instructions.
- [Composer platform configuration](https://getcomposer.org/doc/06-config.md#platform) and [platform checks](https://getcomposer.org/doc/03-cli.md#check-platform-reqs): simulated versus actual environment.
- [Composer version constraints](https://getcomposer.org/doc/articles/versions.md): interpret the promised range correctly.
- [PHPStan configuration](https://phpstan.org/config-reference#phpversion): configure analysis for the intended runtime.
