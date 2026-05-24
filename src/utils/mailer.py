import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config import settings
from src.utils.logger import log_email, log_success, log_error, log_warning

def send_email(
    job: dict,
    ranked_text: str,
    resume_path: str,
    cover_path: str,
    cold_msg_path: str,
    interview_path: str
) -> None:
    """Sends a summary email to Adithya's inbox with the top picks and 4 tailored application files."""
    log_email("Preparing application package email to send via Gmail...")

    if not settings.SENDER_APP_PASSWORD:
        log_error("No SMTP app password found!")
        log_warning("Please configure SENDER_APP_PASSWORD in your .env file to enable email delivery.")
        return

    # Construct MIMEMultipart email structure
    msg = MIMEMultipart()
    msg["Subject"] = f"🚀 ML Internship Alert — {job['title']} at {job['company']} [{job['source']}] | {job['location']}"
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = settings.RECEIVER_EMAIL

    body = f"""Hey Adithya! 👋

Your ML Engineer internship pipeline found fresh opportunities!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TOP MATCH THIS RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Platform : {job.get('source', 'Check listing')}
Role     : {job.get('title', 'Check listing')}
Company  : {job.get('company', 'Check listing')}
Location : {job.get('location', 'Check listing')}
Mode     : {job.get('mode', 'Check listing')}
Stipend  : {job.get('stipend', 'Check listing')}
Duration : {job.get('duration', 'N/A')}
Apply at : {job.get('url', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI TOP PICKS & ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ranked_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📎 ATTACHED FILES (4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ATS-Optimized Resume PDF   → Upload directly to job portals
2. Custom Cover Letter PDF    → Attach to application
3. Cold Message + HR Finder   → Send on LinkedIn TODAY
4. Interview Prep Guide       → Study before every call

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ YOUR ACTION PLAN TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Apply to top match right now
2. Find HR on LinkedIn using the cold message file
3. Send 10 cold messages today using the template
4. Apply to remaining 2 AI picks before end of day

Apply within 24 hours — early applicants always win!
You got this Adithya! 💪

Platforms: Internshala + LinkedIn + Indeed + Naukri + Wellfound + Unstop + HackerEarth
Locations: Hyderabad + Remote + Bangalore
Powered by Ollama (Free Local AI) | Zero Cost | Rs.0 Forever
"""
    msg.attach(MIMEText(body, "plain"))

    # Attach the four generated files
    attachments = [resume_path, cover_path, cold_msg_path, interview_path]
    attached_count = 0
    
    for filepath in attachments:
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(filepath)}"
                )
                msg.attach(part)
                attached_count += 1
            except Exception as ex:
                log_warning(f"Could not attach file {os.path.basename(filepath)}: {ex}")

    log_email(f"Attached {attached_count} tailored files to message.")

    # Dispatch via SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.SENDER_EMAIL, settings.SENDER_APP_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, settings.RECEIVER_EMAIL, msg.as_string())
        log_success("Email sent with all 4 attachments successfully!")
    except Exception as e:
        log_error(f"Email delivery failed: {e}")
        log_warning("Troubleshooting tips: Go to myaccount.google.com -> Security -> App Passwords and generate a 16-character code.")
