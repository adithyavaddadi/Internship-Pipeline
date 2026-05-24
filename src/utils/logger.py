import os
import logging
from src.config.settings import LOGS_DIR

class EmojiFormatter(logging.Formatter):
    """Custom formatter to map log levels/names to visually pleasing terminal emojis."""
    
    LEVEL_EMOJIS = {
        logging.DEBUG: "🐛",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨"
    }

    def format(self, record):
        emoji = self.LEVEL_EMOJIS.get(record.levelno, "")
        
        # Check custom extra markers
        marker = getattr(record, "marker", None)
        if marker == "success":
            emoji = "✅"
        elif marker == "scrape":
            emoji = "🔍"
        elif marker == "ai":
            emoji = "🤖"
        elif marker == "email":
            emoji = "📧"
        elif marker == "message":
            emoji = "💬"
        elif marker == "pdf":
            emoji = "📄"
        elif marker == "trophy":
            emoji = "🏆"
        
        # Visual spacing
        prefix = f"  {emoji}  " if emoji else " "
        record.msg = f"{prefix}{record.msg}"
        return super().format(record)

def setup_logger():
    """Initializes and returns a double-handler logger (stdout + file)."""
    logger = logging.getLogger("internship_pipeline")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if re-called
    if logger.handlers:
        return logger

    # Log format for files (structured and precise)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s"
    )
    
    # Log format for console (human-centric & pretty)
    console_formatter = EmojiFormatter("%(message)s")

    # File Handler
    log_file = os.path.join(LOGS_DIR, "pipeline.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Singleton logger instance
logger = setup_logger()

# Helper logger decorators for rich UI logging
def log_info(msg):
    logger.info(msg)

def log_success(msg):
    logger.info(msg, extra={"marker": "success"})

def log_warning(msg):
    logger.warning(msg)

def log_error(msg):
    logger.error(msg)

def log_scrape(msg):
    logger.info(msg, extra={"marker": "scrape"})

def log_ai(msg):
    logger.info(msg, extra={"marker": "ai"})

def log_email(msg):
    logger.info(msg, extra={"marker": "email"})

def log_msg(msg):
    logger.info(msg, extra={"marker": "message"})

def log_pdf(msg):
    logger.info(msg, extra={"marker": "pdf"})

def log_trophy(msg):
    logger.info(msg, extra={"marker": "trophy"})
