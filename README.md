# AI Skills

Reusable agent skills for engineering rigour, workflow discipline, and AI-assisted development.

This repository is a public catalogue of portable skills that follow the open Agent Skills format. Each skill lives in its own folder under `skills/` and can be installed in compatible tools such as Codex, Claude Code, and Cursor.

## Skills

| Skill | Purpose |
| --- | --- |
| [`lazarus-mode`](skills/lazarus-mode) | Expert engineering rigor for implementation, review, testing, documentation, and release work. |
| [`php-best-practices`](skills/php-best-practices) | BeautifulPHP: version-aware PHP implementation and review with precise contracts and selectively loaded references. |
| [`rust-best-practices`](skills/rust-best-practices) | Rust implementation guidance with concise core instructions and selectively loaded references. |
| [`rust-port`](skills/rust-port) | Port existing code to Rust with explicit compatibility contracts, traceable tests, and selectively loaded language guidance. |
| [`rust-review`](skills/rust-review) | Rust review guidance for evidence-backed correctness, safety, and compatibility findings; independently installable. |
| [`pr-splitter`](skills/pr-splitter) | Decompose oversized pull requests into dependency-aware, reviewable PRs while preserving their combined behaviour. |

## Clone the repository

```sh
git clone git@github.com:kabudu/engineering-agent-skills.git
cd engineering-agent-skills
```

The examples below use symlinks where the host supports them so that a later `git pull` updates every installed skill automatically.

## Install with Codex

Codex discovers personal skills in `~/.agents/skills` and supports symlinked skill folders.

```sh
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/lazarus-mode" ~/.agents/skills/lazarus-mode
```

Codex normally detects skill changes automatically. If the skill does not appear, restart Codex.

## Install with Claude Code

Claude Code discovers personal skills in `~/.claude/skills` and supports symlinked skill folders.

```sh
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/lazarus-mode" ~/.claude/skills/lazarus-mode
```

Claude Code watches an existing skills directory for changes. If you created `~/.claude/skills` while Claude Code was running, restart it once.

## Install with Cursor

Cursor discovers personal skills in `~/.cursor/skills`:

```sh
mkdir -p ~/.cursor/skills
ln -s "$PWD/skills/lazarus-mode" ~/.cursor/skills/lazarus-mode
```

Restart Cursor if the skill does not appear in its skills list.

## Updating

Update the checkout to update every symlinked installation:

```sh
git pull
```

## Adding Skills

Add each new skill in its own directory:

```text
skills/
  new-skill-name/
    SKILL.md
```

Optional companion files, templates, scripts, or agent metadata should live inside the same skill directory so the skill stays portable.

## Repository Layout

```text
skills/
  lazarus-mode/
    SKILL.md
    agents/
      openai.yaml
    references/
      debugging.md
      performance.md
  php-best-practices/
    SKILL.md
    references/
      compatibility.md
      types-and-contracts.md
      security-and-boundaries.md
      testing-and-tooling.md
  pr-splitter/
    SKILL.md
    agents/
      openai.yaml
    references/
      decomposition-playbook.md
  rust-best-practices/
    SKILL.md
    LICENSE
    NOTICE.md
    references/
      api-and-cargo.md
      concurrency.md
      unsafe-and-ffi.md
  rust-port/
    SKILL.md
    LICENSE
    NOTICE.md
    references/
      c-and-cpp.md
      python.md
      go-and-javascript.md
  rust-review/
    SKILL.md
    LICENSE
    NOTICE.md
    references/
      risk-checks.md
```

The Rust skills use the same installation pattern above: substitute `rust-best-practices`, `rust-review`, or `rust-port` for `lazarus-mode`. Each can be installed separately; none requires another skill. Optional host metadata is not required for their use.

Rust evaluation cases and comparison instructions live in [`evals/rust`](evals/rust). The [18-run preliminary report](evals/rust/RESULTS.md) records measured token usage, held-out checks, and verification gaps. Entrypoint compression is distinct from runtime savings; equivalent reliability is not established. That comparison covers the two original adaptations at its recorded revision, not `rust-port` or later reference changes.

BeautifulPHP uses the same installation pattern: substitute `php-best-practices` for `lazarus-mode`. It is independently installable and follows the target project's PHP range, framework conventions, and tooling. Its [evaluation cases](evals/php/README.md) include executable boundary oracles; no model-effectiveness or token-savings results are claimed.

Each skill must have a `SKILL.md` entry point with valid `name` and `description` frontmatter.

## Validate changes

Install the development dependency and run the offline catalogue checks:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_skills.py
python3 -m unittest discover -s tests -v
python3 evals/rust/check_fixtures.py
python3 evals/php/check_fixtures.py
```

The catalogue checker needs Python 3.9+ and PyYAML. It validates portable frontmatter, README discovery links, local resources, reference reachability, and self-contained skill boundaries. Nested references are supported; links into sibling skills or outside the skill folder are rejected. It does not fetch remote links, run model evaluations, or require any agent/plugin installation. Use `--json` for structured diagnostics.

The Rust fixture command also needs Rust. It compiles the unsafe review fixture without executing it, runs the clean fixture's boundary tests, and checks packaging for all three Rust skills. These checks do not establish model effectiveness. The new [porting smoke cases](evals/rust-port/README.md) and [recorded results](evals/rust-port/RESULTS.md) test two focused compatibility boundaries without extending the historical benchmark claims.

The PHP fixture checker needs PHP and verifies that held-out oracles reject buggy seeds and accept known repairs. Select a local interpreter with `--php /path/to/php`; this does not run a model.

[CI](.github/workflows/check.yml) runs the catalogue checker and mutation tests on Python 3.9 and 3.14, plus the Rust fixture checks and PHP oracle checks across PHP 8.2 through 8.5. Workflows use read-only permissions and pinned action revisions. Model evaluations remain explicit local runs and are not part of CI.

## Attribution

The Rust skills adapt [BeautifulRust](https://github.com/morganlinton/BeautifulRust) by Morgan Linton under MIT. Each includes the original licence and a provenance notice recording the source revision and our changes. `rust-port` follows upstream v1.4.0; the original two skills retain their historical source and benchmark pins.

The portable checker was written for this repository, inspired by BeautifulRust's validation work contributed by [mvanhorn](https://github.com/mvanhorn). The MSRV clarification follows the lint-proof work credited to the same contributor in [BeautifulRust v1.4.0](https://github.com/morganlinton/BeautifulRust/blob/a2b22682fa69b5e2d41a5d041663df7d51aac521/CHANGELOG.md). Claude plugin packaging and the upstream source-guide digests are not redistributed.

BeautifulPHP is original guidance inspired by Morgan Linton's BeautifulRust approach, with primary sources linked in its references. It does not copy BeautifulRust skill text or redistribute the linked manuals.

## License

MIT. Retained third-party notices accompany the adapted Rust skills.
