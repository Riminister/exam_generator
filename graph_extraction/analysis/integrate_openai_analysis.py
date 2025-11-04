#!/usr/bin/env python3
"""
Integrate OpenAI Analysis into Question Extraction Pipeline
Lightweight integration that adds OpenAI analysis to existing questions
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from graph_extraction.analysis.openai_question_analyzer import analyze_questions_with_openai
from graph_extraction.recreation.graph_recreator import recreate_graph_for_question


def enhance_exam_analysis_with_openai(
    input_file: str = "data/exam_analysis.json",
    output_file: str = "data/exam_analysis_with_openai.json",
    analyze_graphs: bool = True,
    recreate_graphs: bool = True
) -> Dict:
    """
    Enhance exam analysis with OpenAI insights.
    
    Args:
        input_file: Input exam_analysis.json
        output_file: Output file with OpenAI analysis
        analyze_graphs: Whether to analyze graph descriptions
        recreate_graphs: Whether to recreate graphs with matplotlib
        
    Returns:
        Enhanced data dict
    """
    print("=" * 70)
    print("OpenAI Question Analysis Integration")
    print("=" * 70)
    print()
    
    # Load existing analysis
    print(f"Loading questions from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_questions = []
    for exam in data.get('exams', []):
        all_questions.extend(exam.get('questions', []))
    
    print(f"✅ Loaded {len(all_questions)} questions from {len(data.get('exams', []))} exams")
    print()
    
    # Analyze with OpenAI
    if analyze_graphs:
        print("Analyzing questions with OpenAI...")
        analyzed_questions = analyze_questions_with_openai(
            all_questions,
            analyze_graphs=analyze_graphs
        )
    else:
        analyzed_questions = all_questions
    
    # Recreate graphs
    if recreate_graphs:
        print("\nRecreating graphs for questions with figures...")
        graph_count = 0
        for question in analyzed_questions:
            if question.get('graph_description') and 'error' not in question.get('graph_description', {}):
                graph_path = recreate_graph_for_question(question)
                if graph_path:
                    question['generated_graph_path'] = graph_path
                    graph_count += 1
                    print(f"  ✅ Generated graph for question {question.get('question_number')}")
        
        print(f"\n✅ Recreated {graph_count} graphs")
    
    # Update data structure
    question_idx = 0
    for exam in data.get('exams', []):
        num_questions = len(exam.get('questions', []))
        exam['questions'] = analyzed_questions[question_idx:question_idx + num_questions]
        question_idx += num_questions
    
    # Save enhanced data
    print(f"\nSaving enhanced analysis to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Done!")
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    # Statistics
    questions_with_analysis = sum(1 for q in analyzed_questions if q.get('openai_analysis'))
    questions_with_graphs = sum(1 for q in analyzed_questions if q.get('graph_description'))
    graphs_generated = sum(1 for q in analyzed_questions if q.get('generated_graph_path'))
    
    print(f"Questions analyzed: {questions_with_analysis}/{len(analyzed_questions)}")
    print(f"Questions with graphs: {questions_with_graphs}")
    print(f"Graphs recreated: {graphs_generated}")
    print()
    print("Next steps:")
    print("1. Review enhanced_analysis.json to see OpenAI insights")
    print("2. Check generated_graphs/ folder for recreated figures")
    print("3. Use graph descriptions when generating new questions")
    
    return data


if __name__ == "__main__":
    enhance_exam_analysis_with_openai()

