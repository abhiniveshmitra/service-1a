"""
Main service for Round 1B - Persona-driven relevance ranking
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

from services.round1b.document_loader import DocumentLoader
from services.round1b.persona_matcher import PersonaMatcher
from utils.file_handler import FileHandler
from utils.logger import setup_logger

class RelevanceRanker:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.document_loader = DocumentLoader()
        self.persona_matcher = PersonaMatcher()
        self.file_handler = FileHandler()
    
    def process(self):
        """Main processing pipeline for Round 1B"""
        # FIXED: Use correct relative paths from project root
        input_dir = Path('./app/input')
        output_dir = Path('./app/output')
        
        # Ensure directories exist
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load job queries
        queries_file = input_dir / 'queries.json'
        
        # Add debugging information
        self.logger.info(f'Looking for queries.json at: {queries_file.absolute()}')
        self.logger.info(f'File exists: {queries_file.exists()}')
        
        if not queries_file.exists():
            self.logger.error(f'queries.json not found at {queries_file.absolute()}')
            self.logger.info('Please ensure queries.json is in the app/input/ directory')
            return
        
        try:
            queries = self.file_handler.load_json(queries_file)
            self.logger.info(f'Successfully loaded {len(queries)} queries')
        except Exception as e:
            self.logger.error(f'Error loading queries.json: {str(e)}')
            return
        
        # Process each query
        for query_id, query_data in queries.items():
            try:
                result = self.rank_for_query(query_data, input_dir)
                output_file = output_dir / f'relevance_{query_id}.json'
                self.file_handler.save_json(result, output_file)
                self.logger.info(f'Processed query {query_id}')
                
            except Exception as e:
                self.logger.error(f'Error processing query {query_id}: {str(e)}')
                import traceback
                self.logger.error(traceback.format_exc())
    
    def rank_for_query(self, query_data: Dict, input_dir: Path) -> Dict:
        """Rank documents for a specific persona query"""
        job_role = query_data.get('job_role', '')
        search_query = query_data.get('query', '')
        documents = query_data.get('documents', [])
        
        all_results = []
        
        for doc_info in documents:
            # FIXED: Use input_dir parameter for consistent path resolution
            doc_path = input_dir.parent / 'output' / doc_info['outline_file']
            
            self.logger.debug(f'Looking for outline file: {doc_path.absolute()}')
            
            if doc_path.exists():
                try:
                    # Load document outline
                    outline_data = self.file_handler.load_json(doc_path)
                    
                    # Rank sections
                    ranked_sections = self.persona_matcher.rank_sections(
                        outline_data.get('outline', []),
                        job_role,
                        search_query
                    )
                    
                    # Format results
                    doc_results = {
                        'document': doc_info['name'],
                        'total_sections': len(ranked_sections),
                        'top_matches': [
                            {
                                'section': section[0],
                                'relevance_score': round(section[1], 4),
                                'rank': idx + 1
                            }
                            for idx, section in enumerate(ranked_sections[:10])
                        ]
                    }
                    all_results.append(doc_results)
                    
                except Exception as e:
                    self.logger.error(f'Error processing document {doc_info["name"]}: {str(e)}')
            else:
                self.logger.warning(f'Outline file not found: {doc_path.absolute()}')
        
        return {
            'query_id': query_data.get('id', ''),
            'job_role': job_role,
            'search_query': search_query,
            'results': all_results,
            'metadata': {
                'total_documents': len(documents),
                'processing_time': 'calculated_at_runtime'
            }
        }
