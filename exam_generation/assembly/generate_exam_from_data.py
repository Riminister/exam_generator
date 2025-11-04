#!/usr/bin/env python3
"""
Generate Exams from Existing Questions
Selects and arranges questions from your exam bank to create new exams
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict


def load_questions(json_file: str = "data/exam_analysis.json") -> List[Dict]:
    """Load all questions from exam_analysis.json"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = []
    for exam in data.get('exams', []):
        course_code = exam.get('course_code', 'unknown')
        for q in exam.get('questions', []):
            q_copy = q.copy()
            q_copy['source_exam'] = exam.get('filename', 'unknown')
            q_copy['source_course'] = course_code
            questions.append(q_copy)
    
    return questions


def filter_questions(
    questions: List[Dict],
    question_types: Optional[List[str]] = None,
    min_difficulty: Optional[float] = None,
    max_difficulty: Optional[float] = None,
    course_code: Optional[str] = None,
    min_length: Optional[int] = None,
    exclude_instructions: bool = True
) -> List[Dict]:
    """Filter questions based on criteria"""
    filtered = questions.copy()
    
    # Exclude instruction/header questions
    if exclude_instructions:
        filtered = [
            q for q in filtered 
            if not any(keyword in q.get('text', '').lower()[:100] 
                      for keyword in ['write your student', 'fill in', 'test form', 'answer sheet'])
        ]
    
    # Filter by question type
    if question_types:
        filtered = [q for q in filtered if q.get('question_type') in question_types]
    
    # Filter by difficulty
    if min_difficulty is not None:
        filtered = [q for q in filtered 
                   if q.get('difficulty_score') is not None 
                   and q.get('difficulty_score', 0) >= min_difficulty]
    
    if max_difficulty is not None:
        filtered = [q for q in filtered 
                   if q.get('difficulty_score') is not None 
                   and q.get('difficulty_score', 1) <= max_difficulty]
    
    # Filter by course
    if course_code:
        filtered = [q for q in filtered if q.get('source_course') == course_code]
    
    # Filter by length
    if min_length:
        filtered = [q for q in filtered if len(q.get('text', '')) >= min_length]
    
    return filtered


def generate_exam(
    questions: List[Dict],
    num_questions: int = 10,
    difficulty_distribution: Optional[Dict[str, float]] = None,
    question_type_distribution: Optional[Dict[str, int]] = None,
    randomize: bool = True
) -> List[Dict]:
    """
    Generate an exam by selecting questions based on criteria.
    
    Args:
        questions: List of available questions
        num_questions: Total number of questions to select
        difficulty_distribution: Dict like {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
        question_type_distribution: Dict like {'multiple_choice': 5, 'essay': 3, 'short_answer': 2}
        randomize: Whether to randomize selection within constraints
    
    Returns:
        List of selected questions
    """
    selected = []
    
    # If question type distribution is specified, use it
    if question_type_distribution:
        for q_type, count in question_type_distribution.items():
            type_questions = [q for q in questions if q.get('question_type') == q_type]
            if len(type_questions) < count:
                print(f"⚠️  Warning: Only {len(type_questions)} {q_type} questions available, requested {count}")
                count = len(type_questions)
            
            if randomize:
                selected.extend(random.sample(type_questions, min(count, len(type_questions))))
            else:
                selected.extend(type_questions[:count])
        
        # Fill remaining slots randomly
        remaining = num_questions - len(selected)
        if remaining > 0:
            available = [q for q in questions if q not in selected]
            if randomize:
                selected.extend(random.sample(available, min(remaining, len(available))))
            else:
                selected.extend(available[:remaining])
    
    # If difficulty distribution is specified
    elif difficulty_distribution:
        # Define difficulty ranges
        ranges = {
            'easy': (0.0, 0.4),
            'medium': (0.4, 0.7),
            'hard': (0.7, 1.0)
        }
        
        for difficulty, proportion in difficulty_distribution.items():
            count = int(num_questions * proportion)
            if count == 0:
                continue
                
            min_diff, max_diff = ranges.get(difficulty, (0.0, 1.0))
            diff_questions = [
                q for q in questions
                if q.get('difficulty_score') is not None
                and min_diff <= q.get('difficulty_score', 0) < max_diff
            ]
            
            if len(diff_questions) < count:
                print(f"⚠️  Warning: Only {len(diff_questions)} {difficulty} questions available, requested {count}")
                count = len(diff_questions)
            
            if randomize:
                selected.extend(random.sample(diff_questions, min(count, len(diff_questions))))
            else:
                selected.extend(diff_questions[:count])
        
        # Fill remaining slots
        remaining = num_questions - len(selected)
        if remaining > 0:
            available = [q for q in questions if q not in selected]
            if randomize:
                selected.extend(random.sample(available, min(remaining, len(available))))
            else:
                selected.extend(available[:remaining])
    
    else:
        # Simple random selection
        if randomize:
            selected = random.sample(questions, min(num_questions, len(questions)))
        else:
            selected = questions[:num_questions]
    
    # Shuffle final selection
    if randomize:
        random.shuffle(selected)
    
    return selected[:num_questions]


def format_exam_for_output(questions: List[Dict], title: str = "Generated Exam") -> str:
    """Format selected questions as a printable exam"""
    output = []
    output.append("=" * 70)
    output.append(title.upper())
    output.append("=" * 70)
    output.append("")
    
    for i, q in enumerate(questions, 1):
        output.append(f"\nQuestion {i} [{q.get('question_type', 'unknown').upper()}]")
        if q.get('difficulty_score'):
            output.append(f"Difficulty: {q.get('difficulty_score'):.2f}")
        if q.get('question_marks'):
            output.append(f"Marks: {q.get('question_marks')}")
        output.append("-" * 70)
        output.append(q.get('text', ''))
        output.append("")
    
    output.append("=" * 70)
    output.append(f"\nTotal Questions: {len(questions)}")
    
    return "\n".join(output)


def save_exam_json(questions: List[Dict], output_file: str = "generated_exam.json"):
    """Save generated exam as JSON"""
    exam_data = {
        'title': 'Generated Exam',
        'total_questions': len(questions),
        'questions': questions,
        'metadata': {
            'question_types': list(set(q.get('question_type') for q in questions)),
            'avg_difficulty': sum(q.get('difficulty_score', 0) for q in questions if q.get('difficulty_score')) / 
                            max(len([q for q in questions if q.get('difficulty_score')]), 1),
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exam_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exam saved to: {output_file}")


def main():
    """Main function - demonstrates exam generation"""
    # Fix encoding for Windows
    import sys
    if sys.platform == 'win32':
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 70)
    print("EXAM GENERATOR - Assemble Exams from Question Bank")
    print("=" * 70)
    print()
    
    # Load questions
    print("Loading questions from exam_analysis.json...")
    questions = load_questions()
    print(f"Loaded {len(questions)} total questions")
    print()
    
    # Filter out instruction/header questions
    usable_questions = filter_questions(questions, exclude_instructions=True, min_length=50)
    print(f"{len(usable_questions)} usable questions (after filtering)")
    print()
    
    # Show statistics
    question_types = defaultdict(int)
    for q in usable_questions:
        question_types[q.get('question_type', 'unknown')] += 1
    
    print("Question Type Distribution:")
    for q_type, count in sorted(question_types.items(), key=lambda x: -x[1]):
        print(f"  {q_type}: {count}")
    print()
    
    # Example 1: Generate a balanced exam
    print("Example 1: Generating balanced exam (10 questions, mixed types)")
    exam1 = generate_exam(
        usable_questions,
        num_questions=10,
        question_type_distribution={
            'multiple_choice': 5,
            'essay': 2,
            'short_answer': 2,
            'numerical': 1
        }
    )
    print(f"Generated exam with {len(exam1)} questions")
    print()
    
    # Save example exam
    save_exam_json(exam1, "generated_exam_example.json")
    
    # Example 2: Generate difficulty-balanced exam
    questions_with_difficulty = [q for q in usable_questions if q.get('difficulty_score') is not None]
    if len(questions_with_difficulty) > 0:
        print("Example 2: Generating difficulty-balanced exam")
        exam2 = generate_exam(
            questions_with_difficulty,
            num_questions=8,
            difficulty_distribution={
                'easy': 0.25,
                'medium': 0.50,
                'hard': 0.25
            }
        )
        print(f"Generated exam with {len(exam2)} questions")
        print()
    
    # Print formatted exam
    print("\n" + "=" * 70)
    print("FORMATTED EXAM OUTPUT")
    print("=" * 70)
    print(format_exam_for_output(exam1[:5], "Sample Exam (First 5 Questions)"))
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Customize the generate_exam() function for your needs")
    print("2. Add filters for specific topics or course codes")
    print("3. Export to PDF or Word format")
    print("4. Integrate with your exam management system")
    print()
    print("To generate NEW questions (not just select existing ones):")
    print("  - You'll need to add LLM integration (GPT-4, Claude, etc.)")
    print("  - See EXAM_GENERATION_GUIDE.md for details")


if __name__ == "__main__":
    main()

