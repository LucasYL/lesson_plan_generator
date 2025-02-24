import os
import PyPDF2
from typing import Dict, List, Tuple

class FileProcessor:
    MAX_FILE_SIZE_MB = 10
    MAX_CHARS = 5000
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """Validate file size and type"""
        if not file_path.lower().endswith('.pdf'):
            return False, "Only PDF files are supported"
            
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > FileProcessor.MAX_FILE_SIZE_MB:
            return False, f"File size exceeds limit ({FileProcessor.MAX_FILE_SIZE_MB}MB)"
            
        return True, "File validation passed"
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and format extracted text"""
        # Basic cleaning
        text = text.strip()
        
        # Handle extra whitespace characters
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Handle extra spaces
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"  # Add paragraph separation
                    
            # Clean text
            text = FileProcessor.clean_text(text)
                
            return text, len(text)
            
        except Exception as e:
            raise Exception(f"PDF processing error: {str(e)}")
    
    @staticmethod
    def process_files(file_paths: List[str]) -> Dict[str, str]:
        """Process multiple files and return results"""
        results = {}
        total_chars = 0
        
        for file_path in file_paths[:2]:  # Limit to processing 2 files
            # Validate file
            is_valid, message = FileProcessor.validate_file(file_path)
            if not is_valid:
                results[file_path] = f"File validation failed: {message}"
                continue
                
            # Extract text
            try:
                text, chars = FileProcessor.extract_text_from_pdf(file_path)
                # Only truncate when exceeding total character limit
                if total_chars + chars > FileProcessor.MAX_CHARS:
                    remaining_chars = FileProcessor.MAX_CHARS - total_chars
                    if remaining_chars > 0:
                        text = text[:remaining_chars]
                        chars = len(text)
                    else:
                        continue
                total_chars += chars
                results[file_path] = text
            except Exception as e:
                results[file_path] = f"Processing failed: {str(e)}"
                
        return results 