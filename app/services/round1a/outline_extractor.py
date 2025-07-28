"""
Main service for Round 1A - Enhanced PDF outline extraction
"""

import json
import logging
import re  # ADD THIS IMPORT
from pathlib import Path
from typing import Dict, List

from config.settings import Settings  # ADD THIS IMPORT
from services.round1a.pdf_parser import PDFParser
from services.round1a.heading_detector import HeadingDetector
from utils.file_handler import FileHandler

class OutlineExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = Settings()  # ADD THIS
        self.pdf_parser = PDFParser()
        self.heading_detector = HeadingDetector()
        self.file_handler = FileHandler()
    
    def process(self):
        """Main processing pipeline for Round 1A"""
        # Use settings instead of hardcoded paths
        input_dir = self.settings.get_input_path()
        output_dir = self.settings.get_output_path()
        
        # Ensure directories exist
        self.settings.validate_directories()
        
        pdf_files = list(input_dir.glob('*.pdf'))
        self.logger.info(f'Found {len(pdf_files)} PDF files to process')
        
        if not pdf_files:
            self.logger.warning(f'No PDF files found in {input_dir.absolute()}')
            self.logger.info('Please place PDF files in the app/input/ directory')
            return
        
        for pdf_file in pdf_files:
            try:
                self.logger.info(f'Processing {pdf_file.name}...')
                outline = self.extract_outline(str(pdf_file))
                
                output_filename = self.settings.get_output_filename(pdf_file.name)
                output_file = output_dir / output_filename
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(outline, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f'Successfully processed {pdf_file.name} -> {output_file.name}')
                self.logger.info(f'Extracted {len(outline["outline"])} headings')
                
            except Exception as e:
                self.logger.error(f'Error processing {pdf_file.name}: {str(e)}')
                import traceback
                self.logger.error(traceback.format_exc())
    
    def process_pdf(self, pdf_path: str) -> Dict:  # ADD THIS METHOD for main.py compatibility
        """Process single PDF - wrapper for extract_outline"""
        return self.extract_outline(pdf_path)
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract hierarchical outline from PDF in competition format"""
        
        # Validate PDF before processing
        is_valid, error_msg = self.file_handler.validate_pdf_file(pdf_path)
        if not is_valid:
            raise ValueError(f"Invalid PDF: {error_msg}")
        
        # Extract document title
        document_title = self.pdf_parser.extract_document_title(pdf_path)
        
        # Extract text with metadata
        text_blocks = self.pdf_parser.extract_text_with_metadata(pdf_path)
        doc_stats = self.pdf_parser.get_document_stats(text_blocks)
        
        # Check page limit compliance (hackathon requirement)
        total_pages = len(set(block['page'] for block in text_blocks)) if text_blocks else 0
        if total_pages > self.settings.max_pages_per_pdf:
            self.logger.warning(f'PDF has {total_pages} pages, exceeds {self.settings.max_pages_per_pdf} page limit')
        
        # Detect headings
        headings = self.heading_detector.detect_headings(text_blocks, doc_stats)
        
        # Build flat outline structure (matching sample format)
        outline = self._build_flat_outline(headings)
        
        return {
            'title': document_title if document_title else Path(pdf_path).name.replace('.pdf', ''),
            'outline': outline
        }
    
    def _build_flat_outline(self, headings: List[Dict]) -> List[Dict]:
        """Build flat outline structure matching sample format"""
        flat_outline = []
        
        for heading in headings:
            outline_item = {
                'level': heading['level'],
                'text': self._clean_heading_text(heading['text']),  # Clean the text
                'page': heading['page'] + 1  # Convert to 1-based page numbering
            }
            flat_outline.append(outline_item)
        
        return flat_outline
    
    def _clean_heading_text(self, text: str) -> str:
        """Clean heading text for better presentation"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove trailing periods or colons if they seem excessive
        text = text.rstrip('.:')
        
        # Ensure proper spacing around numbers
        text = re.sub(r'(\d+)\.(\w)', r'\1. \2', text)
        
        return text
