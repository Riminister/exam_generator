#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Text from All Exam PDFs
Bulk text extraction with intelligent OCR selection
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import from same directory - handle both relative and absolute imports
try:
    # Try relative import first (when used as a module)
    from .text_extractor import TextExtractor, extract_text_from_exam
except ImportError:
    # Fallback to absolute import (when run as a script)
    # Add parent directory to path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from text_extraction.pdf_processing.text_extractor import TextExtractor, extract_text_from_exam

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def find_poppler_path() -> Optional[str]:
    """
    Automatically find poppler bin directory.
    Checks: environment variable, project root, script directories, system PATH, and common install locations.
    
    Returns:
        Path to poppler bin directory, or None if not found
    """
    # Check environment variable first
    env_path = os.environ.get('POPPLER_PATH')
    if env_path and Path(env_path).exists():
        return env_path
    
    # Find project root (go up from script directory to find project root)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # text_extraction/pdf_processing -> text_extraction -> project root
    
    # Look for poppler in common locations
    possible_paths = [
        # Project root level (where user placed it)
        project_root / "Release-25.07.0-0" / "poppler-25.07.0" / "Library" / "bin",
        project_root / "poppler" / "bin",
        project_root / "poppler" / "Library" / "bin",
        # Relative to script directory
        script_dir / "Release-25.07.0-0" / "poppler-25.07.0" / "Library" / "bin",
        script_dir / "poppler" / "bin",
        script_dir / "poppler" / "Library" / "bin",
    ]
    
    for path in possible_paths:
        if path.exists():
            # Check for pdftoppm.exe (required for pdf2image)
            pdftoppm = path / "pdftoppm.exe" if sys.platform == 'win32' else path / "pdftoppm"
            if pdftoppm.exists():
                return str(path)
            # Also check for pdftotext.exe as fallback
            pdftotext = path / "pdftotext.exe" if sys.platform == 'win32' else path / "pdftotext"
            if pdftotext.exists():
                return str(path)
    
    # Check if poppler is in system PATH (try to run it)
    if sys.platform == 'win32':
        import subprocess
        try:
            # Try to run pdftoppm to see if it's in PATH
            result = subprocess.run(
                ['pdftoppm', '-h'],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            # If it runs without error, poppler is in PATH
            # Return None to let pdf2image use system PATH
            return None  # None means "use system PATH"
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        # Check common Windows installation locations
        common_paths = [
            Path("C:/poppler/bin"),
            Path("C:/Program Files/poppler/bin"),
            Path("C:/Program Files (x86)/poppler/bin"),
            Path(os.environ.get('LOCALAPPDATA', '')) / "poppler" / "bin",
            Path(os.environ.get('PROGRAMFILES', '')) / "poppler" / "bin",
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / "poppler" / "bin",
        ]
        
        for path in common_paths:
            if path.exists() and (path / "pdftoppm.exe").exists():
                return str(path)
    
    return None


def find_tesseract_cmd() -> Optional[str]:
    """
    Automatically find Tesseract executable.
    
    Returns:
        Path to Tesseract executable, or None if not found
    """
    # Check environment variable first
    env_cmd = os.environ.get('TESSERACT_CMD')
    if env_cmd and Path(env_cmd).exists():
        return env_cmd
    
    # Look for Tesseract in common Windows installation locations
    if sys.platform == 'win32':
        script_dir = Path(__file__).parent
        possible_paths = [
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            # Project directory
            script_dir / "tesseract" / "bin" / "tesseract.exe",
            script_dir / "Tesseract-OCR" / "tesseract.exe",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
    
    return None


def extract_all_exams(
    pdf_directory: str = "data/exam_downloads",
    output_file: str = "data/extracted_text.json",
    use_ocr: bool = False,
    course_codes: Optional[Dict[str, str]] = None,
    to_process_folder: str = "processed",
    processed_folder: str = "to_process"
) -> Dict:
    """
    Extract text from all PDFs in a directory.
    Automatically moves processed PDFs from to_process to processed folder.
    
    Args:
        pdf_directory: Base directory containing subfolders
        output_file: Output JSON file for extracted text
        use_ocr: Whether to use OCR for all PDFs
        course_codes: Optional dict mapping filename -> course_code
        to_process_folder: Subfolder name containing PDFs to process
        processed_folder: Subfolder name for processed PDFs
        
    Returns:
        Dictionary with extraction statistics
    """
    # Set up folder paths
    base_dir = Path(pdf_directory)
    to_process_dir = base_dir / to_process_folder
    processed_dir = base_dir / processed_folder
    
    # Create folders if they don't exist
    to_process_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if to_process folder exists and has PDFs
    if not to_process_dir.exists():
        print(f"❌ To-process directory not found: {to_process_dir}")
        return {}
    
    # Check if there are any PDFs to process
    pdf_files = list(to_process_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"ℹ️  No PDFs found in {to_process_dir}")
        print(f"   All exams may already be processed (check {processed_dir})")
        return {}
    
    # Find and configure poppler path
    poppler_path = find_poppler_path()
    if poppler_path:
        # Validate the poppler path
        poppler_path_obj = Path(poppler_path)
        if poppler_path_obj.exists():
            # Check for pdftoppm (required for pdf2image)
            pdftoppm = poppler_path_obj / "pdftoppm.exe" if sys.platform == 'win32' else poppler_path_obj / "pdftoppm"
            if pdftoppm.exists():
                print(f"✅ Using Poppler from: {poppler_path_obj.resolve()}")
            else:
                print(f"⚠️  Poppler path found but pdftoppm not found: {poppler_path}")
                print("   OCR may fail. Checking for poppler executables...")
                poppler_path = None  # Reset to None if invalid
        else:
            print(f"⚠️  Poppler path specified but doesn't exist: {poppler_path}")
            poppler_path = None
    else:
        # Check if poppler might be in system PATH
        import subprocess
        try:
            result = subprocess.run(
                ['pdftoppm', '-h'] if sys.platform != 'win32' else ['pdftoppm.exe', '-h'],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            print("✅ Poppler found in system PATH (will use automatically)")
            # Set to None to let pdf2image use system PATH
            poppler_path = None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            print("⚠️  Poppler not found in project or system PATH.")
            print("   Options:")
            print("   1. Set POPPLER_PATH environment variable")
            print("   2. Install poppler and add to system PATH")
            print("   3. Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases/")
            print("   4. Extract to project root: Release-25.07.0-0/poppler-25.07.0/Library/bin/")
    
    # Find and configure Tesseract
    tesseract_cmd = find_tesseract_cmd()
    if tesseract_cmd:
        print(f"📍 Using Tesseract from: {tesseract_cmd}")
    else:
        print("⚠️  Tesseract not found. OCR will not work.")
        print("   Set TESSERACT_CMD environment variable or ensure tesseract is in PATH.")
    
    extractor = TextExtractor(poppler_path=poppler_path, tesseract_cmd=tesseract_cmd)
    results = {
        'extractions': [],
        'stats': {
            'total_pdfs': 0,
            'successful': 0,
            'failed': 0,
            'used_ocr': 0,
            'total_words': 0,
            'total_chars': 0,
            'moved_to_processed': 0
        }
    }
    
    results['stats']['total_pdfs'] = len(pdf_files)
    
    print("=" * 70)
    print(f"EXTRACTING TEXT FROM {len(pdf_files)} PDFs")
    print(f"Source: {to_process_dir}")
    print(f"Destination: {processed_dir}")
    print("=" * 70)
    
    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        
        # Get course code if provided
        course_code = None
        if course_codes and pdf_path.name in course_codes:
            course_code = course_codes[pdf_path.name]
        elif course_codes is None:
            # Try to extract from filename (e.g., ECON310.pdf -> ECON310)
            stem = pdf_path.stem
            if re.match(r'^[A-Z]{2,}\d{3,4}$', stem.upper()):
                course_code = stem.upper()
        
        # Extract text
        extraction_result = extractor.extract_text_from_pdf(
            pdf_path,
            use_ocr=use_ocr,
            course_code=course_code
        )
        
        if extraction_result['success']:
            results['stats']['successful'] += 1
            if extraction_result['extraction_method'] == 'ocr':
                results['stats']['used_ocr'] += 1
            
            # Extract words and statistics
            words = extractor.extract_words(extraction_result['text'])
            stats = extractor.extract_text_statistics(extraction_result['text'])
            
            results['stats']['total_words'] += len(words)
            results['stats']['total_chars'] += len(extraction_result['text'])
            
            # Store result
            extraction_data = {
                'filename': pdf_path.name,
                'course_code': course_code,
                'extraction_method': extraction_result['extraction_method'],
                'num_pages': len(extraction_result['pages']),
                'text_length': len(extraction_result['text']),
                'num_words': len(words),
                'num_unique_words': len(extractor.extract_unique_words(extraction_result['text'])),
                'statistics': stats,
                'ocr_config': extraction_result.get('ocr_config'),
                'text': extraction_result['text'],  # Full text
                'pages': extraction_result['pages']  # Text per page
            }
            
            results['extractions'].append(extraction_data)
            
            # Move successfully processed PDF to processed folder
            try:
                destination = processed_dir / pdf_path.name
                pdf_path.rename(destination)
                results['stats']['moved_to_processed'] += 1
                print(f"   ✅ Success ({extraction_result['extraction_method']})")
                print(f"   📁 Moved to: {processed_folder}/")
            except Exception as e:
                print(f"   ✅ Success ({extraction_result['extraction_method']})")
                print(f"   ⚠️  Could not move file: {e}")
            
            print(f"   Pages: {extraction_data['num_pages']}")
            print(f"   Words: {extraction_data['num_words']}")
            if extraction_result.get('ocr_config'):
                print(f"   OCR Language: {extraction_result['ocr_config'].get('ocr_language')}")
        else:
            results['stats']['failed'] += 1
            error_msg = extraction_result.get('error', 'Unknown error')
            error_details = extraction_result.get('error_details', [])
            
            print(f"   ❌ Failed (file remains in {to_process_folder}/)")
            print(f"   Error: {error_msg}")
            if error_details:
                for detail in error_details[:2]:  # Show first 2 error details
                    print(f"   └─ {detail}")
            
            # Store error info for debugging
            extraction_data = {
                'filename': pdf_path.name,
                'course_code': course_code,
                'success': False,

                'error': error_msg,
                'error_details': error_details
            }
            results['extractions'].append(extraction_data)
    
    # Save results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total PDFs: {results['stats']['total_pdfs']}")
    print(f"Successful: {results['stats']['successful']}")
    print(f"Failed: {results['stats']['failed']}")
    print(f"Moved to processed: {results['stats']['moved_to_processed']}")
    print(f"Used OCR: {results['stats']['used_ocr']}")
    print(f"Total words extracted: {results['stats']['total_words']:,}")
    print(f"Total characters: {results['stats']['total_chars']:,}")
    print(f"\n✅ Results saved to: {output_file}")
    print(f"\n📁 Folder Status:")
    remaining = len(list(to_process_dir.glob("*.pdf")))
    processed_count = len(list(processed_dir.glob("*.pdf")))
    print(f"   {to_process_folder}/: {remaining} PDFs remaining")
    print(f"   {processed_folder}/: {processed_count} PDFs processed")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract text from exam PDFs")
    parser.add_argument('--from-folder', type=str, default='processed',
                       help='Folder to read PDFs from (default: processed)')
    parser.add_argument('--to-folder', type=str, default='to_process',
                       help='Folder to move PDFs to after processing (default: to_process)')
    parser.add_argument('--use-ocr', action='store_true',
                       help='Force OCR for all PDFs')
    parser.add_argument('--output', type=str, default='data/extracted_text.json',
                       help='Output JSON file (default: data/extracted_text.json)')
    
    args = parser.parse_args()
    
    # Extract all PDFs with specified options
    extract_all_exams(
        use_ocr=args.use_ocr,
        to_process_folder=args.from_folder,
        processed_folder=args.to_folder,
        output_file=args.output
    )

