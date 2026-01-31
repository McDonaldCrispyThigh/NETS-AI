"""
Logging configuration for NETS Enhancement System
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "NETS-Enhancement", level: str = None, log_file: bool = True) -> logging.Logger:
    """
    Setup centralized logger
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Whether to write to file
        
    Returns:
        Configured logger
    """
    # Get level from env or use default
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_path = log_dir / f"ai_bdd_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger
logger = setup_logger()
