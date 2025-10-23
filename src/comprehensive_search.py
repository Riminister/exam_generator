# Complete Queen's Exam Bank Downloader with Microsoft 2FA
# This version includes comprehensive exam discovery after login

import re
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup

def comprehensive_exam_search():
    """Comprehensive search for exams after login"""
    print("Comprehensive Exam Search After Microsoft 2FA Login")
    print("=" * 60)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Login with Microsoft 2FA
        print("Step 1: Microsoft 2FA Login...")
        success = downloader.login("22yyq", "7GearGlue&")
        
        if not success:
            print("Login failed. Cannot proceed.")
            return
        
        print("\nStep 2: Comprehensive exam search...")
        
        # Try different URLs and methods to find exams
        search_urls = [
            "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/browse/title?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/browse/dateissued?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/browse/author?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/browse/subject?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/browse/type?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/search?query=&scope=cab1b9d2-6777-45cd-b56d-78c608468888",
            "https://qspace.library.queensu.ca/search?query=ELEC&scope=cab1b9d2-6777-45cd-b56d-78c608468888"
        ]
        
        all_exams = []
        
        for i, url in enumerate(search_urls, 1):
            print(f"\nSearching URL {i}/{len(search_urls)}: {url}")
            
            try:
                # Use Selenium to get the page with JavaScript rendering
                downloader.driver.get(url)
                time.sleep(3)
                
                # Get page source after JavaScript execution
                page_source = downloader.driver.page_source
                
                # Save page for debugging
                with open(f'search_page_{i}.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Look for exam links with multiple patterns
                exam_patterns = [
                    r'/items/',
                    r'/handle/',
                    r'/bitstream/',
                    r'/download/'
                ]
                
                found_links = []
                for pattern in exam_patterns:
                    links = soup.find_all('a', href=re.compile(pattern))
                    found_links.extend(links)
                
                print(f"  Found {len(found_links)} potential exam links")
                
                # Process found links
                for link in found_links:
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href')
                        
                        if title and href and len(title) > 3:
                            # Make URL absolute
                            if href.startswith('/'):
                                href = f"https://qspace.library.queensu.ca{href}"
                            
                            exam_info = {
                                'title': title,
                                'url': href,
                                'course': extract_course_code(title),
                                'source_url': url
                            }
                            
                            # Avoid duplicates
                            if not any(exam['url'] == href for exam in all_exams):
                                all_exams.append(exam_info)
                                print(f"    Found: {title}")
                    except Exception as e:
                        continue
                
                # Also check for any text that might indicate exam content
                page_text = soup.get_text().lower()
                exam_keywords = ['exam', 'test', 'midterm', 'final', 'quiz', 'assignment', 'paper']
                found_keywords = [kw for kw in exam_keywords if kw in page_text]
                
                if found_keywords:
                    print(f"  Found exam-related keywords: {found_keywords}")
                
            except Exception as e:
                print(f"  Error searching {url}: {e}")
                continue
        
        print(f"\nStep 3: Results Summary")
        print("=" * 30)
        print(f"Total unique exams found: {len(all_exams)}")
        
        if all_exams:
            print("\nAll exams found:")
            for i, exam in enumerate(all_exams, 1):
                print(f"  {i}. {exam['title']} ({exam['course']})")
                print(f"     URL: {exam['url']}")
                print(f"     Source: {exam['source_url']}")
            
            # Filter by course if requested
            course_filter = input("\nEnter course code to filter (e.g., ELEC371) or press Enter for all: ").strip()
            if course_filter:
                filtered_exams = [exam for exam in all_exams if course_filter.upper() in exam['course'].upper()]
                print(f"\nFiltered results for {course_filter}: {len(filtered_exams)} exams")
                for i, exam in enumerate(filtered_exams, 1):
                    print(f"  {i}. {exam['title']} ({exam['course']})")
        else:
            print("No exams found. This could mean:")
            print("1. The exam collection is currently empty")
            print("2. Exams are in a different location")
            print("3. Additional permissions are required")
            print("4. The collection structure has changed")
            
            print("\nDebugging information saved to search_page_*.html files")
    
    finally:
        downloader.close()

def extract_course_code(title):
    """Extract course code from exam title"""
    patterns = [
        r'\b[A-Z]{3,4}\s*\d{3,4}\b',  # ELEC 371, MATH 100, etc.
        r'\b[A-Z]{2,4}\d{3,4}\b',     # ELEC371, MATH100, etc.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title.upper())
        if match:
            return match.group().replace(' ', '')
    
    return "UNKNOWN"

if __name__ == "__main__":
    comprehensive_exam_search()
