import asyncio
from sqlalchemy import text
from app.core.database import engine

async def cleanup():
    async with engine.connect() as conn:
        print("Cleaning up 'demo-client' data...")
        
        # Delete chunks
        res1 = await conn.execute(text("DELETE FROM kb_chunks WHERE client_id = 'demo-client'"))
        print(f"  Deleted {res1.rowcount} chunks.")
        
        # Delete documents
        res2 = await conn.execute(text("DELETE FROM kb_documents WHERE client_id = 'demo-client'"))
        print(f"  Deleted {res2.rowcount} documents.")
        
        await conn.commit()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(cleanup())
