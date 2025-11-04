#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick script to analyze current dataset before building models"""

import json
import sys
import os
from pathlib import Path
from collections import Counter

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_dataset(json_file="data/exam_analysis.json"):
    """Analyze the current dataset and provide recommendations"""
    
    if not Path(json_file).exists():
        print(f"❌ {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    exams = data.get('exams', [])
    
    if not exams:
        print("❌ No exams found in dataset!")
        return
    
    # Gather statistics
    total_questions = []
    question_types = []
    courses = []
    topics = []
    
    for exam in exams:
        questions = exam.get('questions', [])
        total_questions.extend(questions)
        courses.append(exam.get('course_code', 'unknown'))
        for q in questions:
            question_types.append(q.get('question_type', 'unknown'))
            topics.extend(q.get('topics', []))
    
    # Print analysis
    print("=" * 70)
    print("📊 CURRENT DATASET ANALYSIS")
    print("=" * 70)
    print(f"\n✅ Total Exams: {len(exams)}")
    print(f"✅ Total Questions: {len(total_questions)}")
    print(f"✅ Unique Courses: {len(set(courses))}")
    print(f"   Courses: {', '.join(sorted(set(courses)))}")
    
    print(f"\n📝 Question Types:")
    type_counts = Counter(question_types)
    for qtype, count in type_counts.most_common():
        print(f"   - {qtype}: {count} ({count/len(question_types)*100:.1f}%)")
    
    print(f"\n🏷️  Topics:")
    topic_counts = Counter(topics)
    if topic_counts:
        for topic, count in topic_counts.most_common(10):
            print(f"   - {topic}: {count}")
    else:
        print("   (No topics extracted yet)")
    
    # Calculate average questions per exam
    avg_q_per_exam = len(total_questions) / len(exams) if exams else 0
    print(f"\n📈 Average Questions per Exam: {avg_q_per_exam:.1f}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS FOR MODEL BUILDING")
    print("=" * 70)
    
    if len(total_questions) < 100:
        print("\n⚠️  Dataset is SMALL (<100 questions)")
        print("   → Start with simple models first:")
        print("      • Basic classification (question type)")
        print("      • Simple rule-based difficulty assessment")
        print("      • Test data cleaning pipeline")
        print("\n   → Download more exams AFTER validating approach")
    elif len(total_questions) < 500:
        print("\n✅ Dataset is MEDIUM (100-500 questions)")
        print("   → Good for initial model testing:")
        print("      • Question classification models")
        print("      • Topic extraction/clustering")
        print("      • Basic difficulty prediction")
        print("\n   → Can start model development, but consider:")
        print("      • Downloading more data for better generalization")
        print("      • Focus on one course first to understand patterns")
    else:
        print("\n✅ Dataset is LARGE (500+ questions)")
        print("   → Ready for serious model development:")
        print("      • Train classification models")
        print("      • Build topic models (LDA, etc.)")
        print("      • Fine-tune language models")
        print("\n   → Consider downloading more for:")
        print("      • Better generalization across courses")
        print("      • More diverse question types")
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("   1. Run data cleaning: python exam_analysis/data_cleaner.py")
    print("   2. Build exploratory analysis notebook")
    print("   3. Start with simple ML models (classification, clustering)")
    print("   4. Test approach on this dataset")
    print("   5. If results look good → download more exams")
    print("   6. If issues found → fix pipeline first, then scale up")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_dataset()

