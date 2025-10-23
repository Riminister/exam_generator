# Final Working Exam Downloader
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re
import os
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_final_working_downloader():
    """Final working exam downloader using requests for file download"""
    print("Final Working Exam Downloader - SUCCESS!")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Step 1: Login and get authenticated session
        print("Step 1: Logging in and getting authenticated session...")
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
        
        # Step 2: Copy cookies from Selenium to requests session
        print("\nStep 2: Copying authentication cookies to requests session...")
        cookies = downloader.driver.get_cookies()
        session = requests.Session()
        
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        print(f"Copied {len(cookies)} cookies to requests session")
        
        # Step 3: Navigate to exam collection and get download URL
        print("\nStep 3: Navigating to exam collection and getting download URL...")
        
        # Navigate directly to the exam collection
        exam_collection_url = "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888"
        print(f"\nNavigating to exam collection: {exam_collection_url}")
        downloader.driver.get(exam_collection_url)
        time.sleep(5)
        
        print(f"Exam collection page - URL: {downloader.driver.current_url}")
        print(f"Exam collection page - Title: {downloader.driver.title}")
        
        # Check page content for debugging
        page_source = downloader.driver.page_source
        if "no items to show" in page_source.lower():
            print("WARNING: Still seeing 'No items to show' message")
            print("This might indicate the collection is empty or requires different access")
        else:
            print("Page content looks good - no 'No items to show' message")
        
        # Look for exam links using Selenium WebElements
        exam_links = downloader.driver.find_elements("css selector", "a[href*='/items/']")
        
        if exam_links:
            print(f"Found {len(exam_links)} exam links in search results!")
            
            # Try the first exam
            first_exam = exam_links[0]
            exam_title = first_exam.text.strip()
            exam_url = first_exam.get_attribute('href')
            
            print(f"\n--- Trying Exam: '{exam_title}' ---")
            print(f"Exam URL: {exam_url}")
            
            # Click on the exam
            first_exam.click()
            time.sleep(5)
            
            print(f"Exam page - URL: {downloader.driver.current_url}")
            print(f"Exam page - Title: {downloader.driver.title}")
            
            # Look for the specific download link pattern we found
            download_links = downloader.driver.find_elements("css selector", "a[href*='/bitstreams/'][href*='/download']")
            
            if download_links:
                print(f"Found {len(download_links)} download links!")
                
                # Get the download URL
                first_download = download_links[0]
                download_url = first_download.get_attribute('href')
                download_title = first_download.text.strip()
                
                print(f"\nDownload URL: {download_url}")
                print(f"Download title: {download_title}")
                
                # Step 4: Download file using requests
                print("\nStep 4: Downloading file using requests...")
                
                # Create downloads directory
                download_dir = "downloads"
                os.makedirs(download_dir, exist_ok=True)
                
                # Extract filename from download title
                filename = "downloaded_exam.pdf"
                if download_title:
                    # Try to extract filename from title
                    if ".pdf" in download_title.lower():
                        filename = download_title.split("(")[0].strip() + ".pdf"
                    else:
                        filename = download_title.split("(")[0].strip() + ".pdf"
                
                file_path = os.path.join(download_dir, filename)
                
                print(f"Downloading to: {file_path}")
                
                # Download the file
                try:
                    response = session.get(download_url, stream=True)
                    response.raise_for_status()
                    
                    print(f"Response status: {response.status_code}")
                    print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                    print(f"Content length: {response.headers.get('content-length', 'unknown')}")
                    
                    # Write file to disk
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Check file size
                    file_size = os.path.getsize(file_path)
                    print(f"\n[SUCCESS] DOWNLOAD SUCCESSFUL!")
                    print(f"File saved as: {filename}")
                    print(f"File size: {file_size} bytes")
                    print(f"File path: {file_path}")
                    
                    return True
                    
                except Exception as e:
                    print(f"Download failed: {e}")
                    return False
            else:
                print("No download links found with the correct pattern")
                return False
        else:
            print("No exam links found in search results")
            return False
        
    finally:
        downloader.close()

if __name__ == "__main__":
    test_final_working_downloader()
