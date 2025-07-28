"""
Service 1A Configuration Settings
PDF Outline Extraction Service
"""

import os
from typing import Optional
from pathlib import Path

class Settings:
    def _init_(self):
        # Service identification
        self.service: str = os.getenv('SERVICE', '1A')
        self.round: str = os.getenv('ROUND', 'round1a')
        
        # Directory paths
        self.input_dir: str = '/app/input'
        self.output_dir: str = '/app/output'
        self.logs_dir: str = '/app/logs'
        
        # Logging
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        
        # PDF Processing Settings
        self.max_pages_per_pdf: int = 50  # Hackathon requirement
        self.supported_formats: list = ['.pdf']
        
        # Performance settings for Service 1A
        self.max_memory_mb: int = 512  # Lighter for Service 1A
        self.timeout_seconds: int = 10  # Max 10 seconds per PDF (hackathon req)
        self.max_concurrent_pdfs: int = 1  # Process one at a time
        
        # Output format settings
        self.output_format: str = 'json'
        self.include_page_numbers: bool = True
        self.include_text_snippets: bool = False  # Keep outline lightweight
        
        # PDF Processing Options
        self.extract_bookmarks: bool = True
        self.extract_headings: bool = True
        self.heading_detection_method: str = 'font_analysis'  # or 'regex_patterns'
        
        # Validation settings
        self.validate_output_schema: bool = True
        self.max_heading_levels: int = 6  # H1 through H6
        
        # Error handling
        self.continue_on_error: bool = True
        self.max_retries: int = 2
        
    def get_input_path(self) -> Path:
        """Get input directory as Path object"""
        return Path(self.input_dir)
    
    def get_output_path(self) -> Path:
        """Get output directory as Path object"""
        return Path(self.output_dir)
    
    def get_logs_path(self) -> Path:
        """Get logs directory as Path object"""
        return Path(self.logs_dir)
    
    def validate_directories(self) -> bool:
        """Ensure required directories exist"""
        try:
            self.get_input_path().mkdir(parents=True, exist_ok=True)
            self.get_output_path().mkdir(parents=True, exist_ok=True)
            self.get_logs_path().mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def get_output_filename(self, pdf_filename: str) -> str:
        """Generate output filename for a PDF"""
        pdf_name = Path(pdf_filename).stem
        return f"{pdf_name}.json"
