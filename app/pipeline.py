import asyncio
from datetime import datetime
from app.gmail_client import fetch_tldr_emails
from app.summarizer import summarize_email
from app.whatsapp_sender import send_whatsapp_message
from app.logger import get_logger

logger = get_logger(__name__)

# Maps sender email to display name
SENDER_DISPLAY_NAMES = {
    "dan@tldrnewsletter.com": "TLDR",
    "morning@finshots.in": "Finshots",
}


def _get_source_label(sender: str) -> str:
    """
    Returns display name for a sender email.
    Falls back to the raw sender if not mapped.
    """
    return SENDER_DISPLAY_NAMES.get(sender, sender)


async def run_tldr_pipeline() -> None:
    """
    Main pipeline:
    1. Fetch emails from all configured senders (last 24hrs)
    2. Summarize each with OpenAI
    3. Send summary to Telegram
    """
    logger.info("pipeline starting run_at=%s", datetime.now().isoformat())

    # 1. Fetch emails
    try:
        emails = fetch_tldr_emails()
    except Exception as e:
        logger.error("pipeline failed at gmail fetch error=%s", str(e))
        return

    if not emails:
        logger.info("pipeline no new emails found skipping")
        return

    logger.info("pipeline fetched emails count=%s", len(emails))

    # 2 & 3. Summarize and send each email
    for email in emails:
        subject = email["subject"]
        sender = email.get("sender", "")
        source = _get_source_label(sender)

        logger.info(
            "pipeline processing email source=%s subject=%s",
            source, subject,
        )

        try:
            summary = summarize_email(subject=subject, body=email["body"])
        except Exception as e:
            logger.error(
                "pipeline summarization failed source=%s subject=%s error=%s",
                source, subject, str(e),
            )
            continue

        # Format message with source label
        message = (
            f"📰 *{source}* — {email['date']}\n\n"
            f"{summary}"
        )

        try:
            sent = await send_whatsapp_message(message)
            if sent:
                logger.info(
                    "pipeline message sent successfully source=%s subject=%s",
                    source, subject,
                )
            else:
                logger.warning(
                    "pipeline message send failed source=%s subject=%s",
                    source, subject,
                )
        except Exception as e:
            logger.error(
                "pipeline send failed source=%s subject=%s error=%s",
                source, subject, str(e),
            )

    logger.info("pipeline completed run_at=%s", datetime.now().isoformat())