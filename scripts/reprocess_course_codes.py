#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reprocess All Files to Extract Course Codes
Extracts course codes from filenames and cover pages, then updates exam_analysis.json
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from text_extraction.pdf_processing.cover_page_parser import CoverPageParser
    COVER_PAGE_AVAILABLE = True
except ImportError:
    COVER_PAGE_AVAILABLE = False
    print("⚠️  Cover page parser not available. Will only extract from filenames.")


def extract_course_code_from_filename(filename: str) -> Optional[str]:
    """
    Extract course code from filename.
    Examples:
        ECON212 (1).pdf -> ECON212
        ECON212_SUM.pdf -> ECON212
        econ212.pdf -> ECON212
        ECON110A_s3_4.pdf -> ECON110A
    """
    if not filename:
        return None
    
    # Remove extension
    stem = Path(filename).stem
    
    # Try patterns (order matters - most specific first)
    # First, try to match standard course codes (e.g., ECON212, ECON110A)
    # Pattern: 2-4 letters, 3-4 digits, optional single letter suffix
    standard_pattern = r'^([A-Z]{2,4}\d{3,4}[A-Z]?)(?:_|$|\(|\s|SUM|APR|DEC|apr|dec|sum)'
    match = re.match(standard_pattern, stem.upper())
    if match:
        code = match.group(1)
        if re.match(r'^[A-Z]{2,4}\d{3,4}[A-Z]?$', code):
            return code
    
    # Fallback: try to find course code anywhere in filename
    patterns = [
        r'([A-Z]{2,4}\d{3,4}[A-Z]?)(?:_|$|\(|\s|SUM|APR|DEC)',  # ECON212, ECON110A before separators
        r'([A-Z]{2,4}\d{3,4})',        # ECON212 (no suffix)
        r'([A-Z]{2,4}\s*\d{3,4})',     # ECON 212 (with space)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, stem.upper())
        if matches:
            # Take the first match and clean it
            code = matches[0].replace(' ', '').upper()
            # Basic validation: should be letters + numbers, optional single letter suffix
            if re.match(r'^[A-Z]{2,4}\d{3,4}[A-Z]?$', code):
                # Don't include suffix if it's clearly a suffix word (apr, dec, sum)
                if code.endswith('A') and 'APR' in stem.upper():
                    return code[:-1]  # Remove A from ECON212A if APR is in filename
                if code.endswith('D') and 'DEC' in stem.upper():
                    return code[:-1]  # Remove D from ECON212D if DEC is in filename
                if code.endswith('S') and ('SUM' in stem.upper() or 'SUMMER' in stem.upper()):
                    return code[:-1]  # Remove S from ECON212S if SUM is in filename
                return code
    
    return None


def reprocess_course_codes(
    input_file: str = "data/exam_analysis.json",
    pdf_directory: str = "data/exam_downloads",
    use_cover_page: bool = True,
    output_file: Optional[str] = None
) -> Dict:
    """
    Reprocess all exams to extract course codes.
    
    Args:
        input_file: Path to exam_analysis.json
        pdf_directory: Directory containing PDF files
        use_cover_page: Whether to also extract from cover pages
        output_file: Output file (None = overwrite input_file)
        
    Returns:
        Statistics dictionary
    """
    if output_file is None:
        output_file = input_file
    
    print("\n" + "=" * 70)
    print("REPROCESSING COURSE CODES")
    print("=" * 70)
    print(f"\nInput file: {input_file}")
    print(f"PDF directory: {pdf_directory}")
    print(f"Extract from cover pages: {use_cover_page}")
    print("=" * 70)
    
    # Load data
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return {}
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'exams' not in data:
        print("❌ Error: Expected 'exams' key in JSON")
        return {}
    
    pdf_dir = Path(pdf_directory)
    
    # Initialize cover page parser if available
    parser = None
    if use_cover_page and COVER_PAGE_AVAILABLE:
        parser = CoverPageParser()
    
    stats = {
        'exams_processed': 0,
        'exams_with_existing_code': 0,
        'exams_missing_code': 0,
        'codes_from_filename': 0,
        'codes_from_cover_page': 0,
        'codes_updated': 0,
        'exams_not_found': 0
    }
    
    # Process each exam
    for exam in data['exams']:
        filename = exam.get('filename', '')
        if not filename:
            continue
        
        stats['exams_processed'] += 1
        current_code = exam.get('course_code')
        
        # Check if already has course code
        # But also check if it needs normalization (e.g., ECON212A from ECON212apr)
        if current_code:
            # Try to extract from filename to see if we can improve it
            code_from_filename = extract_course_code_from_filename(filename)
            
            # If filename extraction gives a better code (without false suffix), update it
            if code_from_filename and code_from_filename != current_code:
                # Check if the new code is better (removes false suffixes like A, D, S from apr/dec/sum)
                if len(code_from_filename) < len(current_code) or \
                   (not code_from_filename.endswith(('A', 'D', 'S')) and current_code.endswith(('A', 'D', 'S'))):
                    exam['course_code'] = code_from_filename
                    stats['codes_updated'] += 1
                    stats['codes_from_filename'] += 1
                    print(f"\n📄 {filename}: Updated course code: {current_code} → {code_from_filename}")
                    continue
            else:
                stats['exams_with_existing_code'] += 1
                print(f"\n✅ {filename}: Already has course code: {current_code}")
                continue
        
        stats['exams_missing_code'] += 1
        print(f"\n📄 Processing: {filename}")
        
        # Try to extract from filename first
        code_from_filename = extract_course_code_from_filename(filename)
        
        # Try to extract from cover page if PDF exists
        code_from_cover = None
        pdf_path = pdf_dir / filename
        
        if use_cover_page and parser and pdf_path.exists():
            try:
                metadata = parser.parse_cover_page(pdf_path)
                code_from_cover = metadata.get('course_code')
            except Exception as e:
                print(f"   ⚠️  Error extracting from cover page: {e}")
        elif not pdf_path.exists():
            stats['exams_not_found'] += 1
            print(f"   ⚠️  PDF not found: {pdf_path}")
        
        # Prioritize: cover page > filename
        new_code = code_from_cover or code_from_filename
        
        if new_code:
            exam['course_code'] = new_code
            stats['codes_updated'] += 1
            
            source = "cover page" if code_from_cover else "filename"
            print(f"   ✅ Extracted course code: {new_code} (from {source})")
            
            if code_from_cover:
                stats['codes_from_cover_page'] += 1
            if code_from_filename:
                stats['codes_from_filename'] += 1
        else:
            print(f"   ❌ Could not extract course code")
    
    # Save updated data
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Exams processed: {stats['exams_processed']}")
    print(f"Exams with existing course code: {stats['exams_with_existing_code']}")
    print(f"Exams missing course code: {stats['exams_missing_code']}")
    print(f"\nCourse codes extracted:")
    print(f"  - From filenames: {stats['codes_from_filename']}")
    print(f"  - From cover pages: {stats['codes_from_cover_page']}")
    print(f"  - Total updated: {stats['codes_updated']}")
    if stats['exams_not_found'] > 0:
        print(f"  - PDFs not found: {stats['exams_not_found']}")
    print(f"\n✅ Updated data saved to: {output_file}")
    print("=" * 70)
    
    return stats


if __name__ == "__main__":
    # Check if user wants to process all PDFs in a directory
    import argparse
    
    parser = argparse.ArgumentParser(description="Reprocess course codes from filenames and cover pages")
    parser.add_argument(
        "--input",
        default="data/exam_analysis.json",
        help="Input JSON file (default: data/exam_analysis.json)"
    )
    parser.add_argument(
        "--pdf-dir",
        default="data/exam_downloads",
        help="PDF directory (default: data/exam_downloads)"
    )
    parser.add_argument(
        "--no-cover-page",
        action="store_true",
        help="Skip cover page extraction (only use filenames)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (default: overwrite input file)"
    )
    
    args = parser.parse_args()
    
    reprocess_course_codes(
        input_file=args.input,
        pdf_directory=args.pdf_dir,
        use_cover_page=not args.no_cover_page,
        output_file=args.output
    )

