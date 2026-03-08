from collections.abc import Iterable
import aiosqlite


class DB:
    def __init__(self, db_path="databases.db") -> None:
        self.db_path = db_path
        self.db: aiosqlite.Connection
    async def disconnect(self) -> None:
        if self.db:
            await self.db.close()

    async def connect(self) -> None:
        if self.db:
            return
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        await db.execute('PRAGMA journal_mode=WAL;')
        await db.execute('PRAGMA synchronous=NORMAL;')
        self.db = db

    async def execute(self, query, params=None) -> None:
        if params is None:
            params = ()
        await self.db.execute(query, params)
        await self.db.commit()

    async def fetchone(self, query, params=None) -> aiosqlite.Row | None:
        if params is None:
            params = ()
        cursor = await self.db.execute(query, params)
        row = await cursor.fetchone()
        await cursor.close()
        return row
    
    async def fetchall(self, query, params=None) -> Iterable[aiosqlite.Row] | None:
        if params is None:
            params = ()
        cursor = await self.db.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows
