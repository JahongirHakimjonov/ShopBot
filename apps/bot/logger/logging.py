# apps/bot/logger.py
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Log a message to indicate the logger is initialized
logger.info("Logger initialized")
