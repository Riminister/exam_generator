#!/usr/bin/env python3
"""
Integrate Graph Analysis into Question Processing Pipeline
Adds figure detection and graph generation to existing questions
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add exam_analysis to path
sys.path.insert(0, str(Path(__file__).parent))

from graph_extraction.analysis.graph_analyzer import analyze_questions_with_figures, GraphAnalyzer
from graph_extraction.recreation.graph_generator import generate_graph_for_question, GraphGenerator


def enhance_questions_with_graphs(
    input_file: str = "data/exam_analysis.json",
    output_file: str = "data/exam_analysis_with_graphs.json",
    analyze_existing: bool = True,
    generate_graphs: bool = True
) -> Dict:
    """
    Enhance questions with graph analysis and generation.
    
    Args:
        input_file: Input JSON file with questions
        output_file: Output JSON file with enhanced questions
        analyze_existing: Whether to analyze existing questions for figures
        generate_graphs: Whether to generate graph images
    """
    print("=" * 70)
    print("GRAPH ANALYSIS INTEGRATION")
    print("=" * 70)
    print()
    
    # Load questions
    print(f"Loading questions from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_questions = []
    for exam in data.get('exams', []):
        all_questions.extend(exam.get('questions', []))
    
    print(f"✅ Loaded {len(all_questions)} questions")
    print()
    
    stats = {
        'total_questions': len(all_questions),
        'questions_with_figures': 0,
        'graphs_generated': 0,
        'errors': 0
    }
    
    # Analyze questions for figure references
    if analyze_existing:
        print("Analyzing questions for figure references...")
        try:
            enhanced_questions = analyze_questions_with_figures(all_questions)
            
            for q in enhanced_questions:
                if q.get('has_figures'):
                    stats['questions_with_figures'] += 1
            
            all_questions = enhanced_questions
            print(f"✅ Found {stats['questions_with_figures']} questions with figure references")
            print()
        except Exception as e:
            print(f"⚠️  Error analyzing figures: {e}")
            print("   Continuing without figure analysis...")
            print()
    
    # Generate graphs for questions with figures
    if generate_graphs:
        print("Generating graphs for questions with figures...")
        graph_output_dir = Path("generated_graphs")
        graph_output_dir.mkdir(exist_ok=True)
        
        for question in all_questions:
            if question.get('has_figures'):
                try:
                    graph_path = generate_graph_for_question(
                        question,
                        str(graph_output_dir)
                    )
                    if graph_path:
                        question['generated_graph_path'] = graph_path
                        stats['graphs_generated'] += 1
                        print(f"  ✅ Generated graph for question {question.get('question_number')}")
                except Exception as e:
                    print(f"  ⚠️  Error generating graph for question {question.get('question_number')}: {e}")
                    stats['errors'] += 1
        
        print(f"✅ Generated {stats['graphs_generated']} graphs")
        print()
    
    # Update exam data with enhanced questions
    question_index = 0
    for exam in data.get('exams', []):
        exam_questions = exam.get('questions', [])
        for i in range(len(exam_questions)):
            if question_index < len(all_questions):
                exam['questions'][i] = all_questions[question_index]
                question_index += 1
    
    # Save enhanced data
    print(f"Saving enhanced questions to {output_file}...")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {output_file}")
    print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total questions processed: {stats['total_questions']}")
    print(f"Questions with figure references: {stats['questions_with_figures']}")
    print(f"Graphs generated: {stats['graphs_generated']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 70)
    
    return {
        'stats': stats,
        'output_file': output_file
    }


if __name__ == "__main__":
    enhance_questions_with_graphs()

