#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detect translation questions with poor OCR quality
Identifies questions that contain garbled text (likely Arabic/foreign language)
that was poorly OCR'd, especially translation exercises.
"""

import re
from typing import Dict, List, Optional, Tuple


class TranslationDetector:
    """
    Detects translation questions and flags poor OCR quality for foreign languages.
    """
    
    def __init__(self):
        # Patterns that indicate translation exercises
        self.translation_keywords = [
            r'translate\s+into\s+\w+',
            r'translate\s+from\s+\w+',
            r'translate\s+the\s+following',
            r'\w+\s+translation',
            r'in\s+\w+\s+script',  # "in ARABIC SCRIPT"
            r'answer\s+in\s+\w+',  # "answer in ARABIC"
        ]
        
        # Patterns for common language names in translation exercises
        self.language_names = [
            r'\barabic\b', r'\benglish\b', r'\bfrench\b', r'\bspanish\b',
            r'\bgerman\b', r'\bchinese\b', r'\bjapanese\b', r'\bkorean\b',
            r'\brussian\b', r'\bitalian\b', r'\bportuguese\b'
        ]
        
        # Patterns indicating garbled/OCR text (random capital letters, numbers mixed with letters)
        self.garbled_patterns = [
            r'\b[A-Z]{2,}\s+[0-9]+\s+[A-Z]+\b',  # "YG ll 9 Alsen"
            r'\b[0-9]\s+[A-Z]{2,}\b',  # "9 GAM"
            r'\b[A-Z]{2,}\s+[0-9]+\s+[a-z]+\s+[A-Z]+\b',  # Mixed case/number patterns
            r'[A-Z][a-z]+\s+[0-9]+\s+[A-Z][a-z]+\s+[A-Z]+',  # "Aan YG ll 9 Alsen oh GAM"
        ]
        
        # Arabic-specific OCR artifacts (common garbled patterns)
        # These are short words that don't form valid English words
        self.arabic_ocr_artifacts = [
            r'\b[A-Z][a-z]{1,2}\s+[A-Z]{1,2}\s+[0-9]',  # "Aan YG ll 9"
            r'[A-Z][a-z]+\s+[A-Z]{2,}\s+[A-Z]+\s+[0-9]',  # "Alsen oh GAM"
            r'\b[A-Z][a-z]{1,2}\s+[0-9]',  # Short word + number
            r'\b[0-9]+\s+[A-Z][a-z]{1,2}\s+[A-Z]',  # Number + short word + capital
        ]
        
        # Common English words to exclude from garbled detection
        self.valid_english_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
            'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'few', 'got', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        
        # Threshold: if >20% of words look garbled, flag as poor OCR (lowered from 30%)
        self.garbled_threshold = 0.2
    
    def is_translation_question(self, text: str) -> bool:
        """
        Check if question text indicates a translation exercise.
        
        Args:
            text: Question text
            
        Returns:
            True if this appears to be a translation question
        """
        text_lower = text.lower()
        
        # Check for translation keywords
        for pattern in self.translation_keywords:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def contains_language_reference(self, text: str) -> Optional[str]:
        """
        Check if text mentions a specific language.
        
        Args:
            text: Question text
            
        Returns:
            Language name if found, None otherwise
        """
        text_lower = text.lower()
        for pattern in self.language_names:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(0).title()
        return None
    
    def calculate_garbled_score(self, text: str) -> float:
        """
        Calculate how much of the text appears to be garbled OCR.
        
        Args:
            text: Question text
            
        Returns:
            Score between 0 and 1 (1 = completely garbled)
        """
        if not text or len(text) < 10:
            return 0.0
        
        # Count words that match garbled patterns
        words = text.split()
        if not words:
            return 0.0
        
        garbled_count = 0
        
        for word in words:
            # Skip if it's a valid English word
            word_lower = word.lower().strip('.,!?;:()[]{}')
            if word_lower in self.valid_english_words:
                continue
            
            # Check each garbled pattern in full text context (not just word)
            text_segment = f" {word} "  # Add spaces for better pattern matching
            for pattern in self.garbled_patterns + self.arabic_ocr_artifacts:
                if re.search(pattern, text_segment):
                    garbled_count += 1
                    break
        
        # Also check for sequences that look like OCR errors
        # (short words with numbers and capitals mixed)
        for word in words:
            word_lower = word.lower().strip('.,!?;:()[]{}')
            if word_lower in self.valid_english_words:
                continue
                
            if len(word) > 3:
                # Pattern: Capital-letter-word + number + capital-letter-word
                if re.search(r'[A-Z][a-z]+[0-9]+[A-Z]', word):
                    garbled_count += 1
                elif re.search(r'[0-9]+[A-Z][a-z]+[0-9]', word):
                    garbled_count += 1
        
        # Additional check: Look for sequences like "Aan YG ll 9 Alsen" in full text
        # These are classic Arabic OCR artifacts
        text_lower = text.lower()
        
        # Pattern 1: Short word + 2-letter capital + 2-letter lowercase + number + word
        # Example: "Aan YG ll 9 Alsen"
        if re.search(r'\b[a-z]{2,3}\s+[a-z]{1,2}\s+[a-z]{1,2}\s+\d+\s+[a-z]+\b', text_lower):
            garbled_count += max(3, len(words) * 0.1)  # Weight heavily
        
        # Pattern 2: Mix of short caps, lowercase, and numbers (e.g., "YG ll 9", "98 US y AI")
        if re.search(r'\b[a-z]{1,2}\s+[a-z]{1,2}\s+\d+\b', text_lower) or \
           re.search(r'\b\d+\s+[a-z]{1,2}\s+[a-z]{1,2}\s+[a-z]{1,2}\b', text_lower):
            garbled_count += max(2, len(words) * 0.05)
        
        # Pattern 3: Check for very short non-word sequences (OCR artifacts)
        # Count sequences like "ll", "yg", "ai", "ed" that aren't valid words
        invalid_short_sequences = ['ll', 'yg', 'ai', 'ed', 'gl', 'al', 'gy', 'sg', 'os', 'og']
        for word in words:
            word_clean = word.lower().strip('.,!?;:()[]{}')
            if word_clean in invalid_short_sequences and len(word_clean) <= 2:
                garbled_count += 0.5
        
        # Normalize count (can exceed word count due to pattern matching)
        return min(garbled_count / len(words) if words else 0.0, 1.0)
    
    def has_poor_ocr(self, text: str) -> bool:
        """
        Check if text appears to have poor OCR quality.
        
        Args:
            text: Question text
            
        Returns:
            True if text looks garbled/OCR'd poorly
        """
        garbled_score = self.calculate_garbled_score(text)
        return garbled_score >= self.garbled_threshold
    
    def detect_translation_issues(self, questions: List[Dict]) -> List[Dict]:
        """
        Detect translation questions with poor OCR and flag them.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Updated questions with OCR quality flags
        """
        updated_questions = []
        
        for question in questions:
            updated_q = question.copy()
            text = question.get('text', '')
            
            # Initialize flags
            is_translation = self.is_translation_question(text)
            language = self.contains_language_reference(text)
            poor_ocr = self.has_poor_ocr(text)
            
            # Set flags
            if is_translation:
                updated_q['is_translation_question'] = True
                if language:
                    updated_q['target_language'] = language
            else:
                updated_q['is_translation_question'] = False
            
            if poor_ocr:
                updated_q['has_poor_ocr'] = True
                updated_q['ocr_quality'] = 'poor'
                updated_q['needs_re_extraction'] = True
            else:
                updated_q['has_poor_ocr'] = False
                updated_q['ocr_quality'] = 'good'
                updated_q['needs_re_extraction'] = False
            
            # If it's a translation question with poor OCR, mark for priority re-extraction
            if is_translation and poor_ocr:
                updated_q['ocr_priority'] = 'high'
                # Determine which language is needed for OCR
                # If question says "Translate into ENGLISH", the source text is Arabic
                # If question says "Translate into ARABIC", the source text is English
                text_lower = text.lower()
                if 'translate into english' in text_lower or 'translate to english' in text_lower:
                    updated_q['ocr_language_needed'] = 'arabic'  # Need Arabic OCR for source text
                elif 'translate into arabic' in text_lower or 'translate to arabic' in text_lower:
                    updated_q['ocr_language_needed'] = 'english'  # Need English OCR for source text
                elif language:
                    # If source language detected, use that
                    updated_q['ocr_language_needed'] = language.lower()
                else:
                    # Default to Arabic for ARAB course
                    updated_q['ocr_language_needed'] = 'arabic'
            elif is_translation:
                updated_q['ocr_priority'] = 'medium'
            elif poor_ocr:
                updated_q['ocr_priority'] = 'medium'
                # For non-translation questions with poor OCR, check course code
                # If it's an Arabic course, likely need Arabic OCR
                updated_q['ocr_language_needed'] = 'arabic'  # Default assumption
            else:
                updated_q['ocr_priority'] = 'low'
            
            updated_questions.append(updated_q)
        
        return updated_questions
    
    def get_translation_stats(self, questions: List[Dict]) -> Dict:
        """
        Get statistics about translation questions and OCR quality.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Dictionary with statistics
        """
        total = len(questions)
        translation_count = sum(1 for q in questions if q.get('is_translation_question', False))
        poor_ocr_count = sum(1 for q in questions if q.get('has_poor_ocr', False))
        needs_re_extraction = sum(1 for q in questions if q.get('needs_re_extraction', False))
        high_priority = sum(1 for q in questions if q.get('ocr_priority') == 'high')
        
        # Count by language
        languages = {}
        for q in questions:
            lang = q.get('target_language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        return {
            'total_questions': total,
            'translation_questions': translation_count,
            'translation_percentage': (translation_count / total * 100) if total > 0 else 0,
            'poor_ocr_count': poor_ocr_count,
            'poor_ocr_percentage': (poor_ocr_count / total * 100) if total > 0 else 0,
            'needs_re_extraction': needs_re_extraction,
            'high_priority_re_extraction': high_priority,
            'languages_detected': languages,
        }


def detect_translation_issues_in_file(input_file: str, output_file: Optional[str] = None) -> Dict:
    """
    Detect translation issues in an exam analysis JSON file.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (if None, overwrites input)
        
    Returns:
        Statistics dictionary
    """
    import json
    from pathlib import Path
    
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    detector = TranslationDetector()
    
    if 'exams' in data:
        exams_list = data['exams']
    elif 'questions' in data:
        exams_list = [{'questions': data['questions'], 'filename': 'unknown'}]
    else:
        raise ValueError("Expected 'exams' or 'questions' key in JSON")
    
    all_stats = []
    
    for exam in exams_list:
        questions = exam.get('questions', [])
        if not questions:
            continue
        
        updated_questions = detector.detect_translation_issues(questions)
        exam['questions'] = updated_questions
        
        stats = detector.get_translation_stats(updated_questions)
        stats['filename'] = exam.get('filename', 'unknown')
        all_stats.append(stats)
    
    output_path = Path(output_file) if output_file else input_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {
        'exams_processed': len(all_stats),
        'exam_stats': all_stats,
    }

