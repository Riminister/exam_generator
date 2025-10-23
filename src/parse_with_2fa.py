# Queen's University Exam Bank Downloader with Microsoft 2FA Support
# Handles Microsoft Azure AD authentication with 2FA
import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin, urlparse
import getpass

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class QueensExamBankWith2FA:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://qspace.library.queensu.ca"
        self.exam_collection_url = "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def setup_browser(self, headless=False):
        """Setup browser for Microsoft login"""
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available")
            return False
        
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            # Important: Don't disable cookies for Microsoft login
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup browser: {e}")
            return False
    
    def login_with_microsoft_2fa(self, username=None, password=None):
        """Login to Queen's using Microsoft Azure AD with 2FA"""
        if not self.driver:
            if not self.setup_browser(headless=False):  # Must be visible for 2FA
                return False
        
        if not username:
            username = input("Enter your Queen's NetID: ")
        if not password:
            password = getpass.getpass("Enter your password: ")
        
        try:
            print("Starting Microsoft Azure AD login process...")
            print("This will open a browser window for you to complete 2FA.")
            
            # Navigate to QSpace login
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            print("Looking for Microsoft login button...")
            
            # Look for Microsoft login button/link
            microsoft_selectors = [
                "a[href*='microsoft']",
                "a[href*='azure']",
                "button:contains('Microsoft')",
                "button:contains('Sign in with Microsoft')",
                "a:contains('Microsoft')",
                "a:contains('Sign in with Microsoft')",
                ".microsoft-login",
                "[data-test='microsoft-login']"
            ]
            
            microsoft_button = None
            for selector in microsoft_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found Microsoft login button: {selector}")
                    microsoft_button = button
                    break
                except NoSuchElementException:
                    continue
            
            if not microsoft_button:
                print("No Microsoft login button found. Checking if already on Microsoft login page...")
                current_url = self.driver.current_url
                if "microsoftonline.com" in current_url:
                    print("Already on Microsoft login page, proceeding with credentials...")
                else:
                    print("Current page content:")
                    print(self.driver.page_source[:500])
                    return False
            
            # Click Microsoft login button if found
            if microsoft_button:
                microsoft_button.click()
                time.sleep(3)
            
            print("On Microsoft login page, entering credentials...")
            
            # Find username field (email)
            username_field = None
            username_selectors = [
                "input[type='email']",
                "input[name='loginfmt']",
                "input[id='i0116']",
                "input[placeholder*='netid@queensu.ca']"
            ]
            
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found username field: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                print("Could not find username field")
                return False
            
            # Enter username
            username_field.clear()
            username_field.send_keys(f"{username}@queensu.ca")  # Add @queensu.ca domain
            print("Username entered")
            
            # Find and click Next button
            next_button = None
            next_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Next']",
                "button:contains('Next')",
                "#idSIButton9"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found Next button: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if next_button:
                next_button.click()
                time.sleep(3)
            
            # Find password field
            password_field = None
            password_selectors = [
                "input[type='password']",
                "input[name='passwd']",
                "input[id='i0118']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found password field: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print("Could not find password field")
                return False
            
            # Enter password
            password_field.clear()
            password_field.send_keys(password)
            print("Password entered")
            
            # Find and click Sign In button
            signin_button = None
            signin_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Sign in']",
                "button:contains('Sign in')",
                "#idSIButton9"
            ]
            
            for selector in signin_selectors:
                try:
                    signin_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found Sign In button: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if signin_button:
                signin_button.click()
                print("Sign In button clicked")
            else:
                print("No Sign In button found, trying Enter key")
                password_field.send_keys(Keys.RETURN)
            
            # Wait for 2FA prompt
            print("\n" + "="*60)
            print("IMPORTANT: Complete 2FA authentication in the browser window!")
            print("This may include:")
            print("- SMS code to your phone")
            print("- Authenticator app notification")
            print("- Email verification")
            print("- Other 2FA methods")
            print("="*60)
            
            # Wait for user to complete 2FA
            print("\nWaiting for you to complete 2FA authentication...")
            print("The browser window will remain open for you to complete the process.")
            
            # Wait for redirect back to QSpace
            max_wait_time = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Check if we're back on QSpace
                if "qspace.library.queensu.ca" in current_url and "login" not in current_url:
                    print(f"\n[SUCCESS] Login completed! Redirected to: {current_url}")
                    return True
                
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
                    if error_elements:
                        error_text = error_elements[0].text
                        if error_text and "error" in error_text.lower():
                            print(f"[ERROR] Login error detected: {error_text}")
                            return False
                except:
                    pass
                
                time.sleep(2)
            
            print(f"\n[WARNING] Login timeout after {max_wait_time} seconds")
            print("Please check the browser window and complete 2FA if not already done.")
            
            # Final check
            current_url = self.driver.current_url
            if "qspace.library.queensu.ca" in current_url and "login" not in current_url:
                print("[SUCCESS] Login appears to be successful!")
                return True
            else:
                print("[ERROR] Login may have failed or timed out")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error during Microsoft login: {e}")
            return False
    
    def get_exam_list_after_login(self, course_code=None):
        """Get exam list after successful login"""
        if not self.driver:
            print("[ERROR] No browser session")
            return []
        
        try:
            print("Navigating to exam collection...")
            self.driver.get(self.exam_collection_url)
            time.sleep(5)
            
            # Check if we can see exam content now
            page_source = self.driver.page_source
            if "no items to show" in page_source.lower():
                print("[WARNING] Still seeing 'No items to show'")
                return []
            
            # Look for exam links
            exam_selectors = [
                "a[href*='/items/']",
                "a[href*='/handle/']",
                ".item-list-entry a",
                "ds-item-list-entry a"
            ]
            
            exams = []
            for selector in exam_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Found {len(elements)} exam elements with: {selector}")
                        
                        for element in elements:
                            try:
                                title = element.text.strip()
                                href = element.get_attribute('href')
                                
                                if title and href and len(title) > 3:
                                    exams.append({
                                        'title': title,
                                        'url': href,
                                        'course': self.extract_course_code(title)
                                    })
                            except Exception as e:
                                continue
                        
                        if exams:
                            break
                except Exception as e:
                    continue
            
            # Filter by course code
            if course_code and exams:
                exams = [exam for exam in exams if course_code.upper() in exam['course'].upper()]
            
            return exams
            
        except Exception as e:
            print(f"[ERROR] Error getting exam list: {e}")
            return []
    
    def extract_course_code(self, title):
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
    
    def download_exam(self, exam_url, download_dir="downloads"):
        """Download a specific exam"""
        if not self.driver:
            print("[ERROR] No browser session")
            return False
        
        try:
            os.makedirs(download_dir, exist_ok=True)
            
            print(f"Loading exam page: {exam_url}")
            self.driver.get(exam_url)
            time.sleep(3)
            
            # Look for download links
            download_selectors = [
                "a[href*='/bitstream/']",
                ".bitstream-link",
                "a[href*='download']"
            ]
            
            downloaded_files = []
            
            for selector in download_selectors:
                try:
                    download_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for link in download_links:
                        try:
                            file_url = link.get_attribute('href')
                            filename = link.text.strip() or f"exam_file_{len(downloaded_files)}.pdf"
                            
                            # Clean filename
                            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                            
                            print(f"Downloading: {filename}")
                            
                            # Copy cookies from selenium to requests session
                            cookies = self.driver.get_cookies()
                            for cookie in cookies:
                                self.session.cookies.set(cookie['name'], cookie['value'])
                            
                            file_response = self.session.get(file_url)
                            file_response.raise_for_status()
                            
                            # Save file
                            file_path = os.path.join(download_dir, filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_response.content)
                            
                            downloaded_files.append(file_path)
                            print(f"Downloaded: {file_path}")
                            
                        except Exception as e:
                            print(f"Error downloading file: {e}")
                            continue
                    
                    if downloaded_files:
                        break
                        
                except Exception as e:
                    continue
            
            return downloaded_files
            
        except Exception as e:
            print(f"[ERROR] Error downloading exam: {e}")
            return False
    
    def interactive_download(self):
        """Interactive exam download with 2FA"""
        print("Queen's University Exam Bank Downloader (with Microsoft 2FA)")
        print("=" * 70)
        
        if not self.setup_browser(headless=False):
            return
        
        try:
            # Login with 2FA
            if not self.login_with_microsoft_2fa("22yyq", "7GearGlue&"):
                print("Login failed. Cannot proceed.")
                return
            
            # Get course filter
            course_filter = input("\nEnter course code to filter (e.g., ELEC371) or press Enter for all: ").strip()
            
            # Get exam list
            print("Fetching available exams...")
            exams = self.get_exam_list_after_login(course_filter)
            
            if not exams:
                print("No exams found.")
                return
            
            # Display exams
            print(f"\nFound {len(exams)} exams:")
            for i, exam in enumerate(exams, 1):
                print(f"{i}. {exam['title']} ({exam['course']})")
            
            # Select exam
            while True:
                try:
                    choice = input(f"\nSelect exam to download (1-{len(exams)}) or 'q' to quit: ").strip()
                    if choice.lower() == 'q':
                        return
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(exams):
                        selected_exam = exams[choice_num - 1]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Download selected exam
            print(f"\nDownloading: {selected_exam['title']}")
            downloaded_files = self.download_exam(selected_exam['url'])
            
            if downloaded_files:
                print(f"\nSuccessfully downloaded {len(downloaded_files)} file(s)!")
            else:
                print("Download failed.")
                
        finally:
            self.close()
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    if SELENIUM_AVAILABLE:
        downloader = QueensExamBankWith2FA()
        downloader.interactive_download()
    else:
        print("Selenium not available. Please install with:")
        print("pip install selenium")
