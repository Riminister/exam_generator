#!/usr/bin/env python3
"""
OpenAI Question Generator
Generates new exam questions using OpenAI's GPT models
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: openai package not installed")
    print("   Install it with: pip install openai")
    sys.exit(1)

# Import graph generation
try:
    from graph_extraction.recreation.graph_generator import GraphGenerator
    GRAPH_GENERATION_AVAILABLE = True
except ImportError:
    GRAPH_GENERATION_AVAILABLE = False
    # Graph generation not available (matplotlib required)


class OpenAIQuestionGenerator:
    """Generate questions using OpenAI API"""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None, 
                 generate_graphs: bool = True):
        """
        Initialize the question generator.
        
        Args:
            model: OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-4o-mini)
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            generate_graphs: Whether to generate graphs for questions that need them
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable or run setup_openai.py"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.generate_graphs = generate_graphs and GRAPH_GENERATION_AVAILABLE
        
        if self.generate_graphs:
            self.graph_generator = GraphGenerator()
        else:
            self.graph_generator = None
        
    def load_example_questions(self, json_file: str = "data/exam_analysis.json", num_examples: int = 5) -> List[str]:
        """Load example questions from your exam bank to use as style references"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            examples = []
            for exam in data.get('exams', []):
                for q in exam.get('questions', []):
                    text = q.get('text', '')
                    # Skip very short or instruction questions
                    if len(text) > 50 and not any(keyword in text.lower()[:100] 
                                                  for keyword in ['write your student', 'fill in']):
                        examples.append(text)
                        if len(examples) >= num_examples:
                            return examples
            
            return examples
        except FileNotFoundError:
            print(f"⚠️  Warning: {json_file} not found. Generating without examples.")
            return []
        except Exception as e:
            print(f"⚠️  Warning: Could not load examples: {e}")
            return []
    
    def create_system_prompt(self, course_subject: Optional[str] = None) -> str:
        """Create system prompt for question generation"""
        base_prompt = """You are an expert exam question writer for university-level economics courses.
Your questions should be:
- Clear and unambiguous
- Academically rigorous
- Appropriate for university-level students
- Following the style and format of the provided examples"""
        
        if course_subject:
            base_prompt += f"\nFocus on: {course_subject}"
        
        return base_prompt
    
    def create_user_prompt(
        self,
        topic: str,
        question_type: str = "multiple_choice",
        difficulty: str = "medium",
        examples: Optional[List[str]] = None,
        marks: Optional[float] = None,
        include_graph: bool = False
    ) -> str:
        """Create user prompt for generating a specific question"""
        
        prompt_parts = [
            f"Generate a {difficulty} difficulty {question_type} question about: {topic}",
        ]
        
        if marks:
            prompt_parts.append(f"Worth {marks} marks")
        
        prompt_parts.append("\nRequirements:")
        
        if question_type == "multiple_choice":
            prompt_parts.append("- Include exactly 4-5 answer options (A, B, C, D, E)")
            prompt_parts.append("- Mark the correct answer")
            prompt_parts.append("- Make distractors plausible but incorrect")
        elif question_type == "essay":
            prompt_parts.append("- Require comprehensive analysis")
            prompt_parts.append("- Include specific instructions (e.g., 'Explain', 'Analyze', 'Compare')")
        elif question_type == "short_answer":
            prompt_parts.append("- Require a brief but specific answer")
            prompt_parts.append("- Include key terms or concepts")
        elif question_type == "numerical":
            prompt_parts.append("- Require a calculation")
            prompt_parts.append("- Include all necessary data")
            prompt_parts.append("- Provide the correct numerical answer")
        
        # Add graph requirement if needed
        if include_graph:
            prompt_parts.append("\n- Include a reference to a figure or graph (e.g., 'Refer to Figure 1')")
            prompt_parts.append("- The question should require analyzing the graph to answer")
        
        if examples:
            prompt_parts.append("\nFollow the style of these example questions:")
            for i, example in enumerate(examples[:3], 1):  # Use first 3 examples
                # Truncate long examples
                example_text = example[:500] + "..." if len(example) > 500 else example
                prompt_parts.append(f"\nExample {i}:\n{example_text}")
        
        prompt_parts.append("\nGenerate the question now:")
        
        return "\n".join(prompt_parts)
    
    def generate_question(
        self,
        topic: str,
        question_type: str = "multiple_choice",
        difficulty: str = "medium",
        course_subject: Optional[str] = None,
        marks: Optional[float] = None,
        examples: Optional[List[str]] = None,
        temperature: float = 0.7,
        include_graph: bool = False
    ) -> Dict:
        """
        Generate a single question.
        
        Args:
            include_graph: Whether to include a graph reference and generate a graph
        
        Returns:
            Dict with 'question' (text), 'metadata', and optionally 'graph_path'
        """
        if examples is None:
            examples = self.load_example_questions()
        
        system_prompt = self.create_system_prompt(course_subject)
        user_prompt = self.create_user_prompt(topic, question_type, difficulty, examples, marks, include_graph)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            
            question_text = response.choices[0].message.content.strip()
            
            result = {
                'question': question_text,
                'topic': topic,
                'question_type': question_type,
                'difficulty': difficulty,
                'marks': marks,
                'model_used': self.model,
                'generated': True,
                'has_graph': include_graph
            }
            
            # Generate graph if requested and available
            if include_graph and self.generate_graphs:
                try:
                    # Detect if question actually references a figure
                    import re
                    figure_refs = re.findall(r'[Ff]igure\s+(\d+)', question_text)
                    if figure_refs or 'figure' in question_text.lower():
                        # Determine graph type from topic
                        graph_type = self._determine_graph_type(topic)
                        
                        # Generate graph
                        graph_path = self._generate_graph_for_question(
                            question_text, topic, graph_type
                        )
                        if graph_path:
                            result['graph_path'] = graph_path
                            result['graph_type'] = graph_type
                except Exception as e:
                    print(f"⚠️  Could not generate graph: {e}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating question: {e}")
            return {
                'error': str(e),
                'topic': topic,
                'question_type': question_type
            }
    
    def _determine_graph_type(self, topic: str) -> str:
        """Determine graph type based on topic"""
        topic_lower = topic.lower()
        
        if any(term in topic_lower for term in ['supply', 'demand', 'equilibrium', 'market']):
            return 'supply_demand'
        elif any(term in topic_lower for term in ['production possibilities', 'ppf', 'ppb']):
            return 'production_possibilities'
        elif any(term in topic_lower for term in ['cost', 'marginal', 'average']):
            return 'cost_curves'
        elif any(term in topic_lower for term in ['indifference', 'utility', 'budget']):
            return 'indifference_curve'
        else:
            return 'supply_demand'  # Default
    
    def _generate_graph_for_question(
        self,
        question_text: str,
        topic: str,
        graph_type: str
    ) -> Optional[str]:
        """Generate a graph file for a question"""
        if not self.graph_generator:
            return None
        
        try:
            import re
            # Extract figure number from question
            figure_match = re.search(r'[Ff]igure\s+(\d+)', question_text)
            figure_num = figure_match.group(1) if figure_match else "1"
            
            output_dir = Path("generated_graphs")
            output_dir.mkdir(exist_ok=True)
            
            # Create graph description dict
            graph_desc = {
                'graph_type': graph_type,
                'x_axis': {'label': self._get_axis_label(graph_type, 'x')},
                'y_axis': {'label': self._get_axis_label(graph_type, 'y')}
            }
            
            output_path = output_dir / f"generated_figure_{figure_num}.png"
            
            self.graph_generator.create_graph_from_description(
                graph_desc,
                str(output_path)
            )
            
            return str(output_path)
        except Exception as e:
            print(f"⚠️  Error in graph generation: {e}")
            return None
    
    def _get_axis_label(self, graph_type: str, axis: str) -> str:
        """Get appropriate axis label for graph type"""
        labels = {
            'supply_demand': {'x': 'Quantity', 'y': 'Price'},
            'production_possibilities': {'x': 'Good X', 'y': 'Good Y'},
            'cost_curves': {'x': 'Quantity', 'y': 'Cost'},
            'indifference_curve': {'x': 'Good X', 'y': 'Good Y'}
        }
        return labels.get(graph_type, {'x': 'X', 'y': 'Y'}).get(axis, axis)
    
    def generate_multiple_questions(
        self,
        topics: List[str],
        question_type: str = "multiple_choice",
        difficulty: str = "medium",
        course_subject: Optional[str] = None,
        marks: Optional[float] = None
    ) -> List[Dict]:
        """Generate multiple questions for different topics"""
        questions = []
        examples = self.load_example_questions()
        
        print(f"Generating {len(topics)} {question_type} questions...")
        for i, topic in enumerate(topics, 1):
            print(f"  [{i}/{len(topics)}] Generating question about: {topic}")
            
            question = self.generate_question(
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                course_subject=course_subject,
                marks=marks,
                examples=examples
            )
            
            questions.append(question)
            
            # Small delay to avoid rate limits
            import time
            time.sleep(0.5)
        
        return questions
    
    def generate_exam(
        self,
        num_questions: int = 10,
        question_type_distribution: Optional[Dict[str, int]] = None,
        difficulty_distribution: Optional[Dict[str, float]] = None,
        topics: Optional[List[str]] = None,
        course_subject: str = "Economics"
    ) -> Dict:
        """
        Generate a complete exam with multiple questions.
        
        Args:
            num_questions: Total number of questions
            question_type_distribution: Dict like {'multiple_choice': 5, 'essay': 3}
            difficulty_distribution: Dict like {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
            topics: List of topics to cover (if None, generates generic topics)
            course_subject: Subject area for the exam
        """
        if topics is None:
            # Generate default topics
            topics = [
                "supply and demand",
                "market equilibrium",
                "price elasticity",
                "consumer surplus",
                "producer surplus",
                "market structures",
                "monopoly pricing",
                "game theory",
                "international trade",
                "economic growth"
            ][:num_questions]
        
        all_questions = []
        examples = self.load_example_questions()
        
        # Generate questions based on distribution
        if question_type_distribution:
            for q_type, count in question_type_distribution.items():
                for _ in range(count):
                    topic = topics[len(all_questions) % len(topics)]
                    question = self.generate_question(
                        topic=topic,
                        question_type=q_type,
                        difficulty="medium",
                        course_subject=course_subject,
                        examples=examples
                    )
                    all_questions.append(question)
        else:
            # Simple generation
            for i in range(num_questions):
                topic = topics[i % len(topics)]
                question = self.generate_question(
                    topic=topic,
                    question_type="multiple_choice",
                    difficulty="medium",
                    course_subject=course_subject,
                    examples=examples
                )
                all_questions.append(question)
        
        return {
            'title': f'Generated {course_subject} Exam',
            'total_questions': len(all_questions),
            'questions': all_questions,
            'course_subject': course_subject,
            'generated': True
        }


def main():
    """Example usage"""
    print("=" * 70)
    print("OpenAI Question Generator")
    print("=" * 70)
    print()
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found!")
        print("   Run: python setup_openai.py")
        return
    
    # Initialize generator
    try:
        generator = OpenAIQuestionGenerator(model="gpt-4o-mini")  # Use cheaper model for testing
        print("✅ OpenAI connection established")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Example 1: Generate a single question
    print("Example 1: Generating a single question...")
    question = generator.generate_question(
        topic="supply and demand",
        question_type="multiple_choice",
        difficulty="medium",
        course_subject="Economics"
    )
    
    if 'error' not in question:
        print("\nGenerated Question:")
        print("-" * 70)
        print(question['question'])
        print("-" * 70)
        print()
    
    # Example 2: Generate multiple questions
    print("Example 2: Generating multiple questions...")
    questions = generator.generate_multiple_questions(
        topics=["market equilibrium", "price elasticity"],
        question_type="multiple_choice",
        difficulty="medium",
        course_subject="Economics"
    )
    
    print(f"\n✅ Generated {len(questions)} questions")
    
    # Save to file
    output_file = "generated_questions_openai.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to: {output_file}")
    print()
    print("=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Review generated questions for quality")
    print("2. Adjust prompts in openai_question_generator.py")
    print("3. Try different models (gpt-4, gpt-4-turbo)")
    print("4. Generate full exams with generate_exam() method")


if __name__ == "__main__":
    main()

