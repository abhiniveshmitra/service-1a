"""
Application configuration settings
"""

import os
from typing import Optional

class Settings:
    def __init__(self):
        self.round: str = os.getenv('ROUND', '1A')
        self.input_dir: str = '/app/input'
        self.output_dir: str = '/app/output'
        self.models_dir: str = '/app/models'
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        
        # Model configurations
        self.heading_model_path: Optional[str] = None
        self.embedding_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
        
        # Performance settings
        self.max_memory_mb: int = 1024
        self.timeout_seconds: int = 300
