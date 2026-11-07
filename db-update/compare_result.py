import sqlite3
import sys
from pathlib import Path


ALLOWED = {'films.db', 'films1.db', 'films2.db'}
QUERY = """DELETE FROM films WHERE duration % 2 = 0
           AND genre = (SELECT id FROM genres WHERE title = 'боевик')"""


def main():
    db_name = Path(sys.argv[1]).read_text(encoding='utf-8').strip()
    if db_name not in ALLOWED:
        raise ValueError('unknown database')
    with sqlite3.connect(db_name) as source:
        expected = sqlite3.connect(':memory:')
        source.backup(expected)
    expected.execute(QUERY)
    actual = sqlite3.connect(':memory:')
    actual.executescript(Path(sys.argv[2]).read_text(encoding='utf-8'))
    try:
        for table in ['Films', 'genres']:
            query = f'SELECT * FROM {table} ORDER BY id'
            if actual.execute(query).fetchall() != expected.execute(query).fetchall():
                print(f'wrong answer: table {table} differs')
                return 1
        print('database is correct')
        return 0
    finally:
        expected.close()
        actual.close()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'cannot check database: {exc}')
        sys.exit(1)
