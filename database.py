import aiosqlite


class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS economy (
            guild_id INTEGER,
            user_id INTEGER,
            balance INTEGER DEFAULT 0,
            last_daily INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS levels (
            guild_id INTEGER,
            user_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS birthdays (
            guild_id INTEGER,
            user_id INTEGER,
            month INTEGER,
            day INTEGER,
            PRIMARY KEY (guild_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY (guild_id, key)
        );

        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            created_at INTEGER
        );
        """)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def execute(self, query, params=()):
        async with self.conn.execute(query, params) as cur:
            await self.conn.commit()
            return cur

    async def fetchone(self, query, params=()):
        async with self.conn.execute(query, params) as cur:
            return await cur.fetchone()

    async def fetchall(self, query, params=()):
        async with self.conn.execute(query, params) as cur:
            return await cur.fetchall()

    async def setting(self, guild_id, key, default=None):
        row = await self.fetchone(
            "SELECT value FROM settings WHERE guild_id=? AND key=?",
            (guild_id, key)
        )
        return row["value"] if row else default

    async def set_setting(self, guild_id, key, value):
        await self.execute(
            """INSERT INTO settings(guild_id,key,value) VALUES(?,?,?)
               ON CONFLICT(guild_id,key) DO UPDATE SET value=excluded.value""",
            (guild_id, key, str(value))
        )
