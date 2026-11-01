#!/usr/bin/env python3
import json
import sys

# Стоимость задачи. different=True — доля пройденных тестов, samples не входят.
# Для доли выключите прерывание тестирования при первой ошибке.
MAX_VALUE = 100
DIFFERENT = False


def unique_tests(tests):
    ordered = sorted(tests, key=lambda item: item.get('testName') or '')
    selected = []
    for index, test in enumerate(ordered):
        if index and test.get('testName') == ordered[index - 1].get('testName'):
            continue
        if DIFFERENT and test.get('testsetName') == 'samples':
            continue
        selected.append(test)
    return selected


def main():
    tests = unique_tests(json.load(sys.stdin).get('tests') or [])
    if not tests:
        print(0)
        return
    accepted = sum(1 for test in tests if test.get('verdict') == 'ok')
    if DIFFERENT:
        print(round(MAX_VALUE * accepted / len(tests)))
    else:
        print(MAX_VALUE if accepted == len(tests) else 0)
    print('{}/{}'.format(accepted, len(tests)))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(0)
        print(exc)
