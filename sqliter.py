import sqlite3
from time import time


FILENAME = 'reminderbot.db'


def create_db():
    con = sqlite3.connect(FILENAME)
    cur = con.cursor()
    cur.execute(
        'CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, time INTEGER, text VARCHAR(255), period INTEGER)')
class Sqliter:
    def __init__(self) -> None:
        self.con = sqlite3.connect(FILENAME)
        self.cur = self.con.cursor()
    def insert_reminder(self, task):
        with self.con:
            self.cur.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?)', (None, str(
                task['user_id']), str(task['time']), str(task['text']), str(task['period'])))

    def select_good(self):
        curtime = str(time())
        with self.con:
            self.cur.execute('SELECT * FROM tasks WHERE time < ?', (curtime,))
            res = self.cur.fetchall()
            self.cur.execute(
                'DELETE FROM tasks WHERE time < ? AND period == 0', (curtime,))
            res = [{'id': i[0], 'user_id': i[1], 'time': i[2], 'text': i[3], 'period': i[4]}
                   for i in res]
            self.cur.execute(
                'UPDATE tasks SET time = time + period WHERE time < ?', (curtime,))
            return res

    def select_by_user(self, user_id):
        with self.con:
            self.cur.execute(
                'SELECT * FROM tasks WHERE user_id == ?', (user_id,))
            res = self.cur.fetchall()
            res = [{'id': i[0], 'user_id': i[1], 'time': i[2], 'text': i[3], 'period': i[4]}
                   for i in res]
            return res
    def delete(self, id):
        with self.con:
            self.cur.execute('DELETE FROM tasks WHERE id == ?', (id,))
    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()


if __name__ == '__main__':
    create_db()
