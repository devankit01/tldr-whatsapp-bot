import os
import re
import httpx
from openai import OpenAI
from app.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an expert tech news editor like Inshorts — sharp, fast, and insightful.

Your job:
- Extract the most important and interesting stories from TLDR newsletter
- Write like a senior journalist: clear, direct, no filler
- Each story must be self-contained — reader needs zero context
- Prioritise: AI, startups, big tech, science breakthroughs, developer tools, finance, data, programming languages, open source, security, and privacy
- Skip: job listings, sponsor content, quick links, advertisements

Writing rules:
- Lead with the most important fact (inverted pyramid)
- Include numbers, names, companies where relevant
- No passive voice, no buzzwords, no fluff
- Every word must earn its place"""

SUMMARY_PROMPT = """Summarize the top stories from this TLDR newsletter in Inshorts style.

STRICT FORMAT — follow exactly:

*🔴 HEADLINE IN CAPS*
Crisp 2-3 sentence summary. Who did what, why it matters, what happens next. Max 80 words. No fluff.


Stop at "Quick Links" or "Sponsor" sections — ignore everything after.

Newsletter:
{body}

Additional context from article URLs:
{url_context}"""


def _extract_urls(text: str) -> list[str]:
    """
    Extracts all URLs from the newsletter body.
    """
    pattern = r"https?://[^\s\)\]\>\"\']+"
    urls = re.findall(pattern, text)
    # filter out tracking/unsubscribe/image URLs
    skip_keywords = [
        "unsubscribe",
        "tracking",
        "pixel",
        "click",
        "open",
        "img",
        "beacon",
    ]
    filtered = [
        url for url in urls if not any(kw in url.lower() for kw in skip_keywords)
    ]
    logger.debug("summarizer extracted %s urls from newsletter", len(filtered))
    return filtered[:5]  # limit to top 5 urls


def _fetch_url_content(url: str) -> str:
    """
    Fetches and returns plain text content from a URL.
    Returns empty string on failure.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        response.raise_for_status()

        # strip html tags roughly
        text = re.sub(r"<[^>]+>", " ", response.text)
        text = re.sub(r"\s+", " ", text).strip()

        logger.debug("summarizer fetched url=%s content_length=%s", url, len(text))
        return text[:1000]  # first 1000 chars per url is enough

    except Exception as e:
        logger.warning("summarizer failed to fetch url=%s error=%s", url, str(e))
        return ""


def _build_url_context(body: str) -> str:
    """
    Extracts URLs from body, fetches their content,
    and returns a combined context string.
    """
    urls = _extract_urls(body)
    if not urls:
        return "No additional URL context available."

    context_parts = []
    for url in urls:
        content = _fetch_url_content(url)
        if content:
            context_parts.append(f"URL: {url}\n{content}\n")

    return (
        "\n".join(context_parts)
        if context_parts
        else "No additional URL context available."
    )


def summarize_email(subject: str, body: str) -> str:
    """
    Summarizes a single TLDR email into Inshorts-style cards.
    Fetches URL content for richer context before summarizing.
    """
    logger.info("summarizer starting subject=%s body_length=%s", subject, len(body))

    truncated_body = body[:8000] if len(body) > 8000 else body

    # fetch url context for richer summaries
    logger.info("summarizer fetching url context subject=%s", subject)
    url_context = _build_url_context(truncated_body)
    logger.debug("summarizer url_context_length=%s", len(url_context))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2000,
            temperature=0.3,  # lower = more factual, less creative
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": SUMMARY_PROMPT.format(
                        body=truncated_body,
                        url_context=url_context,
                    ),
                },
            ],
        )

        summary = response.choices[0].message.content
        logger.info(
            "summarizer complete subject=%s input_tokens=%s output_tokens=%s",
            subject,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )
        return summary

    except Exception as e:
        logger.error("summarizer failed subject=%s error=%s", subject, str(e))
        raise
