"""
PDF parsing and text extraction for Round 1A - Simplified Version
"""

import fitz  # PyMuPDF
import logging
import re
from typing import Dict, List, Tuple
from pathlib import Path

class PDFParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_with_metadata(self, pdf_path: str) -> List[Dict]:
        """Extract text blocks with comprehensive font and position metadata"""
        doc = fitz.open(pdf_path)
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text('dict')
            
            for block in blocks['blocks']:
                if 'lines' in block:
                    for line in block['lines']:
                        line_text_parts = []
                        line_font_info = []
                        
                        for span in line['spans']:
                            text = span['text'].strip()
                            if text:
                                line_text_parts.append(text)
                                line_font_info.append({
                                    'size': span['size'],
                                    'flags': span['flags'],
                                    'font': span['font']
                                })
                        
                        if line_text_parts:
                            # Combine spans in the same line
                            combined_text = ' '.join(line_text_parts)
                            
                            # Use the most prominent font in the line
                            primary_font = max(line_font_info, key=lambda x: x['size'])
                            
                            text_blocks.append({
                                'text': combined_text,
                                'font_size': primary_font['size'],
                                'font_flags': primary_font['flags'],
                                'font_name': primary_font['font'],
                                'bbox': line['bbox'],
                                'page': page_num
                            })
        
        doc.close()
        return text_blocks
    
    def extract_document_title(self, pdf_path: str) -> str:
        """Extract document title from first page"""
        doc = fitz.open(pdf_path)
        
        if len(doc) == 0:
            doc.close()
            return ""
        
        # Get text blocks from first page only
        first_page = doc[0]
        blocks = first_page.get_text('dict')
        
        title_candidates = []
        
        for block in blocks['blocks']:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if text and len(text) > 5:  # Reasonable title length
                            # Check if it's in upper part of page (likely title area)
                            if span['bbox'][1] < 200:  # Y coordinate < 200
                                title_candidates.append({
                                    'text': text,
                                    'font_size': span['size'],
                                    'font_flags': span['flags'],
                                    'y_pos': span['bbox'][1]
                                })
        
        doc.close()
        
        if not title_candidates:
            return ""
        
        # Sort by font size (descending) and position (ascending)
        title_candidates.sort(key=lambda x: (-x['font_size'], x['y_pos']))
        
        # Combine top title elements
        title_parts = []
        if title_candidates:
            # Get the largest font size
            max_font_size = title_candidates[0]['font_size']
            
            # Include all text with the same or similar font size
            for candidate in title_candidates:
                if candidate['font_size'] >= max_font_size * 0.9:  # Within 90% of max size
                    title_parts.append(candidate['text'])
                if len(title_parts) >= 3:  # Limit title parts
                    break
        
        return ' '.join(title_parts)
    
    def get_document_stats(self, text_blocks: List[Dict]) -> Dict:
        """Calculate comprehensive document statistics"""
        if not text_blocks:
            return {
                'avg_font_size': 12,
                'max_font_size': 12,
                'min_font_size': 12,
                'total_blocks': 0,
                'font_size_distribution': {},
                'most_common_size': 12,
                'body_text_size': 12
            }
        
        font_sizes = [block['font_size'] for block in text_blocks]
        
        # Calculate font size distribution
        font_size_counts = {}
        for size in font_sizes:
            rounded_size = round(size, 1)
            font_size_counts[rounded_size] = font_size_counts.get(rounded_size, 0) + 1
        
        # Find most common font sizes
        sorted_sizes = sorted(font_size_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'avg_font_size': sum(font_sizes) / len(font_sizes),
            'max_font_size': max(font_sizes),
            'min_font_size': min(font_sizes),
            'total_blocks': len(text_blocks),
            'font_size_distribution': font_size_counts,
            'most_common_size': sorted_sizes[0][0] if sorted_sizes else 12,
            'body_text_size': sorted_sizes[0][0] if sorted_sizes else 12  # Assume most common is body text
        }
