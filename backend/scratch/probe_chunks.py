import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from openai import OpenAI
from dotenv import load_dotenv

async def run():
    sys.stdout.reconfigure(encoding='utf-8')
    load_dotenv()
    
    # Use direct connection if possible, or fail gracefully
    try:
        engine = create_async_engine(os.getenv('DATABASE_URL'))
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        query = "What is Geniffy's privacy policy?"
        print(f"Searching for: {query}")
        
        response = openai_client.embeddings.create(
            input=[query],
            model='text-embedding-3-small'
        )
        embedding = response.data[0].embedding
        
        sql = text("""
            SELECT content, document_id 
            FROM kb_chunks 
            WHERE client_id = :cid 
            ORDER BY embedding <=> CAST(:emb AS vector) 
            LIMIT 5
        """)
        
        async with engine.connect() as conn:
            result = await conn.execute(sql, {
                'cid': '70d0188f-ef36-4c79-b0b6-b215e767d859',
                'emb': str(embedding)
            })
            rows = result.fetchall()
            for i, r in enumerate(rows):
                print(f"\nCHUNK {i} (Doc: {r[1]}):")
                print(r[0])
                print("-" * 40)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run())
