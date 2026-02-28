import asyncio
from datetime import datetime
from app.gmail_client import fetch_tldr_emails
from app.summarizer import summarize_email
from app.whatsapp_sender import send_whatsapp_message
from app.logger import get_logger

logger = get_logger(__name__)


async def run_tldr_pipeline() -> None:
    """
    Main pipeline:
    1. Fetch unread TLDR emails from Gmail
    2. Summarize each with Claude
    3. Send summary to WhatsApp
    """
    logger.info("pipeline starting run_at=%s", datetime.now().isoformat())

    # 1. Fetch emails
    try:
        emails = fetch_tldr_emails()
    except Exception as e:
        logger.error("pipeline failed at gmail fetch error=%s", str(e))
        return

    if not emails:
        logger.info("pipeline no new TLDR emails found, skipping")
        return

    logger.info("pipeline fetched emails count=%s", len(emails))

    # 2 & 3. Summarize and send each email
    for email in emails:
        subject = email["subject"]
        logger.info("pipeline processing email subject=%s", subject)

        try:
            summary = summarize_email(subject=subject, body=email["body"])
        except Exception as e:
            logger.error("pipeline summarization failed subject=%s error=%s", subject, str(e))
            continue

        # Format final WhatsApp message
        whatsapp_message = (
            f"📰 *TLDR Summary* — {email['date']}\n\n"
            f"{summary}"
        )

        try:
            sent = await send_whatsapp_message(whatsapp_message)
            if sent:
                logger.info("pipeline message sent successfully subject=%s", subject)
            else:
                logger.warning("pipeline message send failed subject=%s", subject)
        except Exception as e:
            logger.error("pipeline whatsapp send failed subject=%s error=%s", subject, str(e))

    logger.info("pipeline completed run_at=%s", datetime.now().isoformat())
