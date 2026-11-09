"""Portable TESTLIB_EXITCODE checker for the numeric score in an output file."""
import math
from pathlib import Path
import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        print('0 expected input, output and answer paths')
        return 2
    lines = Path(argv[1]).read_text(encoding='utf-8').splitlines()
    if not lines or not lines[0].strip():
        print('0 empty output')
        return 2
    token = lines[0].strip()
    try:
        score = float(token)
    except ValueError:
        print('0 ' + token)
        return 1
    if not math.isfinite(score):
        print('0 non-finite score')
        return 1
    print(max(0.0, score))
    return 0


if __name__ == '__main__':
    sys.exit(main())
