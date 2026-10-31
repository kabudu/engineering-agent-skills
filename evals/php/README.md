# BeautifulPHP evaluation cases

These newly authored cases support behavioural evaluation of php-best-practices. They are not model results or evidence of token savings. The skill core and references are original summaries, not a PHP translation of BeautifulRust.

## Deterministic oracle checks

From the repository root:

```sh
python3 evals/php/check_fixtures.py
```

The checker needs Python 3.9+ and PHP. It syntax-checks the seeds, known repairs, and oracles, confirms that each oracle rejects its buggy seed and accepts a known repair, and leaves source files untouched. Use `--php /path/to/php` to select a runtime. This checks the evaluation fixtures, not model behaviour or the full language compatibility of the skill.

## Model evaluation protocol

For each case, copy only its fixture folder into a fresh workspace. Give the agent TASK.md, its normal engineering tools, and the skill condition being evaluated. Keep held-out oracles and known repairs outside the agent's accessible workspace. Do not expose this protocol's expected answers. After the agent finishes, run the corresponding oracle against its value.php with each supported test runtime:

```sh
php evals/php/held-out/presence.php /path/to/output/value.php
php evals/php/held-out/list-shape.php /path/to/output/value.php
```

The fixtures promise PHP 8.2 through 8.5. A newer local interpreter and Composer platform override must not cause the model to raise the minimum or claim execution on 8.2. Inspect metadata changes, generated tests, runtime claims, and the diff in addition to oracle outcomes. The presence case exercises missing/null, false-like strings, and invalid types; list-shape exercises sparse keys, ordering, duplicates, and encoding failure.

Compare no skill, the normal core with selectively available references, and an explicitly defined fuller-guidance condition. Keep task inputs, tool access, runtime availability, model settings, and budgets identical. Verify actual skill discovery and isolate unrelated skills, memory, and plugins. Record the exact skill/source revision and hashes, model identifier/settings, reference reads, command events, elapsed time, actual input/cached/output tokens, and failures. Repeat cases before making aggregate claims; do not substitute word-count reduction for runtime token savings. Review outcomes without revealing the condition where practical.

## Additional manual scenarios

These require separate realistic fixtures before use as scored cases:

- A public API refactor with weak callers, named arguments, subclasses, and serialization consumers. Check that strict typing and modern modifiers do not silently break the contract.
- PDO sorting with bound values and user-supplied identifiers, plus template output in HTML and URL contexts. Check identifier allowlisting and context-specific encoding independently.
- A framework integration using its installed version, ORM hydration, and configured analyser extension. Check that generic design preferences do not replace supported framework behaviour.
- Conflicting Composer, CI, and deployment targets, followed by a feature unavailable on the minimum runtime. Check explicit resolution of the conflict and actual minimum-runtime verification.

No model benchmark has been run for BeautifulPHP. The two executable cases are narrow regression tasks, not coverage of every principle above. CI runs only the deterministic oracle checks.
