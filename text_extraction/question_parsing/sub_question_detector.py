# Sub-Question Detector
# Detects sub-questions (e.g., a), i., ii.) that follow numbered questions

import re
from typing import List, Dict


class SubQuestionDetector:
    """
    Detects sub-questions in exam data.
    A sub-question is identified when:
    1. Question text starts with letter/roman numeral markers (a), b), i., ii., etc.)
    2. Previous question starts with a number (1., 2., etc.)
    """
    
    def __init__(self):
        # Patterns for sub-question markers
        self.sub_question_patterns = [
            r'^[a-z]\)\s',           # a) b) c) (with space)
            r'^[a-z]\)',             # a) b) c) (without space)
            r'^\([a-z]\)\s',         # (a) (b) (c)
            r'^\([a-z]\)',           # (a)(b)(c)
            r'^[a-z]\.\s',           # a. b. c. (with space)
            r'^[a-z]\.',             # a.b.c. (without space)
            r'^[ivx]+\.\s',          # i. ii. iii. (with space)
            r'^[ivx]+\.',            # i.ii.iii. (without space)
            r'^\([ivx]+\)\s',        # (i) (ii) (iii)
            r'^\([ivx]+\)',          # (i)(ii)(iii)
        ]
        
        # Patterns for main question markers (numbered)
        self.main_question_patterns = [
            r'^\d+\.\s',             # 1. 2. 3. (with space after)
            r'^\d+\.',                # 1. 2. 7. (period without space)
            r'^Question\s+\d+',      # Question 1, Question 2
            r'^Q\d+\.',              # Q1. Q2.
            r'^\d+\)\s',             # 1) 2) 3)
            r'^\d+\s',               # 1  2  3 (number with space)
        ]
    
    def is_main_question(self, text: str) -> bool:
        """
        Check if question text starts with a main question marker (number).
        
        Args:
            text: Question text
            
        Returns:
            True if starts with numbered marker
        """
        if not text:
            return False
        
        text_stripped = text.strip()
        
        for pattern in self.main_question_patterns:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return True
        
        return False
    
    def is_sub_question_marker(self, text: str) -> bool:
        """
        Check if question text starts with a sub-question marker.
        
        Args:
            text: Question text
            
        Returns:
            True if starts with sub-question marker
        """
        if not text:
            return False
        
        text_stripped = text.strip()
        
        for pattern in self.sub_question_patterns:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return True
        
        return False
    
    def detect_sub_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Detect and mark sub-questions in a list of questions.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Updated list with sub_question question_type set
        """
        updated_questions = []
        
        for i, question in enumerate(questions):
            updated_q = question.copy()
            text = question.get('text', '')
            
            # Check if this looks like a sub-question
            if self.is_sub_question_marker(text):
                # Check if previous question was a main question
                if i > 0:
                    prev_question = questions[i-1]
                    prev_text = prev_question.get('text', '')
                    
                    if self.is_main_question(prev_text):
                        # This is a sub-question following a main question!
                        updated_q['question_type'] = 'sub_question'
                        updated_q['is_sub_question'] = True
                        updated_q['parent_question_number'] = prev_question.get('question_number')
                    else:
                        # Previous wasn't a main question, but check if it's part of sub-question sequence
                        prev_is_sub = prev_question.get('question_type') == 'sub_question'
                        prev_has_flag = prev_question.get('is_sub_question', False)
                        
                        if prev_is_sub or prev_has_flag:
                            # We're in a sequence of sub-questions
                            updated_q['question_type'] = 'sub_question'
                            updated_q['is_sub_question'] = True
                            # Inherit parent from previous sub-question
                            parent_num = prev_question.get('parent_question_number')
                            if parent_num is not None:
                                updated_q['parent_question_number'] = parent_num
                            else:
                                # Previous sub-question didn't have parent, use its question number
                                updated_q['parent_question_number'] = prev_question.get('question_number')
                else:
                    # First question in list can't be a sub-question (no previous question)
                    pass
            
            updated_questions.append(updated_q)
        
        return updated_questions
    
    def get_sub_question_stats(self, questions: List[Dict]) -> Dict:
        """
        Get statistics about sub-questions in the dataset.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Dictionary with sub-question statistics
        """
        sub_question_count = sum(1 for q in questions if q.get('question_type') == 'sub_question')
        total_questions = len(questions)
        
        return {
            'total_questions': total_questions,
            'sub_questions': sub_question_count,
            'main_questions': total_questions - sub_question_count,
            'sub_question_percentage': (sub_question_count / total_questions * 100) if total_questions > 0 else 0
        }


def detect_sub_questions_in_data(
    input_file: str = "data/exam_analysis.json",
    output_file: str = None
) -> Dict:
    """
    Process exam data to detect and mark sub-questions.
    
    Args:
        input_file: Input JSON file
        output_file: Output JSON file (None = same as input)
        
    Returns:
        Dictionary with processing statistics
    """
    import json
    from pathlib import Path
    
    if output_file is None:
        output_file = input_file
    
    print("=" * 70)
    print("SUB-QUESTION DETECTION")
    print("=" * 70)
    
    # Load data
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        return {}
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both data formats
    if 'exams' in data:
        exams_list = data['exams']
    elif 'questions' in data:
        exams_list = [{'questions': data['questions'], 'filename': 'unknown'}]
    else:
        print("Error: Expected 'exams' or 'questions' key in JSON")
        return {}
    
    detector = SubQuestionDetector()
    overall_stats = {
        'exams_processed': 0,
        'total_sub_questions': 0,
        'total_main_questions': 0,
    }
    
    # Process each exam
    for exam in exams_list:
        questions = exam.get('questions', [])
        if not questions:
            continue
        
        overall_stats['exams_processed'] += 1
        filename = exam.get('filename', 'unknown')
        
        # Detect sub-questions
        updated_questions = detector.detect_sub_questions(questions)
        exam['questions'] = updated_questions
        
        # Get stats
        stats = detector.get_sub_question_stats(updated_questions)
        overall_stats['total_sub_questions'] += stats['sub_questions']
        overall_stats['total_main_questions'] += stats['main_questions']
        
        print(f"\nExam: {filename}")
        print(f"   Total questions: {stats['total_questions']}")
        print(f"   Sub-questions: {stats['sub_questions']} ({stats['sub_question_percentage']:.1f}%)")
        print(f"   Main questions: {stats['main_questions']}")
    
    # Save updated data
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Exams processed: {overall_stats['exams_processed']}")
    print(f"Total sub-questions detected: {overall_stats['total_sub_questions']}")
    print(f"Total main questions: {overall_stats['total_main_questions']}")
    print(f"\nUpdated data saved to: {output_file}")
    print("=" * 70)
    
    return overall_stats


if __name__ == "__main__":
    detect_sub_questions_in_data()

