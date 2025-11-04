# 🔗 OpenAI Integration Setup Guide

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install openai python-dotenv
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Your API Key

**Option A: Interactive Setup (Recommended)**
```bash
python setup_openai.py
```

This will:
- Prompt you for your API key
- Save it securely to `.env` file
- Test the connection
- Verify your account works

**Option B: Manual Setup**
1. Get your API key from https://platform.openai.com/api-keys
2. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

⚠️ **Important**: The `.env` file is in `.gitignore` and won't be committed to git.

### Step 3: Test It Works
```bash
python openai_question_generator.py
```

This will generate a sample question to verify everything is working.

---

## 🎯 Usage Examples

### Generate a Single Question

```python
from openai_question_generator import OpenAIQuestionGenerator

generator = OpenAIQuestionGenerator(model="gpt-4o-mini")

question = generator.generate_question(
    topic="supply and demand",
    question_type="multiple_choice",
    difficulty="medium",
    course_subject="Economics"
)

print(question['question'])
```

### Generate Multiple Questions

```python
questions = generator.generate_multiple_questions(
    topics=["market equilibrium", "price elasticity", "consumer surplus"],
    question_type="multiple_choice",
    difficulty="medium",
    course_subject="Economics"
)
```

### Generate a Full Exam

```python
exam = generator.generate_exam(
    num_questions=10,
    question_type_distribution={
        'multiple_choice': 6,
        'essay': 2,
        'short_answer': 2
    },
    course_subject="Economics"
)
```

---

## 🤖 Available Models

OpenAI provides several models with different capabilities and costs:

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| `gpt-4o-mini` | Testing, bulk generation | Low | Fast |
| `gpt-4-turbo` | High quality questions | Medium | Medium |
| `gpt-4` | Best quality | High | Slow |
| `gpt-3.5-turbo` | Budget option | Very Low | Fast |

**Recommendation**: Start with `gpt-4o-mini` for testing, then use `gpt-4-turbo` for production.

---

## 💰 Cost Estimation

**Example costs (as of 2024):**
- `gpt-4o-mini`: ~$0.001 per question
- `gpt-4-turbo`: ~$0.01 per question
- `gpt-4`: ~$0.03 per question

**For 100 questions:**
- `gpt-4o-mini`: ~$0.10
- `gpt-4-turbo`: ~$1.00
- `gpt-4`: ~$3.00

💡 **Tip**: Use `gpt-4o-mini` for bulk generation, then review and regenerate important questions with `gpt-4-turbo`.

---

## 🔧 Customization

### Adjust Question Style

The generator uses your existing questions as examples. To improve quality:

1. **Ensure good examples**: Make sure `exam_analysis.json` has high-quality questions
2. **Modify prompts**: Edit `create_system_prompt()` and `create_user_prompt()` in `openai_question_generator.py`
3. **Adjust temperature**: Lower (0.3) = more consistent, Higher (0.9) = more creative

### Example: Custom System Prompt

```python
def create_system_prompt(self, course_subject=None):
    return """You are an expert exam question writer.
    
    Your questions must:
    - Be clear and unambiguous
    - Test understanding, not memorization
    - Include realistic scenarios
    - Follow university-level academic standards"""
```

---

## 🚨 Common Issues

### "API key not found"
- Run `python setup_openai.py` to set up your key
- Or manually create `.env` file with `OPENAI_API_KEY=sk-...`

### "Rate limit exceeded"
- You're making too many requests too quickly
- Add delays between requests (the script does this automatically)
- Upgrade your OpenAI plan if needed

### "Insufficient quota"
- Your OpenAI account needs credits
- Add payment method at https://platform.openai.com/account/billing

### "Invalid API key"
- Check that your key starts with `sk-`
- Verify the key is correct (no extra spaces)
- Make sure you're using the latest key from OpenAI dashboard

---

## 📊 Integration with Existing Tools

### Combine with Exam Assembly

You can now generate NEW questions AND select existing ones:

```python
from openai_question_generator import OpenAIQuestionGenerator
from generate_exam_from_data import load_questions, generate_exam

# Generate 5 new questions
generator = OpenAIQuestionGenerator()
new_questions = generator.generate_multiple_questions(
    topics=["topic1", "topic2", "topic3", "topic4", "topic5"],
    question_type="multiple_choice"
)

# Select 5 existing questions
existing_questions = load_questions()
selected = generate_exam(existing_questions, num_questions=5)

# Combine them
combined_exam = new_questions + selected
```

---

## 🎓 Best Practices

1. **Start Small**: Test with 1-2 questions before generating many
2. **Review Quality**: Always review generated questions before using
3. **Use Examples**: The generator learns from your existing questions - make sure they're good quality
4. **Iterate Prompts**: Adjust prompts based on output quality
5. **Monitor Costs**: Keep track of API usage, especially with GPT-4
6. **Save Good Prompts**: Document what prompts work best for your use case

---

## 📝 Next Steps

1. ✅ Set up your API key: `python setup_openai.py`
2. ✅ Test generation: `python openai_question_generator.py`
3. ✅ Generate your first exam with new questions
4. ✅ Review and refine prompts for your specific needs
5. ✅ Integrate with your exam management workflow

---

## 🔗 Resources

- OpenAI API Docs: https://platform.openai.com/docs
- API Keys Dashboard: https://platform.openai.com/api-keys
- Usage Dashboard: https://platform.openai.com/usage
- Pricing: https://openai.com/pricing

