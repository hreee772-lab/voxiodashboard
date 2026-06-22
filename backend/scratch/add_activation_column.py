import asyncio
import asyncpg

async def run_migration():
    db_url = "postgresql://postgres:Team%40voicera007@db.tvqpmkazbzkviyegbwtc.supabase.co:5432/postgres"
    print("Connecting to Supabase PostgreSQL using asyncpg...")
    conn = await asyncpg.connect(db_url)
    try:
        # Check if column already exists
        exists = await conn.fetchval("""
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='activation_token';
        """)
        
        if not exists:
            print("Adding column activation_token to users table...")
            await conn.execute("ALTER TABLE users ADD COLUMN activation_token TEXT;")
            print("Column added successfully!")
        else:
            print("Column activation_token already exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
