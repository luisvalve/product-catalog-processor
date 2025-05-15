"""Logging configuration for the product merge application."""
import logging
from typing import Optional
from config.settings import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT

def setup_logger(name: str = __name__, log_file: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger instance.
    
    Args:
        name: The name of the logger instance
        log_file: Optional path to the log file. If None, uses default from settings
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file or LOG_FILE)
    file_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

# Create default logger instance
logger = setup_logger() 