# Queen's University Exam Bank Downloader with Proper Authentication
# Downloads exams from QSpace exam bank collection with Selenium + Authentication
import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin, urlparse
import getpass

# Try to import selenium, install if not available
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
    print("Selenium not available. Install with: pip install selenium")

class QueensExamBankDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://qspace.library.queensu.ca"
        self.exam_collection_url = "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def setup_selenium(self, headless=True):
        """Setup Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available. Please install with: pip install selenium")
            return False
        
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup Selenium: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            return False
    
    def login_with_selenium(self, username=None, password=None):
        """Login to Queen's QSpace using Selenium"""
        if not self.driver:
            if not self.setup_selenium(headless=False):  # Show browser for login
                return False
        
        if not username:
            username = input("Enter your Queen's NetID: ")
        if not password:
            password = getpass.getpass("Enter your password: ")
        
        try:
            print("Navigating to login page...")
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for page to load
            time.sleep(3)
            
            print("Looking for login form...")
            
            # Try different login form selectors
            login_selectors = [
                "input[name='j_username']",
                "input[name='username']", 
                "input[name='netid']",
                "input[type='email']",
                "input[placeholder*='username']",
                "input[placeholder*='netid']"
            ]
            
            username_field = None
            for selector in login_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found username field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                print("Could not find username field. Checking page content...")
                page_source = self.driver.page_source
                with open('login_page.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print("Login page saved to 'login_page.html' for inspection")
                return False
            
            # Find password field
            password_selectors = [
                "input[name='j_password']",
                "input[name='password']",
                "input[type='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found password field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print("Could not find password field")
                return False
            
            # Enter credentials
            print("Entering credentials...")
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button
            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "button:contains('Log In')"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found login button with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                # Try pressing Enter on password field
                print("No login button found, trying Enter key...")
                password_field.send_keys(Keys.RETURN)
            else:
                login_button.click()
            
            # Wait for login to complete
            print("Waiting for login to complete...")
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for success indicators
            success_indicators = ["logout", "welcome", "dashboard", "profile"]
            failure_indicators = ["invalid", "incorrect", "failed", "error", "denied"]
            
            if any(indicator in page_source for indicator in success_indicators):
                print("[SUCCESS] Login successful!")
                return True
            elif any(indicator in page_source for indicator in failure_indicators):
                print("[ERROR] Login failed - invalid credentials")
                return False
            else:
                # Try to access the exam collection to verify
                print("Login status unclear, testing access to exam collection...")
                self.driver.get(self.exam_collection_url)
                time.sleep(3)
                
                # Check if we can see exam content now
                page_source = self.driver.page_source
                if "no items to show" not in page_source.lower():
                    print("[SUCCESS] Login appears successful - can access exam content")
                    return True
                else:
                    print("[ERROR] Login failed - still cannot access exam content")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Error during login: {e}")
            return False
    
    def get_exam_list_with_auth(self, course_code=None):
        """Get list of available exams after authentication"""
        if not self.driver:
            print("[ERROR] No browser session. Please login first.")
            return []
        
        try:
            print("Loading exam collection page...")
            self.driver.get(self.exam_collection_url)
            time.sleep(5)  # Wait for content to load
            
            # Check if we're still seeing "No items to show"
            page_source = self.driver.page_source
            if "no items to show" in page_source.lower():
                print("[WARNING] Still seeing 'No items to show'. Authentication may not be working.")
                return []
            
            # Look for exam items with various selectors
            exam_selectors = [
                "a[href*='/items/']",
                "a[href*='/handle/']",
                ".item-list-entry a",
                "ds-item-list-entry a",
                "[data-test='item-list-entry'] a"
            ]
            
            exams = []
            for selector in exam_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                title = element.text.strip()
                                href = element.get_attribute('href')
                                
                                if title and href and title != "View":
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
            
            # If no specific exam elements found, look for any links that might be exams
            if not exams:
                print("Looking for any exam-related links...")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if href and text and ('item' in href or 'handle' in href) and len(text) > 3:
                            exams.append({
                                'title': text,
                                'url': href,
                                'course': self.extract_course_code(text)
                            })
                    except Exception as e:
                        continue
            
            # Filter by course code if specified
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
    
    def download_exam_with_auth(self, exam_url, download_dir="downloads"):
        """Download a specific exam after authentication"""
        if not self.driver:
            print("[ERROR] No browser session. Please login first.")
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
                "[data-test='bitstream-link']",
                "a[href*='download']",
                "a:contains('Download')",
                "a:contains('View')"
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
                            
                            # Download using requests session (copy cookies from selenium)
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
    
    def interactive_download_with_auth(self):
        """Interactive mode for downloading exams with authentication"""
        print("Queen's University Exam Bank Downloader (Authenticated)")
        print("=" * 60)
        
        # Setup browser
        if not self.setup_selenium(headless=False):
            return
        
        try:
            # Login
            if not self.login_with_selenium():
                print("Login failed. Cannot proceed.")
                return
            
            # Get course filter
            course_filter = input("Enter course code to filter (e.g., ELEC371) or press Enter for all: ").strip()
            
            # Get exam list
            print("Fetching available exams...")
            exams = self.get_exam_list_with_auth(course_filter)
            
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
            downloaded_files = self.download_exam_with_auth(selected_exam['url'])
            
            if downloaded_files:
                print(f"\nSuccessfully downloaded {len(downloaded_files)} file(s)!")
            else:
                print("Download failed.")
                
        finally:
            self.close()
    
    def close(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()

def test_authenticated_access():
    """Test accessing the exam collection with authentication"""
    print("Testing QSpace Access with Authentication")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        if not downloader.setup_selenium(headless=False):
            return False
        
        # Login
        if not downloader.login_with_selenium():
            print("Login failed!")
            return False
        
        # Try to get exam list
        exams = downloader.get_exam_list_with_auth()
        print(f"Found {len(exams)} exams after authentication")
        
        if exams:
            print("Sample exams:")
            for i, exam in enumerate(exams[:5]):
                print(f"  {i+1}. {exam['title']} ({exam['course']})")
        
        return len(exams) > 0
        
    except Exception as e:
        print(f"[ERROR] Error testing authenticated access: {e}")
        return False
    finally:
        downloader.close()

if __name__ == "__main__":
    if SELENIUM_AVAILABLE:
        downloader = QueensExamBankDownloader()
        downloader.interactive_download_with_auth()
    else:
        print("Selenium not available. Please install with:")
        print("pip install selenium")
        print("\nAlso make sure ChromeDriver is installed:")
        print("https://chromedriver.chromium.org/")
