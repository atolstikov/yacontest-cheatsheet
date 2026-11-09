"""Build a complete task ZIP for Contest's YANDEX importer."""
import argparse
import ast
import html
import json
from pathlib import Path
import sys

from package_recipe import PackageError, ROOT, prepare, read_asset, safe_name, write_zip


STATEMENT_DIR = 'statements/.html/ru'
METADATA_FIELDS = (
    'problemTypeMeta', 'testFileType', 'fileSet', 'solutionLimits',
    'compilationLimits', 'fieldTypeMeta', 'validation', 'answerTypeMeta',
    'sectionVisibility', 'checkerSettings', 'postProcessorSettings',
)


def encoded_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def render_markdown(text):
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise PackageError('install import dependencies: python -m pip install -r _packaging/requirements.txt') from exc
    return MarkdownIt('commonmark', {'html': False}).enable('table').render(text)


def prepare_problem(recipe, assets=None):
    config = json.loads((recipe / 'import.json').read_text(encoding='utf-8'))
    statement = (recipe / 'statement.md').read_text(encoding='utf-8').replace('\r\n', '\n')
    if not statement.strip():
        raise PackageError('empty statement.md')
    metadata = {key: config[key] for key in METADATA_FIELDS}
    if metadata['problemTypeMeta'] == 'TEST':
        example = json.loads((recipe / 'example.json').read_text(encoding='utf-8'))
        options = example['options']
        if example['answer_type'] != 'multiple' or not options or not any(o['correct'] for o in options):
            raise PackageError('expected nonempty multiple-choice question with a correct option')
        if any(not o['text'].strip() or '\n' in o['text'] or '\r' in o['text'] for o in options):
            raise PackageError('each option must occupy one nonempty line')
        entries = {
            # The native importer treats a trailing newline as another option.
            'tests/01': '\n'.join(o['text'] for o in options).encode('utf-8'),
            'tests/01.a': ' '.join(str(i) for i, o in enumerate(options, 1) if o['correct']).encode('utf-8'),
            'postprocessor.py': read_asset(recipe, 'postprocessor.py'),
        }
        metadata.update(includeForCompileFiles=[], includeForRunFiles=[], postProcessFiles=['postprocessor.py'])
    elif metadata['problemTypeMeta'] == 'WITH_CHECKER':
        entries = prepare(recipe, assets)
        manifest = json.loads((recipe / 'package.json').read_text(encoding='utf-8'))
        rename = manifest.get('rename', {})
        for field, role in [('includeForCompileFiles', 'compile'), ('includeForRunFiles', 'runtime'), ('postProcessFiles', 'postprocessor')]:
            metadata[field] = [rename.get(name, name) for name in manifest[role]]
        if recipe.name == 'ml-score-prediction':
            # Native packages need an executable checker, rather than uncompiled C++.
            # Use the portable checker adapter; the files-only ZIP keeps pointscmp.cpp.
            entries.pop('pointscmp.cpp', None)
            entries['score_file.py'] = (Path(__file__).parent / 'score_file.py').read_bytes().replace(b'\r\n', b'\n')
    else:
        raise PackageError('unsupported problemTypeMeta')

    metadata.update(
        shortName=recipe.name, names={'ru': config['name']}, defaultLocale='ru',
        metaInfo={'maxScore': config['maxScore']},
        compilerGroupLimits=[], customCompilationLimits=[], generators=[],
        generateTestCommands=[], solutions=[], tags=[], validators=[],
        problemCorrectAnswers=[], problemCompilers={'additionalCompilers': {}},
        solutionTemplates=[], parentProblemId='', rootProblemId='',
    )
    checker_files = metadata['checkerSettings'].get('checkerFiles') or []
    for name in checker_files + metadata['includeForCompileFiles'] + metadata['includeForRunFiles'] + metadata['postProcessFiles']:
        safe_name(name)
        if name not in entries or entries[name] is None:
            raise PackageError(f'referenced file is absent: {name}')

    test_sets = []
    covered_tests = set()
    for test_set in config['testSets']:
        tests = []
        for name in test_set['tests']:
            input_path = safe_name('tests/' + name)
            answer_path = input_path + '.a'
            if input_path not in entries or answer_path not in entries:
                raise PackageError(f'incomplete test pair: {input_path}')
            tests.append(dict(inputPath=input_path, answerPath=answer_path, inputExists=True, answerExists=True))
            covered_tests.add(input_path)
        if not tests:
            raise PackageError('empty test set')
        test_sets.append(dict(name=test_set['name'], inputFilePattern=test_set['inputFilePattern'], answerFilePattern='*.a', matchedTests=tests))
    actual_tests = {name for name in entries if name.startswith('tests/') and not name.endswith('.a')}
    if actual_tests != covered_tests:
        raise PackageError('test sets must cover every packaged test')
    metadata['testSets'] = test_sets

    rendered = render_markdown(statement)
    parts = dict(legend=rendered, inputFormat=None, outputFormat=None, interaction=None, scoring=None, notes=None)
    raw = dict(legend=statement, inputFormat='', outputFormat='', interaction=None, scoring=None, notes='', showLimits=None)
    statement_path = STATEMENT_DIR + '/full_page.html'
    metadata['statements'] = [dict(locale='ru', type='MARKDOWN', path=statement_path, texStatement=None, markdownStatement=None, rawStatement=raw)]
    header = []
    visibility = metadata['sectionVisibility']
    if visibility['showLimits']:
        limits = metadata['solutionLimits']
        header.append('<tr><td>Ограничение времени</td><td>' + str(limits['timeLimitMillis'] / 1000) + ' с</td></tr>')
        header.append('<tr><td>Ограничение памяти</td><td>' + str(limits['memoryLimit'] // (1024 * 1024)) + ' МБ</td></tr>')
    if visibility['showIo']:
        files = metadata['fileSet']
        for label, field, redirect, stream in [('Ввод', 'inputFile', 'redirectStdin', 'стандартный ввод'), ('Вывод', 'outputFile', 'redirectStdout', 'стандартный вывод')]:
            value = files[field] or ''
            if files[redirect]:
                value = stream + (' или ' + value if value else '')
            header.append('<tr><td>' + label + '</td><td>' + html.escape(value) + '</td></tr>')
    samples = []
    if visibility['showSamples']:
        for test_set in test_sets:
            if test_set['name'] != 'samples':
                continue
            for number, test in enumerate(test_set['matchedTests'], 1):
                samples.append('<h3>Пример ' + str(number) + '</h3><table><tr><th>Ввод</th><th>Вывод</th></tr><tr>')
                for field in ['inputPath', 'answerPath']:
                    samples.append('<td><pre>' + html.escape(entries[test[field]].decode('utf-8')) + '</pre></td>')
                samples.append('</tr></table>')
    page = ('<!DOCTYPE html><html lang="ru"><meta charset="utf-8"><div class="problem-statement">'
            '<div class="header"><h1 class="title">' + html.escape(config['name']) + '</h1><table>'
            + ''.join(header) + '</table></div><div class="legend">' + rendered + '</div>'
            + ''.join(samples) + '</div></html>')
    entries[statement_path] = page.encode('utf-8')
    entries[STATEMENT_DIR + '/parts.json'] = encoded_json(parts)
    entries['meta.json'] = encoded_json({'problemMetadata': metadata})
    for name, data in entries.items():
        safe_name(name)
        if data is None:
            raise PackageError(f'missing asset: {name}')
        if name.endswith('.py'):
            ast.parse(data.decode('utf-8'), filename=name)
    return entries


def main(argv=None):
    recipes = sorted(path.parent.name for path in ROOT.glob('*/import.json'))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipes', nargs='*')
    parser.add_argument('--all', action='store_true', help='select every recipe with import.json')
    parser.add_argument('--check', action='store_true', help='validate without writing ZIPs')
    parser.add_argument('--assets', type=Path, help='fallback DIR/recipe/file for missing data')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args(argv)
    if args.all and args.recipes:
        parser.error('use recipe names or --all')
    selected = recipes if args.all else list(dict.fromkeys(args.recipes))
    if not selected or any(name not in recipes for name in selected):
        parser.error('select recipes: ' + ', '.join(recipes))
    prepared = {}
    for name in selected:
        try:
            prepared[name] = prepare_problem(ROOT / name, args.assets)
            print(f'OK {name}: {len(prepared[name])} files (YANDEX)')
        except (ValueError, OSError, SyntaxError, KeyError, TypeError) as exc:
            print(f'ERROR {name}: {exc}', file=sys.stderr)
    if len(prepared) != len(selected):
        return 1
    if not args.check:
        for name, entries in prepared.items():
            destination = args.output / f'{name}.yandex.zip'
            write_zip(entries, destination)
            print(destination)
    return 0


if __name__ == '__main__':
    sys.exit(main())
