#!/usr/bin/env python3
"""
OpenAI Question Analyzer - Lightweight Integration
Uses OpenAI to analyze questions and extract graph/figure descriptions
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OpenAIQuestionAnalyzer:
    """Lightweight OpenAI integration for question analysis"""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """Initialize analyzer"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or run setup_openai.py")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Patterns to detect figure references
        self.figure_patterns = [
            r'[Rr]efer to [Ff]igure\s+(\d+[-\w]*)',
            r'[Ss]ee [Ff]igure\s+(\d+[-\w]*)',
            r'[Ff]igure\s+(\d+[-\w]*)',
            r'[Ff]ig\.\s*(\d+[-\w]*)',
            r'[Tt]he [Dd]iagram',
            r'[Tt]he [Cc]hart',
        ]
    
    def detect_figure_references(self, question_text: str) -> List[Dict]:
        """Detect figure references in question text"""
        references = []
        
        for pattern in self.figure_patterns:
            matches = re.finditer(pattern, question_text)
            for match in matches:
                figure_num = match.group(1) if match.lastindex else None
                references.append({
                    'figure_label': match.group(0),
                    'figure_number': figure_num,
                    'position': match.start()
                })
        
        return references
    
    def analyze_question_content(self, question_text: str) -> Dict:
        """
        Analyze question content using OpenAI.
        Extracts topics, difficulty indicators, and graph descriptions.
        """
        system_prompt = """You are an expert at analyzing exam questions.
Analyze the question and extract:
1. Main topics/concepts
2. Question type indicators
3. Graph/figure descriptions (if referenced)
4. Difficulty indicators
5. Key concepts being tested

Return a JSON response with this structure."""
        
        user_prompt = f"""Analyze this exam question:

{question_text}

Extract:
- Topics: List main topics (e.g., ["supply and demand", "market equilibrium"])
- Question type: multiple_choice, essay, short_answer, numerical, etc.
- Has graph: true/false
- Graph description: If question references a figure/graph, describe what it shows (axes, curves, relationships)
- Difficulty indicators: easy, medium, hard
- Key concepts: List 2-3 key concepts being tested

Return as JSON only."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            analysis = json.loads(result_text)
            
            # Add figure references
            figure_refs = self.detect_figure_references(question_text)
            analysis['figure_references'] = figure_refs
            analysis['has_figures'] = len(figure_refs) > 0
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'has_figures': len(self.detect_figure_references(question_text)) > 0,
                'figure_references': self.detect_figure_references(question_text)
            }
    
    def describe_graph_from_text(self, question_text: str, figure_context: Optional[str] = None) -> Dict:
        """
        Extract graph description from question text that references figures.
        
        Returns dict with:
        - graph_type: supply_demand, production_possibilities, cost_curves, etc.
        - axes: {x: label, y: label}
        - curves: List of curves with labels
        - relationships: Description of relationships shown
        """
        system_prompt = """You are an expert at analyzing economic graphs and figures.
When a question references a figure, extract the graph description in detail."""
        
        context = f"\nContext: {figure_context}\n" if figure_context else ""
        
        user_prompt = f"""This question references a figure/graph:

{question_text}
{context}

Extract the graph description:
- Graph type (supply_demand, production_possibilities, cost_curves, indifference_curve, etc.)
- X-axis label and range
- Y-axis label and range  
- Curves/lines shown (with labels and descriptions)
- Key points or relationships
- Any specific values mentioned

Return as JSON with structure:
{{
  "graph_type": "supply_demand",
  "x_axis": {{"label": "Quantity", "range": [0, 100]}},
  "y_axis": {{"label": "Price", "range": [0, 50]}},
  "curves": [
    {{"name": "Demand", "type": "line", "slope": "negative", "description": "Downward sloping"}},
    {{"name": "Supply", "type": "line", "slope": "positive", "description": "Upward sloping"}}
  ],
  "key_points": ["Equilibrium at Q=50, P=25"],
  "relationships": "Supply and demand intersect at equilibrium"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            return json.loads(result_text)
            
        except Exception as e:
            return {'error': str(e), 'graph_type': 'unknown'}


def analyze_questions_with_openai(
    questions: List[Dict],
    analyze_graphs: bool = True
) -> List[Dict]:
    """
    Analyze questions using OpenAI.
    
    Args:
        questions: List of question dicts
        analyze_graphs: Whether to analyze graph descriptions
        
    Returns:
        Questions with added OpenAI analysis
    """
    if not OPENAI_AVAILABLE or not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI not available. Skipping analysis.")
        return questions
    
    analyzer = OpenAIQuestionAnalyzer()
    analyzed_questions = []
    
    print(f"Analyzing {len(questions)} questions with OpenAI...")
    
    for i, question in enumerate(questions, 1):
        question_text = question.get('text', '')
        
        if not question_text or len(question_text) < 20:
            analyzed_questions.append(question)
            continue
        
        print(f"  [{i}/{len(questions)}] Analyzing question {question.get('question_number', i)}...")
        
        # Analyze question content
        try:
            analysis = analyzer.analyze_question_content(question_text)
            
            # Add analysis to question
            question['openai_analysis'] = analysis
            
            # If question has figures, get graph description
            if analyze_graphs and analysis.get('has_figures'):
                graph_desc = analyzer.describe_graph_from_text(question_text)
                question['graph_description'] = graph_desc
                print(f"    📊 Found graph: {graph_desc.get('graph_type', 'unknown')}")
            
            # Update topics if extracted
            if 'Topics' in analysis or 'topics' in analysis:
                topics = analysis.get('Topics') or analysis.get('topics', [])
                if topics and isinstance(topics, list):
                    question['topics'] = topics
            
        except Exception as e:
            print(f"    ⚠️  Error analyzing: {e}")
            question['openai_analysis'] = {'error': str(e)}
        
        analyzed_questions.append(question)
    
    print(f"✅ Analysis complete!")
    return analyzed_questions


if __name__ == "__main__":
    # Test the analyzer
    print("Testing OpenAI Question Analyzer...")
    
    test_question = """2) Refer to Figure 1-1. For the government, the opportunity cost of one search and rescue helicopter is:
A) 0 kilometres of highway repair.
B) 50 kilometres of highway repair.
C) 100 kilometres of highway repair.
D) 150 kilometres of highway repair.
E) 200 kilometres of highway repair."""
    
    try:
        analyzer = OpenAIQuestionAnalyzer()
        analysis = analyzer.analyze_question_content(test_question)
        print("\nAnalysis Result:")
        print(json.dumps(analysis, indent=2))
        
        if analysis.get('has_figures'):
            graph_desc = analyzer.describe_graph_from_text(test_question)
            print("\nGraph Description:")
            print(json.dumps(graph_desc, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

