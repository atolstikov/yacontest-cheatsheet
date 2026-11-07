import sqlite3


def get_result(name):
    with sqlite3.connect(name) as connection:
        connection.execute(
            "DELETE FROM films WHERE duration % 2 = 0 "
            "AND genre = (SELECT id FROM genres WHERE title = 'боевик')"
        )
        connection.commit()
