# Fixed Exam Access Test
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re

def test_fixed_exam_access():
    """Test fixed approaches to access exams"""
    print("Fixed Exam Access Test")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Step 1: Login (using the working method)
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
        
        # Step 2: Try different search approaches
        print("\nStep 2: Trying different search approaches...")
        
        # Approach 1: Search for "exam" to find any exams
        print("\nApproach 1: Search for 'exam'...")
        downloader.driver.get("https://qspace.library.queensu.ca/search?query=exam")
        time.sleep(5)
        
        print(f"Search page - URL: {downloader.driver.current_url}")
        print(f"Search page - Title: {downloader.driver.title}")
        
        # Save search results
        page_source = downloader.driver.page_source
        with open('exam_search.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Search results saved to 'exam_search.html'")
        
        # Look for exam links using Selenium WebElements
        exam_links = downloader.driver.find_elements("css selector", "a[href*='/items/']")
        
        if exam_links:
            print(f"Found {len(exam_links)} exam links in search results!")
            
            # Try to click on the first exam using Selenium WebElement
            first_exam = exam_links[0]
            exam_title = first_exam.text.strip()
            exam_url = first_exam.get_attribute('href')
            
            print(f"\nClicking on first exam: '{exam_title}'")
            print(f"Exam URL: {exam_url}")
            
            first_exam.click()
            time.sleep(5)
            
            print(f"Exam page - URL: {downloader.driver.current_url}")
            print(f"Exam page - Title: {downloader.driver.title}")
            
            # Look for download links
            download_links = downloader.driver.find_elements("css selector", "a[href*='/bitstream/']")
            
            if download_links:
                print(f"Found {len(download_links)} download links!")
                for i, link in enumerate(download_links[:3], 1):
                    title = link.text.strip()
                    href = link.get_attribute('href')
                    print(f"  {i}. {title} -> {href}")
                
                print("\nSUCCESS: Found downloadable exam files!")
                
                # Try to download the first file
                if download_links:
                    first_download = download_links[0]
                    download_url = first_download.get_attribute('href')
                    download_title = first_download.text.strip()
                    
                    print(f"\nAttempting to download: {download_title}")
                    print(f"Download URL: {download_url}")
                    
                    # Navigate to download URL
                    downloader.driver.get(download_url)
                    time.sleep(3)
                    
                    print(f"Download page - URL: {downloader.driver.current_url}")
                    print(f"Download page - Title: {downloader.driver.title}")
                    
                    # Check if file downloaded or if we need to click a download button
                    download_buttons = downloader.driver.find_elements("css selector", "a[href*='download'], button[onclick*='download'], input[type='submit'][value*='download']")
                    if download_buttons:
                        download_buttons[0].click()
                        time.sleep(3)
                        print("Clicked download button")
                    
                    print("Download attempt completed!")
                
                return True
            else:
                print("No download links found on exam page")
        else:
            print("No exam links found in search results")
        
        # Approach 2: Try searching for specific course codes
        print("\nApproach 2: Search for specific course codes...")
        
        course_codes = ["ELEC", "MATH", "CHEM", "PHYS", "COMP"]
        
        for course in course_codes:
            print(f"\nSearching for {course}...")
            downloader.driver.get(f"https://qspace.library.queensu.ca/search?query={course}")
            time.sleep(3)
            
            exam_links = downloader.driver.find_elements("css selector", "a[href*='/items/']")
            if exam_links:
                print(f"Found {len(exam_links)} exam links for {course}!")
                
                # Look for exam titles
                for i, link in enumerate(exam_links[:3], 1):
                    title = link.text.strip()
                    href = link.get_attribute('href')
                    print(f"  {i}. {title} -> {href}")
                
                # Try clicking on the first exam
                first_exam = exam_links[0]
                first_exam.click()
                time.sleep(3)
                
                print(f"Exam page - URL: {downloader.driver.current_url}")
                print(f"Exam page - Title: {downloader.driver.title}")
                
                # Look for download links
                download_links = downloader.driver.find_elements("css selector", "a[href*='/bitstream/']")
                if download_links:
                    print(f"Found {len(download_links)} download links!")
                    return True
                else:
                    print("No download links found")
                
                break  # Found exams, no need to try other courses
        
        # Approach 3: Try browsing by subject with JavaScript execution
        print("\nApproach 3: Browse by subject with JavaScript execution...")
        downloader.driver.get("https://qspace.library.queensu.ca/browse/subject?scope=699fe318-6bf1-45b5-9b17-61f0d2246003")
        time.sleep(10)
        
        # Execute JavaScript to scroll and trigger dynamic loading
        downloader.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Look for Applied Science link
        applied_science_links = downloader.driver.find_elements("xpath", "//a[contains(text(), 'Applied Science')]")
        
        if applied_science_links:
            print("Found Applied Science link!")
            applied_science_links[0].click()
            time.sleep(5)
            
            print(f"Applied Science page - URL: {downloader.driver.current_url}")
            print(f"Applied Science page - Title: {downloader.driver.title}")
            
            # Look for exam links
            exam_links = downloader.driver.find_elements("css selector", "a[href*='/items/']")
            if exam_links:
                print(f"Found {len(exam_links)} exam links in Applied Science!")
                return True
            else:
                print("No exam links found in Applied Science")
        else:
            print("Could not find Applied Science link")
        
        return False
        
    finally:
        downloader.close()

if __name__ == "__main__":
    test_fixed_exam_access()

