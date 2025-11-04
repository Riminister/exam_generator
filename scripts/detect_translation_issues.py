#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detect translation questions with poor OCR quality
Run this to identify questions that need re-extraction with proper language support
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

from exam_analysis.translation_detector import detect_translation_issues_in_file

def main():
    print("\n" + "=" * 70)
    print("TRANSLATION QUESTION & OCR QUALITY DETECTOR")
    print("=" * 70)
    print("\nThis script detects:")
    print("  1. Translation questions (e.g., 'Translate into English')")
    print("  2. Poor OCR quality (garbled text, especially for Arabic)")
    print("  3. Questions that need re-extraction with proper language support")
    print("\n" + "=" * 70)

    input_file = "data/exam_analysis.json"
    output_file = "data/exam_analysis.json"  # Overwrite input file

    try:
        stats = detect_translation_issues_in_file(input_file, output_file)
        
        print("\n" + "=" * 70)
        print("RESULTS BY EXAM")
        print("=" * 70)
        
        for exam_stat in stats['exam_stats']:
            print(f"\n📄 Exam: {exam_stat['filename']}")
            print(f"   Total questions: {exam_stat['total_questions']}")
            print(f"   Translation questions: {exam_stat['translation_questions']} ({exam_stat['translation_percentage']:.1f}%)")
            print(f"   Poor OCR detected: {exam_stat['poor_ocr_count']} ({exam_stat['poor_ocr_percentage']:.1f}%)")
            print(f"   Needs re-extraction: {exam_stat['needs_re_extraction']}")
            print(f"   High priority: {exam_stat['high_priority_re_extraction']}")
            if exam_stat['languages_detected']:
                print(f"   Languages detected: {', '.join(exam_stat['languages_detected'].keys())}")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        total_translation = sum(s['translation_questions'] for s in stats['exam_stats'])
        total_poor_ocr = sum(s['poor_ocr_count'] for s in stats['exam_stats'])
        total_high_priority = sum(s['high_priority_re_extraction'] for s in stats['exam_stats'])
        
        print(f"Exams processed: {stats['exams_processed']}")
        print(f"Total translation questions: {total_translation}")
        print(f"Total with poor OCR: {total_poor_ocr}")
        print(f"High priority re-extraction: {total_high_priority}")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Review questions marked with:")
        print("   - 'is_translation_question': true")
        print("   - 'has_poor_ocr': true")
        print("   - 'needs_re_extraction': true")
        print("   - 'ocr_priority': 'high'")
        print("\n2. For Arabic questions, see OCR_RE_EXTRACTION_GUIDE.md")
        print("   for instructions on re-extracting with Arabic language support")
        print("\n3. Questions with 'ocr_language_needed' show which language")
        print("   OCR engine should be configured for")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

