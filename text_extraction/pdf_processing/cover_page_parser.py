#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cover Page Parser for Exam PDFs
Extracts metadata from the first page: faculty, course name, professor, total marks, date
"""

import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# PDF processing imports
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    print("Warning: pdfplumber not installed. Install with: pip install pdfplumber")

try:
    import pymupdf  # PyMuPDF
except ImportError:
    pymupdf = None

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class CoverPageParser:
    """
    Extracts metadata from the cover page (first page) of exam PDFs.
    """
    
    def __init__(self):
        # Course code patterns
        self.course_code_patterns = [
            r'COURSE\s*(?:CODE|NUMBER|NUM)?\s*:?\s*([A-Z]{2,}\d{3,4})',
            r'([A-Z]{2,}\s*\d{3,4})',  # Standalone like "ECON 310"
            r'Course:\s*([A-Z]{2,}\d{3,4})',
        ]
        
        # Course name patterns (full name, not just code)
        self.course_name_patterns = [
            r'COURSE\s*NAME\s*:?\s*(.+?)(?:\n|Course|Instructor|Professor|Total|$)',
            r'Course:\s*(.+?)(?:\n|Instructor|Professor|Total|$)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Course|Class|Subject))',
        ]
        
        # Faculty/department patterns
        self.faculty_patterns = [
            r'FACULTY\s*(?:OF|:)?\s*(.+?)(?:\n|Department|School|Course|$)',
            r'DEPARTMENT\s*(?:OF|:)?\s*(.+?)(?:\n|Faculty|School|Course|$)',
            r'SCHOOL\s*(?:OF|:)?\s*(.+?)(?:\n|Faculty|Department|Course|$)',
            r'(Faculty of [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(Department of [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        # Professor/instructor patterns
        self.professor_patterns = [
            r'PROFESSOR\s*:?\s*(.+?)(?:\n|Instructor|Course|Total|$)',
            r'INSTRUCTOR\s*:?\s*(.+?)(?:\n|Professor|Course|Total|$)',
            r'Instructor:\s*(.+?)(?:\n|Professor|Course|Total|$)',
            r'Prof\.\s*(.+?)(?:\n|Instructor|Course|Total|$)',
            r'Dr\.\s*(.+?)(?:\n|Instructor|Course|Total|$)',
        ]
        
        # Total marks patterns (from cover page)
        self.total_marks_patterns = [
            r'TOTAL\s+MARKS?\s*:?\s*(\d+(?:\.\d+)?)',
            r'Total\s+marks?\s*:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s+marks?\s+total',
            r'Total:\s*(\d+(?:\.\d+)?)\s+marks?',
            r'(\d+(?:\.\d+)?)\s+points?\s+total',
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(?:EXAMINATION\s+)?DATE\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'Date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4})',
            r'(Fall|Spring|Summer|Winter)\s+(\d{4})',
            r'(\d{4})',  # Just year (last resort)
        ]
        
        # Month names for date parsing
        self.months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
    
    def extract_first_page_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from the first page of a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            First page text, or None if extraction fails
        """
        if not pdf_path.exists():
            return None
        
        # Try pdfplumber first (better for text layer)
        if pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if len(pdf.pages) > 0:
                        first_page = pdf.pages[0]
                        text = first_page.extract_text()
                        if text:
                            return text
            except Exception as e:
                print(f"   pdfplumber failed: {e}")
        
        # Fallback to PyMuPDF
        if pymupdf:
            try:
                doc = pymupdf.open(pdf_path)
                if len(doc) > 0:
                    first_page = doc[0]
                    text = first_page.get_text()
                    doc.close()
                    if text:
                        return text
            except Exception as e:
                print(f"   PyMuPDF failed: {e}")
        
        return None
    
    def extract_course_code(self, text: str) -> Optional[str]:
        """Extract course code (e.g., ECON310, ARAB100)."""
        if not text:
            return None
        
        for pattern in self.course_code_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Clean up and return first match
                code = matches[0].strip().replace(' ', '').upper()
                # Basic validation: should be letters + numbers
                if re.match(r'^[A-Z]{2,}\d{3,4}$', code):
                    return code
        
        return None
    
    def extract_course_name(self, text: str) -> Optional[str]:
        """Extract full course name."""
        if not text:
            return None
        
        for pattern in self.course_name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                name = matches[0].strip()
                # Filter out common false positives
                if len(name) > 5 and not re.match(r'^\d+$', name):
                    return name
        
        return None
    
    def extract_faculty(self, text: str) -> Optional[str]:
        """Extract faculty or department name."""
        if not text:
            return None
        
        for pattern in self.faculty_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                faculty = matches[0].strip()
                # Filter out very short matches
                if len(faculty) > 3:
                    # Clean up common prefixes
                    faculty = re.sub(r'^(Faculty|Department|School)\s+of\s+', '', faculty, flags=re.IGNORECASE)
                    return faculty.strip()
        
        return None
    
    def extract_professor(self, text: str) -> Optional[str]:
        """Extract professor/instructor name."""
        if not text:
            return None
        
        for pattern in self.professor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                prof = matches[0].strip()
                # Filter out common false positives
                if len(prof) > 2 and not re.match(r'^[\d\s]+$', prof):
                    # Clean up: remove extra whitespace, truncate if too long
                    prof = ' '.join(prof.split()[:5])  # Max 5 words
                    return prof
        
        return None
    
    def extract_total_marks(self, text: str) -> Optional[float]:
        """Extract total marks from cover page."""
        if not text:
            return None
        
        for pattern in self.total_marks_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    marks = float(matches[0])
                    # Sanity check: reasonable range for exam marks
                    if 10 <= marks <= 300:
                        return marks
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_date(self, text: str) -> Optional[Dict[str, any]]:
        """
        Extract exam date and return as dict with parsed date info.
        
        Returns:
            Dict with keys: 'date_string', 'year', 'month', 'day', 'parsed_date', 'relevance_score'
            or None if not found
        """
        if not text:
            return None
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                date_str = matches[0] if isinstance(matches[0], str) else ' '.join(matches)
                date_str = date_str.strip()
                
                # Try to parse the date
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    year = parsed_date.year
                    month = parsed_date.month
                    day = parsed_date.day
                    
                    # Calculate relevance score (newer = more relevant)
                    # Score from 0-1, where 1 = current year, 0 = 20+ years old
                    current_year = datetime.now().year
                    years_old = current_year - year
                    relevance_score = max(0.0, min(1.0, 1.0 - (years_old / 20.0)))
                    
                    return {
                        'date_string': date_str,
                        'year': year,
                        'month': month,
                        'day': day,
                        'parsed_date': parsed_date.isoformat(),
                        'relevance_score': relevance_score
                    }
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats into datetime object."""
        date_str = date_str.strip()
        
        # Try standard formats first
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%B %d %Y',
            '%d %b %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try parsing month name formats
        date_lower = date_str.lower()
        for month_name, month_num in self.months.items():
            if month_name in date_lower:
                # Extract year
                year_match = re.search(r'\d{4}', date_str)
                if year_match:
                    year = int(year_match.group())
                    # Extract day if present
                    day_match = re.search(r'\b(\d{1,2})\b', date_str)
                    day = int(day_match.group(1)) if day_match else 1
                    try:
                        return datetime(year, month_num, day)
                    except ValueError:
                        return datetime(year, month_num, 1)
        
        # Try season + year (e.g., "Fall 2023")
        season_match = re.match(r'(Fall|Spring|Summer|Winter)\s+(\d{4})', date_str, re.IGNORECASE)
        if season_match:
            season, year_str = season_match.groups()
            year = int(year_str)
            # Approximate: Fall = Sept, Spring = Jan, Summer = June, Winter = Dec
            season_months = {
                'fall': 9, 'spring': 1, 'summer': 6, 'winter': 12
            }
            month = season_months.get(season.lower(), 1)
            return datetime(year, month, 1)
        
        # Last resort: just year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            year = int(year_match.group())
            return datetime(year, 1, 1)
        
        return None
    
    def parse_cover_page(self, pdf_path: Path) -> Dict[str, any]:
        """
        Parse cover page of a PDF and extract all metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted metadata:
            - course_code: str or None
            - course_name: str or None
            - faculty: str or None
            - professor: str or None
            - total_marks: float or None
            - date_info: dict or None (contains date_string, year, month, day, parsed_date, relevance_score)
            - extraction_success: bool
        """
        result = {
            'course_code': None,
            'course_name': None,
            'faculty': None,
            'professor': None,
            'total_marks': None,
            'date_info': None,
            'extraction_success': False
        }
        
        # Extract first page text
        text = self.extract_first_page_text(pdf_path)
        if not text:
            return result
        
        result['extraction_success'] = True
        
        # Extract all metadata
        result['course_code'] = self.extract_course_code(text)
        result['course_name'] = self.extract_course_name(text)
        result['faculty'] = self.extract_faculty(text)
        result['professor'] = self.extract_professor(text)
        result['total_marks'] = self.extract_total_marks(text)
        result['date_info'] = self.extract_date(text)
        
        return result


if __name__ == "__main__":
    # Test with a sample PDF
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        # Default test path
        pdf_path = Path("data/exam_downloads/ARAB100.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)
    
    parser = CoverPageParser()
    result = parser.parse_cover_page(pdf_path)
    
    print("=" * 70)
    print(f"COVER PAGE EXTRACTION: {pdf_path.name}")
    print("=" * 70)
    print(f"Course Code: {result['course_code']}")
    print(f"Course Name: {result['course_name']}")
    print(f"Faculty: {result['faculty']}")
    print(f"Professor: {result['professor']}")
    print(f"Total Marks: {result['total_marks']}")
    if result['date_info']:
        print(f"Date: {result['date_info'].get('date_string')}")
        print(f"Year: {result['date_info'].get('year')}")
        print(f"Relevance Score: {result['date_info'].get('relevance_score', 0):.2f}")
    print(f"Extraction Success: {result['extraction_success']}")
    print("=" * 70)

