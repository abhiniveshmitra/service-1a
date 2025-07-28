"""
JSON validation utilities for Service 1A - PDF Outline Extraction
Adobe Hackathon 2025 Competition Format Compliance
"""

import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

class JSONValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_outline_output(self, output_data: Dict) -> tuple[bool, List[str]]:
        """Validate Service 1A PDF outline JSON output format"""
        errors = []
        
        # Check required top-level fields for Service 1A
        required_fields = ['title', 'outline']
        for field in required_fields:
            if field not in output_data:
                errors.append(f'Missing required field: {field}')
        
        # Validate title
        if 'title' in output_data:
            if not isinstance(output_data['title'], str):
                errors.append('Title must be a string')
            elif not output_data['title'].strip():
                errors.append('Title cannot be empty')
        
        # Validate outline structure
        if 'outline' in output_data:
            if not isinstance(output_data['outline'], list):
                errors.append('Outline must be a list')
            else:
                outline_errors = self._validate_outline_sections(output_data['outline'])
                errors.extend(outline_errors)
        
        # Optional: Validate metadata if present
        if 'metadata' in output_data:
            metadata_errors = self._validate_metadata(output_data['metadata'])
            errors.extend(metadata_errors)
        
        return len(errors) == 0, errors
    
    def _validate_outline_sections(self, sections: List[Dict]) -> List[str]:
        """Validate outline section structure for PDF headings"""
        errors = []
        
        if not sections:
            errors.append('Outline cannot be empty')
            return errors
        
        for idx, section in enumerate(sections):
            if not isinstance(section, dict):
                errors.append(f'Section {idx} must be a dictionary')
                continue
            
            # Check required section fields
            required_section_fields = ['level', 'text', 'page']
            for field in required_section_fields:
                if field not in section:
                    errors.append(f'Section {idx} missing required field: {field}')
            
            # Validate level field
            if 'level' in section:
                if section['level'] not in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'title']:
                    errors.append(f'Section {idx} invalid level: {section["level"]}')
            
            # Validate text field
            if 'text' in section:
                if not isinstance(section['text'], str):
                    errors.append(f'Section {idx} text must be a string')
                elif not section['text'].strip():
                    errors.append(f'Section {idx} text cannot be empty')
            
            # Validate page field
            if 'page' in section:
                if not isinstance(section['page'], int) or section['page'] < 1:
                    errors.append(f'Section {idx} page must be a positive integer')
                elif section['page'] > 50:  # Hackathon limit
                    errors.append(f'Section {idx} page {section["page"]} exceeds 50-page limit')
        
        return errors
    
    def _validate_metadata(self, metadata: Dict) -> List[str]:
        """Validate optional metadata structure"""
        errors = []
        
        # Optional fields with type validation
        optional_fields = {
            'total_pages': int,
            'processing_time': (int, float),
            'extraction_method': str,
            'pdf_filename': str
        }
        
        for field, expected_type in optional_fields.items():
            if field in metadata:
                if not isinstance(metadata[field], expected_type):
                    errors.append(f'Metadata {field} must be of type {expected_type.__name__}')
        
        return errors
    
    def validate_output_file(self, file_path: Union[str, Path]) -> tuple[bool, List[str]]:
        """Validate Service 1A output file format"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, [f'File does not exist: {file_path}']
            
            if file_path.suffix.lower() != '.json':
                return False, [f'File must be JSON format: {file_path}']
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.validate_outline_output(data)
                
        except json.JSONDecodeError as e:
            return False, [f'Invalid JSON format: {str(e)}']
        except Exception as e:
            return False, [f'Error reading file: {str(e)}']
    
    def validate_batch_outputs(self, output_dir: Union[str, Path]) -> Dict[str, tuple[bool, List[str]]]:
        """Validate all JSON files in output directory"""
        results = {}
        output_dir = Path(output_dir)
        
        if not output_dir.exists():
            return {'error': (False, [f'Output directory does not exist: {output_dir}'])}
        
        json_files = list(output_dir.glob('*.json'))
        
        if not json_files:
            return {'warning': (True, ['No JSON files found in output directory'])}
        
        for json_file in json_files:
            is_valid, errors = self.validate_output_file(json_file)
            results[json_file.name] = (is_valid, errors)
        
        return results
    
    def get_expected_schema(self) -> Dict:
        """Return expected JSON schema for Service 1A output"""
        return {
            "type": "object",
            "required": ["title", "outline"],
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Document title extracted from PDF"
                },
                "outline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["level", "text", "page"],
                        "properties": {
                            "level": {
                                "type": "string",
                                "enum": ["title", "H1", "H2", "H3", "H4", "H5", "H6"]
                            },
                            "text": {"type": "string"},
                            "page": {"type": "integer", "minimum": 1, "maximum": 50}
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "total_pages": {"type": "integer"},
                        "processing_time": {"type": "number"},
                        "extraction_method": {"type": "string"},
                        "pdf_filename": {"type": "string"}
                    }
                }
            }
        }
