# Simple Test: Click Applied Science Subject
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re

def test_applied_science_click():
    """Test clicking on Applied Science subject to find exams"""
    print("Testing Applied Science Subject Click")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Use the working login method
        print("Step 1: Logging in...")
        if not downloader.setup_selenium(headless=False):
            return
        
        print("Attempting Microsoft Azure AD login for user: 22yyq")
        downloader.driver.get("https://qspace.library.queensu.ca/login")
        time.sleep(3)
        
        print(f"Page title: {downloader.driver.title}")
        print(f"Current URL: {downloader.driver.current_url}")
        
        # Check if already on Microsoft login page
        if "login.microsoftonline.com" in downloader.driver.current_url:
            print("Already on Microsoft login page")
        else:
            print("Looking for Microsoft login button...")
            microsoft_buttons = downloader.driver.find_elements("css selector", "a[href*='microsoft']")
            if not microsoft_buttons:
                microsoft_buttons = downloader.driver.find_elements("xpath", "//a[contains(text(), 'Microsoft')] | //button[contains(text(), 'Microsoft')]")
            
            if microsoft_buttons:
                microsoft_buttons[0].click()
                time.sleep(3)
                print("Clicked Microsoft login button")
            else:
                print("No Microsoft login button found, checking if already redirected...")
        
        if "login.microsoftonline.com" in downloader.driver.current_url:
            print("On Microsoft login page, entering credentials...")
            
            # Find username field
            username_field = None
            username_selectors = [
                "input[name='loginfmt']",
                "input[type='email']",
                "input[id='i0116']",
                "input[placeholder*='netid@queensu.ca']"
            ]
            
            for selector in username_selectors:
                try:
                    username_field = downloader.driver.find_element("css selector", selector)
                    print(f"Found username field: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                print("Could not find username field")
                return False
            
            username_field.send_keys("22yyq@queensu.ca")
            print("Username entered")
            
            # Click Next button
            next_buttons = downloader.driver.find_elements("css selector", "input[type='submit'], button[type='submit']")
            if next_buttons:
                next_buttons[0].click()
                time.sleep(3)
                print("Found Next button: input[type='submit']")
            
            # Find password field
            password_field = None
            password_selectors = [
                "input[name='passwd']",
                "input[type='password']",
                "input[id='i0118']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = downloader.driver.find_element("css selector", selector)
                    print(f"Found password field: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("Could not find password field")
                return False
            
            password_field.send_keys("7GearGlue&")
            print("Password entered")
            
            # Click Sign In button
            signin_buttons = downloader.driver.find_elements("css selector", "input[type='submit'], button[type='submit']")
            if signin_buttons:
                signin_buttons[0].click()
                time.sleep(3)
                print("Found Sign In button: input[type='submit']")
                print("Sign In button clicked")
            
            print("\n" + "="*60)
            print("IMPORTANT: Complete 2FA authentication in the browser window!")
            print("This may include:")
            print("- SMS code to your phone")
            print("- Authenticator app notification")
            print("- Email verification")
            print("- Other 2FA methods")
            print("="*60)
            print("\nWaiting for you to complete 2FA authentication...")
            print("The browser window will remain open for you to complete the process.")
            
            # Wait for redirect back to QSpace
            max_wait = 300  # 5 minutes
            wait_time = 0
            while wait_time < max_wait:
                if "qspace.library.queensu.ca" in downloader.driver.current_url and "login.microsoftonline.com" not in downloader.driver.current_url:
                    print(f"\n[SUCCESS] Login completed! Redirected to: {downloader.driver.current_url}")
                    break
                time.sleep(2)
                wait_time += 2
                if wait_time % 30 == 0:  # Print every 30 seconds
                    print(f"Still waiting for 2FA completion... ({wait_time}s)")
            else:
                print("\n[ERROR] Login timeout - 2FA not completed in time")
                return False
        
        # Step 2: Navigate to subject browse page
        print("\nStep 2: Navigating to subject browse page...")
        downloader.driver.get("https://qspace.library.queensu.ca/browse/subject?scope=699fe318-6bf1-45b5-9b17-61f0d2246003")
        time.sleep(3)
        
        print(f"Subject page - URL: {downloader.driver.current_url}")
        print(f"Subject page - Title: {downloader.driver.title}")
        
        # Step 3: Look for "Applied Science" subject
        print("\nStep 3: Looking for 'Applied Science' subject...")
        
        # Get all links on the page
        links = downloader.driver.find_elements("tag name", "a")
        print(f"Found {len(links)} total links on the page")
        
        applied_science_link = None
        for link in links:
            try:
                text = link.text.strip()
                if "Applied Science" in text:
                    applied_science_link = link
                    print(f"Found Applied Science link: '{text}'")
                    break
            except:
                continue
        
        if applied_science_link:
            applied_science_link.click()
            time.sleep(3)
            print("Clicked Applied Science")
        else:
            print("Could not find Applied Science link")
            # Let's see what links are available
            print("\nAvailable links:")
            for i, link in enumerate(links[:20], 1):  # Show first 20
                try:
                    text = link.text.strip()
                    if text:
                        print(f"  {i}. '{text}'")
                except:
                    continue
            return False
        
        print(f"After Applied Science click - URL: {downloader.driver.current_url}")
        print(f"After Applied Science click - Title: {downloader.driver.title}")
        
        # Step 4: Look for actual exam files
        print("\nStep 4: Looking for actual exam files...")
        
        # Save page for analysis
        page_source = downloader.driver.page_source
        with open('applied_science_exams.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Applied Science page saved to 'applied_science_exams.html'")
        
        # Look for exam links
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for exam-related content
        exam_keywords = ['exam', 'test', 'midterm', 'final', 'quiz', 'ELEC371', 'ELEC']
        page_text = soup.get_text().lower()
        found_keywords = [kw for kw in exam_keywords if kw in page_text]
        
        if found_keywords:
            print(f"Found exam keywords in page: {found_keywords}")
        
        # Look for exam links (different patterns)
        exam_patterns = [
            r'/items/',
            r'/handle/',
            r'/bitstream/',
            r'ELEC371',
            r'ELEC'
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
        
        print(f"\nFound {len(all_exams)} potential exam links:")
        for i, exam in enumerate(all_exams[:10], 1):  # Show first 10
            print(f"  {i}. {exam['title']} ({exam['course']})")
            print(f"     URL: {exam['url']}")
        
        if all_exams:
            print(f"\nSUCCESS: Found {len(all_exams)} exam results!")
            
            # Look specifically for ELEC371
            elec371_exams = [exam for exam in all_exams if 'ELEC371' in exam['title'].upper() or 'ELEC371' in exam['course'].upper()]
            if elec371_exams:
                print(f"\nFound {len(elec371_exams)} ELEC371 exams:")
                for exam in elec371_exams:
                    print(f"  - {exam['title']} ({exam['course']})")
                    print(f"    URL: {exam['url']}")
            else:
                print("\nNo ELEC371 exams found, but found other exams")
            
            return True
        else:
            print("No exam links found in Applied Science")
            return False
        
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
    test_applied_science_click()
