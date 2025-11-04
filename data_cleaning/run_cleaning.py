#!/usr/bin/env python3
"""
Convenience script to run the complete data cleaning pipeline.
This script orchestrates the cleaning process with user-friendly output.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import from data_cleaning module
from data_cleaning.cleaners.data_cleaner import clean_exam_data, ExamDataCleaner
import json


def main():
    """Run the data cleaning pipeline."""
    # Fix encoding for Windows
    if sys.platform == 'win32':
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 70)
    print("EXAM DATA CLEANING PIPELINE")
    print("=" * 70)
    print()
    
    # Check for input file
    input_file = "data/exam_analysis.json"
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"⚠️  Input file not found: {input_file}")
        print()
        print("The exam_analysis.json file should already exist in the data/ folder.")
        print("If it doesn't, you may need to extract questions from PDFs first.")
        print()
        return 1
    
    print(f"✅ Found input file: {input_file}")
    
    # Check file contents
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count questions from exams structure
        if 'exams' in data:
            questions_count = sum(len(exam.get('questions', [])) for exam in data.get('exams', []))
            exams_count = len(data.get('exams', []))
        elif 'questions' in data:
            questions_count = len(data.get('questions', []))
            exams_count = 0
        else:
            questions_count = 0
            exams_count = 0
        
        print(f"   📊 Contains {questions_count} questions from {exams_count} exams")
        print()
        
        if questions_count == 0:
            print("❌ No questions found in input file.")
            print("   The analysis may not have extracted any questions.")
            return 1
            
    except json.JSONDecodeError:
        print(f"❌ Error: {input_file} is not valid JSON")
        return 1
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1
    
    # Set output paths
    output_json = "exam_analysis/cleaned_questions.json"
    output_csv = "exam_analysis/cleaned_questions.csv"
    
    # Ensure output directory exists
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Starting cleaning process...")
    print()
    
    try:
        # Run the cleaning pipeline
        cleaned_questions = clean_exam_data(
            input_file=input_file,
            output_json=output_json,
            output_csv=output_csv
        )
        
        if not cleaned_questions:
            print("❌ Cleaning process failed or produced no results")
            return 1
        
        print()
        print("=" * 70)
        print("✨ CLEANING COMPLETE!")
        print("=" * 70)
        print()
        print(f"📁 Output files created:")
        print(f"   JSON: {output_json}")
        print(f"   CSV:  {output_csv}")
        print()
        print("📝 Next steps:")
        print("   1. Review the cleaned questions in the output files")
        print("   2. Check the cleaning statistics above")
        print("   3. Use cleaned data for ML model training")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleaning interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during cleaning: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

