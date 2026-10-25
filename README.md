# AI Skills

Reusable agent skills for engineering rigour, workflow discipline, and AI-assisted development.

This repository is a public catalogue of portable skills that follow the open Agent Skills format. Each skill lives in its own folder under `skills/` and can be installed in compatible tools such as Codex, Claude Code, and Cursor.

## Skills

| Skill | Purpose |
| --- | --- |
| [`lazarus-mode`](skills/lazarus-mode) | Expert engineering rigor for implementation, review, testing, documentation, and release work. |
| [`rust-best-practices`](skills/rust-best-practices) | Implement, refactor, and debug Rust with concise core guidance and selectively loaded references. |
| [`rust-review`](skills/rust-review) | Review Rust for evidence-backed correctness, safety, and compatibility findings; independently installable. |
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
  rust-review/
    SKILL.md
    LICENSE
    NOTICE.md
    references/
      risk-checks.md
```

The Rust skills use the same installation pattern above: substitute `rust-best-practices` or `rust-review` for `lazarus-mode`. Each can be installed separately; neither requires another skill. Optional host metadata is not required for their use.

Rust evaluation cases and comparison instructions live in [`evals/rust`](evals/rust). The [18-run preliminary report](evals/rust/RESULTS.md) records measured token usage, held-out checks, and verification gaps. Entrypoint compression is distinct from runtime savings; equivalent reliability is not established.

Each skill must have a `SKILL.md` entry point with valid `name` and `description` frontmatter.

## Attribution

The Rust skills adapt [BeautifulRust](https://github.com/morganlinton/BeautifulRust) by Morgan Linton under MIT. Each includes the original licence and a provenance notice recording the source revision and our changes.

## License

MIT. Retained third-party notices accompany the adapted Rust skills.
