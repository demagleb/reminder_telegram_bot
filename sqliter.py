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
    async def __init__(self, loop) -> None:
        self.con = await aiosqlite.connect(FILENAME, loop=loop)
        self.cur = await self.con.cursor()

    async def insert_reminder(self, task):
        async with self.con:
            await self.cur.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?)",
                (
                    None,
                    str(task["user_id"]),
                    str(task["time"]),
                    str(task["text"]),
                    str(task["period"]),
                ),
            )

    async def select_good(self):
        curtime = str(time())
        async with self.con:
            await self.cur.execute("SELECT * FROM tasks WHERE time < ?", (curtime, ))
            res = await self.cur.fetchall()
            await self.cur.execute(
                "DELETE FROM tasks WHERE time < ? AND period == 0",
                (curtime, ))
            res = [{
                "id": i[0],
                "user_id": i[1],
                "time": i[2],
                "text": i[3],
                "period": i[4],
            } for i in res]
            await self.cur.execute(
                "UPDATE tasks SET time = time + period WHERE time < ?",
                (curtime, ))
            return res

    async def select_by_user(self, user_id):
        async with self.con:
            await self.cur.execute("SELECT * FROM tasks WHERE user_id == ?",
                             (user_id, ))
            res = await self.cur.fetchall()
            res = [{
                "id": i[0],
                "user_id": i[1],
                "time": i[2],
                "text": i[3],
                "period": i[4],
            } for i in res]
            return res

    async def delete(self, id):
        async with self.con:
            await self.cur.execute("DELETE FROM tasks WHERE id == ?", (id, ))

    async def commit(self):
        await self.con.commit()

    async def close(self):
        await self.con.close()


if __name__ == "__main__":
    create_db()
