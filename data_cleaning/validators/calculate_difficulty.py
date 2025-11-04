#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate difficulty scores from question marks
Run this to update difficulty scores in your exam data based on marks
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

from data_cleaning.validators.difficulty_calculator import calculate_difficulty_from_marks

if __name__ == "__main__":
    print("\n" + "="*70)
    print("DIFFICULTY SCORE CALCULATOR")
    print("="*70)
    print("\nThis script calculates difficulty scores based on question marks.")
    print("Formula: difficulty_score = question_marks / total_exam_marks")
    print("\nIf marks are not found, difficulty_score will be set to None (unavailable).\n")
    
    # Run the calculation
    stats = calculate_difficulty_from_marks(
        input_file="data/exam_analysis.json",
        output_file="data/exam_analysis.json"  # Overwrite input file
    )
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review the updated exam_analysis.json file")
    print("2. Run data cleaning: python exam_analysis/run_cleaning.py")
    print("   (This will preserve the new difficulty scores)")
    print("3. Questions without marks will have difficulty_score = null")
    print("="*70 + "\n")

