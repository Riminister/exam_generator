# Queen's University Exam Bank Downloader with Microsoft 2FA Support
# Downloads exams from QSpace exam bank collection
import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin, urlparse
import getpass

# Try to import selenium for Microsoft login
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Install with: pip install selenium webdriver-manager")

class QueensExamBankDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://qspace.library.queensu.ca"
        self.exam_collection_url = "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def setup_selenium(self, headless=False):
        """Setup Selenium WebDriver for Microsoft login"""
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available. Please install with: pip install selenium webdriver-manager")
            return False
        
        try:
            print("Setting up Chrome WebDriver with automatic driver management...")
            
            # Configure Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(10)
            print("Chrome WebDriver setup successful!")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup Selenium: {e}")
            print("This might be due to Chrome browser not being installed or network issues.")
            return False
    
    def login(self, username=None, password=None):
        """Login to Queen's QSpace system using Microsoft Azure AD with 2FA"""
        if not username:
            username = input("Enter your Queen's NetID: ")
        if not password:
            password = getpass.getpass("Enter your password: ")
        
        print(f"Attempting Microsoft Azure AD login for user: {username}")
        
        # Setup Selenium for Microsoft login
        if not self.setup_selenium(headless=False):  # Must be visible for 2FA
            return False
        
        try:
            print("Navigating to QSpace login page...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            print(f"Page title: {self.driver.title}")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if we're already on Microsoft login page
            if "microsoftonline.com" in self.driver.current_url:
                print("Already on Microsoft login page")
            else:
                print("Looking for Microsoft login button...")
                # Look for Microsoft login button/link
                microsoft_selectors = [
                    "a[href*='microsoft']",
                    "a[href*='azure']",
                    ".microsoft-login",
                    "[data-test*='microsoft']"
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
                
                if microsoft_button:
                    microsoft_button.click()
                    time.sleep(3)
                else:
                    print("No Microsoft login button found, checking if already redirected...")
            
            print("On Microsoft login page, entering credentials...")
            
            # Find username field (email)
            username_field = None
            username_selectors = [
                "input[name='loginfmt']",
                "input[type='email']",
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
            
            # Enter username with @queensu.ca domain
            username_field.clear()
            username_field.send_keys(f"{username}@queensu.ca")
            print("Username entered")
            
            # Find and click Next button
            next_button = None
            next_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Next']",
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
                    
                    # Copy cookies from selenium to requests session
                    cookies = self.driver.get_cookies()
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])
                    
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
                
                # Copy cookies from selenium to requests session
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                print("[ERROR] Login may have failed or timed out")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error during Microsoft login: {e}")
            return False
    
    def get_exam_list(self, course_code=None):
        """Get list of available exams"""
        try:
            response = self.session.get(self.exam_collection_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            exams = []
            
            # Look for exam links in the collection
            exam_links = soup.find_all('a', href=re.compile(r'/handle/'))
            
            for link in exam_links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                if href and title:
                    full_url = urljoin(self.base_url, href)
                    exams.append({
                        'title': title,
                        'url': full_url,
                        'course': self.extract_course_code(title)
                    })
            
            # Filter by course code if specified
            if course_code:
                exams = [exam for exam in exams if course_code.upper() in exam['course'].upper()]
            
            return exams
            
        except requests.RequestException as e:
            print(f"Error fetching exam list: {e}")
            return []
    
    def extract_course_code(self, title):
        """Extract course code from exam title"""
        # Common patterns for course codes
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
        try:
            # Create download directory
            os.makedirs(download_dir, exist_ok=True)
            
            # Get the exam page
            response = self.session.get(exam_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for download links
            download_links = soup.find_all('a', href=re.compile(r'/bitstream/'))
            
            if not download_links:
                print("No downloadable files found for this exam.")
                return False
            
            downloaded_files = []
            
            for link in download_links:
                file_url = urljoin(self.base_url, link['href'])
                filename = link.get_text(strip=True) or f"exam_file_{len(downloaded_files)}.pdf"
                
                # Clean filename
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                print(f"Downloading: {filename}")
                
                # Download the file
                file_response = self.session.get(file_url)
                file_response.raise_for_status()
                
                # Save file
                file_path = os.path.join(download_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                
                downloaded_files.append(file_path)
                print(f"Downloaded: {file_path}")
            
            return downloaded_files
            
        except requests.RequestException as e:
            print(f"Error downloading exam: {e}")
            return False
    
    def interactive_download(self):
        """Interactive mode for downloading exams"""
        print("Queen's University Exam Bank Downloader")
        print("=" * 50)
        
        # Login
        if not self.login():
            return
        
        # Get course filter
        course_filter = input("Enter course code to filter (e.g., ELEC371) or press Enter for all: ").strip()
        
        # Get exam list
        print("Fetching available exams...")
        exams = self.get_exam_list(course_filter)
        
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
    
    def close(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()

def analyze_page_structure():
    """Analyze the page structure to understand how exams are organized"""
    print("Analyzing QSpace Page Structure")
    print("=" * 40)
    
    downloader = QueensExamBankDownloader()
    
    try:
        response = downloader.session.get(downloader.exam_collection_url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No title found'
            print(f"Page title: {title}")
            
            # Look for different types of links
            all_links = soup.find_all('a', href=True)
            print(f"Total links found: {len(all_links)}")
            
            # Check for different link patterns
            patterns = {
                'handle': r'/handle/',
                'bitstream': r'/bitstream/',
                'item': r'/item/',
                'collection': r'/collection/',
                'community': r'/community/'
            }
            
            for pattern_name, pattern in patterns.items():
                matching_links = soup.find_all('a', href=re.compile(pattern))
                print(f"Links matching '{pattern_name}' pattern: {len(matching_links)}")
                
                if matching_links and len(matching_links) <= 5:  # Show all if 5 or fewer
                    for i, link in enumerate(matching_links):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"  {i+1}. {text} -> {href}")
                elif matching_links:
                    print(f"  Sample links:")
                    for i, link in enumerate(matching_links[:3]):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"    {i+1}. {text} -> {href}")
            
            # Look for any text that might indicate exam content
            page_text = soup.get_text().lower()
            exam_keywords = ['exam', 'test', 'midterm', 'final', 'quiz', 'assignment']
            found_keywords = [kw for kw in exam_keywords if kw in page_text]
            print(f"Exam-related keywords found: {found_keywords}")
            
            # Save the HTML for manual inspection
            with open('qspace_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Page HTML saved to 'qspace_page.html' for manual inspection")
            
            return True
        else:
            print(f"[ERROR] Access denied (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error accessing exam collection: {e}")
        return False

def test_access_without_login():
    """Test if we can access the exam collection without login"""
    print("Queen's QSpace Access Test")
    print("=" * 30)
    
    downloader = QueensExamBankDownloader()
    
    # Test accessing the exam collection page without login
    print("Testing access to exam collection without login...")
    try:
        response = downloader.session.get(downloader.exam_collection_url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS] Successfully accessed exam collection page!")
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No title found'
            print(f"Page title: {title}")
            
            # Check if there are any exam links
            exam_links = soup.find_all('a', href=re.compile(r'/handle/'))
            print(f"Found {len(exam_links)} potential exam links")
            
            if exam_links:
                print("Sample exam links:")
                for i, link in enumerate(exam_links[:3]):
                    print(f"  {i+1}. {link.get_text(strip=True)}")
            
            return True
        else:
            print(f"[ERROR] Access denied (status: {response.status_code})")
            print("Authentication may be required.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error accessing exam collection: {e}")
        return False

def test_login_only():
    """Test function to verify login works"""
    print("\nQueen's QSpace Login Test")
    print("=" * 30)
    
    downloader = QueensExamBankDownloader()
    
    # Test login
    print("Testing login to QSpace...")
    success = downloader.login()
    
    if success:
        print("✅ Login successful!")
        
        # Test accessing the exam collection page
        print("\nTesting access to exam collection...")
        try:
            response = downloader.session.get(downloader.exam_collection_url)
            response.raise_for_status()
            print("✅ Successfully accessed exam collection page!")
            print(f"Page title: {BeautifulSoup(response.content, 'html.parser').title.string if BeautifulSoup(response.content, 'html.parser').title else 'No title found'}")
        except Exception as e:
            print(f"❌ Error accessing exam collection: {e}")
    else:
        print("❌ Login failed!")

def main():
    downloader = QueensExamBankDownloader()
    downloader.interactive_download()

def test_browse_methods():
    """Test different browse methods to find exams"""
    print("Testing Different Browse Methods")
    print("=" * 40)
    
    downloader = QueensExamBankDownloader()
    
    # Different browse URLs to try
    browse_urls = {
        "Recent Submissions": "https://qspace.library.queensu.ca/collections/cab1b9d2-6777-45cd-b56d-78c608468888",
        "By Title": "https://qspace.library.queensu.ca/browse/title?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
        "By Issue Date": "https://qspace.library.queensu.ca/browse/dateissued?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
        "By Author": "https://qspace.library.queensu.ca/browse/author?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
        "By Subject": "https://qspace.library.queensu.ca/browse/subject?scope=cab1b9d2-6777-45cd-b56d-78c608468888",
        "By Type": "https://qspace.library.queensu.ca/browse/type?scope=cab1b9d2-6777-45cd-b56d-78c608468888"
    }
    
    for method, url in browse_urls.items():
        print(f"\nTesting {method}:")
        try:
            response = downloader.session.get(url)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for exam items
                exam_links = soup.find_all('a', href=re.compile(r'/items/'))
                print(f"  Found {len(exam_links)} exam links")
                
                if exam_links:
                    print("  Sample exams:")
                    for i, link in enumerate(exam_links[:3]):
                        title = link.get_text(strip=True)
                        href = link.get('href')
                        print(f"    {i+1}. {title}")
                        print(f"       URL: {href}")
                else:
                    # Check if there's a "No items" message
                    no_items = soup.find(text=re.compile(r'no items', re.I))
                    if no_items:
                        print("  No items found in this browse method")
                    else:
                        print("  No exam links found")
            else:
                print(f"  Failed to access: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")

def test_login_functionality():
    """Test the login functionality with your credentials"""
    print("\nTesting Microsoft 2FA Login Functionality")
    print("=" * 50)
    
    downloader = QueensExamBankDownloader()
    
    try:
        print("This will test the Microsoft Azure AD login with 2FA.")
        print("Your credentials: 22yyq@queensu.ca / 7GearGlue&")
        print("The browser will open for you to complete 2FA.")
        
        proceed = input("\nDo you want to test login? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Login test cancelled.")
            return False
        
        # Use your specific credentials
        success = downloader.login("22yyq", "7GearGlue&")
        
        if success:
            print("\n[SUCCESS] Microsoft 2FA login test passed!")
            print("Now testing access to exam collection after login...")
            
            # Test accessing exam collection after login
            try:
                response = downloader.session.get(downloader.exam_collection_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for exam links
                    exam_links = soup.find_all('a', href=re.compile(r'/items/'))
                    print(f"Found {len(exam_links)} exam links after login")
                    
                    if exam_links:
                        print("Sample exams found:")
                        for i, link in enumerate(exam_links[:3]):
                            title = link.get_text(strip=True)
                            href = link.get('href')
                            print(f"  {i+1}. {title}")
                            print(f"     URL: {href}")
                        return True
                    else:
                        print("Still no exam links found after login.")
                        print("This might indicate the collection is empty or requires additional permissions.")
                        return False
                else:
                    print(f"Failed to access exam collection after login: {response.status_code}")
                    return False
            except Exception as e:
                print(f"Error accessing exam collection after login: {e}")
                return False
        else:
            print("\n[ERROR] Microsoft 2FA login test failed!")
            return False
    finally:
        downloader.close()

if __name__ == "__main__":
    # First test if we can access without login
    can_access = test_access_without_login()
    
    if can_access:
        print("\nGreat! No authentication required.")
        print("\nNow testing different browse methods...")
        test_browse_methods()
        
        # Since we found no exams without login, test with authentication
        print("\n" + "="*60)
        print("Since no exams were found without login, let's test with authentication:")
        test_login_functionality()
    else:
        print("\nAuthentication appears to be required.")
        print("To test login functionality, run:")
        print("  python -c \"from parse import QueensExamBankDownloader; QueensExamBankDownloader().login('your_netid', 'your_password')\"")
