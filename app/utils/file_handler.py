"""
File handling utilities for Service 1A - PDF Outline Extraction
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional

class FileHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_json(self, file_path: Union[str, Path]) -> Dict:
        """Load JSON file with error handling and UTF-8 BOM support"""
        try:
            # First try with utf-8-sig to handle BOM
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except UnicodeDecodeError:
            # Fallback to regular utf-8
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f'Error loading JSON from {file_path}: {str(e)}')
                raise
        except Exception as e:
            self.logger.error(f'Error loading JSON from {file_path}: {str(e)}')
            raise
    
    def save_json(self, data: Dict, file_path: Union[str, Path], indent: int = 2) -> bool:
        """Save data to JSON file without BOM - optimized for outline format"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, separators=(',', ': '))
            self.logger.info(f'JSON saved successfully: {file_path}')
            return True
        except Exception as e:
            self.logger.error(f'Error saving JSON to {file_path}: {str(e)}')
            return False
    
    def ensure_directory(self, dir_path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if necessary"""
        path_obj = Path(dir_path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    
    def get_pdf_files(self, directory: Union[str, Path]) -> List[Path]:
        """Get list of PDF files in directory - Service 1A specific"""
        dir_path = Path(directory)
        if not dir_path.exists():
            self.logger.warning(f'Directory does not exist: {directory}')
            return []
        
        pdf_files = list(dir_path.glob('*.pdf'))
        self.logger.info(f'Found {len(pdf_files)} PDF files in {directory}')
        return pdf_files
    
    def get_file_list(self, directory: Union[str, Path], pattern: str = '*') -> List[Path]:
        """Get list of files matching pattern"""
        dir_path = Path(directory)
        if not dir_path.exists():
            self.logger.warning(f'Directory does not exist: {directory}')
            return []
        
        return list(dir_path.glob(pattern))
    
    def generate_output_filename(self, pdf_path: Union[str, Path]) -> str:
        """Generate output JSON filename for PDF - Service 1A specific"""
        pdf_name = Path(pdf_path).stem
        return f"{pdf_name}_outline.json"
    
    def validate_pdf_file(self, pdf_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """Basic PDF file validation"""
        try:
            pdf_path = Path(pdf_path)
            
            if not pdf_path.exists():
                return False, f"File does not exist: {pdf_path}"
            
            if pdf_path.suffix.lower() != '.pdf':
                return False, f"File is not a PDF: {pdf_path}"
            
            if pdf_path.stat().st_size == 0:
                return False, f"PDF file is empty: {pdf_path}"
            
            # Optional: Check if file is readable
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False, f"Invalid PDF header: {pdf_path}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating PDF: {str(e)}"
