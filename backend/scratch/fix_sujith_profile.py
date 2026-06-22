import asyncio
import asyncpg

async def fix_sujith():
    db_url = "postgresql://postgres:Team%40voicera007@db.tvqpmkazbzkviyegbwtc.supabase.co:5432/postgres"
    conn = await asyncpg.connect(db_url)
    try:
        # Update users table
        user_res = await conn.execute("""
            UPDATE users 
            SET onboarding_completed = true
            WHERE email = 'sk3076239@gmail.com';
        """)
        print(f"Users table updated: {user_res}")
        
        # Get client_id
        row = await conn.fetchrow("SELECT client_id FROM users WHERE email = 'sk3076239@gmail.com';")
        if row and row['client_id']:
            client_id = row['client_id']
            # Update clients table with placeholders if needed
            client_res = await conn.execute("""
                UPDATE clients 
                SET team_size = '2-10', industry = 'Technology'
                WHERE id = $1 AND (team_size IS NULL OR industry IS NULL);
            """, client_id)
            print(f"Clients table updated: {client_res}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_sujith())
