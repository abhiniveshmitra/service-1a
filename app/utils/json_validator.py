"""
JSON validation utilities for competition format compliance
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

class JSONValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_round1a_output(self, output_data: Dict) -> tuple[bool, List[str]]:
        '''Validate Round 1A JSON output format'''
        errors = []
        
        # Check required top-level fields
        required_fields = ['document', 'outline']
        for field in required_fields:
            if field not in output_data:
                errors.append(f'Missing required field: {field}')
        
        # Validate outline structure
        if 'outline' in output_data:
            outline_errors = self._validate_outline_sections(output_data['outline'])
            errors.extend(outline_errors)
        
        return len(errors) == 0, errors
    
    def validate_round1b_output(self, output_data: Dict) -> tuple[bool, List[str]]:
        '''Validate Round 1B JSON output format'''
        errors = []
        
        # Check required fields
        required_fields = ['query_id', 'job_role', 'search_query', 'results']
        for field in required_fields:
            if field not in output_data:
                errors.append(f'Missing required field: {field}')
        
        # Validate results structure
        if 'results' in output_data:
            if not isinstance(output_data['results'], list):
                errors.append('Results must be a list')
            else:
                for idx, result in enumerate(output_data['results']):
                    result_errors = self._validate_result_item(result, idx)
                    errors.extend(result_errors)
        
        return len(errors) == 0, errors
    
    def _validate_outline_sections(self, sections: List[Dict]) -> List[str]:
        '''Validate outline section structure'''
        errors = []
        
        for idx, section in enumerate(sections):
            if not isinstance(section, dict):
                errors.append(f'Section {idx} must be a dictionary')
                continue
            
            # Check required section fields
            required_section_fields = ['text', 'level']
            for field in required_section_fields:
                if field not in section:
                    errors.append(f'Section {idx} missing field: {field}')
            
            # Validate children if present
            if 'children' in section and section['children']:
                child_errors = self._validate_outline_sections(section['children'])
                errors.extend([f'Section {idx} child: {err}' for err in child_errors])
        
        return errors
    
    def _validate_result_item(self, result: Dict, idx: int) -> List[str]:
        '''Validate individual result item'''
        errors = []
        
        required_fields = ['document', 'top_matches']
        for field in required_fields:
            if field not in result:
                errors.append(f'Result {idx} missing field: {field}')
        
        # Validate top_matches structure
        if 'top_matches' in result:
            if not isinstance(result['top_matches'], list):
                errors.append(f'Result {idx} top_matches must be a list')
            else:
                for match_idx, match in enumerate(result['top_matches']):
                    if not isinstance(match, dict):
                        errors.append(f'Result {idx} match {match_idx} must be a dictionary')
                        continue
                    
                    match_fields = ['section', 'relevance_score', 'rank']
                    for field in match_fields:
                        if field not in match:
                            errors.append(f'Result {idx} match {match_idx} missing: {field}')
        
        return errors
    
    def validate_output_file(self, file_path: str, round_type: str) -> tuple[bool, List[str]]:
        '''Validate output file format'''
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if round_type == '1A':
                return self.validate_round1a_output(data)
            elif round_type == '1B':
                return self.validate_round1b_output(data)
            else:
                return False, [f'Unknown round type: {round_type}']
                
        except json.JSONDecodeError as e:
            return False, [f'Invalid JSON format: {str(e)}']
        except Exception as e:
            return False, [f'Error reading file: {str(e)}']
