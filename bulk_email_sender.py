"""
Bulk Email Sender (Gmail SMTP)
==============================

Send personalized bulk emails through Gmail's SMTP server using an
App Password. Includes dry-run mode, per-recipient message count,
rate limiting, and dual logging.

SETUP
-----
1. Enable 2-Step Verification on your Google account.
2. Create an App Password: https://myaccount.google.com/apppasswords
   (Regular Gmail passwords will NOT work with smtplib.)
3. Set environment variables:

   Linux/macOS:
       export GMAIL_ADDRESS="you@gmail.com"
       export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

   Windows (PowerShell):
       $env:GMAIL_ADDRESS="you@gmail.com"
       $env:GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

   Never hardcode credentials in the script.

4. Edit RECIPIENTS, SUBJECT, and BODY_TEMPLATE below.
5. Run:  python bulk_email_sender.py
   DRY_RUN is True by default — set it to False when ready to send.

RESPONSIBLE USE
---------------
- Only email people who opted in.
- Include a clear unsubscribe method.
- Respect Gmail's limits (~500/day personal, ~2000/day Workspace).
- Unsolicited bulk mail risks account suspension and may violate
  anti-spam laws (CAN-SPAM, GDPR, CASL).
"""

import os
import smtplib
import ssl
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 


GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")


RECIPIENTS = [
    {"email": "person1@example.com", "name": "Alex", "count": 1},
    {"email": "person2@example.com", "name": "Sam", "count": 2},
    {"email": "person3@example.com", "name": "Jamie", "count": 1},
]

SUBJECT = "Subject of your message"

BODY_TEMPLATE = """\
Hi {name},

This is the body of your email. Replace this text with your real message.

If you no longer wish to receive these emails, just reply with "unsubscribe"
and you will be removed from the list.

Thanks,
Your Name
"""

DELAY_BETWEEN_EMAILS_SECONDS = 2
DRY_RUN = True  # Set to False to actually send

LOG_FILE = "bulk_email_log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)


def build_message(to_email: str, name: str, index: int = 1) -> MIMEMultipart:
    """Build a single email message.

    `index` is appended to the subject and body so that multiple copies
    sent to the same address look distinct (reduces spam classification).
    """
    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = f"{SUBJECT} ({index})"

    body = BODY_TEMPLATE.format(name=name or "there")
    body += f"\n\n(Message {index})"
    msg.attach(MIMEText(body, "plain"))
    return msg


def send_all():
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logging.error(
            "Missing credentials. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD "
            "environment variables before running."
        )
        return

    if not RECIPIENTS:
        logging.error("RECIPIENTS list is empty — nothing to send.")
        return

    sent, failed = 0, 0
    total_messages = sum(r.get("count", 1) for r in RECIPIENTS)

    if DRY_RUN:
        logging.info("=== DRY RUN MODE — no emails will actually be sent ===")
        for r in RECIPIENTS:
            count = r.get("count", 1)
            logging.info(
                f"[DRY RUN] Would send {count} message(s) to {r['email']}"
            )
        logging.info(
            f"Dry run complete. {total_messages} message(s) would have been sent "
            f"to {len(RECIPIENTS)} recipient(s). Set DRY_RUN = False to actually send."
        )
        return

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

            for r in RECIPIENTS:
                to_email = r["email"]
                name = r.get("name", "")
                count = r.get("count", 1)

                for i in range(count):
                    try:
                        msg = build_message(to_email, name, index=i + 1)
                        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
                        logging.info(f"Sent to {to_email} ({i + 1}/{count})")
                        sent += 1
                    except smtplib.SMTPException as e:
                        logging.error(
                            f"Failed to send to {to_email} ({i + 1}/{count}): {e}"
                        )
                        failed += 1

                    time.sleep(DELAY_BETWEEN_EMAILS_SECONDS)

    except smtplib.SMTPAuthenticationError:
        logging.error(
            "Authentication failed. Check GMAIL_ADDRESS / GMAIL_APP_PASSWORD "
            "and make sure you're using an App Password, not your normal password."
        )
        return
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return

    logging.info(f"Done. Sent: {sent}, Failed: {failed}, Total: {total_messages}")


if __name__ == "__main__":
    logging.info(f"Starting bulk email run at {datetime.now().isoformat()}")
    send_all()
