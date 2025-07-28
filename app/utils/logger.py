"""
Logging configuration for Service 1A - PDF Outline Extraction
Windows & Docker compatible
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str = None, level: str = 'INFO') -> logging.Logger:
    """Setup application logger with cross-platform path handling"""
    
    # Create logger
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter with more context for PDF processing
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [Service1A] %(message)s'
    )
    
    # Console handler (always works)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with relative path
    try:
        # Use relative path that works in both environments
        if Path('/app').exists():
            # Docker environment
            log_dir = Path('/app/logs')
        else:
            # Local development environment
            log_dir = Path('./logs')
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / 'service1a.log')  # Service-specific log
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.debug(f'Service 1A log file created at: {log_dir / "service1a.log"}')
        
    except Exception as e:
        # If file logging fails, continue with console only
        logger.warning(f'Could not setup file logging: {str(e)}')
        logger.info('Using console logging only')
    
    return logger

def log_pdf_processing_start(logger: logging.Logger, pdf_path: str, total_files: int, current_index: int):
    """Helper function for consistent PDF processing logging"""
    logger.info(f"Processing PDF {current_index}/{total_files}: {Path(pdf_path).name}")

def log_outline_extraction_result(logger: logging.Logger, pdf_path: str, sections_found: int, processing_time: float):
    """Helper function for logging extraction results"""
    logger.info(f"Extracted {sections_found} sections from {Path(pdf_path).name} in {processing_time:.2f}s")
