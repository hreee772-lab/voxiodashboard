import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from supabase import create_client, Client

class EmailService:
    def __init__(self):
        self.from_email = "teamvoicera7@gmail.com"
        self.from_name = "Voicera Support"

    def _get_brevo_client(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        return sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    def _get_ist_time(self, utc_time_str: str) -> str:
        try:
            utc_dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
            ist_dt = utc_dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
            return ist_dt.strftime("%A, %d %B %Y at %I:%M %p IST")
        except Exception as e:
            print(f"Time conversion error: {e}")
            return utc_time_str

    def _send_email(self, to_email: str, to_name: str, subject: str, html_content: str, email_type: str):
        if not settings.BREVO_API_KEY:
            print("BREVO_API_KEY not configured")
            return
        try:
            api = self._get_brevo_client()
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={"email": self.from_email, "name": self.from_name},
                subject=subject,
                html_content=html_content
            )
            api.send_transac_email(send_smtp_email)
            print(f"Email sent [{email_type}] to {to_email}")
            self._log_email(email_type, to_email, "sent", {})
        except ApiException as e:
            print(f"Brevo error [{email_type}]: {e}")
            self._log_email(email_type, to_email, "failed", {"error": str(e)})

    def _log_email(self, email_type: str, recipient: str, status: str, metadata: dict):
        try:
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            supabase.table("email_logs").insert({
                "type": email_type,
                "recipient": recipient,
                "status": status,
                "metadata": metadata,
                "sent_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Email log error: {e}")

    async def send_booking_confirmation(self, user_name: str, user_email: str, slot_start_utc: str, issue_summary: str, ticket_id: str):
        ist_display = self._get_ist_time(slot_start_utc)
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">Your support call is confirmed</h2>
            <p>Hi {user_name},</p>
            <p>Your support call has been successfully scheduled.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;color:#666;width:140px;">Date & Time</td><td style="padding:8px;font-weight:700;">{ist_display}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px;color:#666;">Issue Topic</td><td style="padding:8px;">{issue_summary}</td></tr>
                <tr><td style="padding:8px;color:#666;">Ticket ID</td><td style="padding:8px;font-family:monospace;color:#8a4cfc;">#{ticket_id[:8].upper()}</td></tr>
            </table>
            <p>A specialist will connect with you at the scheduled time.</p>
            <p style="color:#666;font-size:12px;">Voicera Support Team</p>
        </div>
        """
        self._send_email(user_email, user_name, "Your support call is confirmed — Voicera", html_content, "booking_confirmation")

    async def send_reminder_email(self, user_name: str, user_email: str, slot_start_utc: str, issue_summary: str):
        ist_display = self._get_ist_time(slot_start_utc)
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">Your support call is in 1 hour</h2>
            <p>Hi {user_name},</p>
            <p>This is a reminder that your scheduled support call is in approximately 1 hour.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;color:#666;width:140px;">Date & Time</td><td style="padding:8px;font-weight:700;">{ist_display}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px;color:#666;">Issue Topic</td><td style="padding:8px;">{issue_summary}</td></tr>
            </table>
            <p style="color:#666;font-size:12px;">Voicera Support Team</p>
        </div>
        """
        self._send_email(user_email, user_name, "Your Voicera support call is in 1 hour", html_content, "reminder")

    async def send_no_show_email(self, user_name: str, user_email: str, issue_summary: str):
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">We missed you</h2>
            <p>Hi {user_name},</p>
            <p>We are sorry we missed you for the scheduled support call regarding <strong>{issue_summary}</strong>.</p>
            <p>Our specialist was unable to connect at the scheduled time. We apologize for the inconvenience.</p>
            <p>Please reply to this email or visit our website to book a new time that works for you.</p>
            <p>Talk soon,<br>Voicera Support Team</p>
        </div>
        """
        self._send_email(user_email, user_name, "We missed you — Rebook your Voicera support call", html_content, "no_show_notification")

    async def send_session_summary(self, user_name: str, user_email: str, issue_summary: str, session_id: str):
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">Your support session summary</h2>
            <p>Hi {user_name},</p>
            <p>Your support session has been resolved. Here is a summary:</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;color:#666;width:140px;">Issue</td><td style="padding:8px;">{issue_summary}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px;color:#666;">Status</td><td style="padding:8px;color:#22c55e;font-weight:700;">Resolved</td></tr>
                <tr><td style="padding:8px;color:#666;">Session ID</td><td style="padding:8px;font-family:monospace;color:#8a4cfc;">#{session_id[:8].upper()}</td></tr>
            </table>
            <p>If you have any further questions, feel free to reach out again.</p>
            <p style="color:#666;font-size:12px;">Voicera Support Team</p>
        </div>
        """
        self._send_email(user_email, user_name, "Your support session summary — Voicera", html_content, "session_summary")

    async def send_invite_email(self, to_email: str, to_name: str, company_name: str, invited_by: str, invite_link: str = ""):
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">You have been invited to Voicera</h2>
            <p>Hi {to_name},</p>
            <p><strong>{invited_by}</strong> has invited you to join <strong>{company_name}</strong> on Voicera — an AI-powered customer support platform.</p>
            <p>Voicera helps your team handle customer queries automatically with AI and escalates to specialists when needed.</p>
            <a href="{invite_link or 'https://voicera-dashboard.teamvoicera7.workers.dev/login'}"
               style="display:inline-block;background:linear-gradient(135deg,#8a4cfc,#bd9dff);color:#fff;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;margin:16px 0;">
                Accept Invitation
            </a>
            <p style="color:#666;font-size:12px;">If you did not expect this invitation you can ignore this email.</p>
            <p>Voicera Support Team</p>
        </div>
        """
        self._send_email(to_email, to_name, f"You have been invited to join {company_name} on Voicera", html_content, "invite")

    async def send_activation_email(self, to_email: str, to_name: str, activation_link: str):
        html_content = f"""
        <div style="font-family:sans-serif;line-height:1.6;color:#333;max-width:500px;margin:0 auto;">
            <h2 style="color:#8a4cfc;">Activate your Voicera account</h2>
            <p>Hi {to_name},</p>
            <p>Thank you for signing up for Voicera! To confirm your email address and activate your account, please click the button below:</p>
            <a href="{activation_link}"
               style="display:inline-block;background:linear-gradient(135deg,#8a4cfc,#bd9dff);color:#fff;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;margin:16px 0;text-align:center;">
                Activate Account
            </a>
            <p>If the button doesn't work, you can copy and paste the following link into your browser:</p>
            <p style="word-break:break-all;font-size:12px;color:#8a4cfc;">{activation_link}</p>
            <p style="color:#666;font-size:12px;">If you did not sign up for Voicera, you can safely ignore this email.</p>
            <p>Voicera Support Team</p>
        </div>
        """
        self._send_email(to_email, to_name, "Activate your Voicera account", html_content, "activation")

email_service = EmailService()

async def send_booking_email(
    to_email: str,
    to_name: str,
    customer_name: str,
    customer_email: str,
    slot_start: str,
    meet_link: str,
    is_specialist: bool
):
    try:
        # Format the datetime
        dt = datetime.fromisoformat(slot_start.replace('Z', '+00:00'))
        formatted_time = dt.strftime('%A, %B %d %Y at %I:%M %p IST')
        
        if is_specialist:
            subject = f"New Support Call Scheduled - {customer_name}"
            html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                <h2 style="color:#6D28D9;">New Support Call Scheduled</h2>
                <p>Hi {to_name},</p>
                <p>A customer has scheduled a support call with you.</p>
                <div style="background:#f8f4ff;border-radius:8px;padding:16px;margin:20px 0;">
                    <p><strong>Customer:</strong> {customer_name} ({customer_email})</p>
                    <p><strong>Time:</strong> {formatted_time}</p>
                    {'<p><strong>Google Meet:</strong> <a href="' + meet_link + '">' + meet_link + '</a></p>' if meet_link else ''}
                </div>
                <p>Please be available at the scheduled time.</p>
                <p>— Voicera Team</p>
            </div>
            """
        else:
            subject = "Your Support Call is Confirmed"
            html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                <h2 style="color:#6D28D9;">Support Call Confirmed ✓</h2>
                <p>Hi {customer_name},</p>
                <p>Your support call has been successfully scheduled.</p>
                <div style="background:#f8f4ff;border-radius:8px;padding:16px;margin:20px 0;">
                    <p><strong>Time:</strong> {formatted_time}</p>
                    {'<p><strong>Join via Google Meet:</strong> <a href="' + meet_link + '" style="color:#6D28D9;">' + meet_link + '</a></p>' if meet_link else ''}
                </div>
                <p>A specialist will join you at the scheduled time. Please be ready.</p>
                <p>— Voicera Support Team</p>
            </div>
            """

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": to_name}],
            sender={"name": "Voicera Support", "email": "support@voicera.ai"},
            subject=subject,
            html_content=html
        )
        api_instance.send_transac_email(send_smtp_email)
    except Exception as e:
        print(f"Send booking email error: {e}")
