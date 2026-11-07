import shutil
import sqlite3
import tempfile
from pathlib import Path

from solution import get_result


name = input().strip()
if name not in {'films.db', 'films1.db', 'films2.db'}:
    raise ValueError('unknown database')
with tempfile.TemporaryDirectory(dir='.') as directory:
    writable = Path(directory) / name
    shutil.copyfile(name, writable)
    get_result(str(writable))
    with sqlite3.connect(writable) as connection:
        with open('output.txt', 'w', encoding='utf-8') as output:
            for line in connection.iterdump():
                output.write(line + '\n')
