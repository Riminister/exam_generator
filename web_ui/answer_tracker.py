"""
Answer Tracker for Difficulty Score Calculation
Tracks user answer attempts and calculates difficulty based on success rates
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AnswerTracker:
    """Track user answer attempts and calculate difficulty scores"""
    
    def __init__(self, data_file: str = "data/user_answer_data.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing answer data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'questions': {},
            'stats': {
                'total_attempts': 0,
                'total_correct': 0,
                'total_incorrect': 0
            }
        }
    
    def _save_data(self):
        """Save answer data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def _get_question_id(self, question_text: str) -> str:
        """Generate a unique ID for a question"""
        import hashlib
        return hashlib.md5(question_text.encode()).hexdigest()[:16]
    
    def record_attempt(
        self,
        question_text: str,
        user_answer: str,
        correct_answer: str,
        question_type: str,
        topic: str,
        course_code: str
    ) -> Dict:
        """
        Record a user's answer attempt
        
        Returns:
            Dictionary with attempt result and updated difficulty score
        """
        question_id = self._get_question_id(question_text)
        
        # Initialize question data if not exists
        if question_id not in self.data['questions']:
            self.data['questions'][question_id] = {
                'question_text': question_text,
                'correct_answer': correct_answer,
                'question_type': question_type,
                'topic': topic,
                'course_code': course_code,
                'attempts': [],
                'correct_count': 0,
                'total_attempts': 0,
                'success_rate': None,
                'calculated_difficulty': None
            }
        
        question_data = self.data['questions'][question_id]
        
        # Check if answer is correct (simple comparison, can be improved)
        is_correct = self._compare_answers(user_answer, correct_answer)
        
        # Record attempt
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'user_answer': user_answer,
            'is_correct': is_correct
        }
        question_data['attempts'].append(attempt)
        question_data['total_attempts'] += 1
        
        if is_correct:
            question_data['correct_count'] += 1
            self.data['stats']['total_correct'] += 1
        else:
            self.data['stats']['total_incorrect'] += 1
        
        self.data['stats']['total_attempts'] += 1
        
        # Calculate success rate
        success_rate = question_data['correct_count'] / question_data['total_attempts']
        question_data['success_rate'] = success_rate
        
        # Calculate difficulty score (lower success rate = higher difficulty)
        # Inverse relationship: success_rate 0.9 = difficulty 0.1, success_rate 0.1 = difficulty 0.9
        calculated_difficulty = 1.0 - success_rate
        question_data['calculated_difficulty'] = calculated_difficulty
        
        self._save_data()
        
        return {
            'is_correct': is_correct,
            'success_rate': success_rate,
            'calculated_difficulty': calculated_difficulty,
            'total_attempts': question_data['total_attempts'],
            'correct_count': question_data['correct_count']
        }
    
    def _compare_answers(self, user_answer: str, correct_answer: str) -> bool:
        """
        Compare user answer with correct answer.
        This is a simple implementation - can be enhanced with fuzzy matching.
        """
        import re
        
        # Normalize both answers
        user_normalized = re.sub(r'[^\w\s]', '', user_answer.lower().strip())
        correct_normalized = re.sub(r'[^\w\s]', '', correct_answer.lower().strip())
        
        # Exact match
        if user_normalized == correct_normalized:
            return True
        
        # Check if user answer is contained in correct answer (for partial credit)
        if user_normalized in correct_normalized and len(user_normalized) > 5:
            return True
        
        # Check if correct answer is contained in user answer
        if correct_normalized in user_normalized and len(correct_normalized) > 5:
            return True
        
        return False
    
    def get_question_stats(self, question_text: str) -> Optional[Dict]:
        """Get statistics for a specific question"""
        question_id = self._get_question_id(question_text)
        return self.data['questions'].get(question_id)
    
    def get_overall_stats(self) -> Dict:
        """Get overall statistics"""
        return self.data['stats']


def extract_multiple_choice_options(answer_text: str) -> List[str]:
    """Extract multiple choice options from answer text"""
    import re
    
    # Look for patterns like "A) option", "1. option", etc.
    options = []
    patterns = [
        r'([A-E])[\)\.]\s*([^\n]+)',
        r'(\d+)[\)\.]\s*([^\n]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, answer_text)
        for match in matches:
            options.append(match[1].strip())
    
    return options if options else None

