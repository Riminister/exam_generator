# Queen's University Exam Bank Downloader with Selenium Support
# Downloads exams from QSpace exam bank collection (JavaScript-enabled)
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
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available. Please install with: pip install selenium")
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup Selenium: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            return False
    
    def get_exam_list_selenium(self, course_code=None):
        """Get list of available exams using Selenium"""
        if not self.driver:
            if not self.setup_selenium():
                return []
        
        try:
            print("Loading exam collection page with JavaScript...")
            self.driver.get(self.exam_collection_url)
            
            # Wait for content to load
            wait = WebDriverWait(self.driver, 10)
            
            # Look for exam items - try different selectors
            exam_selectors = [
                "ds-item-list-entry",
                ".item-list-entry",
                "[data-test='item-list-entry']",
                "a[href*='/items/']",
                "a[href*='/handle/']"
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
                                
                                if title and href:
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
            
            # If no specific exam elements found, look for any links
            if not exams:
                print("Looking for any links on the page...")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                print(f"Found {len(all_links)} total links")
                
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if href and text and ('item' in href or 'handle' in href):
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
            print(f"[ERROR] Error getting exam list with Selenium: {e}")
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
    
    def download_exam_selenium(self, exam_url, download_dir="downloads"):
        """Download a specific exam using Selenium"""
        if not self.driver:
            if not self.setup_selenium():
                return False
        
        try:
            os.makedirs(download_dir, exist_ok=True)
            
            print(f"Loading exam page: {exam_url}")
            self.driver.get(exam_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for download links
            download_selectors = [
                "a[href*='/bitstream/']",
                ".bitstream-link",
                "[data-test='bitstream-link']",
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
                            
                            # Download using requests session
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
    
    def close(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()

def test_selenium_access():
    """Test accessing the exam collection with Selenium"""
    print("Testing QSpace Access with Selenium")
    print("=" * 40)
    
    downloader = QueensExamBankDownloader()
    
    try:
        if not downloader.setup_selenium():
            return False
        
        print("Loading exam collection page...")
        downloader.driver.get(downloader.exam_collection_url)
        
        # Wait a bit for JavaScript to load
        time.sleep(5)
        
        print(f"Page title: {downloader.driver.title}")
        print(f"Current URL: {downloader.driver.current_url}")
        
        # Get page source after JavaScript execution
        page_source = downloader.driver.page_source
        
        # Save the JavaScript-rendered HTML
        with open('qspace_page_selenium.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("JavaScript-rendered HTML saved to 'qspace_page_selenium.html'")
        
        # Try to find exam links
        exams = downloader.get_exam_list_selenium()
        print(f"Found {len(exams)} exams")
        
        if exams:
            print("Sample exams:")
            for i, exam in enumerate(exams[:5]):
                print(f"  {i+1}. {exam['title']} ({exam['course']})")
        
        return len(exams) > 0
        
    except Exception as e:
        print(f"[ERROR] Error testing Selenium access: {e}")
        return False
    finally:
        downloader.close()

if __name__ == "__main__":
    if SELENIUM_AVAILABLE:
        test_selenium_access()
    else:
        print("Selenium not available. Please install with:")
        print("pip install selenium")
        print("\nAlso make sure ChromeDriver is installed:")
        print("https://chromedriver.chromium.org/")
