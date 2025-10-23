# Phase 1 Starter: PDF Analysis & Data Extraction
# This script helps you begin analyzing your exam bank data

import os
import re
import json
import pandas as pd
from pathlib import Path
import PyPDF2
import pdfplumber
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

class ExamBankAnalyzer:
    """
    A class to analyze exam bank data and extract patterns
    This is your starting point for the ML exam generation project
    """
    
    def __init__(self, exam_folder="exam_downloads"):
        self.exam_folder = Path(exam_folder)
        self.exams_data = []
        self.questions_data = []
        self.analysis_results = {}
        
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF files
        Try multiple methods for better results
        """
        text = ""
        
        # Method 1: PyPDF2 (faster, good for simple PDFs)
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PyPDF2 failed for {pdf_path}: {e}")
        
        # Method 2: pdfplumber (better for complex layouts)
        if not text.strip():
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"pdfplumber failed for {pdf_path}: {e}")
        
        return text.strip()
    
    def identify_question_patterns(self, text):
        """
        Identify different types of questions in the text
        This is where you'll learn about pattern recognition
        """
        patterns = {
            'multiple_choice': [
                r'[A-D]\)\s+',  # A) B) C) D)
                r'\(\s*[A-D]\s*\)',  # (A) (B) (C) (D)
                r'[A-D]\.\s+',  # A. B. C. D.
            ],
            'true_false': [
                r'True\s+or\s+False',
                r'T\s*/\s*F',
                r'Circle\s+(True|False)',
            ],
            'short_answer': [
                r'Explain\s+',
                r'Describe\s+',
                r'What\s+is\s+',
                r'Define\s+',
            ],
            'numerical': [
                r'Calculate\s+',
                r'Compute\s+',
                r'Find\s+the\s+value',
                r'Solve\s+for',
            ]
        }
        
        question_types = defaultdict(int)
        
        for question_type, regex_list in patterns.items():
            for pattern in regex_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                question_types[question_type] += len(matches)
        
        return dict(question_types)
    
    def extract_questions(self, text):
        """
        Extract individual questions from exam text
        This is a simplified version - you'll improve this over time
        """
        # Split by common question patterns
        question_patterns = [
            r'\n\s*\d+\.\s+',  # 1. 2. 3.
            r'\n\s*Question\s+\d+',  # Question 1, Question 2
            r'\n\s*Q\d+',  # Q1, Q2
        ]
        
        questions = []
        for pattern in question_patterns:
            parts = re.split(pattern, text)
            if len(parts) > 1:
                # First part is usually header/intro
                for i, part in enumerate(parts[1:], 1):
                    if len(part.strip()) > 50:  # Minimum question length
                        questions.append({
                            'question_number': i,
                            'text': part.strip(),
                            'length': len(part.strip())
                        })
                break
        
        return questions
    
    def analyze_difficulty_indicators(self, question_text):
        """
        Analyze text to estimate question difficulty
        This uses simple heuristics - you'll replace with ML models later
        """
        difficulty_score = 0
        
        # Length-based difficulty (longer questions often harder)
        if len(question_text) > 200:
            difficulty_score += 1
        elif len(question_text) > 100:
            difficulty_score += 0.5
        
        # Keyword-based difficulty
        easy_keywords = ['define', 'list', 'identify', 'name']
        medium_keywords = ['explain', 'describe', 'compare', 'contrast']
        hard_keywords = ['analyze', 'evaluate', 'synthesize', 'critique']
        
        text_lower = question_text.lower()
        
        for keyword in easy_keywords:
            if keyword in text_lower:
                difficulty_score -= 0.5
        
        for keyword in medium_keywords:
            if keyword in text_lower:
                difficulty_score += 0.5
        
        for keyword in hard_keywords:
            if keyword in text_lower:
                difficulty_score += 1
        
        return max(0, min(3, difficulty_score))  # Scale 0-3
    
    def extract_topics(self, text):
        """
        Extract potential topics from text
        This is a simple keyword extraction - you'll use NLP later
        """
        # Common academic terms (you'll expand this)
        academic_terms = [
            'economics', 'business', 'finance', 'accounting', 'marketing',
            'management', 'strategy', 'operations', 'human resources',
            'chemistry', 'physics', 'mathematics', 'biology', 'engineering',
            'computer science', 'programming', 'algorithms', 'data structures'
        ]
        
        topics = []
        text_lower = text.lower()
        
        for term in academic_terms:
            if term in text_lower:
                topics.append(term)
        
        return topics
    
    def process_exam_file(self, pdf_path):
        """
        Process a single exam file and extract all relevant data
        """
        print(f"Processing: {pdf_path.name}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"Could not extract text from {pdf_path.name}")
            return None
        
        # Extract metadata from filename
        filename = pdf_path.stem
        course_match = re.search(r'([A-Z]{2,4}\d{3,4})', filename)
        course_code = course_match.group(1) if course_match else "UNKNOWN"
        
        year_match = re.search(r'(20\d{2})', filename)
        year = int(year_match.group(1)) if year_match else None
        
        # Analyze question patterns
        question_patterns = self.identify_question_patterns(text)
        
        # Extract individual questions
        questions = self.extract_questions(text)
        
        # Process each question
        processed_questions = []
        for q in questions:
            difficulty = self.analyze_difficulty_indicators(q['text'])
            topics = self.extract_topics(q['text'])
            
            processed_questions.append({
                'question_number': q['question_number'],
                'text': q['text'],
                'length': q['length'],
                'difficulty_score': difficulty,
                'topics': topics,
                'question_type': self.classify_question_type(q['text'])
            })
        
        # Store exam data
        exam_data = {
            'filename': pdf_path.name,
            'course_code': course_code,
            'year': year,
            'text_length': len(text),
            'question_count': len(processed_questions),
            'question_patterns': question_patterns,
            'questions': processed_questions
        }
        
        return exam_data
    
    def classify_question_type(self, question_text):
        """
        Simple question type classification
        You'll replace this with ML models later
        """
        text_lower = question_text.lower()
        
        if any(pattern in text_lower for pattern in ['a)', 'b)', 'c)', 'd)']):
            return 'multiple_choice'
        elif any(pattern in text_lower for pattern in ['true', 'false', 't/f']):
            return 'true_false'
        elif any(pattern in text_lower for pattern in ['explain', 'describe', 'what is']):
            return 'short_answer'
        elif any(pattern in text_lower for pattern in ['calculate', 'compute', 'solve']):
            return 'numerical'
        else:
            return 'other'
    
    def analyze_all_exams(self):
        """
        Process all exam files in the folder
        """
        pdf_files = list(self.exam_folder.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.exam_folder}")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            exam_data = self.process_exam_file(pdf_file)
            if exam_data:
                self.exams_data.append(exam_data)
                self.questions_data.extend(exam_data['questions'])
        
        print(f"Successfully processed {len(self.exams_data)} exams")
        print(f"Extracted {len(self.questions_data)} questions")
    
    def generate_analysis_report(self):
        """
        Generate a comprehensive analysis report
        This helps you understand your data before building ML models
        """
        if not self.exams_data:
            print("No data to analyze. Run analyze_all_exams() first.")
            return
        
        print("\n" + "="*60)
        print("EXAM BANK ANALYSIS REPORT")
        print("="*60)
        
        # Basic statistics
        total_exams = len(self.exams_data)
        total_questions = len(self.questions_data)
        avg_questions_per_exam = total_questions / total_exams if total_exams > 0 else 0
        
        print(f"Total Exams: {total_exams}")
        print(f"Total Questions: {total_questions}")
        print(f"Average Questions per Exam: {avg_questions_per_exam:.1f}")
        
        # Course distribution
        courses = [exam['course_code'] for exam in self.exams_data]
        course_counts = Counter(courses)
        print(f"\nCourse Distribution:")
        for course, count in course_counts.most_common():
            print(f"  {course}: {count} exams")
        
        # Question type distribution
        question_types = [q['question_type'] for q in self.questions_data]
        type_counts = Counter(question_types)
        print(f"\nQuestion Type Distribution:")
        for q_type, count in type_counts.most_common():
            percentage = (count / total_questions) * 100
            print(f"  {q_type}: {count} ({percentage:.1f}%)")
        
        # Difficulty distribution
        difficulties = [q['difficulty_score'] for q in self.questions_data]
        difficulty_counts = Counter(difficulties)
        print(f"\nDifficulty Distribution:")
        for diff, count in difficulty_counts.most_common():
            percentage = (count / total_questions) * 100
            print(f"  Level {diff}: {count} ({percentage:.1f}%)")
        
        # Topic analysis
        all_topics = []
        for q in self.questions_data:
            all_topics.extend(q['topics'])
        topic_counts = Counter(all_topics)
        print(f"\nTop Topics:")
        for topic, count in topic_counts.most_common(10):
            print(f"  {topic}: {count} questions")
        
        # Question length analysis
        lengths = [q['length'] for q in self.questions_data]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        print(f"\nQuestion Length Analysis:")
        print(f"  Average Length: {avg_length:.0f} characters")
        print(f"  Shortest: {min(lengths) if lengths else 0} characters")
        print(f"  Longest: {max(lengths) if lengths else 0} characters")
    
    def save_data(self, output_file="exam_analysis.json"):
        """
        Save the analyzed data for future use
        """
        data_to_save = {
            'exams': self.exams_data,
            'questions': self.questions_data,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {output_file}")
    
    def create_visualizations(self):
        """
        Create visualizations to understand your data better
        """
        if not self.questions_data:
            print("No data to visualize. Run analyze_all_exams() first.")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Exam Bank Analysis Dashboard', fontsize=16)
        
        # Question type distribution
        question_types = [q['question_type'] for q in self.questions_data]
        type_counts = Counter(question_types)
        axes[0, 0].pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
        axes[0, 0].set_title('Question Type Distribution')
        
        # Difficulty distribution
        difficulties = [q['difficulty_score'] for q in self.questions_data]
        axes[0, 1].hist(difficulties, bins=4, alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Difficulty Score Distribution')
        axes[0, 1].set_xlabel('Difficulty Score')
        axes[0, 1].set_ylabel('Number of Questions')
        
        # Question length distribution
        lengths = [q['length'] for q in self.questions_data]
        axes[1, 0].hist(lengths, bins=20, alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Question Length Distribution')
        axes[1, 0].set_xlabel('Character Count')
        axes[1, 0].set_ylabel('Number of Questions')
        
        # Course distribution
        courses = [exam['course_code'] for exam in self.exams_data]
        course_counts = Counter(courses)
        axes[1, 1].bar(course_counts.keys(), course_counts.values())
        axes[1, 1].set_title('Exams per Course')
        axes[1, 1].set_xlabel('Course Code')
        axes[1, 1].set_ylabel('Number of Exams')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('exam_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Visualization saved as 'exam_analysis_dashboard.png'")

def main():
    """
    Main function to run the analysis
    This is your starting point!
    """
    print("🎓 AI Exam Generation Project - Phase 1 Starter")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = ExamBankAnalyzer("exam_downloads")
    
    # Process all exams
    analyzer.analyze_all_exams()
    
    # Generate analysis report
    analyzer.generate_analysis_report()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    # Save data for future use
    analyzer.save_data()
    
    print("\n🎉 Phase 1 Complete!")
    print("You now have a foundation for your ML exam generation project.")
    print("Next steps:")
    print("1. Review the analysis report")
    print("2. Look at the visualizations")
    print("3. Start learning about NLP and ML")
    print("4. Move to Phase 2: Building ML models")

if __name__ == "__main__":
    main()
