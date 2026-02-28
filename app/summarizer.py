import os
from openai import OpenAI
from app.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a concise newsletter summarizer like Inshorts.
Extract the most important stories from TLDR newsletter emails.
Format strictly for WhatsApp with bold headings and plain summaries."""

SUMMARY_PROMPT = """Summarize this TLDR newsletter into  Inshorts style.

Format each card EXACTLY like this (no deviations):

*NEWS HEADLINE IN BOLD CAPS*
One crisp paragraph. Max 60 words. Who, what, why it matters. No fluff.



Newsletter:
{body}"""


def summarize_email(subject: str, body: str) -> str:
    """
    Summarizes a single TLDR email into 5 Inshorts-style WhatsApp cards.
    Bold heading + plain content + divider per card. One message per email.
    """
    logger.info("summarizer starting subject=%s body_length=%s", subject, len(body))

    truncated_body = body[:8000] if len(body) > 8000 else body

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": SUMMARY_PROMPT.format(body=truncated_body)},
            ],
        )

        summary = response.choices[0].message.content
        logger.info(
            "summarizer complete subject=%s input_tokens=%s output_tokens=%s",
            subject,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )
        print("Summary:\n", summary)
        return summary

    except Exception as e:
        logger.error("summarizer failed subject=%s error=%s", subject, str(e))
        raise
