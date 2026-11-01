#!/usr/bin/env python3
import json
import sys


def test_score(test):
    score = test.get('score') or {}
    if 'doubleScore' in score:
        return float(score['doubleScore'])
    if 'longScore' in score:
        return float(score['longScore'])
    return 0.0


def main():
    # json.load, not json.loads(input()): the documented payload is several lines.
    tests = json.load(sys.stdin).get('tests') or []
    seen = set()
    total = 0.0
    lines = []
    for test in tests:
        name = test.get('testName')
        if name in seen:
            continue
        seen.add(name)
        value = test_score(test) if test.get('verdict') == 'ok' else 0.0
        total += value
        lines.append('{} {} {}'.format(name, test.get('verdict'), value))
    print(total)
    if lines:
        print('\n'.join(lines))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(0)
        print(exc)
