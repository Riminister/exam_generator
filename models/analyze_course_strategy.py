#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze course distribution and recommend focused testing strategy"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_course_strategy(json_file="data/exam_analysis.json"):
    """Analyze courses and recommend testing strategy"""
    
    if not Path(json_file).exists():
        print(f"❌ {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    exams = data.get('exams', [])
    
    # Gather course statistics
    courses = defaultdict(lambda: {'questions': 0, 'exams': 0, 'question_types': defaultdict(int)})
    
    for exam in exams:
        course = exam.get('course_code', 'unknown')
        questions = exam.get('questions', [])
        
        courses[course]['exams'] += 1
        courses[course]['questions'] += len(questions)
        
        for q in questions:
            qtype = q.get('question_type', 'unknown')
            courses[course]['question_types'][qtype] += 1
    
    # Sort by question count
    sorted_courses = sorted(courses.items(), key=lambda x: x[1]['questions'], reverse=True)
    
    print("=" * 70)
    print("📊 COURSE ANALYSIS & STRATEGIC RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n📈 Current Course Distribution:")
    print("-" * 70)
    
    for course, stats in sorted_courses:
        avg_q = stats['questions'] / stats['exams'] if stats['exams'] > 0 else 0
        top_types = sorted(stats['question_types'].items(), key=lambda x: x[1], reverse=True)[:2]
        type_str = ", ".join([f"{t}({c})" for t, c in top_types])
        print(f"{course:10s}: {stats['questions']:3d} questions from {stats['exams']:2d} exams "
              f"(~{avg_q:.1f} q/exam) | Types: {type_str}")
    
    # Categorize courses
    print("\n" + "=" * 70)
    print("🎯 STRATEGIC RECOMMENDATIONS FOR EXAM GENERATION")
    print("=" * 70)
    
    # Tier 1: Ready for course-specific generation (50+ questions)
    tier1 = [(c, s) for c, s in sorted_courses if s['questions'] >= 50]
    
    # Tier 2: Nearly ready (30-49 questions)
    tier2 = [(c, s) for c, s in sorted_courses if 30 <= s['questions'] < 50]
    
    # Tier 3: Need more data (15-29 questions)
    tier3 = [(c, s) for c, s in sorted_courses if 15 <= s['questions'] < 30]
    
    # Tier 4: Too few (<15 questions)
    tier4 = [(c, s) for c, s in sorted_courses if s['questions'] < 15]
    
    print("\n✅ TIER 1: Ready for Course-Specific Generation (50+ questions)")
    if tier1:
        for course, stats in tier1:
            needed = max(0, 50 - stats['questions'])
            print(f"   ✓ {course:10s}: {stats['questions']:3d} questions - READY TO TEST!")
            print(f"     → Can build course-specific model now")
            print(f"     → Minimum for generation: 50-100 questions (you have {stats['questions']})")
    else:
        print("   (None yet - need to collect more exams)")
    
    print("\n⚠️  TIER 2: Nearly Ready (30-49 questions) - FOCUS HERE!")
    if tier2:
        for course, stats in tier2:
            needed = max(0, 50 - stats['questions'])
            exams_needed = max(1, int(needed / (stats['questions'] / stats['exams'])))
            print(f"   • {course:10s}: {stats['questions']:3d} questions")
            print(f"     → Need {needed:2d} more questions (~{exams_needed} more exams)")
            print(f"     → Priority: HIGH - Quick wins!")
        print("\n   💡 RECOMMENDATION: Focus on Tier 2 courses first!")
        print("      These are closest to being viable and will give you fastest results.")
    else:
        print("   (None - courses need more data)")
    
    print("\n📊 TIER 3: Building Base (15-29 questions)")
    if tier3:
        for course, stats in tier3:
            needed = max(0, 50 - stats['questions'])
            exams_needed = max(1, int(needed / (stats['questions'] / stats['exams'])))
            print(f"   • {course:10s}: {stats['questions']:3d} questions → Need {needed:2d} more (~{exams_needed} exams)")
    else:
        print("   (None)")
    
    print("\n❌ TIER 4: Too Few Questions (<15)")
    if tier4:
        for course, stats in tier4:
            needed = max(0, 50 - stats['questions'])
            exams_needed = max(1, int(needed / (stats['questions'] / stats['exams']))) if stats['questions'] > 0 else 10
            print(f"   • {course:10s}: {stats['questions']:3d} questions → Need {needed:2d} more (~{exams_needed} exams)")
    else:
        print("   (None)")
    
    # Strategic recommendations
    print("\n" + "=" * 70)
    print("💡 STRATEGIC RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n🎯 For Course-Specific Exam Generation, you need:")
    print("   • Minimum: 50-100 questions per course (for basic patterns)")
    print("   • Ideal: 100-200 questions per course (for robust generation)")
    print("   • Optimal: 200+ questions per course (for production quality)")
    
    if tier2:
        top_course = tier2[0][0]
        top_stats = tier2[0][1]
        needed = 50 - top_stats['questions']
        exams_needed = max(1, int(needed / (top_stats['questions'] / top_stats['exams'])))
        print(f"\n🚀 TOP PRIORITY: Focus on {top_course}")
        print(f"   • Currently: {top_stats['questions']} questions")
        print(f"   • Need: {needed} more questions (~{exams_needed} more exams)")
        print(f"   • Time to ready: Fastest path to course-specific generation!")
    
    print("\n📋 RECOMMENDED APPROACH:")
    print("   1. ✅ Start with GENERAL model (all courses) - You can do this NOW")
    print("      → Use all 294 questions to build baseline")
    print("      → Test question type classification & difficulty prediction")
    print("      → Validate your pipeline works")
    print("\n   2. 🎯 Pick 2-3 courses from TIER 2 for focused testing")
    print("      → Collect 2-5 more exams for each")
    print("      → Build course-specific models")
    print("      → Compare performance vs general model")
    print("\n   3. 📈 Scale up the winners")
    print("      → Focus on courses that show promise")
    print("      → Build exam generation for those courses")
    print("\n   4. 🔄 Expand to more courses")
    print("      → Use lessons learned from focused testing")
    print("      → Apply to other courses")
    
    print("\n" + "=" * 70)
    print("⏱️  TIMELINE ESTIMATES")
    print("=" * 70)
    
    if tier2:
        print("\nFor Tier 2 courses (30-49 questions):")
        print("   • Collect 2-5 more exams per course: 1-2 days")
        print("   • Build course-specific model: 2-4 hours")
        print("   • Test exam generation: 1 day")
        print("   • Total: ~1 week to working course-specific generation")
    
    print("\nFor general model (all courses):")
    print("   • Test current dataset: TODAY (2-4 hours)")
    print("   • Iterate and improve: 2-3 days")
    print("   • Build basic generation: 1 week")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_course_strategy()

