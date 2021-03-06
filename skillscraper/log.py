import sys
from loguru import logger

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    filter="sub.module",
)
logger.add("logs/{time:YYYY-MM-DD}.log")
