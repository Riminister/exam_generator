#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse Questions from Extracted Text
Converts extracted_text.json → exam_analysis.json with individual questions
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import from same directory
try:
    from text_extraction.question_parsing.question_type_detector import QuestionTypeDetector
except ImportError:
    # Fallback for direct script execution
    from question_type_detector import QuestionTypeDetector

# Import from data_cleaning
try:
    from data_cleaning.validators.difficulty_calculator import DifficultyCalculator
except ImportError:
    # Fallback
    from difficulty_calculator import DifficultyCalculator

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class QuestionParser:
    """
    Parses questions from extracted exam text.
    """
    
    def __init__(self):
        self.type_detector = QuestionTypeDetector()
        self.difficulty_calc = DifficultyCalculator()
        
        # Patterns for question markers
        self.question_patterns = [
            r'^(\d+)\.\s+',           # 1. 2. 3.
            r'^Question\s+(\d+)',      # Question 1, Question 2
            r'^Q(\d+)\.',              # Q1. Q2.
            r'^(\d+)\)\s+',            # 1) 2) 3)
            r'^[IVX]+\.\s+',           # I. II. III. IV. (Roman numerals)
        ]
    
    def extract_questions_from_text(self, text: str, course_code: Optional[str] = None) -> List[Dict]:
        """
        Extract individual questions from exam text.
        
        Args:
            text: Full exam text
            course_code: Optional course code for context
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # Remove page numbers and headers
        text = self._clean_text(text)
        
        # Split by question markers
        # Try multiple patterns to find questions
        question_splits = []
        
        # Pattern 1: Numbered questions (1., 2., 3.)
        pattern1 = re.compile(r'(?=^(\d+)\.\s+)', re.MULTILINE)
        matches = list(pattern1.finditer(text))
        
        if len(matches) >= 2:
            # Found numbered questions
            for i, match in enumerate(matches):
                start = match.start()
                if i < len(matches) - 1:
                    end = matches[i + 1].start()
                else:
                    end = len(text)
                
                question_text = text[start:end].strip()
                if len(question_text) > 20:  # Minimum length filter
                    question_splits.append({
                        'text': question_text,
                        'number': int(match.group(1)) if match.group(1) else None
                    })
        else:
            # Pattern 2: Roman numerals (I., II., III.)
            pattern2 = re.compile(r'(?=^([IVX]+)\.\s+)', re.MULTILINE)
            matches = list(pattern2.finditer(text))
            
            if len(matches) >= 2:
                for i, match in enumerate(matches):
                    start = match.start()
                    if i < len(matches) - 1:
                        end = matches[i + 1].start()
                    else:
                        end = len(text)
                    
                    question_text = text[start:end].strip()
                    if len(question_text) > 20:
                        # Convert roman to number
                        roman = match.group(1)
                        num = self._roman_to_int(roman)
                        question_splits.append({
                            'text': question_text,
                            'number': num
                        })
            else:
                # Pattern 3: Generic splits by double newlines or long lines
                # This is a fallback
                paragraphs = text.split('\n\n')
                for i, para in enumerate(paragraphs):
                    para = para.strip()
                    if len(para) > 50 and any(keyword in para.lower() for keyword in 
                                             ['?', 'answer', 'explain', 'calculate', 'describe', 'discuss']):
                        question_splits.append({
                            'text': para,
                            'number': i + 1
                        })
        
        # Convert to question objects
        question_num = 1
        for split in question_splits:
            q_text = split['text']
            q_num = split.get('number') or question_num
            
            # Detect question type
            q_type = self.type_detector.detect_question_type(q_text, len(q_text))
            
            # Extract difficulty/marks
            marks = self.difficulty_calc.extract_question_marks(q_text)
            
            question = {
                'question_number': q_num,
                'text': q_text,
                'question_type': q_type,
                'length': len(q_text),
                'question_marks': marks,
                'topics': [],
                'difficulty_score': None  # Will be calculated later
            }
            
            questions.append(question)
            question_num = q_num + 1
        
        return questions
    
    def _clean_text(self, text: str) -> str:
        """Remove page numbers and common headers."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip pure page numbers
            if re.match(r'^\d+\s*$', line.strip()):
                continue
            # Skip common headers
            if any(header in line for header in [
                'QUEEN\'S UNIVERSITY', 'FINAL EXAMINATION', 'FACULTY OF',
                'INSTRUCTIONS TO STUDENTS', 'ANSWER ALL QUESTIONS'
            ]):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _roman_to_int(self, roman: str) -> int:
        """Convert roman numeral to integer."""
        roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        result = 0
        prev_value = 0
        
        for char in reversed(roman):
            value = roman_map.get(char, 0)
            if value < prev_value:
                result -= value
            else:
                result += value
            prev_value = value
        
        return result


def parse_extracted_text_to_questions(
    input_file: str = "data/extracted_text.json",
    output_file: str = "data/exam_analysis.json"
) -> Dict:
    """
    Parse extracted text into structured questions.
    
    Args:
        input_file: Path to extracted_text.json
        output_file: Path to save exam_analysis.json
        
    Returns:
        Dictionary with parsing statistics
    """
    print("=" * 70)
    print("PARSING QUESTIONS FROM EXTRACTED TEXT")
    print("=" * 70)
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return {}
    
    # Load extracted text
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = QuestionParser()
    difficulty_calc = DifficultyCalculator()
    
    results = {
        'exams': [],
        'stats': {
            'total_exams': 0,
            'total_questions': 0,
            'exams_parsed': 0,
            'exams_failed': 0
        }
    }
    
    # Process each extraction
    for extraction in data.get('extractions', []):
        filename = extraction.get('filename', 'unknown')
        course_code = extraction.get('course_code')
        text = extraction.get('text', '')
        
        print(f"\n📄 Processing: {filename}")
        
        if not text or len(text.strip()) < 100:
            print(f"   ⚠️  Skipping: Text too short or empty")
            results['stats']['exams_failed'] += 1
            continue
        
        # Extract questions
        try:
            questions = parser.extract_questions_from_text(text, course_code)
            
            if not questions:
                print(f"   ⚠️  No questions found")
                results['stats']['exams_failed'] += 1
                continue
            
            # Calculate difficulty scores
            questions_with_difficulty, difficulty_stats = difficulty_calc.process_exam_questions(questions)
            
            # Create exam entry
            exam_data = {
                'filename': filename,
                'course_code': course_code,
                'year': None,
                'text_length': len(text),
                'question_count': len(questions_with_difficulty),
                'questions': questions_with_difficulty
            }
            
            results['exams'].append(exam_data)
            results['stats']['total_exams'] += 1
            results['stats']['total_questions'] += len(questions_with_difficulty)
            results['stats']['exams_parsed'] += 1
            
            print(f"   ✅ Found {len(questions_with_difficulty)} questions")
            print(f"   📊 Marks found: {difficulty_stats['questions_with_marks']}/{len(questions_with_difficulty)}")
            
        except Exception as e:
            print(f"   ❌ Error parsing: {e}")
            results['stats']['exams_failed'] += 1
            continue
    
    # Save results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total exams processed: {results['stats']['total_exams']}")
    print(f"Successfully parsed: {results['stats']['exams_parsed']}")
    print(f"Failed: {results['stats']['exams_failed']}")
    print(f"Total questions extracted: {results['stats']['total_questions']}")
    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    parse_extracted_text_to_questions()

