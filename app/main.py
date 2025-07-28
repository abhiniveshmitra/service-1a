"""
Service 1A: PDF Outline Extraction
Adobe Hackathon 2025 - Challenge 1A Compliant
"""

import sys
import os
import time
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from config.settings import Settings
from services.round1a.outline_extractor import OutlineExtractor
from utils.logger import setup_logger
from utils.file_handler import FileHandler
from utils.json_validator import JSONValidator

def main():
    """Main application entry point for Service 1A - PDF Outline Extraction"""
    logger = setup_logger()
    settings = Settings()
    file_handler = FileHandler()
    validator = JSONValidator()
    
    logger.info("Starting Adobe Hackathon Service 1A - PDF Outline Extraction")
    logger.info(f"Service: {getattr(settings, 'service', '1A')}")
    logger.info(f"Round: {getattr(settings, 'round', 'round1a')}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Validate and create directories using Settings
        if not settings.validate_directories():
            logger.error("Failed to create required directories")
            sys.exit(1)
        
        logger.info("Initializing PDF Outline Extraction")
        outline_extractor = OutlineExtractor()
        
        # Get directories from settings
        input_dir = settings.get_input_path()
        output_dir = settings.get_output_path()
        
        logger.info(f"Input directory: {input_dir.absolute()}")
        logger.info(f"Output directory: {output_dir.absolute()}")
        
        # Get PDF files using FileHandler
        pdf_files = file_handler.get_pdf_files(input_dir)
        
        if not pdf_files:
            logger.warning("No PDF files found in input directory")
            logger.info(f"Please place PDF files in {input_dir} directory")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        # Process each PDF with timing and validation
        successful_count = 0
        failed_count = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            start_time = time.time()
            
            try:
                logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
                
                # Validate PDF file before processing
                is_valid, error_msg = file_handler.validate_pdf_file(pdf_file)
                if not is_valid:
                    logger.error(f"Invalid PDF {pdf_file.name}: {error_msg}")
                    failed_count += 1
                    continue
                
                # Extract outline
                outline_data = outline_extractor.extract_outline(str(pdf_file))
                
                # Generate output filename using settings
                output_filename = settings.get_output_filename(pdf_file.name)
                output_file = output_dir / output_filename
                
                # Save JSON output using FileHandler
                if file_handler.save_json(outline_data, output_file):
                    processing_time = time.time() - start_time
                    
                    # Validate output format
                    is_valid, validation_errors = validator.validate_output_file(output_file)
                    if not is_valid:
                        logger.warning(f"Output validation issues for {pdf_file.name}: {validation_errors}")
                    
                    # Check timing compliance (≤10 seconds requirement)
                    if processing_time > settings.timeout_seconds:
                        logger.warning(f"Processing time {processing_time:.2f}s exceeds {settings.timeout_seconds}s limit")
                    
                    logger.info(f"✅ Successfully processed {pdf_file.name} -> {output_file.name}")
                    logger.info(f"   Extracted {len(outline_data.get('outline', []))} headings in {processing_time:.2f}s")
                    successful_count += 1
                else:
                    logger.error(f"Failed to save output for {pdf_file.name}")
                    failed_count += 1
                
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
                logger.error(f"   Processing failed after {processing_time:.2f}s")
                failed_count += 1
                
                # Continue processing other files if configured to do so
                if settings.continue_on_error:
                    logger.info("Continuing with next PDF...")
                    continue
                else:
                    raise
        
        # Final summary
        logger.info("=" * 50)
        logger.info(f"Service 1A processing completed")
        logger.info(f"✅ Successful: {successful_count} PDFs")
        if failed_count > 0:
            logger.warning(f"❌ Failed: {failed_count} PDFs")
        logger.info(f"📁 Output directory: {output_dir.absolute()}")
        
        # Optional: Validate all output files
        if successful_count > 0:
            logger.info("Validating all output files...")
            validation_results = validator.validate_batch_outputs(output_dir)
            
            valid_files = sum(1 for result in validation_results.values() if result[0])
            logger.info(f"📋 Validation: {valid_files}/{len(validation_results)} files passed validation")
        
        # Exit with appropriate code
        if failed_count > 0 and successful_count == 0:
            logger.error("All PDF processing failed")
            sys.exit(1)
        elif failed_count > 0:
            logger.warning("Some PDFs failed processing")
            sys.exit(2)  # Partial success
        else:
            logger.info("All PDFs processed successfully")
        
    except Exception as e:
        logger.error(f"Service 1A critical error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
