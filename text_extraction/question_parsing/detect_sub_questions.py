#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detect and mark sub-questions in exam data
Sub-questions are identified when they start with letters/roman numerals (a), i.) 
and follow a numbered question
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from text_extraction.question_parsing.sub_question_detector import detect_sub_questions_in_data

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUB-QUESTION DETECTION")
    print("="*70)
    print("\nThis script detects sub-questions in your exam data.")
    print("Sub-questions start with letters/roman numerals (a), i., ii.)")
    print("and follow numbered questions (1., 2., etc.)")
    print("\nSub-questions will be marked with question_type = 'sub_question'\n")
    
    # Run detection
    stats = detect_sub_questions_in_data(
        input_file="data/exam_analysis.json",
        output_file="data/exam_analysis.json"  # Overwrite input file
    )
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review the updated exam_analysis.json file")
    print("2. Run data cleaning: python exam_analysis/run_cleaning.py")
    print("   (This will preserve sub_question types)")
    print("3. Sub-questions can be filtered or grouped with parent questions")
    print("="*70 + "\n")

