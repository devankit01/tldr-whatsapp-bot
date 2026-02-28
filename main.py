import asyncio
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.pipeline import run_tldr_pipeline
from app.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


async def main():
    hour = int(os.getenv("SCHEDULE_HOUR", 8))
    minute = int(os.getenv("SCHEDULE_MINUTE", 0))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_tldr_pipeline,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="tldr_pipeline",
        name="TLDR WhatsApp Pipeline",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("scheduler started running daily at %02d:%02d", hour, minute)
    logger.info("press Ctrl+C to stop")

    # Run once immediately on startup
    logger.info("running pipeline immediately on startup")
    await run_tldr_pipeline()

    # Keep running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("scheduler shutting down")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
