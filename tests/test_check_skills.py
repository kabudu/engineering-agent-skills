"""Mutation tests for portable discovery, resource boundaries, and offline validation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('check_skills', ROOT/'scripts/check_skills.py')
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root/'skills/example'
        self.write('README.md', '# Skills\n\n[Example](skills/example)\n')
        self.write('skills/example/SKILL.md', '---\nname: example\ndescription: Validate a portable example.\n---\n\n# Example\n\n[Guide](references/guide.md)\n')
        self.write('skills/example/references/guide.md', '# Guide\n')

    def write(self, name, text):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def errors(self):
        return [p.message for p in CHECKER.check_repo(self.root) if p.level == 'error']

    def test_portable_repo_without_plugin_manifests(self):
        self.assertEqual(self.errors(), [])
        self.assertFalse((self.root/'.claude-plugin').exists())

    def test_all_real_skills_pass(self):
        self.assertEqual([p for p in CHECKER.check_repo(ROOT) if p.level == 'error'], [])

    def test_invalid_frontmatter(self):
        entry = self.skill/'SKILL.md'
        for content in ('# No frontmatter', '---\nname: [\n---\nBody', '---\n- example\n---\nBody'):
            with self.subTest(content=content):
                entry.write_text(content)
                self.assertTrue(self.errors())

    def test_duplicate_fields_are_rejected(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text().replace('name: example', 'name: example\nname: different'))
        self.assertTrue(any('duplicate' in e for e in self.errors()))

    def test_name_must_match_folder(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text().replace('name: example', 'name: other'))
        self.assertTrue(any('does not match folder' in e for e in self.errors()))

    def test_description_type_and_limit(self):
        for value in ('false', 'null', '""', 'x'*1025):
            with self.subTest(value=value[:20]):
                self.write('skills/example/SKILL.md', f'---\nname: example\ndescription: {value}\n---\nBody\n[Guide](references/guide.md)\n')
                self.assertTrue(any('description' in e for e in self.errors()))

    def test_folded_description_and_metadata(self):
        self.write('skills/example/SKILL.md', '---\nname: example\ndescription: >-\n  A folded\n  description.\nmetadata:\n  author: example\n---\nBody\n[Guide](references/guide.md)\n')
        self.assertEqual(self.errors(), [])

    def test_missing_entrypoint(self):
        (self.skill/'SKILL.md').unlink()
        self.assertTrue(any('cannot read' in e for e in self.errors()))

    def test_broken_local_link(self):
        (self.skill/'references/guide.md').unlink()
        self.assertTrue(any('missing local resource' in e for e in self.errors()))

    def test_backtick_resource_is_checked(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text()+'\nRun `scripts/missing.py`.\n')
        self.assertTrue(any('scripts/missing.py' in e for e in self.errors()))

    def test_nested_reference_graph_is_allowed(self):
        self.write('skills/example/references/guide.md', '[Detail](nested/detail.md)\n')
        self.write('skills/example/references/nested/detail.md', '[Back](../guide.md)\n')
        self.assertEqual(self.errors(), [])

    def test_unreachable_reference_is_rejected(self):
        self.write('skills/example/references/unused.md', '# Forgotten\n')
        self.assertTrue(any('unreachable' in e for e in self.errors()))

    def test_sibling_skill_does_not_mask_missing_resource(self):
        self.write('skills/other/SKILL.md', '---\nname: other\ndescription: Another skill.\n---\n[Guide](references/guide.md)\n')
        self.write('skills/other/references/guide.md', '# Other guide\n')
        (self.skill/'references/guide.md').unlink()
        self.assertTrue(any('missing local resource' in e for e in self.errors()))

    def test_cross_skill_resource_breaks_standalone_install(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text()+'\n[Other](../another/guide.md)\n')
        self.write('skills/another/guide.md', '# Other\n')
        self.assertTrue(any('escapes its portable boundary' in e for e in self.errors()))

    def test_symlink_cannot_hide_external_reference(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)/'external.md'
            target.write_text('# External\n')
            local = self.skill/'references/guide.md'
            local.unlink()
            local.symlink_to(target)
            self.assertTrue(any('outside its portable boundary' in e or 'escapes its portable boundary' in e for e in self.errors()))

    def test_external_entrypoint_is_rejected_before_reading(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)/'SKILL.md'
            target.write_text('---\nname: example\ndescription: External.\n---\nBody\n')
            entry = self.skill/'SKILL.md'
            entry.unlink()
            entry.symlink_to(target)
            original_read = Path.read_text
            def guarded_read(path, *args, **kwargs):
                if path == entry:
                    raise AssertionError('external entrypoint was read')
                return original_read(path, *args, **kwargs)
            with patch.object(Path, 'read_text', guarded_read):
                self.assertTrue(any('entrypoint resolves outside' in e for e in self.errors()))

    def test_reference_definitions_and_encoded_paths(self):
        self.write('skills/example/references/guide.md', '[Details][detail]\n\n[detail]: <nested/with%20space.md>\n')
        self.write('skills/example/references/nested/with space.md', '# Details\n')
        self.assertEqual(self.errors(), [])

    def test_fenced_examples_are_not_links(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text()+'\n~~~markdown\n[Example](missing.md)\n`references/not-real.md`\n~~~\n')
        self.assertEqual(self.errors(), [])

    def test_external_links_are_not_fetched(self):
        entry = self.skill/'SKILL.md'
        entry.write_text(entry.read_text()+'\n[Docs](https://example.invalid/guide)\n')
        with patch('socket.create_connection', side_effect=AssertionError('network access')):
            self.assertEqual(self.errors(), [])

    def test_readme_catalogue_must_include_every_skill(self):
        self.write('README.md', '# Empty catalogue\n')
        self.assertTrue(any('not linked in README' in e for e in self.errors()))

    def test_adapted_skill_retains_licence(self):
        self.write('skills/example/NOTICE.md', '# Upstream credit\n')
        self.assertTrue(any('retain its licence' in e for e in self.errors()))

    def test_cli_reports_failure_as_json(self):
        (self.skill/'references/guide.md').unlink()
        result = subprocess.run([sys.executable, str(ROOT/'scripts/check_skills.py'), str(self.root), '--json'], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload['ok'])
        self.assertGreater(payload['error_count'], 0)

    def test_invalid_utf8_is_a_diagnostic(self):
        (self.skill/'references/guide.md').write_bytes(b'\xff')
        self.assertTrue(any('UTF-8' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
