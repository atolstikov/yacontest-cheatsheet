import sqlite3


QUERY = """SELECT title From Films where duration < 90 and duration != ''
        AND genre = (Select id from genres where title='драма')
        """


def main():
    connection = sqlite3.connect(input())
    try:
        rows = connection.execute(QUERY).fetchall()
    finally:
        connection.close()
    print('\n'.join(row[0] for row in rows))


if __name__ == '__main__':
    main()
