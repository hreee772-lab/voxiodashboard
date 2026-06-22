import asyncio
import asyncpg

async def check_user():
    db_url = "postgresql://postgres:Team%40voicera007@db.tvqpmkazbzkviyegbwtc.supabase.co:5432/postgres"
    conn = await asyncpg.connect(db_url)
    try:
        row = await conn.fetchrow("""
            SELECT u.id, u.email, u.full_name, u.onboarding_completed, u.display_preference,
                   c.id as client_id, c.company_name, c.team_size, c.industry
            FROM users u
            JOIN clients c ON u.client_id = c.id
            WHERE u.email = 'sk3076239@gmail.com';
        """)
        if row:
            print("\n--- USER PROFILE IN DB ---")
            for k, v in row.items():
                print(f"{k}: {v}")
        else:
            print("User not found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_user())
