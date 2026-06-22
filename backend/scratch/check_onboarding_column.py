import asyncio
import asyncpg

async def check_columns():
    db_url = "postgresql://postgres:Team%40voicera007@db.tvqpmkazbzkviyegbwtc.supabase.co:5432/postgres"
    print("Connecting to database...")
    conn = await asyncpg.connect(db_url)
    try:
        # Check users table columns
        users_cols = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='users';
        """)
        print("\n--- USERS TABLE COLUMNS ---")
        for col in users_cols:
            print(f"{col['column_name']}: {col['data_type']}")

        # Check clients table columns
        clients_cols = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='clients';
        """)
        print("\n--- CLIENTS TABLE COLUMNS ---")
        for col in clients_cols:
            print(f"{col['column_name']}: {col['data_type']}")
            
        # Get users and onboarding status
        users = await conn.fetch("""
            SELECT id, email, full_name, onboarding_completed, display_preference
            FROM users
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        print("\n--- RECENT USERS ---")
        for u in users:
            print(f"ID: {u['id']}, Email: {u['email']}, Name: {u['full_name']}, Onboarding Completed: {u['onboarding_completed']}, Pref: {u['display_preference']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_columns())
