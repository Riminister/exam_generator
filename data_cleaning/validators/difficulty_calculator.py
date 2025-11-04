# Difficulty Score Calculator based on Question Marks
# Calculates difficulty_score = question_marks / total_exam_marks

import re
import sys
from typing import Dict, List, Optional, Tuple, Any

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class DifficultyCalculator:
    """
    Calculate difficulty scores based on question marks vs total exam marks.
    Difficulty score = question_marks / total_exam_marks
    """
    
    def __init__(self):
        # Patterns to extract marks from question text
        # Examples: "(10pts)", "(10 pts)", "10 points", "10pts", "[10 MARKS]", etc.
        self.mark_patterns = [
            r'\((\d+)\s*(?:pts?|points?|marks?)\)',  # (10pts), (10 pts), (10 points), (10 marks)
            r'\[(\d+)\s*(?:pts?|points?|marks?|MARKS?)\]',  # [10 MARKS], [10 marks]
            r'(\d+)\s*(?:pts?|points?|marks?)\s*[\.\)]',  # 10pts., 10 points.
            r'\((\d+)\)',  # (10) - often used in exams
            r'(\d+)\s*(?:pts?|points?|marks?)(?:\s|$)',  # 10pts, 10 points (standalone)
            r'worth\s+(\d+)\s*(?:pts?|points?|marks?)',  # "worth 10 points"
            r'(\d+)\s*(?:pts?|points?|marks?)\s*each',  # "10 points each"
        ]
    
    def extract_question_marks(self, question_text: str) -> Optional[float]:
        """
        Extract marks/points value from question text.
        
        Args:
            question_text: The question text that may contain marks
            
        Returns:
            Marks value as float, or None if not found
        """
        if not question_text:
            return None
        
        # Try each pattern
        for pattern in self.mark_patterns:
            matches = re.findall(pattern, question_text, re.IGNORECASE)
            if matches:
                # Take the first match (usually marks are at the start/end of question)
                try:
                    marks = float(matches[0])
                    if marks > 0:  # Valid marks must be positive
                        return marks
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def calculate_total_exam_marks(self, questions: List[Dict], exam_data: Optional[Dict] = None) -> Optional[float]:
        """
        Calculate total marks for an exam.
        First tries to use total_marks_from_cover (from cover page extraction),
        otherwise sums all question marks.
        
        Args:
            questions: List of question dictionaries
            exam_data: Optional exam dictionary with metadata (may contain total_marks_from_cover)
            
        Returns:
            Total marks as float, or None if unable to calculate
        """
        # Prefer total marks from cover page (more reliable)
        if exam_data and exam_data.get('total_marks_from_cover'):
            cover_total = exam_data['total_marks_from_cover']
            # Validate: should be in reasonable range
            if 10 <= cover_total <= 300:
                return float(cover_total)
        
        # Fallback: sum question marks
        total = 0.0
        found_any = False
        
        for question in questions:
            text = question.get('text', '')
            marks = self.extract_question_marks(text)
            
            if marks is not None:
                total += marks
                found_any = True
        
        if found_any:
            return total
        else:
            return None
    
    def calculate_difficulty_score(
        self, 
        question_marks: Optional[float], 
        total_exam_marks: Optional[float]
    ) -> Optional[float]:
        """
        Calculate difficulty score = question_marks / total_exam_marks.
        
        Args:
            question_marks: Marks for this question (None if not found)
            total_exam_marks: Total marks for the exam (None if not found)
            
        Returns:
            Difficulty score (0-1), or None if unavailable
        """
        if question_marks is None or total_exam_marks is None:
            return None
        
        if total_exam_marks <= 0:
            return None
        
        # Calculate normalized difficulty score
        score = question_marks / total_exam_marks
        
        # Ensure it's in valid range (should be 0-1, but allow slightly >1 for edge cases)
        return max(0.0, min(1.0, score))
    
    def process_exam_questions(self, questions: List[Dict], exam_data: Optional[Dict] = None) -> Tuple[List[Dict], Dict]:
        """
        Process all questions in an exam to calculate difficulty scores.
        
        Args:
            questions: List of question dictionaries with 'text' field
            exam_data: Optional exam dictionary with metadata (for cover page total marks)
            
        Returns:
            Tuple of (updated_questions, stats_dict)
            stats_dict contains:
                - total_exam_marks: Total marks found
                - questions_with_marks: Count of questions with marks found
                - questions_without_marks: Count of questions without marks
                - questions_with_scores: Count of questions with calculated scores
                - marks_source: 'cover_page' or 'calculated_sum'
        """
        stats = {
            'total_exam_marks': None,
            'questions_with_marks': 0,
            'questions_without_marks': 0,
            'questions_with_scores': 0,
            'marks_source': None,
        }
        
        # First pass: extract marks for each question
        question_marks_list = []
        for question in questions:
            text = question.get('text', '')
            marks = self.extract_question_marks(text)
            question_marks_list.append(marks)
            
            if marks is not None:
                stats['questions_with_marks'] += 1
            else:
                stats['questions_without_marks'] += 1
        
        # Calculate total exam marks (prefer cover page if available)
        total_marks = self.calculate_total_exam_marks(questions, exam_data)
        
        # Track where marks came from
        if exam_data and exam_data.get('total_marks_from_cover') and total_marks == exam_data['total_marks_from_cover']:
            stats['marks_source'] = 'cover_page'
        elif total_marks:
            stats['marks_source'] = 'calculated_sum'
        
        # Error handling: if total marks > 300, likely extraction error
        if total_marks is not None and total_marks > 300:
            print(f"   Warning: Total marks ({total_marks}) exceeds 300, likely extraction error")
            print(f"   Setting total marks to None for this exam")
            total_marks = None
        
        stats['total_exam_marks'] = total_marks
        
        # Second pass: calculate difficulty scores
        updated_questions = []
        for question, question_marks in zip(questions, question_marks_list):
            updated_q = question.copy()
            
            # Calculate difficulty score
            difficulty = self.calculate_difficulty_score(question_marks, total_marks)
            updated_q['difficulty_score'] = difficulty
            updated_q['question_marks'] = question_marks  # Store raw marks too
            
            if difficulty is not None:
                stats['questions_with_scores'] += 1
            
            updated_questions.append(updated_q)
        
        return updated_questions, stats


def calculate_difficulty_from_marks(
    input_file: str = "data/exam_analysis.json",
    output_file: Optional[str] = None
) -> Dict:
    """
    Process exam data to calculate difficulty scores based on marks.
    
    Args:
        input_file: Input JSON file with exam data
        output_file: Output JSON file (None = same as input_file to overwrite)
        
    Returns:
        Dictionary with processing statistics
    """
    import json
    from pathlib import Path
    
    if output_file is None:
        output_file = input_file
    
    print("=" * 70)
    print("CALCULATING DIFFICULTY SCORES FROM MARKS")
    print("=" * 70)
    
    # Load data
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return {}
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats: {exams: [...]} and {questions: [...]}
    if 'exams' in data:
        exams_list = data['exams']
    elif 'questions' in data:
        # Convert flat list format to exam format for processing
        exams_list = [{'questions': data['questions'], 'filename': 'unknown'}]
    else:
        print("❌ Error: Expected 'exams' or 'questions' key in JSON")
        return {}
    
    calculator = DifficultyCalculator()
    overall_stats = {
        'exams_processed': 0,
        'exams_with_marks': 0,
        'exams_without_marks': 0,
        'total_questions_with_scores': 0,
        'total_questions_without_scores': 0,
    }
    
    # Process each exam
    for exam in exams_list:
        questions = exam.get('questions', [])
        if not questions:
            continue
        
        overall_stats['exams_processed'] += 1
        
        # Process questions for this exam (pass exam dict for cover page marks)
        updated_questions, stats = calculator.process_exam_questions(questions, exam)
        exam['questions'] = updated_questions
        
        # Update overall stats
        if stats['total_exam_marks'] is not None:
            overall_stats['exams_with_marks'] += 1
        else:
            overall_stats['exams_without_marks'] += 1
        
        overall_stats['total_questions_with_scores'] += stats['questions_with_scores']
        overall_stats['total_questions_without_scores'] += stats['questions_without_marks']
        
        # Print exam-level stats
        filename = exam.get('filename', 'unknown')
        total_marks = stats['total_exam_marks'] if stats['total_exam_marks'] else 'Not found'
        marks_count = stats['questions_with_marks']
        scores_count = stats['questions_with_scores']
        marks_source = stats.get('marks_source', 'unknown')
        print(f"\nExam: {filename}")
        print(f"   Total marks: {total_marks} (from {marks_source})")
        print(f"   Questions with marks: {marks_count}/{len(questions)}")
        print(f"   Questions with scores: {scores_count}/{len(questions)}")
    
    # Save updated data
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Exams processed: {overall_stats['exams_processed']}")
    print(f"Exams with marks: {overall_stats['exams_with_marks']}")
    print(f"Exams without marks: {overall_stats['exams_without_marks']}")
    print(f"Questions with scores: {overall_stats['total_questions_with_scores']}")
    print(f"Questions without scores: {overall_stats['total_questions_without_scores']}")
    print(f"\nUpdated data saved to: {output_file}")
    print("=" * 70)
    
    return overall_stats


if __name__ == "__main__":
    calculate_difficulty_from_marks()

