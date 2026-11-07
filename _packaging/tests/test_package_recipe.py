import importlib.util
import json
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SPEC = importlib.util.spec_from_file_location('package_recipe', Path(__file__).resolve().parents[1] / 'package_recipe.py')
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.recipe = self.directory / 'demo'
        (self.recipe / 'tests').mkdir(parents=True)
        self.config = dict(compile=['build.sh'], runtime=['data.db'], checker=[], postprocessor=[], tests=['001'])
        (self.recipe / 'build.sh').write_bytes(b'#!/bin/sh\r\npython3 solution.py\r\n')
        (self.recipe / 'data.db').write_bytes(b'SQLite\x00\r\n\xff')
        (self.recipe / 'tests/001').write_bytes(b'hello\r\n')
        (self.recipe / 'tests/001.a').write_bytes(b'world\r\n')
        (self.recipe / 'solution.py').write_text('raise RuntimeError("must not be uploaded")', encoding='utf-8')
        self.save_config()

    def save_config(self):
        (self.recipe / 'package.json').write_text(json.dumps(self.config), encoding='utf-8')

    def test_archive_is_deterministic_and_normalizes_only_text(self):
        entries = package.prepare(self.recipe)
        first, second = self.directory / 'a.zip', self.directory / 'b.zip'
        package.write_zip(entries, first)
        package.write_zip(entries, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(set(archive.namelist()), {'build.sh', 'data.db', 'tests/001', 'tests/001.a'})
            self.assertEqual(archive.read('build.sh'), b'#!/bin/sh\npython3 solution.py\n')
            self.assertEqual(archive.read('data.db'), b'SQLite\x00\r\n\xff')
            self.assertEqual(archive.getinfo('build.sh').external_attr >> 16 & 0o777, 0o755)

    def test_missing_answer_is_rejected(self):
        (self.recipe / 'tests/001.a').unlink()
        with self.assertRaisesRegex(package.PackageError, 'missing files: tests/001.a'):
            package.prepare(self.recipe)

    def test_extra_old_test_is_rejected(self):
        (self.recipe / 'tests/002').touch()
        with self.assertRaisesRegex(package.PackageError, 'unlisted test files'):
            package.prepare(self.recipe)

    def test_http_renaming_replaces_old_paths(self):
        self.config['rename'] = {'tests/001': 'tests/01', 'tests/001.a': 'tests/01.a'}
        self.save_config()
        entries = package.prepare(self.recipe)
        self.assertIn('tests/01', entries)
        self.assertNotIn('tests/001', entries)

    def test_path_traversal_and_collisions_are_rejected(self):
        for target in ['../outside', '/absolute', 'C:/outside', 'tests/../01', 'tests\\01', 'build.sh']:
            with self.subTest(target=target):
                self.config['rename'] = {'tests/001': target}
                self.save_config()
                with self.assertRaises(package.PackageError):
                    package.prepare(self.recipe)

    def test_external_data_can_fill_missing_asset(self):
        (self.recipe / 'data.db').unlink()
        assets = self.directory / 'assets'
        (assets / 'demo').mkdir(parents=True)
        (assets / 'demo/data.db').write_bytes(b'external')
        entries = package.prepare(self.recipe, assets)
        self.assertEqual(entries['data.db'], b'external')

    def test_failed_batch_writes_no_archives(self):
        broken = self.directory / 'broken'
        broken.mkdir()
        config = dict(self.config, runtime=['missing.db'])
        (broken / 'package.json').write_text(json.dumps(config), encoding='utf-8')
        output = self.directory / 'output'
        with patch.object(package, 'ROOT', self.directory):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                status = package.main(['demo', 'broken', '--output', str(output)])
        self.assertEqual(status, 1)
        self.assertFalse(output.exists())

    def test_python_syntax_error_is_rejected(self):
        self.config['checker'] = ['checker.py']
        (self.recipe / 'checker.py').write_text('def invalid(', encoding='utf-8')
        self.save_config()
        with self.assertRaises(SyntaxError):
            package.prepare(self.recipe)


if __name__ == '__main__':
    unittest.main()
