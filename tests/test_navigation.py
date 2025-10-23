# Test Correct Navigation After Successful Login
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re

def test_correct_navigation():
    """Test the correct navigation path after successful login"""
    print("Testing Correct Navigation Path")
    print("Navigation: Home -> Communities & Collections -> Exams & Syllabi -> By Subject")
    print("=" * 70)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Step 1: Login (using the working method)
        print("Step 1: Logging in...")
        if not downloader.login("22yyq", "7GearGlue&"):
            print("Login failed")
            return
        
        print("Login successful! Now testing navigation...")
        
        # Step 2: Navigate to QSpace Home
        print("\nStep 2: Going to QSpace Home...")
        downloader.driver.get("https://qspace.library.queensu.ca/home")
        time.sleep(3)
        
        print(f"Home page title: {downloader.driver.title}")
        print(f"Home page URL: {downloader.driver.current_url}")
        
        # Step 3: Look for "Communities & Collections" link
        print("\nStep 3: Looking for 'Communities & Collections' link...")
        
        # Get all links on the page
        links = downloader.driver.find_elements("tag name", "a")
        print(f"Found {len(links)} total links on home page")
        
        communities_link = None
        for link in links:
            try:
                text = link.text.strip()
                if "Communities & Collections" in text or "Communities" in text:
                    communities_link = link
                    print(f"Found 'Communities & Collections' link: '{text}'")
                    break
            except:
                continue
        
        if communities_link:
            communities_link.click()
            time.sleep(3)
            print("Clicked 'Communities & Collections'")
        else:
            print("Could not find 'Communities & Collections' link, trying direct navigation...")
            downloader.driver.get("https://qspace.library.queensu.ca/communities")
            time.sleep(3)
        
        print(f"After navigation - URL: {downloader.driver.current_url}")
        print(f"After navigation - Title: {downloader.driver.title}")
        
        # Step 4: Look for "Exams & Syllabi" community
        print("\nStep 4: Looking for 'Exams & Syllabi' community...")
        
        links = downloader.driver.find_elements("tag name", "a")
        exams_link = None
        
        for link in links:
            try:
                text = link.text.strip()
                if "Exams & Syllabi" in text or "Exams" in text:
                    exams_link = link
                    print(f"Found Exams & Syllabi link: '{text}'")
                    break
            except:
                continue
        
        if exams_link:
            exams_link.click()
            time.sleep(3)
            print("Clicked 'Exams & Syllabi'")
        else:
            print("Could not find 'Exams & Syllabi' link, trying direct navigation...")
            downloader.driver.get("https://qspace.library.queensu.ca/communities/699fe318-6bf1-45b5-9b17-61f0d2246003")
            time.sleep(3)
        
        print(f"After Exams navigation - URL: {downloader.driver.current_url}")
        print(f"After Exams navigation - Title: {downloader.driver.title}")
        
        # Step 5: Look for "By Subject" option
        print("\nStep 5: Looking for 'By Subject' option...")
        
        links = downloader.driver.find_elements("tag name", "a")
        subject_link = None
        
        for link in links:
            try:
                text = link.text.strip()
                if "By Subject" in text or "Subject" in text:
                    subject_link = link
                    print(f"Found subject link: '{text}'")
                    break
            except:
                continue
        
        if subject_link:
            subject_link.click()
            time.sleep(3)
            print("Clicked subject link")
        else:
            print("Could not find subject link, trying direct navigation...")
            downloader.driver.get("https://qspace.library.queensu.ca/communities/699fe318-6bf1-45b5-9b17-61f0d2246003/browse/subject")
            time.sleep(3)
        
        print(f"After subject navigation - URL: {downloader.driver.current_url}")
        print(f"After subject navigation - Title: {downloader.driver.title}")
        
        # Step 6: Look for search functionality
        print("\nStep 6: Looking for search functionality...")
        
        # Save page for analysis
        page_source = downloader.driver.page_source
        with open('subject_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Subject page saved to 'subject_page.html'")
        
        # Look for search box
        search_inputs = downloader.driver.find_elements("css selector", "input[type='search'], input[name='query'], input[placeholder*='search']")
        
        if search_inputs:
            search_box = search_inputs[0]
            print("Found search box!")
            
            # Try searching for ELEC371
            course_to_search = "ELEC371"
            search_box.clear()
            search_box.send_keys(course_to_search)
            print(f"Entered search term: {course_to_search}")
            
            # Look for search button
            search_buttons = downloader.driver.find_elements("css selector", "button[type='submit'], input[type='submit']")
            if search_buttons:
                search_buttons[0].click()
                time.sleep(3)
                print("Clicked search button")
            else:
                search_box.send_keys("\n")
                time.sleep(3)
                print("Pressed Enter to search")
            
            # Analyze search results
            print(f"\nSearch results - URL: {downloader.driver.current_url}")
            print(f"Search results - Title: {downloader.driver.title}")
            
            # Look for exam results
            page_source = downloader.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for any exam-related content
            exam_keywords = ['exam', 'test', 'midterm', 'final', 'quiz', 'ELEC371']
            page_text = soup.get_text().lower()
            found_keywords = [kw for kw in exam_keywords if kw in page_text]
            
            if found_keywords:
                print(f"Found exam keywords in page: {found_keywords}")
                
                # Look for exam links
                exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
                print(f"Found {len(exam_links)} potential exam links")
                
                for i, link in enumerate(exam_links[:5]):
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    print(f"  {i+1}. {title} -> {href}")
                
                if exam_links:
                    print(f"\nSUCCESS: Found {len(exam_links)} exam results!")
                    return True
            else:
                print("No exam keywords found in search results")
        else:
            print("No search functionality found")
        
        # Step 7: Try alternative approach - go directly to Exams & Syllabi community
        print("\nStep 7: Trying Exams & Syllabi community...")
        downloader.driver.get("https://qspace.library.queensu.ca/communities/699fe318-6bf1-45b5-9b17-61f0d2246003")
        time.sleep(3)
        
        print(f"Exams community - URL: {downloader.driver.current_url}")
        print(f"Exams community - Title: {downloader.driver.title}")
        
        # Save this page too
        page_source = downloader.driver.page_source
        with open('exams_community.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Exams community page saved to 'exams_community.html'")
        
        # Look for exam links
        soup = BeautifulSoup(page_source, 'html.parser')
        exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
        
        if exam_links:
            print(f"Found {len(exam_links)} exam links in Exams community!")
            for i, link in enumerate(exam_links[:5]):
                title = link.get_text(strip=True)
                href = link.get('href')
                print(f"  {i+1}. {title} -> {href}")
            return True
        else:
            print("No exam links found in Exams community")
        
        return False
        
    finally:
        downloader.close()

if __name__ == "__main__":
    test_correct_navigation()
