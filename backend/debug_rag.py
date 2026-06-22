import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

from app.services.bot_service import bot_service
from app.core.database import SessionLocal

async def test():
    try:
        async with SessionLocal() as db:
            print("Running bot_service.get_bot_response...")
            res = await bot_service.get_bot_response(
                db=db, 
                client_id='70d0188f-ef36-4c79-b0b6-b215e767d859', 
                user_message='What is Geniffy privacy policy?'
            )
            print("RESULT:", res)
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
