#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detect and update question types in exam data
Adds multiple_choice detection and other question types
"""

import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from text_extraction.question_parsing.question_type_detector import detect_question_types_in_data

if __name__ == "__main__":
    print("\n" + "="*70)
    print("QUESTION TYPE DETECTION")
    print("="*70)
    print("\nThis script detects question types including:")
    print("  - multiple_choice (A), B), C), D), E) options)")
    print("  - true_false (True/False questions)")
    print("  - numerical (Calculate, compute, solve)")
    print("  - essay (Explain, describe, discuss)")
    print("  - short_answer (What is, Who is, etc.)")
    print("  - other (default)")
    print("\nRunning detection...\n")
    
    # Run detection
    stats = detect_question_types_in_data(
        input_file="data/exam_analysis.json",
        output_file="data/exam_analysis.json"  # Overwrite input file
    )
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review the updated exam_analysis.json file")
    print("2. Run data cleaning: python exam_analysis/run_cleaning.py")
    print("   (This will extract multiple choice options)")
    print("3. Re-run model building to see improved classification")
    print("="*70 + "\n")

