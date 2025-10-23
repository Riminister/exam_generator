# Comprehensive Exam Access Test
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re

def test_comprehensive_exam_access():
    """Test comprehensive approaches to access exams"""
    print("Comprehensive Exam Access Test")
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
        
        # Step 2: Try multiple approaches to access exams
        print("\nStep 2: Trying multiple approaches to access exams...")
        
        # Approach 1: Direct search for ELEC371
        print("\nApproach 1: Direct search for ELEC371...")
        downloader.driver.get("https://qspace.library.queensu.ca/search?query=ELEC371")
        time.sleep(5)
        
        print(f"Search page - URL: {downloader.driver.current_url}")
        print(f"Search page - Title: {downloader.driver.title}")
        
        # Save search results
        page_source = downloader.driver.page_source
        with open('elec371_search.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Search results saved to 'elec371_search.html'")
        
        # Look for exam links in search results
        soup = BeautifulSoup(page_source, 'html.parser')
        exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
        
        if exam_links:
            print(f"Found {len(exam_links)} exam links in search results!")
            for i, link in enumerate(exam_links[:5], 1):
                title = link.get_text(strip=True)
                href = link.get('href')
                print(f"  {i}. {title} -> {href}")
            
            # Try to click on the first exam
            if exam_links:
                first_exam = exam_links[0]
                print(f"\nClicking on first exam: {first_exam.get_text(strip=True)}")
                first_exam.click()
                time.sleep(3)
                
                print(f"Exam page - URL: {downloader.driver.current_url}")
                print(f"Exam page - Title: {downloader.driver.title}")
                
                # Look for download links
                exam_page_source = downloader.driver.page_source
                exam_soup = BeautifulSoup(exam_page_source, 'html.parser')
                download_links = exam_soup.find_all('a', href=re.compile(r'/bitstream/'))
                
                if download_links:
                    print(f"Found {len(download_links)} download links!")
                    for i, link in enumerate(download_links[:3], 1):
                        title = link.get_text(strip=True)
                        href = link.get('href')
                        print(f"  {i}. {title} -> {href}")
                    
                    print("\nSUCCESS: Found downloadable exam files!")
                    return True
                else:
                    print("No download links found on exam page")
            
            return True
        else:
            print("No exam links found in search results")
        
        # Approach 2: Browse by subject with longer wait
        print("\nApproach 2: Browse by subject with longer wait...")
        downloader.driver.get("https://qspace.library.queensu.ca/browse/subject?scope=699fe318-6bf1-45b5-9b17-61f0d2246003")
        time.sleep(10)  # Wait longer for dynamic content
        
        print(f"Subject page - URL: {downloader.driver.current_url}")
        print(f"Subject page - Title: {downloader.driver.title}")
        
        # Save subject page
        page_source = downloader.driver.page_source
        with open('subject_page_detailed.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Subject page saved to 'subject_page_detailed.html'")
        
        # Look for Applied Science link with more specific selectors
        applied_science_link = None
        
        # Try different selectors
        selectors = [
            "a:contains('Applied Science')",
            "a[href*='Applied%20Science']",
            "a[href*='Applied Science']",
            ".list-group-item a",
            ".browse-entry a"
        ]
        
        for selector in selectors:
            try:
                if ":contains" in selector:
                    # Use XPath for text-based search
                    xpath = "//a[contains(text(), 'Applied Science')]"
                    applied_science_link = downloader.driver.find_element("xpath", xpath)
                else:
                    applied_science_link = downloader.driver.find_element("css selector", selector)
                
                print(f"Found Applied Science link with selector: {selector}")
                break
            except:
                continue
        
        if applied_science_link:
            applied_science_link.click()
            time.sleep(5)
            print("Clicked Applied Science")
            
            print(f"Applied Science page - URL: {downloader.driver.current_url}")
            print(f"Applied Science page - Title: {downloader.driver.title}")
            
            # Look for exam links
            page_source = downloader.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
            
            if exam_links:
                print(f"Found {len(exam_links)} exam links in Applied Science!")
                for i, link in enumerate(exam_links[:5], 1):
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    print(f"  {i}. {title} -> {href}")
                return True
            else:
                print("No exam links found in Applied Science")
        else:
            print("Could not find Applied Science link")
        
        # Approach 3: Try direct URL to a known exam
        print("\nApproach 3: Try direct URL to exam collection...")
        downloader.driver.get("https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888")
        time.sleep(5)
        
        print(f"Collection page - URL: {downloader.driver.current_url}")
        print(f"Collection page - Title: {downloader.driver.title}")
        
        # Save collection page
        page_source = downloader.driver.page_source
        with open('collection_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Collection page saved to 'collection_page.html'")
        
        # Look for exam links
        soup = BeautifulSoup(page_source, 'html.parser')
        exam_links = soup.find_all('a', href=re.compile(r'/items/|/handle/'))
        
        if exam_links:
            print(f"Found {len(exam_links)} exam links in collection!")
            for i, link in enumerate(exam_links[:5], 1):
                title = link.get_text(strip=True)
                href = link.get('href')
                print(f"  {i}. {title} -> {href}")
            return True
        else:
            print("No exam links found in collection")
        
        return False
        
    finally:
        downloader.close()

if __name__ == "__main__":
    test_comprehensive_exam_access()

