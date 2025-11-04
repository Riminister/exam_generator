#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context-Based OCR Selector
Determines appropriate OCR settings based on exam type (language, math, etc.)
"""

import re
import sys
from typing import Dict, Optional, List
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class OCRContextSelector:
    """
    Determines appropriate OCR method and settings based on exam content type.
    """
    
    def __init__(self):
        # Language course codes and their OCR languages
        self.language_courses = {
            'ARAB': {'lang': 'ara+eng', 'language_name': 'Arabic', 'needs_translation': False},
            'FREN': {'lang': 'fra+eng', 'language_name': 'French', 'needs_translation': False},
            'SPAN': {'lang': 'spa+eng', 'language_name': 'Spanish', 'needs_translation': False},
            'GERM': {'lang': 'deu+eng', 'language_name': 'German', 'needs_translation': False},
            'ITAL': {'lang': 'ita+eng', 'language_name': 'Italian', 'needs_translation': False},
            'CHIN': {'lang': 'chi_sim+eng', 'language_name': 'Chinese', 'needs_translation': False},
            'JAPA': {'lang': 'jpn+eng', 'language_name': 'Japanese', 'needs_translation': False},
            'KORE': {'lang': 'kor+eng', 'language_name': 'Korean', 'needs_translation': False},
            'RUSS': {'lang': 'rus+eng', 'language_name': 'Russian', 'needs_translation': False},
            'PORT': {'lang': 'por+eng', 'language_name': 'Portuguese', 'needs_translation': False},
        }
        
        # Math/equation course codes
        self.math_courses = {
            'MATH', 'STAT', 'PHYS', 'CHEM', 'ENGR', 'ELEC', 'MECH', 'CIVL'
        }
        
        # Keywords that indicate math content
        self.math_keywords = [
            'equation', 'formula', 'derivative', 'integral', 'calculus',
            'algebra', 'geometry', 'trigonometry', 'matrix', 'vector',
            'solve for', 'calculate', 'show that', 'prove that'
        ]
        
        # Keywords that indicate language content
        self.language_keywords = [
            'translate', 'translation', 'grammar', 'vocabulary',
            'conjugate', 'verb', 'adjective', 'noun', 'pronoun'
        ]
    
    def detect_exam_type(self, course_code: Optional[str], first_page_text: Optional[str] = None) -> Dict[str, any]:
        """
        Detect exam type and determine OCR settings.
        
        Args:
            course_code: Course code (e.g., ARAB100, MATH101)
            first_page_text: Optional first page text for additional context
            
        Returns:
            Dict with OCR configuration:
            - ocr_language: str (e.g., 'ara+eng', 'eng', 'fra+eng')
            - exam_type: str ('language', 'math', 'general')
            - needs_math_ocr: bool
            - detected_language: str (if language exam)
            - ocr_config: str (Tesseract config string)
        """
        result = {
            'ocr_language': 'eng',  # Default to English
            'exam_type': 'general',
            'needs_math_ocr': False,
            'detected_language': None,
            'ocr_config': '--psm 6',  # Default: uniform block of text
            'recommended_ocr_method': 'tesseract'
        }
        
        # Normalize course code
        if course_code:
            course_code = course_code.upper()
            course_prefix = re.match(r'^([A-Z]{2,4})', course_code)
            if course_prefix:
                prefix = course_prefix.group(1)
                
                # Check for language courses
                if prefix in self.language_courses:
                    lang_info = self.language_courses[prefix]
                    result['ocr_language'] = lang_info['lang']
                    result['exam_type'] = 'language'
                    result['detected_language'] = lang_info['language_name']
                    result['needs_translation'] = lang_info.get('needs_translation', False)
                    result['ocr_config'] = '--psm 6'  # Uniform block works well for mixed languages
                    return result
                
                # Check for math courses
                if prefix in self.math_courses:
                    result['exam_type'] = 'math'
                    result['needs_math_ocr'] = True
                    result['ocr_language'] = 'eng'  # Math uses English + symbols
                    result['ocr_config'] = '--psm 6'
                    result['recommended_ocr_method'] = 'mathpix_or_tesseract'  # MathPix better for equations
                    return result
        
        # Use first page text for additional context if available
        if first_page_text:
            text_lower = first_page_text.lower()
            
            # Check for language keywords
            if any(keyword in text_lower for keyword in self.language_keywords):
                # Try to detect which language from text patterns
                if 'arabic' in text_lower or 'عربي' in first_page_text:
                    result['ocr_language'] = 'ara+eng'
                    result['exam_type'] = 'language'
                    result['detected_language'] = 'Arabic'
                elif 'french' in text_lower or 'français' in first_page_text:
                    result['ocr_language'] = 'fra+eng'
                    result['exam_type'] = 'language'
                    result['detected_language'] = 'French'
                elif 'spanish' in text_lower or 'español' in first_page_text:
                    result['ocr_language'] = 'spa+eng'
                    result['exam_type'] = 'language'
                    result['detected_language'] = 'Spanish'
            
            # Check for math keywords
            if any(keyword in text_lower for keyword in self.math_keywords):
                result['exam_type'] = 'math'
                result['needs_math_ocr'] = True
                result['recommended_ocr_method'] = 'mathpix_or_tesseract'
        
        return result
    
    def get_ocr_instructions(self, config: Dict[str, any]) -> str:
        """
        Get human-readable OCR instructions based on config.
        
        Args:
            config: OCR configuration dict from detect_exam_type()
            
        Returns:
            String with instructions for OCR extraction
        """
        instructions = []
        
        if config['exam_type'] == 'language':
            instructions.append(f"Language exam detected: {config['detected_language']}")
            instructions.append(f"Use OCR language: {config['ocr_language']}")
            instructions.append("DO NOT enable auto-translation - extract original text only")
            
        elif config['exam_type'] == 'math':
            instructions.append("Math/equation exam detected")
            if config['recommended_ocr_method'] == 'mathpix_or_tesseract':
                instructions.append("Recommended: MathPix API for better equation recognition")
                instructions.append("Fallback: Tesseract with --psm 6")
            instructions.append("Ensure proper handling of mathematical symbols and equations")
            
        else:
            instructions.append("General exam - standard English OCR")
            instructions.append(f"Use OCR language: {config['ocr_language']}")
        
        instructions.append(f"Tesseract config: {config['ocr_config']}")
        
        return "\n".join(instructions)
    
    def should_re_extract(self, course_code: Optional[str], current_ocr_quality: str = 'unknown') -> bool:
        """
        Determine if an exam should be re-extracted based on type and current OCR quality.
        
        Args:
            course_code: Course code
            current_ocr_quality: Current OCR quality assessment
            
        Returns:
            True if re-extraction recommended
        """
        if not course_code:
            return False
        
        course_code = course_code.upper()
        course_prefix = re.match(r'^([A-Z]{2,4})', course_code)
        
        if course_prefix:
            prefix = course_prefix.group(1)
            # Language exams should always use proper OCR
            if prefix in self.language_courses:
                return True
        
        # Re-extract if quality is poor
        if current_ocr_quality in ['poor', 'bad', 'needs_re_extraction']:
            return True
        
        return False


if __name__ == "__main__":
    # Test the selector
    selector = OCRContextSelector()
    
    test_cases = [
        ("ARAB100", None),
        ("FREN101", None),
        ("MATH201", None),
        ("ECON310", None),
        ("ELEC252", None),
    ]
    
    print("=" * 70)
    print("OCR CONTEXT SELECTOR TEST")
    print("=" * 70)
    
    for course_code, first_page in test_cases:
        config = selector.detect_exam_type(course_code, first_page)
        print(f"\nCourse: {course_code}")
        print(f"  Type: {config['exam_type']}")
        print(f"  OCR Language: {config['ocr_language']}")
        print(f"  Needs Math OCR: {config['needs_math_ocr']}")
        if config['detected_language']:
            print(f"  Detected Language: {config['detected_language']}")
        print(f"  Instructions:")
        print(f"    {selector.get_ocr_instructions(config).replace(chr(10), chr(10) + '    ')}")
    
    print("\n" + "=" * 70)

