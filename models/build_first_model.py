#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build your first ML model for question classification
This is a simple starter that you can build upon
"""

import json
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def load_exam_data(json_file="data/exam_analysis.json"):
    """Load exam data from JSON file"""
    print(f"Loading data from {json_file}...")
    
    if not Path(json_file).exists():
        raise FileNotFoundError(f"{json_file} not found! Run extraction first.")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to flat list of questions
    questions = []
    for exam in data.get('exams', []):
        course = exam.get('course_code', 'unknown')
        for q in exam.get('questions', []):
            questions.append({
                'text': q.get('text', ''),
                'question_type': q.get('question_type', 'unknown'),
                'difficulty_score': q.get('difficulty_score', 0.0),
                'length': q.get('length', 0),
                'topics': q.get('topics', []),
                'course_code': course,
            })
    
    print(f"Loaded {len(questions)} questions")
    return questions


def prepare_features(questions):
    """Convert questions to features"""
    print("\nPreparing features...")
    
    # Basic text features
    df = pd.DataFrame(questions)
    
    # Text length features
    df['char_count'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    df['avg_word_length'] = df['char_count'] / (df['word_count'] + 1)
    
    # Question markers
    df['has_question_mark'] = df['text'].str.contains('?', regex=False, na=False).astype(int)
    df['has_explain'] = df['text'].str.contains('explain|describe|discuss', case=False, na=False).astype(int)
    df['has_calculate'] = df['text'].str.contains('calculate|compute|find', case=False, na=False).astype(int)
    df['has_list'] = df['text'].str.contains('list|enumerate|name', case=False, na=False).astype(int)
    
    # Multiple choice markers
    df['has_options'] = df['text'].str.contains(r'[a-e]\)|\(a\)|\(b\)|\(c\)|\(d\)|\(e\)', case=False, na=False).astype(int)
    
    # Difficulty features
    df['difficulty_score'] = df['difficulty_score'].fillna(0)
    
    # Course as category (optional)
    df['course_numeric'] = pd.Categorical(df['course_code']).codes
    
    print(f"Created {len(df.columns)} features")
    print(f"Features: {list(df.columns)}")
    
    return df


def build_classification_model(df):
    """Build a simple question type classifier"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    from sklearn.preprocessing import StandardScaler
    
    print("\n" + "="*70)
    print("Building Question Type Classification Model")
    print("="*70)
    
    # Prepare target
    y = df['question_type']
    
    # Check class distribution
    print(f"\nClass distribution:")
    print(y.value_counts())
    
    # Prepare text features (TF-IDF)
    print("\nExtracting text features (TF-IDF)...")
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        min_df=2,
        max_df=0.95
    )
    
    X_text = vectorizer.fit_transform(df['text'])
    print(f"Text features shape: {X_text.shape}")
    
    # Prepare numerical features
    numerical_features = [
        'char_count', 'word_count', 'avg_word_length',
        'has_question_mark', 'has_explain', 'has_calculate', 'has_list', 'has_options',
        'difficulty_score', 'length'
    ]
    
    X_num = df[numerical_features].values
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    
    # Combine features
    from scipy.sparse import hstack
    X = hstack([X_text, X_num_scaled])
    print(f"Combined features shape: {X.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train model
    print("\nTraining Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nOverall Accuracy: {accuracy:.2%}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance (top words)
    print("\n" + "="*70)
    print("Top Important Words for Each Class:")
    print("="*70)
    
    feature_names = list(vectorizer.get_feature_names_out()) + numerical_features
    
    for class_idx, class_name in enumerate(model.classes_):
        coef = model.coef_[class_idx]
        top_indices = np.argsort(np.abs(coef))[-10:][::-1]
        print(f"\n{class_name}:")
        for idx in top_indices:
            if idx < len(vectorizer.get_feature_names_out()):
                print(f"  {feature_names[idx]}: {coef[idx]:.3f}")
    
    return model, vectorizer, scaler, accuracy


def build_difficulty_model(df):
    """Build a difficulty prediction model (regression) - IMPROVED VERSION"""
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_squared_error
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    
    print("\n" + "="*70)
    print("Building Difficulty Prediction Model (IMPROVED)")
    print("="*70)
    
    # Prepare target
    y = df['difficulty_score']
    
    # Filter out questions with no difficulty score
    valid_mask = y.notna() & (y > 0)
    df_valid = df[valid_mask].copy()
    y_valid = y[valid_mask]
    
    if len(df_valid) < 20:
        print(f"\n⚠️  Not enough data for difficulty prediction ({len(df_valid)} samples)")
        print("   Need questions with difficulty scores > 0")
        return None
    
    print(f"\nUsing {len(df_valid)} questions with difficulty scores")
    print(f"   (Out of {len(df)} total questions - {len(df_valid)/len(df)*100:.1f}% coverage)")
    
    # IMPROVEMENT 1: Add question type features
    if 'question_type' in df_valid.columns:
        df_valid['is_essay'] = (df_valid['question_type'] == 'essay').astype(int)
        df_valid['is_multiple_choice'] = (df_valid['question_type'] == 'multiple_choice').astype(int)
        df_valid['is_short_answer'] = (df_valid['question_type'] == 'short_answer').astype(int)
        df_valid['is_numerical'] = (df_valid['question_type'] == 'numerical').astype(int)
    
    # IMPROVEMENT 2: Add cognitive level features
    df_valid['has_prove'] = df_valid['text'].str.contains('prove|show|demonstrate|derive', case=False, na=False).astype(int)
    df_valid['has_analyze'] = df_valid['text'].str.contains('analyze|evaluate|critique|compare|contrast', case=False, na=False).astype(int)
    df_valid['has_explain'] = df_valid['text'].str.contains('explain|describe|discuss', case=False, na=False).astype(int)
    df_valid['has_list'] = df_valid['text'].str.contains('list|enumerate|name|identify', case=False, na=False).astype(int)
    
    # IMPROVEMENT 3: Better text features with n-grams
    print("\nExtracting improved text features (TF-IDF with bigrams)...")
    vectorizer = TfidfVectorizer(
        max_features=300,
        stop_words='english',
        min_df=2,
        max_df=0.95,
        ngram_range=(1, 2)  # Include bigrams for better context
    )
    X_text = vectorizer.fit_transform(df_valid['text'])
    
    # IMPROVEMENT 4: Enhanced numerical features
    numerical_features = [
        'char_count', 'word_count', 'avg_word_length',
        'has_question_mark', 'has_explain', 'has_calculate', 'has_list',
        'has_prove', 'has_analyze',  # New cognitive features
        'length'
    ]
    
    # Add question type features if available
    if 'is_essay' in df_valid.columns:
        numerical_features.extend(['is_essay', 'is_multiple_choice', 'is_short_answer', 'is_numerical'])
    
    X_num = df_valid[numerical_features].values
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    
    # Combine
    from scipy.sparse import hstack
    X = hstack([X_text, X_num_scaled])
    print(f"Feature matrix shape: {X.shape} ({X_text.shape[1]} text + {len(numerical_features)} numerical)")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_valid, test_size=0.2, random_state=42
    )
    
    # IMPROVEMENT 5: Try Gradient Boosting (often better than RF for this)
    print("\nTraining Gradient Boosting model...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42,
        subsample=0.8
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print("\n" + "="*70)
    print("RESULTS (IMPROVED MODEL)")
    print("="*70)
    print(f"\nR² Score: {r2:.3f} (closer to 1.0 is better)")
    print(f"RMSE: {rmse:.3f} (lower is better, difficulty is 0-1 scale)")
    
    # Compare to baseline
    if r2 > 0.4:
        print("\n✅ Significant improvement! Model shows good predictive power!")
    elif r2 > 0.35:
        print("\n✅ Improved! Better than original 0.308")
    elif r2 > 0.308:
        print("\n⚠️  Slightly better, but still room for improvement")
    else:
        print("\n⚠️  Model still struggles - main issue: sparse data (only {:.1f}% have scores)".format(len(df_valid)/len(df)*100))
        print("   Solutions:")
        print("   1. Improve mark extraction to get scores for more questions")
        print("   2. Use alternative difficulty signal (question type + keywords)")
        print("   3. Consider manual labeling of difficulty for training set")
    
    print("\nImprovements made:")
    print("  ✅ Added question type features (essay, MC, etc.)")
    print("  ✅ Added cognitive level keywords (prove, analyze, etc.)")
    print("  ✅ Used Gradient Boosting instead of Random Forest")
    print("  ✅ Added bigrams to TF-IDF for better context")
    print("  ✅ Standardized numerical features")
    
    return model, r2


def main():
    """Main function"""
    print("="*70)
    print("BUILDING YOUR FIRST ML MODELS")
    print("="*70)
    
    # Load data
    try:
        questions = load_exam_data()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nRun extraction first:")
        print("  python extract_manual_downloads.py")
        return
    
    if len(questions) < 20:
        print(f"\n⚠️  Not enough questions ({len(questions)})")
        print("   Need at least 20 questions to build models")
        print("   Download more exams first")
        return
    
    # Prepare features
    df = prepare_features(questions)
    
    # Build classification model
    try:
        clf_model, vectorizer, scaler, accuracy = build_classification_model(df)
        
        if accuracy > 0.70:
            print("\n✅ Great! Model accuracy >70% - ready to iterate and improve!")
        elif accuracy > 0.50:
            print("\n⚠️  Model accuracy is moderate (50-70%) - consider:")
            print("   - Better text preprocessing")
            print("   - More features")
            print("   - Using BERT embeddings instead of TF-IDF")
        else:
            print("\n❌ Model accuracy is low (<50%) - need to:")
            print("   - Check data quality")
            print("   - Review feature engineering")
            print("   - Consider simpler baseline")
        
    except Exception as e:
        print(f"\n❌ Error building classification model: {e}")
        import traceback
        traceback.print_exc()
    
    # Build difficulty model (if enough data)
    try:
        diff_model = build_difficulty_model(df)
    except Exception as e:
        print(f"\n⚠️  Skipping difficulty model: {e}")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review model results above")
    print("2. Try improving features (see MODEL_BUILDING_GUIDE.md)")
    print("3. Experiment with different models")
    print("4. If models work well (>70% accuracy), download more exams")
    print("5. If models struggle, review data quality and preprocessing")
    print("\nSee MODEL_BUILDING_GUIDE.md for detailed guidance!")
    print("="*70)


if __name__ == "__main__":
    main()

