#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Cover Page Metadata from All Exams
Updates exam_analysis.json with metadata from cover pages: faculty, professor, total marks, date
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import our modules (relative imports)
from .cover_page_parser import CoverPageParser
from .ocr_context_selector import OCRContextSelector

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def process_exam_metadata(
    input_file: str = "data/exam_analysis.json",
    pdf_directory: str = "data/exam_downloads",
    output_file: Optional[str] = None
) -> Dict:
    """
    Process all exams and extract cover page metadata.
    
    Args:
        input_file: Input JSON file with exam data
        pdf_directory: Directory containing PDF files
        output_file: Output JSON file (None = same as input_file)
        
    Returns:
        Dictionary with processing statistics
    """
    if output_file is None:
        output_file = input_file
    
    print("=" * 70)
    print("EXTRACTING COVER PAGE METADATA")
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
    if not pdf_dir.exists():
        print(f"❌ Error: PDF directory not found: {pdf_directory}")
        return {}
    
    parser = CoverPageParser()
    ocr_selector = OCRContextSelector()
    
    stats = {
        'exams_processed': 0,
        'exams_with_metadata': 0,
        'exams_with_course_code': 0,
        'exams_with_professor': 0,
        'exams_with_faculty': 0,
        'exams_with_total_marks': 0,
        'exams_with_date': 0,
        'exams_updated': 0
    }
    
    # Process each exam
    for exam in data['exams']:
        filename = exam.get('filename', '')
        if not filename:
            continue
        
        stats['exams_processed'] += 1
        pdf_path = pdf_dir / filename
        
        if not pdf_path.exists():
            print(f"\n⚠️  PDF not found: {filename}")
            continue
        
        print(f"\nProcessing: {filename}")
        
        # Parse cover page
        metadata = parser.parse_cover_page(pdf_path)
        
        # Get OCR context
        course_code = metadata.get('course_code') or exam.get('course_code')
        first_page_text = parser.extract_first_page_text(pdf_path)
        ocr_config = ocr_selector.detect_exam_type(course_code, first_page_text)
        
        # Update exam data
        updated = False
        
        # Update course_code if found on cover page
        if metadata.get('course_code') and metadata['course_code'] != exam.get('course_code'):
            exam['course_code'] = metadata['course_code']
            updated = True
            stats['exams_with_course_code'] += 1
        
        # Add course_name if found
        if metadata.get('course_name'):
            exam['course_name'] = metadata['course_name']
            updated = True
        
        # Add faculty if found
        if metadata.get('faculty'):
            exam['faculty'] = metadata['faculty']
            updated = True
            stats['exams_with_faculty'] += 1
        
        # Add professor if found
        if metadata.get('professor'):
            exam['professor'] = metadata['professor']
            updated = True
            stats['exams_with_professor'] += 1
        
        # Add total marks from cover page (prefer over calculated sum)
        if metadata.get('total_marks'):
            exam['total_marks_from_cover'] = metadata['total_marks']
            updated = True
            stats['exams_with_total_marks'] += 1
        
        # Add date info if found
        if metadata.get('date_info'):
            date_info = metadata['date_info']
            exam['exam_date'] = date_info.get('parsed_date')
            exam['exam_year'] = date_info.get('year')
            exam['exam_month'] = date_info.get('month')
            exam['exam_day'] = date_info.get('day')
            exam['date_string'] = date_info.get('date_string')
            exam['relevance_score'] = date_info.get('relevance_score')
            updated = True
            stats['exams_with_date'] += 1
        
        # Add OCR context info
        exam['ocr_config'] = {
            'ocr_language': ocr_config['ocr_language'],
            'exam_type': ocr_config['exam_type'],
            'needs_math_ocr': ocr_config['needs_math_ocr'],
            'detected_language': ocr_config.get('detected_language'),
            'recommended_ocr_method': ocr_config.get('recommended_ocr_method', 'tesseract')
        }
        
        # Print what was found
        if metadata['extraction_success']:
            stats['exams_with_metadata'] += 1
            found_items = []
            if metadata.get('course_code'):
                found_items.append(f"Course: {metadata['course_code']}")
            if metadata.get('professor'):
                found_items.append(f"Professor: {metadata['professor']}")
            if metadata.get('faculty'):
                found_items.append(f"Faculty: {metadata['faculty']}")
            if metadata.get('total_marks'):
                found_items.append(f"Total Marks: {metadata['total_marks']}")
            if metadata.get('date_info'):
                found_items.append(f"Date: {metadata['date_info'].get('date_string')} ({metadata['date_info'].get('year')})")
            
            if found_items:
                print(f"   ✅ Found: {', '.join(found_items)}")
            else:
                print(f"   ⚠️  Cover page extracted but no metadata found")
        else:
            print(f"   ⚠️  Could not extract cover page")
        
        if updated:
            stats['exams_updated'] += 1
    
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
    print(f"Exams with metadata extracted: {stats['exams_with_metadata']}")
    print(f"Exams updated: {stats['exams_updated']}")
    print(f"\nMetadata found:")
    print(f"  - Course codes: {stats['exams_with_course_code']}")
    print(f"  - Professors: {stats['exams_with_professor']}")
    print(f"  - Faculties: {stats['exams_with_faculty']}")
    print(f"  - Total marks: {stats['exams_with_total_marks']}")
    print(f"  - Dates: {stats['exams_with_date']}")
    print(f"\n✅ Updated data saved to: {output_file}")
    print("=" * 70)
    
    return stats


if __name__ == "__main__":
    process_exam_metadata()

