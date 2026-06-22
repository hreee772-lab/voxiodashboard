import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.celery_app import celery_app
from app.core.database import async_session
from app.services.email_service import email_service

def run_async(coro):
    """Helper to run async coroutines in sync Celery tasks."""
    return asyncio.run(coro)

@celery_app.task
def send_reminders():
    """Runs every 10 minutes to send call reminders."""
    return run_async(_send_reminders())

async def _send_reminders():
    now = datetime.now(timezone.utc)
    # Window: 50 to 70 minutes ahead
    window_start = now + timedelta(minutes=50)
    window_end = now + timedelta(minutes=70)

    sent_count = 0
    async with async_session() as db:
        try:
            query = text("""
                SELECT id, user_name, user_email, slot_start, issue_summary
                FROM bookings
                WHERE status = 'confirmed'
                  AND reminder_sent = false
                  AND slot_start >= :window_start
                  AND slot_start <= :window_end
            """)
            
            result = await db.execute(query, {
                "window_start": window_start,
                "window_end": window_end
            })
            
            bookings = result.fetchall()
            
            for b in bookings:
                try:
                    # Convert to string if it's a datetime object
                    slot_start_str = b.slot_start.isoformat() if hasattr(b.slot_start, 'isoformat') else str(b.slot_start)
                    
                    await email_service.send_reminder_email(
                        user_name=b.user_name,
                        user_email=b.user_email,
                        slot_start_utc=slot_start_str,
                        issue_summary=b.issue_summary
                    )
                    
                    update_query = text("""
                        UPDATE bookings
                        SET reminder_sent = true
                        WHERE id = :id
                    """)
                    await db.execute(update_query, {"id": b.id})
                    await db.commit()
                    sent_count += 1
                except Exception as e:
                    print(f"Error sending reminder for booking {b.id}: {e}")
                    await db.rollback()
        except Exception as e:
            print(f"DATABASE ERROR in send_reminders: {e}")

    print(f"Sent {sent_count} reminders.")
    return sent_count

@celery_app.task
def check_no_shows():
    """Runs every 5 minutes to detect and handle no-shows."""
    return run_async(_check_no_shows())

async def _check_no_shows():
    now = datetime.now(timezone.utc)
    # No-show threshold: slot_end < now - 15 minutes
    threshold = now - timedelta(minutes=15)

    no_show_count = 0
    async with async_session() as db:
        try:
            query = text("""
                SELECT id, session_id, user_name, user_email, issue_summary
                FROM bookings
                WHERE status = 'confirmed'
                  AND slot_end < :threshold
            """)
            
            result = await db.execute(query, {"threshold": threshold})
            bookings = result.fetchall()
            
            for b in bookings:
                try:
                    # 1. Update bookings status
                    update_booking = text("""
                        UPDATE bookings
                        SET status = 'no_show'
                        WHERE id = :id
                    """)
                    await db.execute(update_booking, {"id": b.id})
                    
                    # 2. Update related ticket status
                    update_ticket = text("""
                        UPDATE tickets
                        SET status = 'no_show'
                        WHERE session_id = :session_id
                    """)
                    await db.execute(update_ticket, {"session_id": b.session_id})
                    
                    # 3. Send no-show email
                    await email_service.send_no_show_email(
                        user_name=b.user_name,
                        user_email=b.user_email,
                        issue_summary=b.issue_summary
                    )
                    
                    await db.commit()
                    no_show_count += 1
                except Exception as e:
                    print(f"Error processing no-show for booking {b.id}: {e}")
                    await db.rollback()
        except Exception as e:
            print(f"DATABASE ERROR in check_no_shows: {e}")

    print(f"Detected {no_show_count} no-shows.")
    return no_show_count
