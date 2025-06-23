# tests/test_logger.py
from config.logger import get_logger

logger = get_logger("TestLogger")

logger.info("This is an info message.")
logger.debug("This is a debug message.")
logger.warning("This is a warning.")
logger.error("This is an error.")


# use it anywhere
# example Use
"""
from config.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting review agent")
logger.error("Failed to connect to DB")
"""
