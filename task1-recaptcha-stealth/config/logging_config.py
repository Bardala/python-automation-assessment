"""Global Project Logging Configuration."""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from .settings import OUTPUT_DIR, PROJECT_ROOT

LOG_FILE = os.path.join(PROJECT_ROOT, "outputs", "automation.log")

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevents duplicate handlers if called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console Handler
        stream_h = logging.StreamHandler(sys.stdout)
        stream_h.setFormatter(formatter)
        logger.addHandler(stream_h)
        
        # File Handler (Rotating)
        file_h = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
        file_h.setFormatter(formatter)
        logger.addHandler(file_h)
        
    return logger

import os
