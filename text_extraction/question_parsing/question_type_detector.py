#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Type Detector
Detects question types: multiple_choice, essay, short_answer, numerical, true_false, other
"""

import re
from typing import Dict, List, Optional


class QuestionTypeDetector:
    """
    Detects question types based on text patterns and structure.
    """
    
    def __init__(self):
        # Multiple choice patterns - look for options like A) B) C) or (a) (b) (c)
        self.mc_patterns = [
            r'[A-E]\)\s+[A-Z]',      # A) Option text
            r'\([a-e]\)\s+[A-Z]',     # (a) Option text
            r'[a-e]\.\s+[A-Z]',       # a. Option text
            r'^[A-E]\s+[A-Z]',        # A Option text (at start)
        ]
        
        # True/False patterns
        self.tf_patterns = [
            r'\btrue\s+or\s+false\b',
            r'\btrue/false\b',
            r'\bT/F\b',
            r'\bt\.?\s*f\.?\b',
            r'circle\s+(true|false)',
        ]
        
        # Numerical/calculation patterns
        self.numerical_patterns = [
            r'\bcalculate\b',
            r'\bcompute\b',
            r'\bfind\s+(the\s+)?(value|result|answer|solution)',
            r'\bsolve\s+for\b',
            r'\bevaluate\b',
            r'\bdetermine\s+(the\s+)?(value|number|amount)',
            r'\d+\s*[+\-*/=]\s*\d+',  # Contains math operations
        ]
        
        # Short answer patterns (typically short, direct questions)
        self.short_answer_patterns = [
            r'^\w+\s+is\s+',          # "What is...", "Who is..."
            r'^\w+\s+are\s+',         # "What are...", "Where are..."
            r'^\w+\s+does\s+',        # "What does..."
            r'^\w+\s+do\s+',          # "What do..."
            r'name\s+',
            r'list\s+',
            r'identify\s+',
        ]
        
        # Essay patterns (longer, requires explanation)
        self.essay_patterns = [
            r'\bexplain\b',
            r'\bdescribe\b',
            r'\bdiscuss\b',
            r'\banalyze\b',
            r'\bcompare\b',
            r'\bcontrast\b',
            r'\bevaluate\b',
            r'\bcritique\b',
            r'\bargue\b',
            r'\bprove\b',
            r'\bshow\s+that\b',
            r'\bwhy\b',
            r'\bhow\b',
        ]
    
    def detect_multiple_choice(self, text: str) -> bool:
        """
        Detect if question is multiple choice.
        
        Checks for:
        - Multiple option markers (A), B), C), D), E))
        - At least 2 options present
        - Common MC patterns
        """
        # Count option markers
        option_count = 0
        
        # Check for uppercase letter options
        uppercase_options = len(re.findall(r'[A-E]\)', text))
        lowercase_options = len(re.findall(r'\([a-e]\)', text))
        dot_options = len(re.findall(r'[a-e]\.\s', text))
        
        option_count = max(uppercase_options, lowercase_options, dot_options)
        
        # Multiple choice typically has 2-5 options
        if option_count >= 2:
            return True
        
        # Check for patterns that indicate MC format
        mc_indicators = [
            'choose the best',
            'select the',
            'circle the',
            'mark the',
            'which of the following',
            'all of the above',
            'none of the above',
        ]
        
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in mc_indicators):
            if option_count >= 1:  # At least one option marker found
                return True
        
        return False
    
    def detect_question_type(self, text: str, length: Optional[int] = None) -> str:
        """
        Detect question type from text.
        
        Args:
            text: Question text
            length: Optional question length in characters
            
        Returns:
            Question type: 'multiple_choice', 'true_false', 'numerical', 
                          'essay', 'short_answer', or 'other'
        """
        if not text:
            return 'other'
        
        text_lower = text.lower()
        
        # Check multiple choice first (most specific pattern)
        if self.detect_multiple_choice(text):
            return 'multiple_choice'
        
        # Check true/false
        if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.tf_patterns):
            return 'true_false'
        
        # Check numerical/calculation (if it's not too long, likely not essay)
        has_numerical = any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.numerical_patterns)
        if has_numerical:
            # If question is short and has calculations, it's numerical
            # If long with calculations, might still be essay (e.g., "Explain and calculate...")
            if length and length < 200:
                return 'numerical'
            elif not length and len(text) < 200:
                return 'numerical'
        
        # Check essay (typically longer and uses essay keywords)
        has_essay_keywords = any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.essay_patterns)
        if has_essay_keywords:
            # If very short, might be short answer
            if length and length > 150:
                return 'essay'
            elif not length and len(text) > 150:
                return 'essay'
        
        # Check short answer (short questions starting with what/who/where)
        if any(re.search(pattern, text_lower) for pattern in self.short_answer_patterns):
            # Short answer is typically shorter than essay
            if length and length < 200:
                return 'short_answer'
            elif not length and len(text) < 200:
                return 'short_answer'
        
        # Default to 'other' if no clear pattern
        return 'other'
    
    def detect_question_types_batch(self, questions: List[Dict]) -> List[Dict]:
        """
        Detect question types for a batch of questions.
        
        Args:
            questions: List of question dictionaries with 'text' and optionally 'length'
            
        Returns:
            Updated questions with 'question_type' added/updated
        """
        updated_questions = []
        
        for question in questions:
            updated_q = question.copy()
            text = question.get('text', '')
            length = question.get('length') or len(text)
            
            # Only detect if question_type is not already set or is 'other'
            current_type = question.get('question_type', 'other')
            if current_type == 'other' or not current_type:
                detected_type = self.detect_question_type(text, length)
                updated_q['question_type'] = detected_type
            else:
                # Preserve existing type (e.g., 'sub_question' detected earlier)
                updated_q['question_type'] = current_type
            
            updated_questions.append(updated_q)
        
        return updated_questions


def detect_question_types_in_data(
    input_file: str = "data/exam_analysis.json",
    output_file: Optional[str] = None
) -> Dict:
    """
    Detect question types for all questions in exam data.
    
    Args:
        input_file: Input JSON file with exam data
        output_file: Output JSON file (None = same as input_file)
        
    Returns:
        Dictionary with detection statistics
    """
    import json
    from pathlib import Path
    
    if output_file is None:
        output_file = input_file
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return {}
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'exams' not in data:
        print("❌ Error: Expected 'exams' key in JSON")
        return {}
    
    detector = QuestionTypeDetector()
    stats = {
        'total_questions': 0,
        'type_counts': {},
        'exams_processed': 0
    }
    
    print("=" * 70)
    print("DETECTING QUESTION TYPES")
    print("=" * 70)
    
    # Process each exam
    for exam in data.get('exams', []):
        questions = exam.get('questions', [])
        if not questions:
            continue
        
        filename = exam.get('filename', 'unknown')
        updated_questions = detector.detect_question_types_batch(questions)
        exam['questions'] = updated_questions
        
        # Count types
        for q in updated_questions:
            qtype = q.get('question_type', 'other')
            stats['type_counts'][qtype] = stats['type_counts'].get(qtype, 0) + 1
            stats['total_questions'] += 1
        
        stats['exams_processed'] += 1
        print(f"\n{filename}: {len(updated_questions)} questions processed")
    
    # Save updated data
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Exams processed: {stats['exams_processed']}")
    print(f"Total questions: {stats['total_questions']}")
    print(f"\nQuestion type distribution:")
    for qtype, count in sorted(stats['type_counts'].items(), key=lambda x: x[1], reverse=True):
        pct = count / stats['total_questions'] * 100 if stats['total_questions'] > 0 else 0
        print(f"  {qtype}: {count} ({pct:.1f}%)")
    
    print(f"\n✅ Updated data saved to: {output_file}")
    print("=" * 70)
    
    return stats


if __name__ == "__main__":
    detect_question_types_in_data()

