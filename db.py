from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect('db/finance.db')
cursor = conn.cursor()


def insert(table: str, column_values: Dict) -> None:
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ', '.join('?' * len(column_values.keys()))
    cursor.executemany(
        f'INSERT INTO {table} '
        f'({columns}) '
        f'VALUES ({placeholders})',
        values
    )
    conn.commit()


def fetch_all(table: str, columns: List[str]) -> List[Tuple]:
    column_joined = ', '.join(columns)
    cursor.execute(f'SELECT {column_joined} FROM {table}')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)

    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f'DELETE FROM {table} WHERE id={row_id}')
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """DB is initialized"""
    with open('createdb.sql', encoding='utf-8') as f:
        sql = f.read()

    cursor.executescript(sql)
    conn.commit


def check_db_exists():
    """Check if DB is initialized. If not - initializes"""
    cursor.execute(
        'SELECT name FROM sqlite_master WHERE type="table" AND name="expense"'
    )
    table_exists = cursor.fetchall()
    
    if table_exists:
        return

    _init_db()
