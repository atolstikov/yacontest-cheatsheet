"""Build reproducible Contest upload ZIPs using explicit recipe manifests."""
import argparse
import ast
import json
from pathlib import Path, PurePosixPath
import os
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ROLES = ('compile', 'runtime', 'checker', 'postprocessor')
BINARY_SUFFIXES = {'.db', '.sqlite', '.zip', '.png', '.jpg', '.pdf'}


class PackageError(ValueError):
    pass


def safe_name(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise PackageError(f'invalid relative path: {name!r}')
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {'.', '..'} or ':' in part for part in name.split('/')):
        raise PackageError(f'unsafe relative path: {name!r}')
    if any(not part for part in name.split('/')):
        raise PackageError(f'empty path component: {name!r}')
    return name


def read_asset(directory, name):
    name = safe_name(name)
    source = directory / name
    if not source.is_file():
        return None
    if not source.resolve().is_relative_to(directory.resolve()):
        raise PackageError(f'asset escapes recipe directory: {name}')
    return source.read_bytes()


def prepare(recipe, assets=None):
    config = json.loads((recipe / 'package.json').read_text(encoding='utf-8'))
    required = []
    for role in ROLES:
        values = config[role]
        if not isinstance(values, list):
            raise PackageError(f'{role} must be a list')
        required.extend(values)
    if not config['tests']:
        raise PackageError('at least one test is required')
    if len(config['tests']) != len(set(config['tests'])):
        raise PackageError('duplicate test names')
    required.extend(f'tests/{name}{suffix}' for name in config['tests'] for suffix in ('', '.a'))
    expected_tests = {f'{name}{suffix}' for name in config['tests'] for suffix in ('', '.a')}
    actual_tests = {p.relative_to(recipe / 'tests').as_posix() for p in (recipe / 'tests').rglob('*') if p.is_file()}
    extras = actual_tests - expected_tests
    if extras:
        raise PackageError('unlisted test files: ' + ', '.join(sorted(extras)))
    rename = config.get('rename', {})
    unknown = set(rename) - set(required)
    if unknown:
        raise PackageError('rename refers to unlisted files: ' + ', '.join(sorted(unknown)))
    entries = {}
    missing = []
    for name in dict.fromkeys(required):
        safe_name(name)
        data = read_asset(recipe, name)
        if data is None and assets is not None:
            data = read_asset(assets / recipe.name, name)
        if data is None:
            missing.append(name)
            continue
        target = safe_name(rename.get(name, name))
        if target in entries:
            raise PackageError(f'duplicate ZIP path: {target}')
        if Path(name).suffix not in BINARY_SUFFIXES:
            text = data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
            if Path(name).suffix == '.py':
                ast.parse(text, filename=name)
            data = text.encode('utf-8')
        entries[target] = data
    if missing:
        raise PackageError('missing files: ' + ', '.join(missing) + '; supply them under --assets DIR/' + recipe.name)
    return entries


def write_zip(entries, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.zip', delete=False) as file:
            temporary = Path(file.name)
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in sorted(entries.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                executable = name.endswith('.sh') or name == 'check_py'
                info.external_attr = (0o100755 if executable else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compresslevel=9)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    recipes = sorted(path.parent.name for path in ROOT.glob('*/package.json'))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipes', nargs='*', choices=recipes)
    parser.add_argument('--all', action='store_true', help='select all recipes with package.json')
    parser.add_argument('--check', action='store_true', help='validate without writing archives')
    parser.add_argument('--assets', type=Path, help='fallback DIR/recipe/file for missing local data')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args(argv)
    if args.all and args.recipes:
        parser.error('use recipe names or --all')
    selected = recipes if args.all else args.recipes
    if not selected:
        parser.error('specify at least one recipe or --all')
    prepared = {}
    for name in dict.fromkeys(selected):
        try:
            prepared[name] = prepare(ROOT / name, args.assets)
            print(f'OK {name}: {len(prepared[name])} files')
        except (ValueError, OSError, SyntaxError, KeyError, TypeError) as exc:
            print(f'ERROR {name}: {exc}', file=sys.stderr)
    if len(prepared) != len(set(selected)):
        return 1
    if not args.check:
        for name, entries in prepared.items():
            destination = args.output / f'{name}.zip'
            write_zip(entries, destination)
            print(destination)
    return 0


if __name__ == '__main__':
    sys.exit(main())
