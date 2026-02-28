import os
from twilio.rest import Client
from app.logger import get_logger

logger = get_logger(__name__)


def get_twilio_client() -> Client:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env")

    return Client(account_sid, auth_token)


async def send_whatsapp_message(message: str) -> bool:
    """
    Sends a WhatsApp message via Twilio WhatsApp API.

    Setup (one-time):
    1. Sign up at https://www.twilio.com (free $15 trial credit)
    2. Go to Messaging → Try it out → Send a WhatsApp message
    3. Send the join code to +1 415 523 8886 on WhatsApp
    4. Copy Account SID and Auth Token from Twilio dashboard
    5. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
       TWILIO_WHATSAPP_FROM and TWILIO_WHATSAPP_TO in .env
    """
    from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    to_number = os.getenv("TWILIO_WHATSAPP_TO")

    if not to_number:
        logger.error("twilio TWILIO_WHATSAPP_TO not set in .env")
        raise ValueError("TWILIO_WHATSAPP_TO must be set in .env")

    logger.info(
        "twilio sending whatsapp message to=%s message_length=%s",
        to_number,
        len(message),
    )

    try:
        client = get_twilio_client()
        msg = client.messages.create(
            from_=from_number,
            to=to_number,
            body=message,
        )

        logger.info(
            "twilio message sent successfully to=%s sid=%s status=%s",
            to_number,
            msg.sid,
            msg.status,
        )
        return True

    except Exception as e:
        logger.error(
            "twilio message failed to=%s error=%s",
            to_number,
            str(e),
        )
        return False
