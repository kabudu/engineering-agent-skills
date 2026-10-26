#!/usr/bin/env python3
"""Validate this portable skill catalogue offline (Python 3.9+, PyYAML).

Validation design inspired by BeautifulRust's checker contributed by mvanhorn.
This implementation uses PyYAML and has no plugin-manifest or host dependency.
See README.md#attribution for provenance.
"""
import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
SKIP = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', 'target'}
LINK = re.compile(r'\]\(\s*(<[^>]+>|[^\s)]+)|^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)', re.M)
RESOURCE = re.compile(r'`((?:references|scripts|assets)/[^`\s]+)`')


class UniqueLoader(yaml.SafeLoader):
    """Reject ambiguous duplicate mappings instead of silently keeping the last value."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(None, None, 'unhashable key', key_node.start_mark) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(None, None, f'duplicate key: {key}', key_node.start_mark)
            result[key] = self.construct_object(value_node, deep=deep)
        return result


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    level: str
    message: str


def prose(text):
    """Keep line numbers while excluding fenced code examples from link validation."""
    output, fence, width = [], None, 0
    for line in text.splitlines():
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence is None and match:
            fence, width = match[1][0], len(match[1])
            output.append('')
        elif fence is not None:
            if match and match[1][0] == fence and len(match[1]) >= width and not match[2].strip():
                fence = None
            output.append('')
        else:
            output.append(line)
    return '\n'.join(output)


def check_repo(root):
    root = Path(root).resolve()
    problems, edges = [], {}

    def report(path, message, line=1, level='error'):
        path = Path(path)
        label = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        problems.append(Problem(label, line, level, message))

    def read(path):
        try:
            return path.read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as exc:
            report(path, f'cannot read UTF-8 text: {exc}')
            return None

    skills_root = root/'skills'
    skills = sorted(p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith('.')) if skills_root.is_dir() else []
    if not skills:
        report(skills_root, 'no skill directories found')
    for skill in skills:
        entry = skill/'SKILL.md'
        if not skill.resolve().is_relative_to(root):
            report(entry, 'skill folder resolves outside the repository')
            continue
        if not entry.resolve().is_relative_to(skill.resolve()):
            report(entry, 'entrypoint resolves outside its skill folder')
            continue
        text = read(entry)
        if text is None:
            continue
        lines = text.splitlines()
        if not lines or lines[0] != '---' or '---' not in lines[1:]:
            report(entry, 'missing YAML frontmatter delimiters')
            continue
        end = lines.index('---', 1)
        try:
            data = yaml.load('\n'.join(lines[1:end]), Loader=UniqueLoader)
        except yaml.YAMLError as exc:
            report(entry, f'invalid frontmatter: {exc}', getattr(getattr(exc, 'problem_mark', None), 'line', 0)+2)
            continue
        if not isinstance(data, dict):
            report(entry, 'frontmatter must be a mapping')
            continue
        for key in data:
            if key not in FIELDS:
                report(entry, f'unsupported portable frontmatter key: {key}')
        name, description = data.get('name'), data.get('description')
        if not isinstance(name, str) or len(name) > 64 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            report(entry, 'name must be 1-64 lowercase ASCII letters/digits separated by hyphens')
        elif name != skill.name:
            report(entry, f'name {name!r} does not match folder {skill.name!r}')
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            report(entry, 'description must be nonempty text of at most 1024 characters')
        for key in ('license', 'compatibility', 'allowed-tools'):
            if key in data and not isinstance(data[key], str):
                report(entry, f'{key} must be text')
        if isinstance(data.get('compatibility'), str) and len(data['compatibility']) > 500:
            report(entry, 'compatibility exceeds 500 characters')
        if 'metadata' in data and not isinstance(data['metadata'], dict):
            report(entry, 'metadata must be a mapping')
        if not '\n'.join(lines[end+1:]).strip():
            report(entry, 'skill body is empty')
        if len(lines[end+1:]) > 500:
            report(entry, 'body exceeds 500 lines; consider selectively loaded references', level='warning')
        if (skill/'NOTICE.md').is_file() and not (skill/'LICENSE').is_file():
            report(skill/'LICENSE', 'a skill with a provenance notice must retain its licence')

    readme = root/'README.md'
    docs = [p for p in root.rglob('*.md') if not any(part in SKIP for part in p.relative_to(root).parts)] if root.is_dir() else []
    if not readme.is_file():
        report(readme, 'missing README catalogue')
    for path in sorted(docs):
        owner = next((s for s in skills if path.is_relative_to(s)), None)
        boundary = owner.resolve() if owner else root
        if not path.resolve().is_relative_to(boundary):
            report(path, 'Markdown file resolves outside its portable boundary')
            continue
        text = read(path)
        if text is None:
            continue
        text = prose(text)
        targets = [(m.start(), (m[1] or m[2]).strip('<>')) for m in LINK.finditer(text)]
        if owner:
            targets += [(m.start(), m[1]) for m in RESOURCE.finditer(text)]
        edges[path.resolve()] = set()
        for position, target in targets:
            line = text[:position].count('\n')+1
            try:
                parsed = urlsplit(target)
            except ValueError:
                report(path, f'invalid link: {target}', line)
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local = unquote(parsed.path)
            resolved = (path.parent/local).resolve()
            if Path(local).is_absolute() or not resolved.is_relative_to(boundary):
                report(path, f'local resource escapes its portable boundary: {target}', line)
            elif not resolved.exists():
                report(path, f'missing local resource: {target}', line)
            else:
                edges[path.resolve()].add(resolved)
    catalogue = edges.get(readme.resolve(), set())
    for skill in skills:
        if skill.resolve() not in catalogue and (skill/'SKILL.md').resolve() not in catalogue:
            report(readme, f'skill not linked in README catalogue: {skill.name}')
        reachable, pending = set(), [(skill/'SKILL.md').resolve()]
        while pending:
            item = pending.pop()
            if item in reachable:
                continue
            reachable.add(item)
            pending.extend(edges.get(item, ()))
        references = skill/'references'
        if references.is_dir():
            for resource in sorted(p for p in references.rglob('*') if p.is_file() and not p.name.startswith('.')):
                if resource.resolve() not in reachable:
                    report(resource, 'reference is unreachable from SKILL.md')
    return sorted(set(problems), key=lambda p: (p.path, p.line, p.level, p.message))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=ROOT)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    problems = check_repo(args.root)
    errors = sum(p.level == 'error' for p in problems)
    warnings = sum(p.level == 'warning' for p in problems)
    if args.json:
        print(json.dumps({'ok':not errors, 'error_count':errors, 'warning_count':warnings, 'problems':[asdict(p) for p in problems]}, indent=2))
    else:
        for p in problems:
            print(f'{p.path}:{p.line}: {p.level}: {p.message}')
        print(f'{errors} errors, {warnings} warnings')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
