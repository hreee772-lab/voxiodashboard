import asyncio
import asyncpg

async def check_onboarded():
    db_url = "postgresql://postgres:Team%40voicera007@db.tvqpmkazbzkviyegbwtc.supabase.co:5432/postgres"
    conn = await asyncpg.connect(db_url)
    try:
        users = await conn.fetch("""
            SELECT id, email, onboarding_completed, display_preference
            FROM users
            WHERE onboarding_completed = true
            LIMIT 10;
        """)
        print("\n--- ONBOARDED USERS ---")
        for u in users:
            print(f"ID: {u['id']}, Email: {u['email']}, Onboarding Completed: {u['onboarding_completed']}, Pref: {u['display_preference']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_onboarded())
