import imaplib
import email
import os
from email.header import decode_header
from datetime import datetime, timedelta
from app.logger import get_logger

logger = get_logger(__name__)


def fetch_tldr_emails(max_results: int = 10) -> list[dict]:
    """
    Fetches TLDR emails from the last 24 hours via IMAP.
    Marks each fetched email as read.
    """
    gmail_email = os.getenv("GMAIL_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    sender = os.getenv("TLDR_SENDER", "dan@tldrnewsletter.com")

    # Last 24 hours date filter (IMAP uses DD-Mon-YYYY format)
    since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

    logger.info(
        "gmail connecting via IMAP email=%s since=%s", gmail_email, since_date
    )

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_email, app_password)
        mail.select("inbox")
        logger.info("gmail connected successfully")

    except Exception as e:
        logger.error("gmail IMAP connection failed error=%s", str(e))
        raise

    # Search emails from TLDR sender since yesterday
    status, messages = mail.search(
        None, f'(FROM "{sender}" SINCE "{since_date}")'
    )

    if status != "OK" or not messages[0]:
        logger.warning("gmail no TLDR emails found in last 24 hours")
        mail.logout()
        return []

    email_ids = messages[0].split()
    logger.info("gmail found %s TLDR emails in last 24 hours", len(email_ids))

    # Take latest N
    email_ids = email_ids[-max_results:]

    emails = []
    for email_id in reversed(email_ids):
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        date = msg.get("Date", "Unknown")

        # Extract plain text body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # Mark as read
        mail.store(email_id, "+FLAGS", "\\Seen")
        logger.info(
            "gmail marked as read subject=%s date=%s body_length=%s",
            subject, date, len(body)
        )

        emails.append({
            "subject": subject,
            "date": date,
            "body": body,
        })

    mail.logout()
    logger.info("gmail disconnected fetched=%s emails", len(emails))
    return emails