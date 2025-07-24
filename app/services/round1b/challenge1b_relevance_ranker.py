"""
Updated Round 1B Relevance Ranker for Challenge 1B Compliance
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

from services.round1b.document_loader import DocumentLoader
from services.round1b.persona_matcher import PersonaMatcher
from services.round1b.challenge1b_input_handler import Challenge1BInputHandler
from services.round1b.challenge1b_output_formatter import Challenge1BOutputFormatter
from utils.file_handler import FileHandler
from utils.logger import setup_logger

class Challenge1BRelevanceRanker:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.document_loader = DocumentLoader()
        self.persona_matcher = PersonaMatcher()
        self.file_handler = FileHandler()
        self.input_handler = Challenge1BInputHandler()
        self.output_formatter = Challenge1BOutputFormatter()
    
    def process(self):
        """Main processing pipeline for Challenge 1B"""
        input_dir = Path('./app/input')
        output_dir = Path('./app/output')
        
        # Ensure directories exist
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Look for challenge1b_input.json files
        challenge_files = list(input_dir.glob('challenge1b_input*.json'))
        
        if not challenge_files:
            # Fallback to legacy queries.json format for backward compatibility
            self.logger.info("No challenge1b_input.json found, checking for legacy queries.json")
            return self._process_legacy_format()
        
        # Process each challenge input file
        for challenge_file in challenge_files:
            try:
                self.logger.info(f'Processing challenge file: {challenge_file.name}')
                
                # Load and convert challenge input
                challenge_input = self.input_handler.load_challenge_input(challenge_file)
                query_data = self.input_handler.convert_to_internal_format(challenge_input)
                
                # Process the challenge
                result = self.rank_for_challenge(query_data, input_dir)
                
                # Generate output filename
                challenge_id = query_data.get("challenge_id", "unknown")
                output_file = output_dir / f'challenge1b_output_{challenge_id}.json'
                
                # Save result
                self.file_handler.save_json(result, output_file)
                self.logger.info(f'Completed challenge {challenge_id}')
                
            except Exception as e:
                self.logger.error(f'Error processing {challenge_file.name}: {str(e)}')
                import traceback
                self.logger.error(traceback.format_exc())
    
    def rank_for_challenge(self, query_data: Dict, input_dir: Path) -> Dict:
        """Process single challenge with persona-driven ranking"""
        job_role = query_data.get('job_role', '')
        search_query = query_data.get('query', '')
        documents = query_data.get('documents', [])
        
        all_sections = []
        all_ranked_sections = []
        
        for doc_info in documents:
            # Look for outline file in output directory
            outline_path = input_dir.parent / 'output' / doc_info['outline_file']
            
            self.logger.debug(f'Looking for outline: {outline_path}')
            
            if outline_path.exists():
                try:
                    # Load document outline
                    outline_data = self.file_handler.load_json(outline_path)
                    sections = outline_data.get('outline', [])
                    
                    # Add document name to each section
                    for section in sections:
                        section['document'] = doc_info['name']
                    
                    all_sections.extend(sections)
                    
                    # Rank sections for this document
                    ranked_sections = self.persona_matcher.rank_sections(
                        sections, job_role, search_query
                    )
                    
                    all_ranked_sections.extend(ranked_sections)
                    
                except Exception as e:
                    self.logger.error(f'Error processing {doc_info["name"]}: {str(e)}')
            else:
                self.logger.warning(f'Outline not found: {outline_path}')
        
        # Sort all sections by relevance score
        all_ranked_sections.sort(key=lambda x: x[1], reverse=True)
        
        # Format to challenge1b output structure
        return self.output_formatter.format_challenge_output(
            query_data, all_ranked_sections, all_sections
        )
    
    def _process_legacy_format(self):
        """Backward compatibility for existing queries.json format"""
        from services.round1b.relevance_ranker import RelevanceRanker
        legacy_ranker = RelevanceRanker()
        legacy_ranker.process()
