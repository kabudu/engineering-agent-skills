# Testing and tooling

Sources reviewed 2026-10-31. Prefer repository scripts and installed tool versions. Do not install a new toolchain or upgrade dependencies solely to satisfy a generic checklist.

## Select checks by their evidence

1. Inspect Composer scripts, test configuration, formatter rules, analysis configuration, CI, and available runtimes. Use the project's runner, whether PHPUnit, Pest, or another established tool.
2. Run syntax checks on affected PHP files with the intended interpreter. `php -l` checks syntax, not function availability, types, or behaviour. A successful check on the latest PHP does not prove older-runtime compatibility.
3. Run focused behavioural tests, then affected integration checks. Test the minimum supported runtime and other relevant supported versions where available. Report unavailable runtime coverage rather than silently substituting the local interpreter.
4. Run the configured PHPStan or Psalm checks and formatter in check mode for review. Respect baselines for existing debt; do not regenerate them or add suppressions to hide a regression. Use framework extensions/stubs already configured by the project.
5. For migrations or broad compatibility promises, use PHPCompatibility when its installed version supports the intended range. Set its testVersion appropriately and inspect coverage limitations. Runtime tests still matter.
6. Validate changed Composer metadata and actual platform requirements. Use dependency audit checks when dependency changes or the requested security scope makes them relevant. Installing from a lockfile and updating dependencies are different operations; avoid incidental lockfile churn.

## Tests that protect behaviour

Use independent expected results, not expectations computed by the implementation under test. Cover missing versus null, zero-like values, ordering, serialization shape, encoding, and exception paths when relevant. Verify transaction/cleanup behaviour through appropriate integration tests rather than assuming mocks prove it. Ensure framework fixtures actually boot the affected integration.

A green test suite does not justify changes outside the promised contract. For reviews, distinguish missing evidence from a demonstrated defect and avoid speculative findings presented as facts.

## Style and sources

Use the repository's formatter configuration. Without a project standard, select an explicit target-compatible PER Coding Style ruleset supported by the chosen tool. Do not copy a formatting manual into the prompt or impose a newer preset that emits unsupported syntax.

- [PHP-FIG PER Coding Style](https://www.php-fig.org/per/coding-style/): evolving successor to PSR-12; preserve existing PSR-12 or framework conventions where established.
- [PHP CLI options](https://www.php.net/manual/en/features.commandline.options.php): syntax-check scope.
- [PHPStan configuration](https://phpstan.org/config-reference) and [Psalm documentation](https://psalm.dev/docs/): analysis configuration, suppression policy, and type precision.
- [PHPCompatibility](https://github.com/PHPCompatibility/PHPCompatibility): scanner configuration and version coverage.
- [Composer CLI](https://getcomposer.org/doc/03-cli.md): validation, platform requirements, and dependency operations.
- [PHPUnit documentation](https://docs.phpunit.de/): select the documentation for the project's installed major version.
