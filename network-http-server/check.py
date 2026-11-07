import subprocess
import sys


result = subprocess.run([
    sys.executable, '-m', 'flake8', '--jobs=1', '--select=E',
    '--ignore=W,E126', '--max-line-length=121', 'solution.py',
], check=False)
if result.returncode:
    print('Код не соответствует стандарту PEP8\nили в нем есть синтаксические ошибки')
    sys.exit(result.returncode)
