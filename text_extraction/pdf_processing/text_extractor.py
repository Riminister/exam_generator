#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Extractor for Exam PDFs
Extracts text from PDFs with intelligent OCR selection based on exam type
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

# PDF processing imports
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pymupdf  # PyMuPDF
except ImportError:
    pymupdf = None

# OCR imports
try:
    import pytesseract
    from PIL import Image
    try:
        import pdf2image
    except ImportError:
        pdf2image = None
except ImportError:
    pytesseract = None

# Import our modules (relative imports since in same directory)
from .ocr_context_selector import OCRContextSelector
from .cover_page_parser import CoverPageParser

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class TextExtractor:
    """
    Extracts text from PDF files with intelligent OCR selection.
    Uses context-based OCR for language/math exams.
    """
    
    def __init__(self, poppler_path: Optional[str] = None, tesseract_cmd: Optional[str] = None):
        """
        Initialize TextExtractor.
        
        Args:
            poppler_path: Optional path to Poppler bin directory (for Windows).
                         If None, will try to use PATH or check environment variable.
            tesseract_cmd: Optional path to Tesseract executable (for Windows).
                          If None, will try to find it automatically or use PATH.
        """
        self.ocr_selector = OCRContextSelector()
        self.cover_parser = CoverPageParser()
        self.poppler_path = poppler_path
        # Check for environment variable
        if not self.poppler_path:
            self.poppler_path = os.environ.get('POPPLER_PATH')
        
        # Configure Tesseract
        self._configure_tesseract(tesseract_cmd)
    
    def _configure_tesseract(self, tesseract_cmd: Optional[str] = None):
        """
        Configure pytesseract to use Tesseract.
        
        Args:
            tesseract_cmd: Optional path to Tesseract executable
        """
        if pytesseract is None:
            return
        
        # If already configured via parameter or environment variable, use it
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            return
        
        env_tesseract = os.environ.get('TESSERACT_CMD')
        if env_tesseract:
            pytesseract.pytesseract.tesseract_cmd = env_tesseract
            return
        
        # Try to find Tesseract automatically (Windows)
        if sys.platform == 'win32':
            possible_paths = [
                Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
                Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
                Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Tesseract-OCR/tesseract.exe",
                # Project directory
                Path(__file__).parent.parent / "tesseract" / "bin" / "tesseract.exe",
                Path(__file__).parent.parent / "Tesseract-OCR" / "tesseract.exe",
            ]
            
            for path in possible_paths:
                if path.exists():
                    pytesseract.pytesseract.tesseract_cmd = str(path)
                    return
        
        # If not found, pytesseract will try to use it from PATH
        # which will raise an error if not available (handled in extraction code)
    
    def extract_text_from_pdf(
        self,
        pdf_path: Path,
        use_ocr: bool = False,
        ocr_language: Optional[str] = None,
        course_code: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR (for scanned PDFs)
            ocr_language: OCR language code (e.g., 'ara+eng', 'fra+eng')
            course_code: Course code for context-based OCR selection
            
        Returns:
            Dict with:
            - text: str - Extracted text
            - pages: List[str] - Text per page
            - extraction_method: str - 'pdfplumber', 'pymupdf', or 'ocr'
            - ocr_config: dict - OCR configuration used
            - success: bool
        """
        result = {
            'text': '',
            'pages': [],
            'extraction_method': None,
            'ocr_config': None,
            'success': False,
            'error': None,
            'error_details': []
        }
        
        if not pdf_path.exists():
            result['error'] = 'File not found'
            return result
        
        # Get OCR config if not provided
        if use_ocr and not ocr_language:
            if course_code:
                ocr_config = self.ocr_selector.detect_exam_type(course_code)
                ocr_language = ocr_config['ocr_language']
            else:
                # Try to detect from cover page
                first_page_text = self.cover_parser.extract_first_page_text(pdf_path)
                if first_page_text:
                    # Extract course code from first page
                    detected_code = self.cover_parser.extract_course_code(first_page_text)
                    if detected_code:
                        ocr_config = self.ocr_selector.detect_exam_type(detected_code, first_page_text)
                        ocr_language = ocr_config['ocr_language']
                        result['ocr_config'] = ocr_config
                    else:
                        ocr_language = 'eng'  # Default to English
                else:
                    ocr_language = 'eng'  # Default to English
        
        # Try pdfplumber first (better for text layer, preserves formatting)
        if not use_ocr and pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    # Check if PDF is encrypted
                    if pdf.metadata and pdf.metadata.get('/Encrypted') == 'true':
                        error_msg = "PDF is password-protected (encrypted)"
                        result['error'] = error_msg
                        result['error_details'].append(error_msg)
                        return result
                    
                    pages_text = []
                    full_text = []
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            pages_text.append(text)
                            full_text.append(text)
                    
                    if full_text:
                        result['text'] = '\n\n'.join(full_text)
                        result['pages'] = pages_text
                        result['extraction_method'] = 'pdfplumber'
                        result['success'] = True
                        return result
            except Exception as e:
                error_msg = f"pdfplumber failed: {str(e)}"
                # Check for common error types
                error_str = str(e).lower()
                if 'password' in error_str or 'encrypted' in error_str:
                    error_msg = "PDF is password-protected (encrypted)"
                    result['error'] = error_msg
                elif 'corrupt' in error_str or 'damaged' in error_str:
                    error_msg = "PDF appears to be corrupted or damaged"
                    result['error'] = error_msg
                warnings.warn(error_msg)
                result['error_details'].append(error_msg)
        
        # Try PyMuPDF as fallback (also for text layer)
        if not use_ocr and pymupdf:
            try:
                doc = pymupdf.open(pdf_path)
                
                # Check if PDF is encrypted
                if doc.needs_pass:
                    error_msg = "PDF is password-protected (encrypted)"
                    result['error'] = error_msg
                    result['error_details'].append(error_msg)
                    doc.close()
                    return result
                
                pages_text = []
                full_text = []
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    if text:
                        pages_text.append(text)
                        full_text.append(text)
                
                doc.close()
                
                if full_text:
                    result['text'] = '\n\n'.join(full_text)
                    result['pages'] = pages_text
                    result['extraction_method'] = 'pymupdf'
                    result['success'] = True
                    return result
            except Exception as e:
                error_msg = f"PyMuPDF failed: {str(e)}"
                # Check for common error types
                error_str = str(e).lower()
                if 'password' in error_str or 'encrypted' in error_str:
                    error_msg = "PDF is password-protected (encrypted)"
                    result['error'] = error_msg
                elif 'corrupt' in error_str or 'damaged' in error_str:
                    error_msg = "PDF appears to be corrupted or damaged"
                    result['error'] = error_msg
                warnings.warn(error_msg)
                result['error_details'].append(error_msg)
        
        # Use OCR if requested or if text extraction failed
        if use_ocr or (not result['success'] and pytesseract):
            if not pdf2image:
                error_msg = "pdf2image not installed. Cannot use OCR. Install with: pip install pdf2image"
                warnings.warn(error_msg)
                result['error'] = error_msg
                result['error_details'].append(error_msg)
                return result
            if not pytesseract:
                error_msg = "pytesseract not installed. Cannot use OCR. Install with: pip install pytesseract"
                result['error'] = error_msg
                result['error_details'].append(error_msg)
                return result
            
            try:
                # Convert PDF to images
                # Use poppler_path if specified (required on Windows)
                # Validate poppler path before using it
                poppler_to_use = None
                if self.poppler_path:
                    # If poppler_path is explicitly set (not None), validate it
                    poppler_path_obj = Path(self.poppler_path)
                    if poppler_path_obj.exists():
                        # Check for required poppler executables
                        pdftoppm = poppler_path_obj / "pdftoppm.exe"
                        if not pdftoppm.exists():
                            pdftoppm = poppler_path_obj / "pdftoppm"  # Linux/Mac
                        if pdftoppm.exists():
                            poppler_to_use = str(poppler_path_obj)
                        else:
                            error_msg = f"Poppler path found but pdftoppm not found in {self.poppler_path}"
                            result['error'] = error_msg
                            result['error_details'].append(error_msg)
                            warnings.warn(error_msg)
                            return result
                    else:
                        error_msg = f"Poppler path specified but doesn't exist: {self.poppler_path}"
                        result['error'] = error_msg
                        result['error_details'].append(error_msg)
                        warnings.warn(error_msg)
                        return result
                
                # Attempt conversion
                # If poppler_to_use is set, use it; otherwise try system PATH
                if poppler_to_use:
                    images = pdf2image.convert_from_path(str(pdf_path), poppler_path=poppler_to_use)
                else:
                    # Try without path - will use system PATH if poppler is installed there
                    # This works on Linux/Mac and Windows if poppler is in PATH
                    images = pdf2image.convert_from_path(str(pdf_path))
                
                pages_text = []
                full_text = []
                
                ocr_config_used = result.get('ocr_config') or {'ocr_language': ocr_language or 'eng'}
                
                for image in images:
                    # Use specified language or default
                    lang = ocr_language or 'eng'
                    
                    # Extract text with OCR
                    text = pytesseract.image_to_string(image, lang=lang, config='--psm 6')
                    
                    if text.strip():
                        pages_text.append(text)
                        full_text.append(text)
                
                if full_text:
                    result['text'] = '\n\n'.join(full_text)
                    result['pages'] = pages_text
                    result['extraction_method'] = 'ocr'
                    result['ocr_config'] = ocr_config_used
                    result['success'] = True
                else:
                    result['success'] = False
                    result['error'] = 'OCR extracted no text (empty pages or OCR language issue)'
                    result['error_details'].append('OCR completed but no text was extracted')
                    
            except Exception as e:
                error_msg = f"OCR failed: {str(e)}"
                # Provide more helpful error messages
                error_str = str(e).lower()
                if 'poppler' in error_str or 'page count' in error_str:
                    if sys.platform == 'win32':
                        error_msg = f"Poppler not found or not configured correctly. {str(e)}"
                        error_msg += "\n   Install poppler and set POPPLER_PATH environment variable."
                        error_msg += "\n   Or download poppler and place it in the project directory."
                    else:
                        error_msg = f"Poppler not found. Install poppler: sudo apt-get install poppler-utils (Linux) or brew install poppler (Mac)"
                warnings.warn(error_msg)
                result['error'] = error_msg
                result['error_details'].append(error_msg)
        
        # Set final error if all methods failed
        if not result['success']:
            if not result['error']:
                result['error'] = 'All extraction methods failed'
            if not result['error_details']:
                result['error_details'].append('No text could be extracted from PDF')
        
        return result
    
    def extract_words(
        self,
        text: str,
        min_length: int = 2,
        remove_numbers: bool = False,
        lowercase: bool = False
    ) -> List[str]:
        """
        Extract individual words from text.
        
        Args:
            text: Input text
            min_length: Minimum word length
            remove_numbers: Remove words that are only numbers
            lowercase: Convert to lowercase
            
        Returns:
            List of words
        """
        if not text:
            return []
        
        # Extract words using regex (letters, numbers, and common punctuation)
        # This preserves special characters in words like "it's", "don't", etc.
        words = re.findall(r'\b\w+\b', text)
        
        # Filter by length
        words = [w for w in words if len(w) >= min_length]
        
        # Remove numbers if requested
        if remove_numbers:
            words = [w for w in words if not w.isdigit()]
        
        # Convert to lowercase if requested
        if lowercase:
            words = [w.lower() for w in words]
        
        return words
    
    def extract_unique_words(
        self,
        text: str,
        min_length: int = 2,
        remove_numbers: bool = False,
        lowercase: bool = True
    ) -> List[str]:
        """
        Extract unique words from text (removes duplicates).
        
        Args:
            text: Input text
            min_length: Minimum word length
            remove_numbers: Remove words that are only numbers
            lowercase: Convert to lowercase (recommended for uniqueness)
            
        Returns:
            List of unique words (sorted)
        """
        words = self.extract_words(text, min_length, remove_numbers, lowercase)
        unique_words = sorted(list(set(words)))
        return unique_words
    
    def extract_text_statistics(self, text: str) -> Dict[str, any]:
        """
        Get statistics about the extracted text.
        
        Args:
            text: Input text
            
        Returns:
            Dict with statistics:
            - total_chars: int
            - total_words: int
            - total_sentences: int
            - unique_words: int
            - avg_word_length: float
            - avg_sentence_length: float
        """
        if not text:
            return {
                'total_chars': 0,
                'total_words': 0,
                'total_sentences': 0,
                'unique_words': 0,
                'avg_word_length': 0.0,
                'avg_sentence_length': 0.0
            }
        
        words = self.extract_words(text)
        unique_words = self.extract_unique_words(text)
        
        # Count sentences (simple: split by . ! ?)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        stats = {
            'total_chars': len(text),
            'total_words': len(words),
            'total_sentences': len(sentences),
            'unique_words': len(unique_words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0.0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0.0
        }
        
        return stats


def extract_text_from_exam(
    pdf_path: Path,
    course_code: Optional[str] = None,
    use_ocr: bool = False
) -> Dict[str, any]:
    """
    Convenience function to extract text from an exam PDF.
    Automatically detects OCR settings based on course code.
    
    Args:
        pdf_path: Path to PDF file
        course_code: Course code (e.g., 'ARAB100', 'MATH201')
        use_ocr: Whether to force OCR (default: only if text extraction fails)
        
    Returns:
        Dict with extracted text and metadata
    """
    extractor = TextExtractor()
    return extractor.extract_text_from_pdf(pdf_path, use_ocr=use_ocr, course_code=course_code)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        pdf_path = Path("data/exam_downloads/ARAB100.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)
    
    print("=" * 70)
    print(f"TEXT EXTRACTION: {pdf_path.name}")
    print("=" * 70)
    
    extractor = TextExtractor()
    
    # Try text extraction first (no OCR)
    result = extractor.extract_text_from_pdf(pdf_path, use_ocr=False)
    
    if result['success']:
        print(f"✅ Extraction successful using: {result['extraction_method']}")
        print(f"   Pages: {len(result['pages'])}")
        print(f"   Total characters: {len(result['text'])}")
        
        # Extract words
        words = extractor.extract_words(result['text'])
        unique_words = extractor.extract_unique_words(result['text'])
        
        print(f"   Total words: {len(words)}")
        print(f"   Unique words: {len(unique_words)}")
        
        # Show statistics
        stats = extractor.extract_text_statistics(result['text'])
        print(f"\n📊 Statistics:")
        print(f"   Average word length: {stats['avg_word_length']:.2f}")
        print(f"   Average sentence length: {stats['avg_sentence_length']:.2f} words")
        
        # Show first 200 characters
        print(f"\n📄 First 200 characters:")
        print(result['text'][:200] + "...")
        
    else:
        print("❌ Text extraction failed")
        print("   Try using OCR: python exam_analysis/text_extractor.py --ocr <pdf_path>")
    
    print("=" * 70)

