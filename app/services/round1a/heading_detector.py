"""
Advanced heading detection with improved pattern recognition
"""

import re
import logging
from typing import Dict, List, Tuple

class HeadingDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced heading patterns
        self.heading_patterns = [
            # Numbered sections (1., 1.1, 1.1.1, etc.)
            r'^\d+(\.\d+)*\.?\s+[A-Z]',
            # Roman numerals (I., II., III., etc.)
            r'^[IVX]+\.?\s+[A-Z]',
            # Letter sections (A., B., C., etc.)
            r'^[A-Z]\.?\s+[A-Z]',
            # All caps headings
            r'^[A-Z][A-Z\s]{2,}$',
            # Title case headings
            r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*:?\s*$',
            # Common heading words
            r'^(Chapter|Section|Part|Appendix|Table|Figure|Introduction|Conclusion|Summary|Background|Overview|References|Bibliography)\b',
        ]
        
        # Common heading keywords
        self.heading_keywords = [
            'introduction', 'background', 'overview', 'summary', 'conclusion',
            'references', 'bibliography', 'appendix', 'table', 'figure',
            'chapter', 'section', 'part', 'acknowledgements', 'acknowledgments',
            'abstract', 'methodology', 'results', 'discussion', 'future work',
            'contents', 'revision', 'history', 'requirements', 'specifications'
        ]
    
    def calculate_heading_score(self, block: Dict, doc_stats: Dict) -> float:
        """Enhanced multi-factor heading detection scoring"""
        score = 0.0
        text = block['text'].strip()
        
        if not text:
            return 0.0
        
        # Font size factor (35% weight)
        body_text_size = doc_stats.get('body_text_size', doc_stats['avg_font_size'])
        font_ratio = block['font_size'] / body_text_size
        
        if font_ratio >= 1.4:
            score += 0.35
        elif font_ratio >= 1.2:
            score += 0.25
        elif font_ratio >= 1.1:
            score += 0.15
        
        # Bold/formatting factor (25% weight)
        if block['font_flags'] & 2**4:  # Bold flag
            score += 0.25
        
        # Pattern matching (25% weight)
        text_lower = text.lower()
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                score += 0.25
                break
        
        # Keyword matching (10% weight)
        for keyword in self.heading_keywords:
            if keyword in text_lower:
                score += 0.1
                break
        
        # Length and formatting factors (5% weight)
        if 3 <= len(text) <= 100:  # Reasonable heading length
            score += 0.03
        
        if text.endswith(':'):  # Colon often indicates heading
            score += 0.02
        
        # Position factor - headings often at start of line
        if block['bbox'][0] < 100:  # Left margin
            score += 0.02
        
        return min(score, 1.0)
    
    def determine_heading_level(self, block: Dict, doc_stats: Dict) -> str:
        """Determine heading level (H1, H2, H3, H4) based on font size and patterns"""
        text = block['text'].strip()
        font_size = block['font_size']
        body_size = doc_stats.get('body_text_size', doc_stats['avg_font_size'])
        
        # Check for numbered patterns that indicate hierarchy
        numbered_match = re.match(r'^(\d+)(\.\d+)*\.?\s+', text)
        if numbered_match:
            dots = numbered_match.group(0).count('.')
            if dots == 0:  # 1., 2., 3. = H1
                return "H1"
            elif dots == 1:  # 1.1, 1.2, 1.3 = H2
                return "H2"
            elif dots == 2:  # 1.1.1, 1.1.2 = H3
                return "H3"
            else:  # 1.1.1.1 = H4
                return "H4"
        
        # Font size based level determination
        font_ratio = font_size / body_size
        
        if font_ratio >= 1.6:
            return "H1"
        elif font_ratio >= 1.4:
            return "H2"
        elif font_ratio >= 1.2:
            return "H3"
        else:
            return "H4"
    
    def detect_headings(self, text_blocks: List[Dict], doc_stats: Dict) -> List[Dict]:
        """Identify heading blocks with confidence scores and levels"""
        headings = []
        
        for block in text_blocks:
            text = block['text'].strip()
            if not text or len(text) < 2:
                continue
            
            score = self.calculate_heading_score(block, doc_stats)
            
            if score >= 0.4:  # Lower threshold for better recall
                level = self.determine_heading_level(block, doc_stats)
                
                headings.append({
                    'text': text,
                    'level': level,
                    'confidence': score,
                    'page': block['page'],
                    'bbox': block['bbox'],
                    'font_size': block['font_size']
                })
        
        # Sort by page and then by vertical position
        headings.sort(key=lambda x: (x['page'], x['bbox'][1]))
        
        # Post-process to improve hierarchy
        headings = self._refine_heading_hierarchy(headings)
        
        return headings
    
    def _refine_heading_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """Refine heading hierarchy based on document structure"""
        if len(headings) < 2:
            return headings
        
        # Analyze font size patterns to improve level detection
        font_sizes = [h['font_size'] for h in headings]
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Map font sizes to heading levels
        size_to_level = {}
        for i, size in enumerate(unique_sizes[:4]):  # Max 4 levels
            size_to_level[size] = f"H{i+1}"
        
        # Update levels based on font size mapping
        for heading in headings:
            if heading['font_size'] in size_to_level:
                heading['level'] = size_to_level[heading['font_size']]
        
        return headings
