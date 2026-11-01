#!/usr/bin/env python3
import sys
from datetime import datetime

# None — балл юнит-тестов без изменений.
# Чтобы включить штраф, поставьте дедлайн, например datetime(2026, 12, 1, 0, 0).
# Каждый начатый день после него умножает балл на (1 - 0.1 * дни), но не ниже половины.
DEADLINE = None


def penalize(score):
    if DEADLINE is None:
        return score
    passed = datetime.now() - DEADLINE
    days = 0 if passed.total_seconds() <= 0 else passed.days + 1
    return score * (1.0 - min(0.5, days * 0.1))


def main():
    if len(sys.argv) < 3:
        print('0 checker arguments missing')
        sys.exit(1)

    with open(sys.argv[2], encoding='utf-8') as handle:
        lines = [line.strip() for line in handle.readlines() if line.strip()]
    if not lines:
        print('0 empty output')
        sys.exit(1)

    try:
        score = penalize(float(lines[-1].split()[0]))
    except ValueError:
        print('0 cannot parse score')
        sys.exit(2)

    if score <= 0:
        print('0 Wrong answer')
        sys.exit(1)
    print(score)


if __name__ == '__main__':
    main()
