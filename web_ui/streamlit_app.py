#!/usr/bin/env python3
"""
Streamlit Web UI for Exam Generation System
Quick and easy interface for generating exam questions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import json
from typing import Dict, List, Optional

# Import our modules
try:
    from exam_generation.openai.openai_question_generator import OpenAIQuestionGenerator
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("⚠️ OpenAI module not found. Install with: pip install openai")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    st.error("⚠️ Pandas not installed. Install with: pip install pandas")

# Page config
st.set_page_config(
    page_title="Exam Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .question-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_existing_questions():
    """Load existing questions from exam_analysis.json"""
    try:
        analysis_file = project_root / "data" / "exam_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
    except Exception as e:
        st.error(f"Error loading questions: {e}")
    return None


def generate_question_with_openai(topic: str, question_type: str, difficulty: str, course_subject: str):
    """Generate a question using OpenAI"""
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        generator = OpenAIQuestionGenerator(model="gpt-4o-mini")
        question = generator.generate_question(
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            course_subject=course_subject
        )
        return question
    except Exception as e:
        st.error(f"Error generating question: {e}")
        return None


def main():
    # Header
    st.markdown('<div class="main-header">📝 Exam Question Generator</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page",
        ["Generate Questions", "Question Bank", "Build Exam", "Statistics"]
    )
    
    if page == "Generate Questions":
        render_generate_page()
    elif page == "Question Bank":
        render_question_bank_page()
    elif page == "Build Exam":
        render_build_exam_page()
    elif page == "Statistics":
        render_statistics_page()


def render_generate_page():
    """Render the question generation page"""
    st.header("🤖 Generate New Questions")
    
    if not OPENAI_AVAILABLE:
        st.error("OpenAI module not available. Please install: pip install openai")
        st.info("Also ensure OPENAI_API_KEY is set in your environment.")
        return
    
    # Check for API key (try Streamlit secrets first, then environment)
    import os
    api_key = None
    
    # Try Streamlit secrets (for deployed apps)
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass
    
    # Fallback to environment variable (for local development)
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY not found.")
        st.info("""
        **For local development:** Set environment variable or create `.env` file
        **For Streamlit Cloud:** Add secret in app settings
        """)
        return
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("Topic", placeholder="e.g., supply and demand")
        question_type = st.selectbox(
            "Question Type",
            ["multiple_choice", "short_answer", "essay", "true_false", "numerical"]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["easy", "medium", "hard"]
        )
        course_subject = st.text_input("Course Subject", placeholder="e.g., Economics")
    
    # Generate button
    if st.button("🚀 Generate Question", type="primary"):
        if not topic:
            st.warning("Please enter a topic")
            return
        
        with st.spinner("Generating question... This may take 10-30 seconds"):
            try:
                question = generate_question_with_openai(
                    topic=topic,
                    question_type=question_type,
                    difficulty=difficulty,
                    course_subject=course_subject or "General"
                )
            except Exception as e:
                st.error(f"Error generating question: {e}")
                st.info("Make sure your OpenAI API key is valid and you have credits.")
                question = None
        
        if question and 'error' not in question:
            st.success("✅ Question generated!")
            
            # Display question
            st.markdown("### Generated Question")
            st.markdown(f'<div class="question-card">{question.get("question", "No question")}</div>', unsafe_allow_html=True)
            
            # Display answer if available
            if question.get("answer"):
                with st.expander("View Answer"):
                    st.write(question["answer"])
            
            # Display metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Type", question.get("question_type", "N/A"))
            with col2:
                st.metric("Difficulty", question.get("difficulty", "N/A"))
            with col3:
                st.metric("Topic", question.get("topic", "N/A"))
            
            # Save option
            if st.button("💾 Save Question"):
                # TODO: Implement save functionality
                st.success("Question saved! (TODO: Implement save)")
        else:
            st.error("Failed to generate question. Check your API key and try again.")


def render_question_bank_page():
    """Render the question bank browser"""
    st.header("📚 Question Bank")
    
    data = load_existing_questions()
    if not data:
        st.info("No questions found. Generate some questions first!")
        return
    
    # Extract all questions
    all_questions = []
    for exam in data.get('exams', []):
        for q in exam.get('questions', []):
            q['exam_filename'] = exam.get('filename', 'Unknown')
            q['course_code'] = exam.get('course_code', 'Unknown')
            all_questions.append(q)
    
    if not all_questions:
        st.info("No questions in the bank yet.")
        return
    
    st.metric("Total Questions", len(all_questions))
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        course_codes = sorted(set(q.get('course_code', 'Unknown') for q in all_questions))
        selected_course = st.selectbox("Course", ["All"] + course_codes)
    
    with col2:
        question_types = sorted(set(q.get('question_type', 'unknown') for q in all_questions))
        selected_type = st.selectbox("Question Type", ["All"] + question_types)
    
    with col3:
        search_term = st.text_input("Search", placeholder="Search question text...")
    
    # Filter questions
    filtered_questions = all_questions
    if selected_course != "All":
        filtered_questions = [q for q in filtered_questions if q.get('course_code') == selected_course]
    if selected_type != "All":
        filtered_questions = [q for q in filtered_questions if q.get('question_type') == selected_type]
    if search_term:
        filtered_questions = [q for q in filtered_questions if search_term.lower() in q.get('text', '').lower()]
    
    st.metric("Filtered Results", len(filtered_questions))
    
    # Display questions
    for i, question in enumerate(filtered_questions[:20]):  # Show first 20
        with st.expander(f"Question {i+1}: {question.get('text', '')[:50]}..."):
            st.write(f"**Text:** {question.get('text', 'N/A')}")
            st.write(f"**Type:** {question.get('question_type', 'N/A')}")
            st.write(f"**Course:** {question.get('course_code', 'N/A')}")
            st.write(f"**Difficulty Score:** {question.get('difficulty_score', 'N/A')}")
            st.write(f"**Marks:** {question.get('question_marks', 'N/A')}")


def render_build_exam_page():
    """Render the exam builder page"""
    st.header("📝 Build Exam")
    st.info("🚧 Exam builder coming soon! This will let you select questions and create a complete exam.")


def render_statistics_page():
    """Render statistics dashboard"""
    st.header("📊 Statistics")
    
    data = load_existing_questions()
    if not data:
        st.info("No data available. Process some exams first!")
        return
    
    # Calculate statistics
    total_exams = len(data.get('exams', []))
    all_questions = []
    for exam in data.get('exams', []):
        all_questions.extend(exam.get('questions', []))
    
    total_questions = len(all_questions)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Exams", total_exams)
    with col2:
        st.metric("Total Questions", total_questions)
    with col3:
        avg_questions = total_questions / total_exams if total_exams > 0 else 0
        st.metric("Avg Questions/Exam", f"{avg_questions:.1f}")
    with col4:
        courses = set(exam.get('course_code') for exam in data.get('exams', []) if exam.get('course_code'))
        st.metric("Unique Courses", len(courses))
    
    # Question type distribution
    if PANDAS_AVAILABLE and all_questions:
        st.subheader("Question Type Distribution")
        question_types = [q.get('question_type', 'unknown') for q in all_questions]
        type_counts = pd.Series(question_types).value_counts()
        st.bar_chart(type_counts)
    
    # Course distribution
    if all_questions:
        st.subheader("Questions by Course")
        course_counts = {}
        for q in all_questions:
            course = q.get('course_code', 'Unknown')
            course_counts[course] = course_counts.get(course, 0) + 1
        
        if PANDAS_AVAILABLE:
            st.bar_chart(pd.Series(course_counts))
        else:
            for course, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{course}**: {count} questions")


if __name__ == "__main__":
    main()

