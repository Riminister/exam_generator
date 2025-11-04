#!/usr/bin/env python3
"""Check current data status"""

import json
from pathlib import Path

def check_data_status():
    """Check current data status"""
    print("=" * 70)
    print("DATA STATUS CHECK")
    print("=" * 70)
    print()
    
    # Check exam_analysis.json
    exam_file = Path("data/exam_analysis.json")
    if exam_file.exists():
        with open(exam_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        exams = data.get('exams', [])
        total_questions = sum(len(e.get('questions', [])) for e in exams)
        print(f"exam_analysis.json:")
        print(f"  Exams: {len(exams)}")
        print(f"  Total Questions: {total_questions}")
        print()
        
        # Show exam breakdown
        print("Exam Breakdown:")
        for exam in exams:
            q_count = len(exam.get('questions', []))
            filename = exam.get('filename', 'unknown')
            course = exam.get('course_code', 'N/A')
            print(f"  - {filename}: {q_count} questions (Course: {course})")
    else:
        print("exam_analysis.json: NOT FOUND")
    
    print()
    
    # Check extracted_text.json
    extracted_file = Path("data/extracted_text.json")
    if extracted_file.exists():
        with open(extracted_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        extractions = data.get('extractions', [])
        print(f"extracted_text.json:")
        print(f"  Extractions: {len(extractions)}")
    else:
        print("extracted_text.json: NOT FOUND")
    
    print()
    
    # Check to_process folder
    to_process = Path("data/exam_downloads/to_process")
    if to_process.exists():
        pdfs = list(to_process.glob("*.pdf"))
        print(f"PDFs in to_process/: {len(pdfs)}")
        if len(pdfs) > 0:
            print(f"  (These PDFs failed extraction and need OCR)")
    else:
        print("to_process/ folder: NOT FOUND")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    check_data_status()

