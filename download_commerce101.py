# Commerce 101 Midterm Downloader
import time
import os
import requests
from src.parse import QueensExamBankDownloader

def download_commerce101_midterms():
    """Download all Commerce 101 midterms"""
    print("Commerce 101 Midterm Downloader")
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
        
        # Step 3: Search for Commerce 101 exams
        print("\nStep 3: Searching for Commerce 101 exams...")
        
        # Create downloads directory
        download_dir = "exam_downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # Search terms for Commerce 101
        search_terms = [
            "COMM101",
            "Commerce 101", 
            "COMM 101",
            "Commerce101",
            "COMM-101"
        ]
        
        downloaded_files = []
        
        for search_term in search_terms:
            print(f"\nSearching for: '{search_term}'")
            search_url = f"https://qspace.library.queensu.ca/search?query={search_term}"
            downloader.driver.get(search_url)
            time.sleep(5)
            
            print(f"Search page - URL: {downloader.driver.current_url}")
            print(f"Search page - Title: {downloader.driver.title}")
            
            # Look for exam links using Selenium WebElements
            exam_links = downloader.driver.find_elements("css selector", "a[href*='/items/']")
            
            if exam_links:
                print(f"Found {len(exam_links)} results for '{search_term}'")
                
                for exam_link in exam_links:
                    try:
                        exam_title = exam_link.text.strip()
                        exam_url = exam_link.get_attribute('href')
                        
                        if not exam_title or len(exam_title) < 3:
                            continue
                            
                        print(f"Checking exam: '{exam_title}'")
                        
                        # Check if this is a Commerce 101 exam (more flexible search)
                        if ("COMM101" in exam_title.upper() or 
                            "COMM 101" in exam_title.upper() or 
                            "COMMERCE 101" in exam_title.upper() or
                            ("COMM" in exam_title.upper() and "101" in exam_title)):
                            
                            print(f"\n[FOUND] Commerce 101 Exam: '{exam_title}'")
                            
                            # Navigate to the exam page
                            downloader.driver.get(exam_url)
                            time.sleep(5)
                            
                            print(f"Exam page - URL: {downloader.driver.current_url}")
                            print(f"Exam page - Title: {downloader.driver.title}")
                            
                            # Look for download links
                            download_links = downloader.driver.find_elements("css selector", "a[href*='/bitstreams/'][href*='/download']")
                            
                            if download_links:
                                print(f"Found {len(download_links)} download links!")
                                
                                # Download all files for this exam
                                for i, download_link in enumerate(download_links):
                                    try:
                                        download_url = download_link.get_attribute('href')
                                        download_title = download_link.text.strip()
                                        
                                        print(f"\nDownloading file {i+1}: {download_title}")
                                        print(f"Download URL: {download_url}")
                                        
                                        # Create filename
                                        filename = f"COMM101_{len(downloaded_files)+1}.pdf"
                                        if download_title and ".pdf" in download_title.lower():
                                            # Clean filename
                                            clean_title = download_title.split("(")[0].strip()
                                            clean_title = clean_title.replace(" ", "_").replace("/", "_")
                                            filename = f"COMM101_{clean_title}.pdf"
                                        
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
                                            print(f"[SUCCESS] File downloaded: {filename}")
                                            print(f"File size: {file_size} bytes")
                                            print(f"File path: {file_path}")
                                            
                                            downloaded_files.append({
                                                'filename': filename,
                                                'path': file_path,
                                                'size': file_size,
                                                'title': exam_title
                                            })
                                            
                                        except Exception as e:
                                            print(f"Download failed: {e}")
                                            continue
                                            
                                    except Exception as e:
                                        print(f"Error processing download link: {e}")
                                        continue
                            else:
                                print("No download links found for this exam")
                    except Exception as e:
                        print(f"Error processing exam: {e}")
                        continue
            else:
                print(f"No results found for '{search_term}'")
        
        # Summary
        print(f"\n" + "="*60)
        print(f"COMMERCE 101 DOWNLOAD SUMMARY")
        print(f"="*60)
        print(f"Total files downloaded: {len(downloaded_files)}")
        
        if downloaded_files:
            print(f"\nDownloaded files:")
            for i, file_info in enumerate(downloaded_files, 1):
                print(f"  {i}. {file_info['filename']} ({file_info['size']} bytes)")
                print(f"     From: {file_info['title']}")
                print(f"     Path: {file_info['path']}")
        else:
            print(f"\nNo Commerce 101 exams were found or downloaded.")
            print(f"Searched terms: {', '.join(search_terms)}")
        
        return len(downloaded_files) > 0
        
    finally:
        downloader.close()

if __name__ == "__main__":
    download_commerce101_midterms()
