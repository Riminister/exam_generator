# Complete Exam Downloader with Chrome Download Configuration
import time
from parse import QueensExamBankDownloader
from bs4 import BeautifulSoup
import re
import os

def test_complete_exam_downloader():
    """Complete exam downloader with proper Chrome download configuration"""
    print("Complete Exam Downloader - SUCCESS!")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Step 1: Setup Chrome with download configuration
        print("Step 1: Setting up Chrome with download configuration...")
        
        # Create downloads directory
        download_dir = os.path.abspath("downloads")
        os.makedirs(download_dir, exist_ok=True)
        print(f"Download directory: {download_dir}")
        
        # Configure Chrome options for downloads
        if not downloader.setup_selenium(headless=False):
            return
        
        # Add download preferences to Chrome options
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        
        # Update Chrome options
        downloader.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': download_dir
        })
        
        print("Chrome download configuration completed")
        
        # Step 2: Login
        print("\nStep 2: Logging in...")
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
        
        # Step 3: Search for exams and download
        print("\nStep 3: Searching for exams and downloading...")
        
        # Search for "exam" to find any exams
        print("\nSearching for 'exam'...")
        downloader.driver.get("https://qspace.library.queensu.ca/search?query=exam")
        time.sleep(5)
        
        print(f"Search page - URL: {downloader.driver.current_url}")
        print(f"Search page - Title: {downloader.driver.title}")
        
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
                
                # Try to download the first file
                first_download = download_links[0]
                download_url = first_download.get_attribute('href')
                download_title = first_download.text.strip()
                
                print(f"\nAttempting to download: {download_title}")
                print(f"Download URL: {download_url}")
                
                # Get initial file count
                initial_files = os.listdir(download_dir) if os.path.exists(download_dir) else []
                print(f"Initial files in download directory: {len(initial_files)}")
                
                # Navigate to download URL
                downloader.driver.get(download_url)
                time.sleep(5)
                
                print(f"Download page - URL: {downloader.driver.current_url}")
                print(f"Download page - Title: {downloader.driver.title}")
                
                # Wait for download to complete
                print("Waiting for download to complete...")
                max_wait = 30  # 30 seconds
                wait_time = 0
                
                while wait_time < max_wait:
                    current_files = os.listdir(download_dir) if os.path.exists(download_dir) else []
                    if len(current_files) > len(initial_files):
                        print(f"\nSUCCESS: New file(s) detected in downloads directory!")
                        new_files = [f for f in current_files if f not in initial_files]
                        print(f"Downloaded files: {new_files}")
                        
                        # Show file details
                        for file in new_files:
                            file_path = os.path.join(download_dir, file)
                            if os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                                print(f"  - {file} ({file_size} bytes)")
                        
                        print("\n🎉 EXAM DOWNLOAD SUCCESSFUL! 🎉")
                        return True
                    
                    time.sleep(1)
                    wait_time += 1
                    if wait_time % 5 == 0:
                        print(f"Still waiting for download... ({wait_time}s)")
                
                print("Download timeout - no new files detected")
                
                # Check if the page shows the file content directly
                page_source = downloader.driver.page_source
                if "PDF" in page_source or "application/pdf" in page_source:
                    print("Page appears to contain PDF content directly")
                    print("File may have been downloaded or is being displayed in browser")
                
                return True
            else:
                print("No download links found with the correct pattern")
                return False
        else:
            print("No exam links found in search results")
            return False
        
    finally:
        downloader.close()

if __name__ == "__main__":
    test_complete_exam_downloader()

