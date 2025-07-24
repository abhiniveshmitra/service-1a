"""
Updated main.py with full Challenge 1B compliance
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from config.settings import Settings
from services.round1a.outline_extractor import OutlineExtractor
from services.round1b.collection_processor import CollectionProcessor
from utils.logger import setup_logger

def main():
    """Main application entry point with full Challenge 1B support"""
    logger = setup_logger()
    settings = Settings()
    
    logger.info("Starting Adobe Hackathon Application - Challenge 1B Compliant")
    logger.info(f"Round: {settings.round}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        if settings.round == "1A":
            logger.info("Initializing Round 1A - PDF Outline Extraction")
            outline_extractor = OutlineExtractor()
            outline_extractor.process()
            logger.info("Round 1A processing completed")
            
        elif settings.round == "1B":
            logger.info("Initializing Round 1B - Challenge 1B Multi-Collection Processing")
            collection_processor = CollectionProcessor()
            
            # Process collections from different possible locations
            root_paths = [
                Path('./collections'),  # Primary collections directory
                Path('./'),             # Current directory for individual collections
                Path('./app/collections')  # Alternative location
            ]
            
            processed = False
            for root_path in root_paths:
                if root_path.exists():
                    logger.info(f"Checking for collections in: {root_path.absolute()}")
                    collection_processor.process_all_collections(root_path)
                    processed = True
                    break
            
            if not processed:
                logger.warning("No collection directories found. Processing as legacy format.")
                collection_processor.process_all_collections(Path('./'))
            
            logger.info("Round 1B processing completed")
            
        else:
            logger.error(f"Unknown round: {settings.round}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
