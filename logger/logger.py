import sys

from loguru import logger

from config import secrets
from logger.async_logger import AsyncBetterStackSink

log_sink = AsyncBetterStackSink(
    secrets.BETTER_STACK_SOURCE_TOKEN
)

logger.remove()
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
)

async def init_logger():
    """
    Initialize the asynchronous logging sink.

    - Starts the background task inside AsyncBetterStackSink that will send logs to BetterStack.
    - Adds the async sink as a Loguru logging handler with INFO level and async enqueue enabled.
    """
    await log_sink.start()
    logger.add(
        log_sink.write,
        level="INFO",
        enqueue=True
    )

