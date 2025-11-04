# Web UI for Exam Generation System

## Quick Start

### Install Streamlit
```bash
pip install streamlit
```

### Run the UI
```bash
streamlit run web_ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### ✅ Current Features:
1. **Generate Questions** - Use OpenAI to generate new questions
2. **Question Bank** - Browse existing questions with filters
3. **Build Exam** - (Coming soon) Assemble exams from questions
4. **Statistics** - View question bank statistics

### 🚧 Coming Soon:
- Exam assembly interface
- Question editing
- Export to PDF/Word
- Save/load exam templates
- Model testing interface

## Pages

### Generate Questions
- Input topic, difficulty, question type
- Generate using OpenAI
- Preview and save generated questions

### Question Bank
- Browse all questions
- Filter by course, type, difficulty
- Search questions
- View question details

### Build Exam
- Select questions from bank
- Create exam structure
- Preview and export exam

### Statistics
- View question bank statistics
- Question type distribution
- Course distribution
- Average questions per exam

## Configuration

### OpenAI API Key
Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_key_here
```

Or create a `.env` file:
```
OPENAI_API_KEY=your_key_here
```

## Next Steps

1. **Test the UI** - Run it and see what works
2. **Add Features** - Based on what you need
3. **Upgrade Later** - To FastAPI + React if needed

## Troubleshooting

### "OpenAI module not found"
```bash
pip install openai
```

### "Pandas not installed"
```bash
pip install pandas
```

### API Key not found
- Set `OPENAI_API_KEY` environment variable
- Or create `.env` file in project root

### Port already in use
```bash
streamlit run web_ui/streamlit_app.py --server.port 8502
```

