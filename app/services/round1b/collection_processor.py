"""
Adobe Hackathon Challenge 1B Collection Processor
Discovers and processes multiple collection folders
"""

import logging
from pathlib import Path
from typing import List, Dict
import json

from services.round1b.challenge1b_input_handler import Challenge1BInputHandler
from services.round1b.challenge1b_output_formatter import Challenge1BOutputFormatter
from services.round1b.persona_matcher import PersonaMatcher
from utils.file_handler import FileHandler
from utils.logger import setup_logger

class CollectionProcessor:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.input_handler = Challenge1BInputHandler()
        self.output_formatter = Challenge1BOutputFormatter()
        self.persona_matcher = PersonaMatcher()
        self.file_handler = FileHandler()
    
    def discover_collections(self, root_path: Path) -> List[Path]:
        """Discover all collection folders containing challenge1b_input.json"""
        collections = []
        
        if not root_path.exists():
            self.logger.warning(f"Root path does not exist: {root_path}")
            return collections
        
        # Look for collection directories
        for item in root_path.iterdir():
            if item.is_dir():
                input_file = item / 'challenge1b_input.json'
                if input_file.exists():
                    collections.append(item)
                    self.logger.info(f"Found collection: {item.name}")
        
        return collections
    
    def process_all_collections(self, root_path: Path = None):
        """Process all discovered collections"""
        if root_path is None:
            root_path = Path('./collections')
        
        collections = self.discover_collections(root_path)
        
        if not collections:
            self.logger.warning("No collections found. Looking for legacy format...")
            return self._fallback_to_legacy()
        
        self.logger.info(f"Processing {len(collections)} collections")
        
        for collection_path in collections:
            try:
                self.process_single_collection(collection_path)
            except Exception as e:
                self.logger.error(f"Error processing collection {collection_path.name}: {str(e)}")
                import traceback
                self.logger.error(traceback.format_exc())
    
    def process_single_collection(self, collection_path: Path):
        """Process a single collection folder"""
        self.logger.info(f"Processing collection: {collection_path.name}")
        
        # Load challenge input
        input_file = collection_path / 'challenge1b_input.json'
        challenge_input = self.input_handler.load_challenge_input(input_file)
        
        # Convert to internal format
        query_data = self.input_handler.convert_to_internal_format(challenge_input)
        
        # Process documents in this collection
        all_ranked_sections = []
        all_sections = []
        
        documents = query_data.get('documents', [])
        job_role = query_data.get('job_role', '')
        search_query = query_data.get('query', '')
        
        for doc_info in documents:
            # Look for outline files in collection or app/output
            outline_paths = [
                collection_path / f"{doc_info['name'].replace('.pdf', '_outline.json')}",
                Path('./app/output') / doc_info['outline_file'],
                collection_path / 'PDFs' / f"{doc_info['name'].replace('.pdf', '_outline.json')}"
            ]
            
            outline_path = None
            for path in outline_paths:
                if path.exists():
                    outline_path = path
                    break
            
            if outline_path:
                try:
                    # Load document outline
                    outline_data = self.file_handler.load_json(outline_path)
                    sections = outline_data.get('outline', [])
                    
                    # Add document name to each section
                    for section in sections:
                        section['document'] = doc_info['name']
                        section['title'] = doc_info.get('title', doc_info['name'])
                    
                    all_sections.extend(sections)
                    
                    # Rank sections for this document
                    ranked_sections = self.persona_matcher.rank_sections(
                        sections, job_role, search_query
                    )
                    
                    all_ranked_sections.extend(ranked_sections)
                    
                    self.logger.info(f"Processed {len(sections)} sections from {doc_info['name']}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing document {doc_info['name']}: {str(e)}")
            else:
                self.logger.warning(f"Outline not found for {doc_info['name']} in collection {collection_path.name}")
        
        # Sort all sections by relevance score
        all_ranked_sections.sort(key=lambda x: x[1], reverse=True)
        
        # Format to challenge1b output structure
        result = self.output_formatter.format_challenge_output(
            query_data, all_ranked_sections, all_sections
        )
        
        # Save output to collection folder
        output_file = collection_path / 'challenge1b_output.json'
        self.file_handler.save_json(result, output_file)
        
        challenge_id = query_data.get('challenge_id', 'unknown')
        self.logger.info(f"Completed collection {collection_path.name} (Challenge ID: {challenge_id})")
        self.logger.info(f"Generated {len(result.get('extracted_sections', []))} extracted sections")
    
    def _fallback_to_legacy(self):
        """Fallback to legacy queries.json processing"""
        self.logger.info("Falling back to legacy queries.json processing")
        from services.round1b.relevance_ranker import RelevanceRanker
        legacy_ranker = RelevanceRanker()
        legacy_ranker.process()
