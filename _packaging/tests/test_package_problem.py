import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

PACKAGING = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGING))
import package_problem as package


class ProblemPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_all_recipes_produce_self_contained_reproducible_packages(self):
        assets = self.directory / 'assets' / 'ml-score-prediction'
        assets.mkdir(parents=True)
        (assets / 'true_answers.csv').write_text('target\n' + '1\n0\n' * 1570, encoding='utf-8')
        for recipe in sorted(package.ROOT.glob('*/import.json')):
            with self.subTest(recipe=recipe.parent.name):
                entries = package.prepare_problem(recipe.parent, assets.parent)
                meta = json.loads(entries['meta.json'])['problemMetadata']
                self.assertEqual(meta['shortName'], recipe.parent.name)
                self.assertEqual(meta['solutions'], [])
                self.assertEqual(meta['parentProblemId'], '')
                self.assertEqual(meta['rootProblemId'], '')
                self.assertNotIn('author', meta)
                for role in ['includeForCompileFiles', 'includeForRunFiles', 'postProcessFiles']:
                    self.assertTrue(set(meta[role]).issubset(entries))
                for test_set in meta['testSets']:
                    for test in test_set['matchedTests']:
                        self.assertIn(test['inputPath'], entries)
                        self.assertIn(test['answerPath'], entries)
                self.assertFalse(any(n.startswith('solutions/') or n in ['expression.py', 'solution.py', 'readme.md'] for n in entries))
                self.assertNotIn(b'admin.contest.yandex.ru', entries['meta.json'])
                first, second = self.directory / 'a.zip', self.directory / 'b.zip'
                package.write_zip(entries, first)
                package.write_zip(package.prepare_problem(recipe.parent, assets.parent), second)
                self.assertEqual(first.read_bytes(), second.read_bytes())
                with zipfile.ZipFile(first) as archive:
                    self.assertIsNone(archive.testzip())

    def test_question_contains_options_and_one_based_correct_answers(self):
        entries = package.prepare_problem(package.ROOT / 'test-problem')
        options = json.loads((package.ROOT / 'test-problem/example.json').read_text(encoding='utf-8'))['options']
        self.assertEqual(entries['tests/01'].decode().splitlines(), [o['text'] for o in options])
        self.assertFalse(entries['tests/01'].endswith(b'\n'))
        self.assertEqual(entries['tests/01.a'], b'1 3')
        meta = json.loads(entries['meta.json'])['problemMetadata']
        self.assertEqual(meta['fieldTypeMeta'], 'CHECKBOXES')
        self.assertEqual(meta['answerTypeMeta'], 'CHECKBOX')
        self.assertEqual(meta['metaInfo']['maxScore'], 100)

    def test_flask_samples_are_separate_from_five_scored_tests(self):
        meta = json.loads(package.prepare_problem(package.ROOT / 'network-http-server')['meta.json'])['problemMetadata']
        groups = {s['name']: {t['inputPath'] for t in s['matchedTests']} for s in meta['testSets']}
        self.assertEqual(len(groups['samples']), 2)
        self.assertEqual(len(groups['All tests']), 5)
        self.assertFalse(groups['samples'] & groups['All tests'])

    def test_rendered_statement_includes_limits_and_sample_io(self):
        entries = package.prepare_problem(package.ROOT / 'network-http-server')
        page = entries['statements/.html/ru/full_page.html'].decode('utf-8')
        self.assertIn('Ограничение времени', page)
        self.assertIn('64 МБ', page)
        self.assertIn('Пример 2', page)
        self.assertIn('127.0.0.1:7777/7/8', page)
        self.assertIn('&lt;a&gt;', page)

    def test_markdown_source_and_rendering_are_in_package(self):
        entries = package.prepare_problem(package.ROOT / 'db-sqlite')
        metadata = json.loads(entries['meta.json'])['problemMetadata']
        statement = metadata['statements'][0]
        self.assertEqual(statement['type'], 'MARKDOWN')
        self.assertEqual(statement['rawStatement']['legend'], (package.ROOT / 'db-sqlite/statement.md').read_text(encoding='utf-8'))
        page = entries[statement['path']].decode('utf-8')
        self.assertIn('<table>', page)
        self.assertIn('<code>Films.id</code>', page)
        self.assertIn('<h2>', page)

    def test_missing_ml_answers_fail_without_writing_any_batch_archives(self):
        output = self.directory / 'output'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = package.main(['db-sqlite', 'ml-score-prediction', '--assets', str(self.directory), '--output', str(output)])
        self.assertEqual(status, 1)
        self.assertFalse(output.exists())

    def test_missing_checker_and_uncovered_tests_are_rejected(self):
        source = package.ROOT / 'db-sqlite'
        config = json.loads((source / 'import.json').read_text(encoding='utf-8'))
        original_read = Path.read_text
        def changed_read(path, *args, **kwargs):
            if path == source / 'import.json':
                return json.dumps(config)
            return original_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', changed_read):
            config['checkerSettings']['checkerFiles'] = ['missing.py']
            with self.assertRaisesRegex(package.PackageError, 'referenced file'):
                package.prepare_problem(source)
            config['checkerSettings']['checkerFiles'] = ['compare_result.py']
            config['testSets'][0]['tests'].pop()
            with self.assertRaisesRegex(package.PackageError, 'cover every'):
                package.prepare_problem(source)

    def test_score_adapter_keeps_zero_and_partial_scores_and_rejects_errors(self):
        output = self.directory / 'answer.txt'
        for content, expected_code, expected_score in [('0\n', 0, 0), ('1.0522688719\n', 0, 1.0522688719), ('2\n', 0, 2), ('-1\n', 0, 0), ('incorrect shape\n', 1, None), ('1 trailing text\n', 1, None), ('nan\n', 1, None), ('inf\n', 1, None), ('', 2, None)]:
            with self.subTest(content=content):
                output.write_text(content, encoding='utf-8')
                result = subprocess.run([sys.executable, '-B', str(PACKAGING / 'score_file.py'), 'unused.in', str(output), 'unused.a'], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, expected_code)
                if expected_score is not None:
                    self.assertAlmostEqual(float(result.stdout), expected_score)


if __name__ == '__main__':
    unittest.main()
