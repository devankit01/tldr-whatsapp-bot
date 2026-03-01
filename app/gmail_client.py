import imaplib
import email
import os
from email.header import decode_header
from datetime import datetime, timedelta
from app.logger import get_logger

logger = get_logger(__name__)

# Add more senders here anytime
SENDERS = [
    os.getenv("TLDR_SENDER", "dan@tldrnewsletter.com"),
    "morning@finshots.in",
]


def _fetch_emails_from_sender(
    mail: imaplib.IMAP4_SSL,
    sender: str,
    since_date: str,
    max_results: int,
) -> list[dict]:
    """
    Fetches UNREAD emails from a single sender since given date.
    Marks each as read after fetching.
    """
    status, messages = mail.search(
        None, f'(UNSEEN FROM "{sender}" SINCE "{since_date}")'
    )

    if status != "OK" or not messages[0]:
        logger.info("gmail no unread emails found sender=%s since=%s", sender, since_date)
        return []

    email_ids = messages[0].split()
    logger.info("gmail found %s unread emails sender=%s", len(email_ids), sender)

    # take latest N
    email_ids = email_ids[-max_results:]

    emails = []
    for email_id in reversed(email_ids):
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        date = msg.get("Date", "Unknown")

        # extract plain text body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # mark as read immediately after fetching
        mail.store(email_id, "+FLAGS", "\\Seen")
        logger.info(
            "gmail fetched and marked read sender=%s subject=%s date=%s body_length=%s",
            sender, subject, date, len(body),
        )

        emails.append({
            "sender": sender,
            "subject": subject,
            "date": date,
            "body": body,
        })

    return emails


def fetch_tldr_emails(max_results: int = 15) -> list[dict]:
    """
    Fetches UNREAD emails from all configured senders in last 24 hours.
    Marks each as read after fetching — safe to run multiple times, no duplicates.
    """
    gmail_email = os.getenv("GMAIL_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

    logger.info(
        "gmail connecting via IMAP email=%s since=%s senders=%s",
        gmail_email, since_date, SENDERS,
    )

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_email, app_password)
        mail.select("inbox")
        logger.info("gmail connected successfully")
    except Exception as e:
        logger.error("gmail IMAP connection failed error=%s", str(e))
        raise

    # fetch from all senders
    all_emails = []
    for sender in SENDERS:
        try:
            emails = _fetch_emails_from_sender(mail, sender, since_date, max_results)
            all_emails.extend(emails)
        except Exception as e:
            logger.error("gmail failed to fetch sender=%s error=%s", sender, str(e))
            continue

    mail.logout()
    logger.info(
        "gmail disconnected total_fetched=%s from %s senders",
        len(all_emails), len(SENDERS),
    )
    return all_emails