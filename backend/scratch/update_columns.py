import asyncio
from app.core.database import async_session
from sqlalchemy import text

async def main():
    async with async_session() as session:
        print("Running SQL ALTER TABLE statements...")
        
        sqls = [
            "ALTER TABLE bot_config ADD COLUMN IF NOT EXISTS escalation_keywords TEXT;",
            "ALTER TABLE bot_config ADD COLUMN IF NOT EXISTS voice_greeting TEXT;",
            "ALTER TABLE bot_config ADD COLUMN IF NOT EXISTS chat_greeting TEXT;",
            "ALTER TABLE bot_config ADD COLUMN IF NOT EXISTS response_format TEXT;"
        ]
        
        for sql in sqls:
            await session.execute(text(sql))
        await session.commit()
        print("SQL executed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
