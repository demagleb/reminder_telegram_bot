import aiosqlite
import sqlite3
from time import time

FILENAME = "reminderbot.db"


def create_db():
    con = sqlite3.connect(FILENAME)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, time INTEGER, text VARCHAR(255), period INTEGER)"
    )


class Sqliter:
    def __init__(self) -> None:
        pass

    async def insert_reminder(self, task):
        async with aiosqlite.connect(FILENAME) as con:
            await con.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?)",
                (
                    None,
                    str(task["user_id"]),
                    str(task["time"]),
                    str(task["text"]),
                    str(task["period"]),
                ),
            )
            await con.commit()

    async def select_good(self):
        curtime = str(time())
        async with aiosqlite.connect(FILENAME) as con:
            async with con.cursor() as cur:
                await cur.execute("SELECT * FROM tasks WHERE time < ?",
                                  (curtime, ))
                res = await cur.fetchall()
                await cur.execute(
                    "DELETE FROM tasks WHERE time < ? AND period == 0",
                    (curtime, ))
                res = [{
                    "id": i[0],
                    "user_id": i[1],
                    "time": i[2],
                    "text": i[3],
                    "period": i[4],
                } for i in res]
                await cur.execute(
                    "UPDATE tasks SET time = time + period WHERE time < ?",
                    (curtime, ))
                await con.commit()
                return res

    async def select_by_user(self, user_id):
        async with aiosqlite.connect(FILENAME) as con:
            async with con.cursor() as cur:
                await cur.execute("SELECT * FROM tasks WHERE user_id == ?",
                                  (user_id, ))
                res = await cur.fetchall()
                res = [{
                    "id": i[0],
                    "user_id": i[1],
                    "time": i[2],
                    "text": i[3],
                    "period": i[4],
                } for i in res]
                return res

    async def delete(self, id):
        async with aiosqlite.connect(FILENAME) as con:
            await con.execute("DELETE FROM tasks WHERE id == ?", (id, ))
            await con.commit()


if __name__ == "__main__":
    create_db()
