import sqlite3


if __name__ == '__main__':
    con = sqlite3.connect(input())
    cur = con.cursor()
    result = cur.execute(
        """SELECT title From Films where duration < 90
        AND genre = (Select id from genres where title='драма')
        """
    ).fetchall()
    con.close()
    print("\n".join(map(lambda item: item[0], result)))
