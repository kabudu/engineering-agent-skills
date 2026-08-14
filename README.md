# AI Skills

Reusable agent skills for engineering rigour, workflow discipline, and AI-assisted development.

This repository is a public catalogue of portable skills that follow the open Agent Skills format. Each skill lives in its own folder under `skills/` and can be installed in compatible tools such as Codex, Claude Code, and Cursor.

## Skills

| Skill | Purpose |
| --- | --- |
| [`lazarus-mode`](skills/lazarus-mode) | Expert engineering rigor for implementation, review, testing, documentation, and release work. |

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
```

Each skill must have a `SKILL.md` entry point with valid `name` and `description` frontmatter.

## License

MIT
