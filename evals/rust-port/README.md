# Rust port smoke cases

These small fixtures exercise semantic boundaries that an idiomatic-looking translation can miss. They are authored for this repository and use no external dependencies.

- `c-bytes`: a length-delimited byte parser with arbitrary byte keys, nullable input, distinct format/overflow errors, and defined first-error precedence. The Rust return value replaces the C output parameters; there is no FFI requirement.
- `python-lines`: Python `splitlines` behaviour over valid Unicode scalar text, with empty lines removed and nonempty lines preserved verbatim. Tests include CRLF, non-ASCII separators, whitespace-only lines, and a control character that is not a separator.

CI runs the original C/Python source tests and static skill checks. It does not run a model or execute generated ports.

## Explicit model smoke test

With an authenticated Codex CLI, a C compiler, Python, and Rust installed:

```sh
python3 evals/rust-port/run_smoke.py --output /tmp/rust-port-smokes --model gpt-6-luna
```

Use a fresh output directory. The script runs two sequential model tasks, with a default timeout of 180 seconds each, consuming the account's allowance. It disables unrelated skills, verifies that only `rust-port` is enabled, and provides the original source and tests without the post-run Rust contract tests. It reuses the existing comparison runner's configuration and cancellation helpers. Ctrl-C stops active model calls and prevents the second task from starting.

The original source is committed in each temporary workspace. The model ports the code, tests, and API mappings. Afterwards, independent Rust contract tests are added and executed; the script checks that the original source remains unchanged and porting notes exist. Raw runtime events remain outside the repository. Inspect generated code and the evidence before publishing it.

The [recorded smoke results](RESULTS.md) include source hashes, generated artifacts, and limitations.

These two tasks are functional smoke tests, not a baseline/upstream comparison or proof of general compatibility. The historical 18-run benchmark remains pinned to its original revision and does not evaluate `rust-port`.
