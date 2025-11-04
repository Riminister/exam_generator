# 📊 OpenAI Graph Integration Guide

## Overview

This integration uses OpenAI to:
1. **Analyze questions** - Extract topics, difficulty, and graph descriptions
2. **Describe graphs** - When questions reference figures, OpenAI describes them
3. **Recreate graphs** - Use matplotlib to recreate graphs from descriptions

## Quick Start

### Step 1: Analyze Existing Questions

```bash
python integrate_openai_analysis.py
```

This will:
- Analyze all questions in `exam_analysis.json`
- Extract graph descriptions for questions with figures
- Recreate graphs using matplotlib
- Save enhanced data to `exam_analysis_with_openai.json`

### Step 2: Check Results

- **Enhanced analysis**: `data/exam_analysis_with_openai.json`
- **Generated graphs**: `generated_graphs/` folder
- Each graph is named: `question_{number}_figure_{number}.png`

## How It Works

### 1. Question Analysis

For each question, OpenAI extracts:
```json
{
  "topics": ["supply and demand", "market equilibrium"],
  "question_type": "multiple_choice",
  "has_graph": true,
  "difficulty_indicators": "medium",
  "key_concepts": ["opportunity cost", "trade-offs"]
}
```

### 2. Graph Description

When a question references a figure (e.g., "Refer to Figure 1-1"), OpenAI describes it:
```json
{
  "graph_type": "supply_demand",
  "x_axis": {"label": "Quantity", "range": [0, 100]},
  "y_axis": {"label": "Price", "range": [0, 50]},
  "curves": [
    {"name": "Demand", "slope": "negative"},
    {"name": "Supply", "slope": "positive"}
  ]
}
```

### 3. Graph Recreation

Matplotlib recreates the graph from the description:
- Supply/demand curves
- Production possibilities boundaries
- Cost curves
- Indifference curves

## Usage in Question Generation

When generating NEW questions, you can:

### Option 1: Use Existing Graph Descriptions

```python
from openai_question_generator import OpenAIQuestionGenerator
from exam_analysis.openai_question_analyzer import OpenAIQuestionAnalyzer

# Load existing graph descriptions
with open('data/exam_analysis_with_openai.json') as f:
    data = json.load(f)

# Find questions with graphs
graph_questions = [q for q in all_questions if q.get('graph_description')]

# Use graph description when generating new question
generator = OpenAIQuestionGenerator()
new_question = generator.generate_question(
    topic="supply and demand",
    graph_description=graph_questions[0]['graph_description']
)
```

### Option 2: Generate New Graph Description

```python
analyzer = OpenAIQuestionAnalyzer()

# Generate question text
question_text = "Refer to Figure 1-1 showing supply and demand curves..."

# Get graph description
graph_desc = analyzer.describe_graph_from_text(question_text)

# Recreate graph
from exam_analysis.graph_recreator import GraphRecreator
recreator = GraphRecreator()
fig = recreator.create_from_description(graph_desc, "new_graph.png")
```

## Supported Graph Types

1. **Supply and Demand** (`supply_demand`)
   - Demand curve (downward sloping)
   - Supply curve (upward sloping)
   - Equilibrium point

2. **Production Possibilities** (`production_possibilities`)
   - PPF curve (concave)
   - Attainable/unattainable regions

3. **Cost Curves** (`cost_curves`)
   - ATC, AVC, MC curves
   - U-shaped relationships

4. **Indifference Curves** (`indifference_curve`)
   - Budget lines
   - Utility curves

## Example Workflow

### Analyzing Existing Questions

```python
from integrate_openai_analysis import enhance_exam_analysis_with_openai

# Enhance all questions with OpenAI analysis
enhanced_data = enhance_exam_analysis_with_openai(
    input_file="data/exam_analysis.json",
    output_file="data/exam_analysis_with_openai.json",
    analyze_graphs=True,
    recreate_graphs=True
)
```

### Generating Questions with Graphs

```python
from openai_question_generator import OpenAIQuestionGenerator
from exam_analysis.graph_recreator import GraphRecreator

generator = OpenAIQuestionGenerator()

# Generate question that needs a graph
question = generator.generate_question(
    topic="supply and demand",
    question_type="multiple_choice",
    difficulty="medium"
)

# If question mentions a figure, create the graph
if "figure" in question['question'].lower():
    recreator = GraphRecreator()
    
    # Create appropriate graph type
    graph_desc = {
        "graph_type": "supply_demand",
        "x_axis": {"label": "Quantity", "range": [0, 100]},
        "y_axis": {"label": "Price", "range": [0, 50]}
    }
    
    recreator.create_from_description(
        graph_desc,
        f"generated_graphs/question_{question['question_number']}_graph.png"
    )
```

## Integration Points

### 1. Question Extraction Pipeline

Add to `parse_questions_from_text.py`:
```python
from exam_analysis.openai_question_analyzer import analyze_questions_with_openai

# After parsing questions
questions = parser.extract_questions_from_text(text)

# Add OpenAI analysis
questions = analyze_questions_with_openai(questions, analyze_graphs=True)
```

### 2. Data Cleaning Pipeline

Add to `exam_analysis/data_cleaner.py`:
```python
from exam_analysis.openai_question_analyzer import analyze_questions_with_openai

# After cleaning
cleaned_questions = cleaner.clean_dataset(questions_data)

# Enhance with OpenAI analysis
cleaned_questions = analyze_questions_with_openai(cleaned_questions)
```

### 3. Question Generation

Update `openai_question_generator.py` to automatically create graphs when generating questions that reference figures.

## Cost Considerations

- **Question Analysis**: ~$0.001 per question (using gpt-4o-mini)
- **Graph Description**: ~$0.001 per graph
- **Total for 100 questions**: ~$0.20

## Tips

1. **Batch Processing**: Analyze all questions at once to save API calls
2. **Cache Results**: Save graph descriptions to avoid re-analyzing
3. **Review Quality**: Check generated graphs match original intent
4. **Customize Graphs**: Modify `graph_recreator.py` for your specific graph types

## Troubleshooting

### "OpenAI API key not found"
- Run `python setup_openai.py` to set up your key

### "Graph type not recognized"
- Add custom graph type to `graph_recreator.py`
- Or provide more detailed description in prompt

### "Graph doesn't match description"
- Review OpenAI description accuracy
- Adjust graph recreation parameters
- Manually tune graph properties

---

**Next Steps:**
1. Run `python integrate_openai_analysis.py` to analyze your questions
2. Review generated graphs in `generated_graphs/` folder
3. Use graph descriptions when generating new questions

