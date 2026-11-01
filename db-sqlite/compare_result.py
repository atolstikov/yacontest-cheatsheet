#!/usr/bin/env python3
import sqlite3
import sys
from urllib.parse import quote

OK = 0
WA = 1
PE = 2
CHECKER_FAILED = 3

QUERY = """SELECT title From Films where duration < 90 and duration != ''
        AND genre = (Select id from genres where title='драма')
        """


def author(db_name):
    uri = 'file:{}?mode=ro'.format(quote(db_name))
    connection = sqlite3.connect(uri, uri=True)
    try:
        rows = connection.execute(QUERY).fetchall()
    finally:
        connection.close()
    return [row[0] for row in rows]


def main():
    if len(sys.argv) < 4:
        print('PE')
        print('checker expects input, output and answer paths')
        sys.exit(PE)

    try:
        db_name = open(sys.argv[1], encoding='utf-8').read().strip()
        user_result = [
            line.strip()
            for line in open(sys.argv[2], encoding='utf-8').read().splitlines()
            if line.strip()
        ]
    except UnicodeError as exc:
        print('PE')
        print(exc)
        sys.exit(PE)

    try:
        author_result = author(db_name)
    except sqlite3.Error as exc:
        print('checker failed')
        print(exc)
        sys.exit(CHECKER_FAILED)

    if user_result == author_result:
        print('OK')
        sys.exit(OK)

    print('WA')
    print('expected {} lines, found {}'.format(len(author_result), len(user_result)))
    sys.exit(WA)


if __name__ == '__main__':
    main()
