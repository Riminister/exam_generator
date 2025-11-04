#!/usr/bin/env python3
"""
Graph and Figure Analysis using OpenAI Vision API
Analyzes images/diagrams in exam questions and extracts graph descriptions
"""

import os
import re
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io


class GraphAnalyzer:
    """Analyze graphs and figures in exam questions using OpenAI Vision"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the graph analyzer.
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or run setup_openai.py")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Patterns to detect figure references
        self.figure_patterns = [
            r'[Rr]efer to [Ff]igure\s+(\d+[-\w]*)',
            r'[Ss]ee [Ff]igure\s+(\d+[-\w]*)',
            r'[Ff]igure\s+(\d+[-\w]*)',
            r'[Ff]ig\.\s*(\d+[-\w]*)',
            r'[Tt]he [Ff]igure [Aa]bove',
            r'[Tt]he [Dd]iagram [Bb]elow',
            r'[Tt]he [Cc]hart [Ss]hown',
        ]
    
    def detect_figure_references(self, question_text: str) -> List[Dict]:
        """
        Detect if a question references a figure or graph.
        
        Returns:
            List of dicts with 'figure_id', 'reference_text', 'position'
        """
        references = []
        
        for pattern in self.figure_patterns:
            matches = re.finditer(pattern, question_text)
            for match in matches:
                figure_id = match.group(1) if match.groups() else "unknown"
                references.append({
                    'figure_id': figure_id,
                    'reference_text': match.group(0),
                    'position': match.start(),
                    'pattern': pattern
                })
        
        return references
    
    def extract_images_from_pdf(self, pdf_path: str, page_num: int) -> List[Image.Image]:
        """
        Extract images from a specific PDF page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            
        Returns:
            List of PIL Images
        """
        try:
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                return []
            
            page = doc[page_num]
            images = []
            
            # Get image list
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                images.append(image)
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"⚠️  Error extracting images from PDF: {e}")
            return []
    
    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string for OpenAI API"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def analyze_image_with_openai(
        self,
        image: Image.Image,
        question_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze an image using OpenAI Vision API.
        
        Args:
            image: PIL Image to analyze
            question_context: Optional question text for context
            
        Returns:
            Dict with 'description', 'graph_type', 'data_points', etc.
        """
        try:
            # Convert image to base64
            base64_image = self.image_to_base64(image)
            
            # Create prompt
            prompt = """Analyze this graph or diagram from an economics exam question.
            
            Provide a detailed description including:
            1. Type of graph (supply/demand, production possibilities, cost curves, etc.)
            2. Axes labels and units
            3. Key data points, curves, and their labels
            4. Important values or ranges
            5. Any annotations or special features
            
            Format your response as structured information that could be used to recreate this graph programmatically.
            
            If this is a graph, also extract:
            - X-axis: label and range
            - Y-axis: label and range
            - Curves/lines with their equations or key points
            - Areas marked (e.g., consumer surplus, deadweight loss)
            """
            
            if question_context:
                prompt += f"\n\nContext from the question: {question_context[:200]}"
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use vision-capable model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            description = response.choices[0].message.content
            
            # Try to extract structured data
            graph_data = self._parse_graph_description(description)
            
            return {
                'description': description,
                'graph_type': graph_data.get('graph_type'),
                'x_axis': graph_data.get('x_axis'),
                'y_axis': graph_data.get('y_axis'),
                'curves': graph_data.get('curves', []),
                'data_points': graph_data.get('data_points', []),
                'areas': graph_data.get('areas', []),
                'raw_response': description
            }
            
        except Exception as e:
            print(f"❌ Error analyzing image with OpenAI: {e}")
            return {
                'error': str(e),
                'description': None
            }
    
    def _parse_graph_description(self, description: str) -> Dict:
        """
        Parse OpenAI's description to extract structured graph data.
        
        This is a basic parser - can be enhanced with more sophisticated NLP.
        """
        graph_data = {
            'graph_type': None,
            'x_axis': {},
            'y_axis': {},
            'curves': [],
            'data_points': [],
            'areas': []
        }
        
        description_lower = description.lower()
        
        # Detect graph type
        if 'supply' in description_lower and 'demand' in description_lower:
            graph_data['graph_type'] = 'supply_demand'
        elif 'production possibilities' in description_lower:
            graph_data['graph_type'] = 'production_possibilities'
        elif 'cost' in description_lower and 'curve' in description_lower:
            graph_data['graph_type'] = 'cost_curves'
        elif 'indifference' in description_lower:
            graph_data['graph_type'] = 'indifference_curve'
        
        # Extract axes (basic pattern matching)
        x_axis_match = re.search(r'x[- ]axis[:\s]+([^\n]+)', description, re.IGNORECASE)
        if x_axis_match:
            graph_data['x_axis']['label'] = x_axis_match.group(1).strip()
        
        y_axis_match = re.search(r'y[- ]axis[:\s]+([^\n]+)', description, re.IGNORECASE)
        if y_axis_match:
            graph_data['y_axis']['label'] = y_axis_match.group(1).strip()
        
        return graph_data
    
    def analyze_question_with_figures(
        self,
        question_text: str,
        pdf_path: Optional[str] = None,
        page_num: Optional[int] = None
    ) -> Dict:
        """
        Analyze a question that references figures.
        
        Args:
            question_text: The question text
            pdf_path: Optional path to PDF file
            page_num: Optional page number in PDF
            
        Returns:
            Dict with figure references and analysis
        """
        # Detect figure references
        figure_refs = self.detect_figure_references(question_text)
        
        result = {
            'has_figures': len(figure_refs) > 0,
            'figure_references': figure_refs,
            'figure_analyses': []
        }
        
        # If we have PDF and page number, extract and analyze images
        if pdf_path and page_num is not None and Path(pdf_path).exists():
            images = self.extract_images_from_pdf(pdf_path, page_num)
            
            for i, image in enumerate(images):
                analysis = self.analyze_image_with_openai(image, question_text)
                result['figure_analyses'].append({
                    'image_index': i,
                    'analysis': analysis
                })
        
        return result


def analyze_questions_with_figures(
    questions: List[Dict],
    pdf_source: Optional[str] = None
) -> List[Dict]:
    """
    Analyze all questions to detect and describe figures.
    
    Args:
        questions: List of question dicts
        pdf_source: Optional path to source PDF
        
    Returns:
        Questions with added figure analysis
    """
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not set. Skipping figure analysis.")
        return questions
    
    analyzer = GraphAnalyzer()
    analyzed_questions = []
    
    for question in questions:
        question_text = question.get('text', '')
        
        # Detect if question has figure references
        figure_info = analyzer.analyze_question_with_figures(question_text)
        
        if figure_info['has_figures']:
            question['has_figures'] = True
            question['figure_references'] = figure_info['figure_references']
            question['figure_analyses'] = figure_info['figure_analyses']
            print(f"  📊 Question {question.get('question_number')} references figures")
        
        analyzed_questions.append(question)
    
    return analyzed_questions


if __name__ == "__main__":
    # Test the analyzer
    print("Testing Graph Analyzer...")
    
    test_question = "Refer to Figure 1-1. For the government, the opportunity cost of one search and rescue helicopter is:"
    
    analyzer = GraphAnalyzer()
    result = analyzer.analyze_question_with_figures(test_question)
    
    print(f"Has figures: {result['has_figures']}")
    print(f"References: {result['figure_references']}")

