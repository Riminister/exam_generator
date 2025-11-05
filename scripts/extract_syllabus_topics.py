#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Topics from Course Syllabi
Processes syllabus PDFs and extracts course topics for dropdown menus
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

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
    from text_extraction.pdf_processing.text_extractor import TextExtractor
    from text_extraction.pdf_processing.cover_page_parser import CoverPageParser
except ImportError:
    print("❌ Error: Could not import text extraction modules")
    sys.exit(1)


def extract_course_code_from_filename(filename: str) -> Optional[str]:
    """Extract course code from filename (e.g., ECON212.pdf -> ECON212)"""
    if not filename:
        return None
    
    stem = Path(filename).stem
    
    # Match course code patterns
    patterns = [
        r'^([A-Z]{2,4}\d{3,4}[A-Z]?)',  # ECON212, ECON110A
        r'([A-Z]{2,4}\d{3,4})',          # ECON 212 (with space)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, stem.upper())
        if match:
            code = match.group(1).replace(' ', '').upper()
            if re.match(r'^[A-Z]{2,4}\d{3,4}[A-Z]?$', code):
                return code
    
    return None


def extract_topics_from_text(text: str) -> List[str]:
    """
    Extract topics from syllabus text.
    Looks for common patterns like:
    - "Topics:" or "Course Topics:"
    - Numbered/bulleted lists
    - Chapter/section headings
    """
    topics = []
    
    if not text or len(text) < 50:
        return topics
    
    text_lines = text.split('\n')
    
    # Common topic section headers
    topic_headers = [
        r'topics?\s*:',
        r'course\s+topics?\s*:',
        r'course\s+content\s*:',
        r'course\s+outline\s*:',
        r'subject\s+matter\s*:',
        r'covered\s+topics?\s*:',
        r'learning\s+objectives?\s*:',
        r'chapter\s+\d+',
        r'unit\s+\d+',
        r'week\s+\d+',
    ]
    
    in_topic_section = False
    topic_section_lines = []
    
    # Find topic section
    for i, line in enumerate(text_lines):
        line_lower = line.lower().strip()
        
        # Check if this line is a topic header
        for header_pattern in topic_headers:
            if re.search(header_pattern, line_lower):
                in_topic_section = True
                # Start collecting from next few lines
                break
        
        if in_topic_section:
            # Collect lines until we hit a clear section break
            if line.strip():
                # Stop if we hit another major section
                if re.search(r'^(textbook|required\s+reading|assessment|grading|exam|assignment|schedule)', line_lower):
                    break
                topic_section_lines.append(line.strip())
                
                # Stop after collecting too many lines (likely not topics)
                if len(topic_section_lines) > 50:
                    break
    
    # Extract topics from collected lines
    for line in topic_section_lines:
        # Remove numbering (1., 2., i., ii., etc.)
        cleaned = re.sub(r'^[\d\w]+[\.\)]\s*', '', line)
        cleaned = re.sub(r'^[ivx]+\.\s*', '', cleaned, flags=re.IGNORECASE)
        
        # Remove common prefixes
        cleaned = re.sub(r'^(chapter|unit|week|lecture|topic)\s+\d+[:\s]*', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up
        cleaned = cleaned.strip()
        
        # Skip if too short or looks like metadata
        if len(cleaned) < 3 or len(cleaned) > 100:
            continue
        
        # Skip if it's just a header or separator
        if cleaned.lower() in ['topics', 'course topics', 'content', '']:
            continue
        
        # Skip if it's mostly numbers or symbols
        if re.match(r'^[\d\s\-\.]+$', cleaned):
            continue
        
        # Add if it looks like a topic
        if cleaned and cleaned not in topics:
            topics.append(cleaned)
    
    # If we didn't find topics in a section, try to find bulleted/numbered lists
    if not topics:
        for line in text_lines:
            # Look for lines starting with bullets or numbers
            if re.match(r'^[\s]*[•\-\*\d]+[\s]+[A-Z]', line):
                cleaned = re.sub(r'^[\s]*[•\-\*\d]+[\s]+', '', line).strip()
                if 5 < len(cleaned) < 80 and cleaned not in topics:
                    topics.append(cleaned)
    
    # Limit to reasonable number of topics
    return topics[:30]


def extract_syllabus_topics(
    syllabus_dir: str = "data/syllabi",
    output_file: str = "data/syllabus_topics.json",
    use_ocr: bool = True
) -> Dict:
    """
    Extract topics from all syllabus PDFs.
    
    Args:
        syllabus_dir: Directory containing syllabus PDFs
        output_file: Output JSON file for topics
        use_ocr: Whether to use OCR for scanned PDFs
        
    Returns:
        Dictionary with extraction statistics
    """
    print("\n" + "=" * 70)
    print("EXTRACTING TOPICS FROM COURSE SYLLABI")
    print("=" * 70)
    print(f"\nSyllabus directory: {syllabus_dir}")
    print(f"Output file: {output_file}")
    print(f"Use OCR: {use_ocr}")
    print("=" * 70)
    
    syllabus_path = Path(syllabus_dir)
    if not syllabus_path.exists():
        print(f"⚠️  Creating syllabus directory: {syllabus_dir}")
        syllabus_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Please add syllabus PDF files to: {syllabus_path.absolute()}")
        return {}
    
    # Find all PDF files
    pdf_files = list(syllabus_path.glob("*.pdf"))
    if not pdf_files:
        print(f"\n⚠️  No PDF files found in {syllabus_dir}")
        print(f"   Please add syllabus PDF files to: {syllabus_path.absolute()}")
        return {}
    
    print(f"\nFound {len(pdf_files)} syllabus file(s)")
    
    # Load existing topics if any
    existing_topics = {}
    output_path = Path(output_file)
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_topics = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load existing topics: {e}")
    
    # Initialize extractor
    extractor = TextExtractor()
    parser = CoverPageParser()
    
    stats = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'topics_extracted': 0,
        'courses_updated': 0
    }
    
    # Process each syllabus
    for pdf_file in pdf_files:
        stats['processed'] += 1
        course_code = extract_course_code_from_filename(pdf_file.name)
        
        if not course_code:
            print(f"\n⚠️  {pdf_file.name}: Could not extract course code from filename")
            print(f"   Expected format: ECON212.pdf or ECON110A.pdf")
            stats['failed'] += 1
            continue
        
        print(f"\n📄 Processing: {pdf_file.name}")
        print(f"   Course Code: {course_code}")
        
        # Extract text from PDF
        result = extractor.extract_text_from_pdf(
            pdf_file,
            use_ocr=use_ocr,
            course_code=course_code
        )
        
        if not result.get('success'):
            error = result.get('error', 'Unknown error')
            print(f"   ❌ Failed to extract text: {error}")
            stats['failed'] += 1
            continue
        
        text = result.get('text', '')
        if not text or len(text) < 100:
            print(f"   ⚠️  Extracted text too short or empty")
            stats['failed'] += 1
            continue
        
        print(f"   ✅ Extracted {len(text)} characters")
        
        # Extract topics
        topics = extract_topics_from_text(text)
        
        if not topics:
            print(f"   ⚠️  No topics found in syllabus")
            stats['failed'] += 1
            continue
        
        # Store topics
        existing_topics[course_code] = {
            'course_code': course_code,
            'filename': pdf_file.name,
            'topics': topics,
            'topic_count': len(topics)
        }
        
        stats['successful'] += 1
        stats['topics_extracted'] += len(topics)
        stats['courses_updated'] += 1
        
        print(f"   ✅ Extracted {len(topics)} topics")
        print(f"   📋 Topics: {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
    
    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_topics, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Syllabi processed: {stats['processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total topics extracted: {stats['topics_extracted']}")
    print(f"Courses with topics: {stats['courses_updated']}")
    print(f"\n✅ Topics saved to: {output_file}")
    print("=" * 70)
    
    if stats['successful'] > 0:
        print("\n🎉 Topics are now available in the Streamlit app!")
        print("   The topic dropdown will appear when you select a course.")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract topics from course syllabi")
    parser.add_argument(
        "--syllabus-dir",
        default="data/syllabi",
        help="Directory containing syllabus PDFs (default: data/syllabi)"
    )
    parser.add_argument(
        "--output",
        default="data/syllabus_topics.json",
        help="Output JSON file (default: data/syllabus_topics.json)"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Skip OCR (only use text extraction)"
    )
    
    args = parser.parse_args()
    
    extract_syllabus_topics(
        syllabus_dir=args.syllabus_dir,
        output_file=args.output,
        use_ocr=not args.no_ocr
    )

