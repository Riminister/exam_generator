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


def get_econ_courses():
    """Get list of ECON courses from the data"""
    data = load_existing_questions()
    if not data:
        return []
    
    courses = set()
    for exam in data.get('exams', []):
        # Try to get course code from exam
        course_code = exam.get('course_code')
        
        # If not available, try to extract from filename
        if not course_code:
            filename = exam.get('filename', '')
            # Extract ECON code from filename (e.g., ECON212, ECON222)
            import re
            match = re.search(r'ECON\d{3}', filename.upper())
            if match:
                course_code = match.group(0)
        
        # Only add ECON courses
        if course_code and course_code.upper().startswith('ECON'):
            courses.add(course_code.upper())
    
    return sorted(list(courses))


def load_syllabus_topics():
    """Load syllabus topics from JSON file"""
    try:
        topics_file = project_root / "data" / "syllabus_topics.json"
        if topics_file.exists():
            with open(topics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading syllabus topics: {e}")
    return {}


def get_course_topics(course_code: str) -> List[str]:
    """Get topics for a specific course"""
    topics_data = load_syllabus_topics()
    course_data = topics_data.get(course_code.upper())
    if course_data:
        return course_data.get('topics', [])
    return []


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
        ["Generate Questions", "Question Bank", "Build Exam"]
    )
    
    if page == "Generate Questions":
        render_generate_page()
    elif page == "Question Bank":
        render_question_bank_page()
    elif page == "Build Exam":
        render_build_exam_page()


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
    
    # Get available ECON courses
    econ_courses = get_econ_courses()
    
    if not econ_courses:
        st.warning("⚠️ No ECON courses found in your data. Please process some ECON exams first.")
        st.info("The app will restrict to ECON courses only.")
        default_course = "Economics"
    else:
        # Auto-select first course (or use session state to remember selection)
        if 'selected_econ_course' not in st.session_state:
            st.session_state.selected_econ_course = econ_courses[0]
        
        selected_course = st.selectbox(
            "Select ECON Course",
            econ_courses,
            index=econ_courses.index(st.session_state.selected_econ_course) if st.session_state.selected_econ_course in econ_courses else 0,
            help=f"Found {len(econ_courses)} ECON course(s) in your data"
        )
        st.session_state.selected_econ_course = selected_course
        default_course = selected_course
    
    # Get topics for selected course
    course_topics = get_course_topics(default_course) if default_course != "Economics" else []
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        if course_topics:
            # Show dropdown if topics are available
            topic = st.selectbox(
                "Topic",
                ["Select a topic..."] + course_topics,
                help=f"Topics from {default_course} syllabus"
            )
            if topic == "Select a topic...":
                topic = None
        else:
            # Show text input if no topics available
            topic = st.text_input(
                "Topic",
                placeholder="e.g., supply and demand",
                help=f"No syllabus topics found for {default_course}. Add syllabus to data/syllabi/ folder and run extract_syllabus_topics.py"
            )
        
        question_type = st.selectbox(
            "Question Type",
            ["multiple_choice", "short_answer", "essay", "true_false", "numerical"]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["easy", "medium", "hard"]
        )
        # Course subject is automatically set from selected ECON course
        course_subject = default_course
    
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
            
            # Display metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Type", question.get("question_type", "N/A"))
            with col2:
                st.metric("Difficulty", question.get("difficulty", "N/A"))
            with col3:
                st.metric("Topic", question.get("topic", "N/A"))
            
            # Show answer button
            if question.get("answer"):


                # Use a unique key for each question to track answer visibility
                answer_key = f"show_answer_{hash(question.get('question', ''))}"
                
                if answer_key not in st.session_state:
                    st.session_state[answer_key] = False
                
                if not st.session_state[answer_key]:
                    if st.button("🔍 Show Answer", type="secondary", key="show_ans_btn"):
                        st.session_state[answer_key] = True
                        st.rerun()
                else:
                    st.markdown("### Answer")
                    st.markdown(f'<div class="question-card">{question["answer"]}</div>', unsafe_allow_html=True)
                    if st.button("🔄 Hide Answer", key="hide_ans_btn"):
                        st.session_state[answer_key] = False
                        st.rerun()
            
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
    
    # Extract all questions with course codes
    all_questions = []
    for exam in data.get('exams', []):
        # Get course code from exam level
        exam_course_code = exam.get('course_code')
        
        # If not available, extract from filename
        if not exam_course_code:
            filename = exam.get('filename', '')
            import re
            match = re.search(r'ECON\d{3}', filename.upper())
            if match:
                exam_course_code = match.group(0)
            else:
                exam_course_code = 'Unknown'
        
        # Add course code to each question
        for q in exam.get('questions', []):
            q_copy = q.copy()
            q_copy['exam_filename'] = exam.get('filename', 'Unknown')
            q_copy['course_code'] = exam_course_code
            all_questions.append(q_copy)
    
    if not all_questions:
        st.info("No questions in the bank yet.")
        return
    
    st.metric("Total Questions", len(all_questions))
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get unique course codes (handle None values safely)
        course_codes_set = set()
        for q in all_questions:
            course_code = q.get('course_code')
            if course_code:
                course_codes_set.add(str(course_code))
            else:
                course_codes_set.add('Unknown')
        
        course_codes = sorted(list(course_codes_set))
        selected_course = st.selectbox("Course", ["All"] + course_codes)
    
    with col2:
        question_types = sorted(set(q.get('question_type', 'unknown') for q in all_questions))
        selected_type = st.selectbox("Question Type", ["All"] + question_types)
    
    with col3:
        search_term = st.text_input("Search", placeholder="Search question text...")
    
    # Filter questions
    filtered_questions = all_questions
    if selected_course != "All":
        filtered_questions = [q for q in filtered_questions if str(q.get('course_code', 'Unknown')) == selected_course]
    if selected_type != "All":
        filtered_questions = [q for q in filtered_questions if q.get('question_type') == selected_type]
    if search_term:
        filtered_questions = [q for q in filtered_questions if search_term.lower() in q.get('text', '').lower()]
    
    st.metric("Filtered Results", len(filtered_questions))
    
    # Display questions
    if not filtered_questions:
        st.info("No questions match your filters. Try adjusting your search criteria.")
    else:
        for i, question in enumerate(filtered_questions[:20]):  # Show first 20
            question_text = question.get('text', '')
            preview_text = question_text[:50] + "..." if len(question_text) > 50 else question_text
            with st.expander(f"Question {i+1}: {preview_text}"):
                st.write(f"**Text:** {question_text}")
                st.write(f"**Type:** {question.get('question_type', 'N/A')}")
                st.write(f"**Course:** {question.get('course_code', 'N/A')}")
                st.write(f"**Difficulty Score:** {question.get('difficulty_score', 'N/A')}")
                st.write(f"**Marks:** {question.get('question_marks', 'N/A')}")
                st.write(f"**From:** {question.get('exam_filename', 'N/A')}")


def render_build_exam_page():
    """Render the exam builder page"""
    st.header("📝 Build Exam")
    st.info("🚧 Exam builder coming soon! This will let you select questions and create a complete exam.")


if __name__ == "__main__":
    main()

