# Queen's Exam Bank Downloader - Correct Navigation Path
# Follows: Home → All of QSpace → By Subject → Search

import re
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup

def navigate_correct_path():
    """Navigate using the correct QSpace path"""
    print("Queen's Exam Bank Downloader - Correct Navigation")
    print("=" * 60)
    print("Navigation: Home -> All of QSpace -> By Subject -> Search")
    print("=" * 60)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Step 1: Microsoft 2FA Login
        print("Step 1: Microsoft 2FA Login...")
        success = downloader.login("22yyq", "7GearGlue&")
        
        if not success:
            print("Login failed. Cannot proceed.")
            return
        
        # Step 2: Navigate to QSpace Home
        print("\nStep 2: Navigating to QSpace Home...")
        downloader.driver.get("https://qspace.library.queensu.ca/home")
        time.sleep(3)
        
        print(f"Current page: {downloader.driver.title}")
        print(f"Current URL: {downloader.driver.current_url}")
        
        # Step 3: Click "All of QSpace" tab
        print("\nStep 3: Looking for 'All of QSpace' tab...")
        
        # Look for "All of QSpace" link/tab
        all_qspace_selectors = [
            "a:contains('All of QSpace')",
            "a[href*='browse']",
            ".navbar-nav a",
            "nav a"
        ]
        
        all_qspace_link = None
        for selector in all_qspace_selectors:
            try:
                # Try different approaches to find the link
                if ":contains" in selector:
                    # Use XPath for text-based search
                    xpath = "//a[contains(text(), 'All of QSpace')]"
                    all_qspace_link = downloader.driver.find_element("xpath", xpath)
                else:
                    all_qspace_link = downloader.driver.find_element("css selector", selector)
                
                print(f"Found 'All of QSpace' link: {selector}")
                break
            except:
                continue
        
        if all_qspace_link:
            all_qspace_link.click()
            time.sleep(3)
            print("Clicked 'All of QSpace'")
        else:
            print("Could not find 'All of QSpace' link, trying direct navigation...")
            # Try direct navigation to browse page
            downloader.driver.get("https://qspace.library.queensu.ca/browse")
            time.sleep(3)
        
        print(f"After navigation - URL: {downloader.driver.current_url}")
        print(f"After navigation - Title: {downloader.driver.title}")
        
        # Step 4: Look for "By Subject" option
        print("\nStep 4: Looking for 'By Subject' option...")
        
        subject_selectors = [
            "a:contains('By Subject')",
            "a[href*='subject']",
            ".browse-option",
            ".list-group-item"
        ]
        
        subject_link = None
        for selector in subject_selectors:
            try:
                if ":contains" in selector:
                    xpath = "//a[contains(text(), 'By Subject')]"
                    subject_link = downloader.driver.find_element("xpath", xpath)
                else:
                    subject_link = downloader.driver.find_element("css selector", selector)
                
                print(f"Found 'By Subject' link: {selector}")
                break
            except:
                continue
        
        if subject_link:
            subject_link.click()
            time.sleep(3)
            print("Clicked 'By Subject'")
        else:
            print("Could not find 'By Subject' link, trying direct navigation...")
            downloader.driver.get("https://qspace.library.queensu.ca/browse/subject")
            time.sleep(3)
        
        print(f"After subject navigation - URL: {downloader.driver.current_url}")
        print(f"After subject navigation - Title: {downloader.driver.title}")
        
        # Step 5: Look for search functionality
        print("\nStep 5: Looking for search functionality...")
        
        # Save current page for analysis
        page_source = downloader.driver.page_source
        with open('subject_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Subject page saved to 'subject_page.html' for analysis")
        
        # Look for search box
        search_selectors = [
            "input[type='search']",
            "input[name='query']",
            "input[placeholder*='search']",
            ".search-box input",
            "#search-box"
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                search_box = downloader.driver.find_element("css selector", selector)
                print(f"Found search box: {selector}")
                break
            except:
                continue
        
        if search_box:
            print("Found search functionality!")
            
            # Try searching for a course
            course_to_search = input("Enter course code to search for (e.g., ELEC371): ").strip()
            if course_to_search:
                search_box.clear()
                search_box.send_keys(course_to_search)
                print(f"Entered search term: {course_to_search}")
                
                # Look for search button
                search_button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Search')",
                    ".search-button"
                ]
                
                search_button = None
                for selector in search_button_selectors:
                    try:
                        if ":contains" in selector:
                            xpath = "//button[contains(text(), 'Search')]"
                            search_button = downloader.driver.find_element("xpath", xpath)
                        else:
                            search_button = downloader.driver.find_element("css selector", selector)
                        break
                    except:
                        continue
                
                if search_button:
                    search_button.click()
                    time.sleep(3)
                    print("Clicked search button")
                else:
                    # Try Enter key
                    search_box.send_keys("\n")
                    time.sleep(3)
                    print("Pressed Enter to search")
                
                # Analyze search results
                print(f"\nSearch results - URL: {downloader.driver.current_url}")
                print(f"Search results - Title: {downloader.driver.title}")
                
                # Look for exam results
                page_source = downloader.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Look for exam links
                exam_patterns = [
                    r'/items/',
                    r'/handle/',
                    r'/bitstream/'
                ]
                
                all_exams = []
                for pattern in exam_patterns:
                    links = soup.find_all('a', href=re.compile(pattern))
                    for link in links:
                        title = link.get_text(strip=True)
                        href = link.get('href')
                        if title and href and len(title) > 3:
                            all_exams.append({
                                'title': title,
                                'url': href,
                                'course': extract_course_code(title)
                            })
                
                print(f"\nFound {len(all_exams)} potential exam results:")
                for i, exam in enumerate(all_exams[:10], 1):  # Show first 10
                    print(f"  {i}. {exam['title']} ({exam['course']})")
                    print(f"     URL: {exam['url']}")
                
                if all_exams:
                    print(f"\nTotal exams found: {len(all_exams)}")
                    return all_exams
                else:
                    print("No exam results found in search")
            else:
                print("No search term provided")
        else:
            print("No search functionality found")
        
        # Step 6: Try alternative navigation paths
        print("\nStep 6: Trying alternative navigation...")
        
        alternative_urls = [
            "https://qspace.library.queensu.ca/browse/subject",
            "https://qspace.library.queensu.ca/search",
            "https://qspace.library.queensu.ca/browse/title",
            "https://qspace.library.queensu.ca/communities/699fe318-6bf1-45b5-9b17-61f0d2246003"  # Exams & Syllabi community
        ]
        
        for url in alternative_urls:
            print(f"Trying: {url}")
            downloader.driver.get(url)
            time.sleep(3)
            
            page_source = downloader.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for any exam-related content
            exam_keywords = ['exam', 'test', 'midterm', 'final', 'quiz']
            page_text = soup.get_text().lower()
            found_keywords = [kw for kw in exam_keywords if kw in page_text]
            
            if found_keywords:
                print(f"  Found exam keywords: {found_keywords}")
                
                # Look for exam links
                exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
                if exam_links:
                    print(f"  Found {len(exam_links)} exam links!")
                    for link in exam_links[:5]:
                        print(f"    - {link.get_text(strip=True)}")
                    break
            else:
                print(f"  No exam content found")
        
        return []
        
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
    navigate_correct_path()
