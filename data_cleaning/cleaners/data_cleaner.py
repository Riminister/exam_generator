# Data Cleaning Module for Exam Bank Data
# This module prepares raw exam data for ML training and future exam generation

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import pandas as pd
from difflib import SequenceMatcher


class ExamDataCleaner:
    """
    Comprehensive data cleaning pipeline for exam bank data.
    Prepares extracted exam data for machine learning models.
    """
    
    def __init__(self, min_question_length: int = 20, min_answer_length: int = 10):
        """
        Initialize the data cleaner.
        
        Args:
            min_question_length: Minimum character length for valid questions
            min_answer_length: Minimum character length for valid answers
        """
        self.min_question_length = min_question_length
        self.min_answer_length = min_answer_length
        self.cleaned_data = []
        self.cleaning_stats = {
            'total_questions': 0,
            'removed_duplicates': 0,
            'removed_too_short': 0,
            'removed_invalid': 0,
            'removed_noise': 0,
            'final_count': 0
        }
        
        # Common patterns to identify and remove
        self.noise_patterns = [
            r'Page \d+ of \d+',
            r'\d+/\d+/\d+',  # Dates
            r'© \d{4}',
            r'Confidential',
            r'DO NOT WRITE',
            r'Turn over',
            r'See next page',
            r'Continued\.\.\.',
            r'\[.*?\]',  # Square brackets content
            r'\(Page \d+\)',
        ]
        
        # Common headers/footers
        self.header_footer_patterns = [
            r'QUEEN\'?S UNIVERSITY',
            r'KINGSTON.*?ONTARIO',
            r'EXAMINATION.*?\d{4}',
            r'COURSE.*?CODE',
            r'INSTRUCTOR.*?:',
        ]
    
    def clean_text(self, text: str) -> str:
        """
        Basic text cleaning: remove extra whitespace, normalize formatting.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove non-printable control chars (keep common unicode letters)
        text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]', ' ', text)
        
        # De-hyphenate common OCR linebreak hyphens
        text = re.sub(r'-\s*\n', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix common encoding issues
        text = text.replace('\ufeff', '')  # BOM
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        text = text.replace('\u202a', '')  # Left-to-right embedding
        text = text.replace('\u202b', '')  # Right-to-left embedding
        text = text.replace('\u202c', '')  # Pop directional formatting
        text = text.replace('\u202d', '')  # Left-to-right override
        text = text.replace('\u202e', '')  # Right-to-left override
        
        # Normalize quotes/dashes
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201C', '"').replace('\u201D', '"')
        
        # Normalize dashes
        text = text.replace('—', '-').replace('–', '-')
        
        return text
    
    def remove_noise(self, text: str) -> str:
        """
        Remove common noise patterns from exam text.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with noise removed
        """
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove headers/footers
        for pattern in self.header_footer_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return self.clean_text(text)
    
    def validate_question(self, question: Dict) -> bool:
        """
        Validate that a question meets quality criteria.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if question is valid, False otherwise
        """
        text = question.get('text', '')
        
        # Check minimum length
        if len(text) < self.min_question_length:
            return False
        
        # Check if it's mostly whitespace
        if len(text.strip()) < self.min_question_length:
            return False
        
        # Check if it's mostly punctuation
        letters = sum(1 for c in text if c.isalpha())
        letter_ratio = (letters / len(text)) if text else 0
        if letter_ratio < 0.15:  # allow OCR noise but require some letters
            return False
        
        # Check for actual content (at least one letter or number)
        if not re.search(r'[a-zA-Z0-9]', text):
            return False
        
        # Check if it's clearly not a question (e.g., "Page 1", "Answer Key")
        invalid_patterns = [
            r'^page \d+$',
            r'^answer key',
            r'^table of contents',
            r'^instructions:',
            r'^exam duration:',
            r'^total marks:',
        ]
        text_lower = text.lower().strip()
        if any(re.match(pattern, text_lower) for pattern in invalid_patterns):
            return False
        
        return True
    
    def extract_multiple_choice_options(self, question_text: str) -> Tuple[str, List[str]]:
        """
        Extract multiple choice question and its options.
        
        Args:
            question_text: Full question text including options
            
        Returns:
            Tuple of (cleaned_question_text, list_of_options)
        """
        # Patterns for multiple choice options
        option_patterns = [
            r'([A-D]\)[^\w])',  # A) B) C) D)
            r'\(([A-D])\)',     # (A) (B) (C) (D)
            r'([A-D]\.\s)',      # A. B. C. D.
            r'([A-D]\s+[A-Z])',  # A Some text
        ]
        
        options = []
        cleaned_text = question_text
        
        for pattern in option_patterns:
            matches = list(re.finditer(pattern, question_text))
            if len(matches) >= 2:  # At least 2 options found
                # Split question at first option
                first_match = matches[0]
                question_part = question_text[:first_match.start()].strip()
                
                # Extract options
                for i, match in enumerate(matches):
                    if i < len(matches) - 1:
                        start = match.end()
                        end = matches[i + 1].start()
                    else:
                        start = match.end()
                        end = len(question_text)
                    
                    option_text = question_text[start:end].strip()
                    option_text = self.clean_text(option_text)
                    if option_text and len(option_text) >= 3:
                        options.append(option_text)
                
                cleaned_text = question_part
                break
        
        return cleaned_text, options
    
    def remove_duplicates(self, questions: List[Dict], similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Remove duplicate or highly similar questions.
        
        Args:
            questions: List of question dictionaries
            similarity_threshold: Minimum similarity to consider duplicates (0-1)
            
        Returns:
            List of unique questions
        """
        unique_questions = []
        seen_hashes = set()
        
        for question in questions:
            text = question.get('text', '').lower().strip()
            
            # Create a simple hash for exact duplicates
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in seen_hashes:
                self.cleaning_stats['removed_duplicates'] += 1
                continue
            
            # Check for similar questions using simple similarity
            is_duplicate = False
            for existing in unique_questions:
                existing_text = existing.get('text', '').lower().strip()
                similarity = SequenceMatcher(None, text, existing_text).ratio()
                
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    self.cleaning_stats['removed_duplicates'] += 1
                    break
            
            if not is_duplicate:
                seen_hashes.add(text_hash)
                unique_questions.append(question)
        
        return unique_questions
    
    def clean_question_structure(self, question: Dict) -> Dict:
        """
        Clean and structure a single question.
        
        Args:
            question: Question dictionary from raw extraction
            
        Returns:
            Cleaned and structured question dictionary
        """
        text = question.get('text', '')
        
        # Remove noise
        text = self.remove_noise(text)
        
        # Extract question type and clean accordingly
        # Preserve sub_question type if already detected
        question_type = question.get('question_type', 'other')
        
        # Get difficulty score (can be None if unavailable)
        difficulty_score = question.get('difficulty_score')
        # If None or not set, keep it as None (unavailable), don't default to 0
        
        cleaned_question = {
            'id': question.get('question_number', 0),
            'text': text,
            'question_type': question_type,  # Preserves 'sub_question' if detected
            'original_length': len(question.get('text', '')),
            'cleaned_length': len(text),
            'topics': question.get('topics', []),
            'difficulty_score': difficulty_score,  # Can be None if marks not found
        }
        
        # Preserve sub-question metadata if present
        if question.get('is_sub_question'):
            cleaned_question['is_sub_question'] = True
        if question.get('parent_question_number') is not None:
            cleaned_question['parent_question_number'] = question.get('parent_question_number')
        
        # Extract multiple choice options if applicable
        if question_type == 'multiple_choice':
            question_text, options = self.extract_multiple_choice_options(text)
            cleaned_question['text'] = question_text
            cleaned_question['options'] = options
            cleaned_question['num_options'] = len(options)
        
        return cleaned_question
    
    def clean_dataset(self, questions_data: List[Dict]) -> List[Dict]:
        """
        Main cleaning pipeline for a dataset of questions.
        
        Args:
            questions_data: List of raw question dictionaries
            
        Returns:
            List of cleaned question dictionaries
        """
        self.cleaning_stats['total_questions'] = len(questions_data)
        cleaned_questions = []
        
        print(f"Starting data cleaning pipeline...")
        print(f"Initial question count: {len(questions_data)}")
        
        # Step 1: Clean individual questions
        for question in questions_data:
            cleaned_q = self.clean_question_structure(question)
            
            # Validate question
            if not self.validate_question(cleaned_q):
                if len(cleaned_q['text']) < self.min_question_length:
                    self.cleaning_stats['removed_too_short'] += 1
                else:
                    self.cleaning_stats['removed_invalid'] += 1
                continue
            
            cleaned_questions.append(cleaned_q)
        
        print(f"After validation: {len(cleaned_questions)} questions")
        
        # Step 2: Remove duplicates
        cleaned_questions = self.remove_duplicates(cleaned_questions)
        print(f"After duplicate removal: {len(cleaned_questions)} questions")
        
        self.cleaning_stats['final_count'] = len(cleaned_questions)
        
        return cleaned_questions
    
    def generate_cleaning_report(self) -> Dict:
        """
        Generate a report of the cleaning process.
        
        Returns:
            Dictionary with cleaning statistics
        """
        total_removed = (
            self.cleaning_stats['removed_duplicates'] +
            self.cleaning_stats['removed_too_short'] +
            self.cleaning_stats['removed_invalid'] +
            self.cleaning_stats['removed_noise']
        )
        
        retention_rate = (
            (self.cleaning_stats['final_count'] / self.cleaning_stats['total_questions'] * 100)
            if self.cleaning_stats['total_questions'] > 0 else 0
        )
        
        report = {
            **self.cleaning_stats,
            'total_removed': total_removed,
            'retention_rate': f"{retention_rate:.1f}%"
        }
        
        return report
    
    def save_cleaned_data(self, cleaned_questions: List[Dict], output_path: str = "exam_analysis/cleaned_questions.json"):
        """
        Save cleaned data to JSON file.
        
        Args:
            cleaned_questions: List of cleaned question dictionaries
            output_path: Path to save the cleaned data
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            'cleaned_questions': cleaned_questions,
            'cleaning_stats': self.generate_cleaning_report(),
            'metadata': {
                'total_questions': len(cleaned_questions),
                'data_source': 'exam_downloads',
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Cleaned data saved to: {output_path}")
        print(f"   Total questions saved: {len(cleaned_questions)}")
    
    def export_to_dataframe(self, cleaned_questions: List[Dict]) -> pd.DataFrame:
        """
        Convert cleaned questions to pandas DataFrame for analysis.
        
        Args:
            cleaned_questions: List of cleaned question dictionaries
            
        Returns:
            pandas DataFrame
        """
        df_data = []
        
        for q in cleaned_questions:
            row = {
                'id': q.get('id'),
                'text': q.get('text'),
                'question_type': q.get('question_type'),
                'difficulty_score': q.get('difficulty_score'),
                'topics': ', '.join(q.get('topics', [])),
                'text_length': q.get('cleaned_length', 0),
            }
            
            if q.get('question_type') == 'multiple_choice':
                row['num_options'] = q.get('num_options', 0)
            
            df_data.append(row)
        
        return pd.DataFrame(df_data)
    
    def export_to_csv(self, cleaned_questions: List[Dict], output_path: str = "exam_analysis/cleaned_questions.csv"):
        """
        Export cleaned questions to CSV file.
        
        Args:
            cleaned_questions: List of cleaned question dictionaries
            output_path: Path to save the CSV file
        """
        df = self.export_to_dataframe(cleaned_questions)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n✅ Data exported to CSV: {output_path}")
        print(f"   Shape: {df.shape}")


def clean_exam_data(
    input_file: str = "data/exam_analysis.json",
    output_json: str = "exam_analysis/cleaned_questions.json",
    output_csv: str = "exam_analysis/cleaned_questions.csv"
) -> List[Dict]:
    """
    Main function to clean exam data from analysis results.
    
    Args:
        input_file: Path to JSON file with raw exam analysis results
        output_json: Path to save cleaned JSON data
        output_csv: Path to save cleaned CSV data
        
    Returns:
        List of cleaned question dictionaries
    """
    print("=" * 60)
    print("EXAM DATA CLEANING PIPELINE")
    print("=" * 60)
    
    # Load raw data
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Please run extraction first to generate data/exam_analysis.json")
        return []
    
    # Check if file is empty
    if input_path.stat().st_size == 0:
        print(f"❌ Error: Input file is empty: {input_file}")
        print("   Please run extraction first to generate data/exam_analysis.json")
        return []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in file {input_file}")
        print(f"   JSON decode error: {e}")
        print("   Please check the file format or regenerate it")
        return []
    except Exception as e:
        print(f"❌ Error reading file {input_file}: {e}")
        return []
    
    # Handle both data formats
    if 'exams' in data:
        # Flatten questions from all exams
        questions_data = []
        for exam in data.get('exams', []):
            questions_data.extend(exam.get('questions', []))
    elif 'questions' in data:
        questions_data = data.get('questions', [])
    else:
        print("❌ Error: Expected 'exams' or 'questions' key in JSON")
        return []
    
    if not questions_data:
        print("❌ Error: No questions found in input file")
        return []
    
    # Initialize cleaner
    cleaner = ExamDataCleaner()
    
    # Clean the data
    cleaned_questions = cleaner.clean_dataset(questions_data)
    
    # Generate and display report
    report = cleaner.generate_cleaning_report()
    print("\n" + "=" * 60)
    print("CLEANING REPORT")
    print("=" * 60)
    print(f"Total questions processed: {report['total_questions']}")
    print(f"Removed duplicates: {report['removed_duplicates']}")
    print(f"Removed (too short): {report['removed_too_short']}")
    print(f"Removed (invalid): {report['removed_invalid']}")
    print(f"Final count: {report['final_count']}")
    print(f"Retention rate: {report['retention_rate']}")
    print("=" * 60)
    
    # Save cleaned data
    cleaner.save_cleaned_data(cleaned_questions, output_json)
    cleaner.export_to_csv(cleaned_questions, output_csv)
    
    print("\n✅ Data cleaning complete!")
    print(f"   Ready for ML training with {len(cleaned_questions)} cleaned questions")
    
    return cleaned_questions


if __name__ == "__main__":
    # Run the cleaning pipeline
    clean_exam_data()

