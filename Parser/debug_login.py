# Debug version to fix Queen's login form detection
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

class QueensLoginDebugger:
    def __init__(self):
        self.driver = None
    
    def setup_browser(self):
        """Setup browser with debugging"""
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available")
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            # Don't run headless so we can see what's happening
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup browser: {e}")
            return False
    
    def debug_login_page(self):
        """Debug the login page to find the correct form fields"""
        print("Debugging Queen's Login Page")
        print("=" * 40)
        
        if not self.setup_browser():
            return False
        
        try:
            print("Navigating to Queen's login page...")
            self.driver.get("https://qspace.library.queensu.ca/login")
            time.sleep(5)
            
            print(f"Page title: {self.driver.title}")
            print(f"Current URL: {self.driver.current_url}")
            
            # Save the page source for inspection
            page_source = self.driver.page_source
            with open('queens_login_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("Login page saved to 'queens_login_debug.html'")
            
            # Look for all input fields
            print("\nLooking for all input fields...")
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(all_inputs)} input fields:")
            
            for i, input_field in enumerate(all_inputs):
                try:
                    field_type = input_field.get_attribute('type') or 'text'
                    field_name = input_field.get_attribute('name') or 'no-name'
                    field_id = input_field.get_attribute('id') or 'no-id'
                    field_placeholder = input_field.get_attribute('placeholder') or 'no-placeholder'
                    field_class = input_field.get_attribute('class') or 'no-class'
                    
                    print(f"  {i+1}. Type: {field_type}, Name: {field_name}, ID: {field_id}")
                    print(f"     Placeholder: {field_placeholder}, Class: {field_class}")
                except Exception as e:
                    print(f"  {i+1}. Error reading field: {e}")
            
            # Look for forms
            print("\nLooking for forms...")
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"Found {len(forms)} forms:")
            
            for i, form in enumerate(forms):
                try:
                    form_action = form.get_attribute('action') or 'no-action'
                    form_method = form.get_attribute('method') or 'no-method'
                    form_id = form.get_attribute('id') or 'no-id'
                    form_class = form.get_attribute('class') or 'no-class'
                    
                    print(f"  {i+1}. Action: {form_action}, Method: {form_method}")
                    print(f"     ID: {form_id}, Class: {form_class}")
                except Exception as e:
                    print(f"  {i+1}. Error reading form: {e}")
            
            # Try to find username and password fields specifically
            print("\nLooking for username/password fields...")
            
            # Common username field patterns
            username_patterns = [
                "input[type='email']",
                "input[placeholder*='Email address']",
                "input[placeholder*='email']",
                "input[name='j_username']",
                "input[name='username']",
                "input[name='netid']",
                "input[name='user']",
                "input[placeholder*='username']",
                "input[placeholder*='netid']",
                "input[id*='username']",
                "input[id*='netid']",
                "input[id*='user']"
            ]
            
            username_field = None
            for pattern in username_patterns:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, pattern)
                    print(f"Found username field: {pattern}")
                    username_field = field
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                print("No username field found with common patterns")
            
            # Common password field patterns
            password_patterns = [
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "input[name='j_password']",
                "input[name='password']",
                "input[name='pass']",
                "input[id*='password']",
                "input[id*='pass']"
            ]
            
            password_field = None
            for pattern in password_patterns:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, pattern)
                    print(f"Found password field: {pattern}")
                    password_field = field
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print("No password field found with common patterns")
            
            # Try to login if we found both fields
            if username_field and password_field:
                print("\nAttempting login with found fields...")
                try:
                    username_field.clear()
                    username_field.send_keys("22yyq")
                    print("Username entered successfully")
                    
                    password_field.clear()
                    password_field.send_keys("7GearGlue&")
                    print("Password entered successfully")
                    
                    # Look for submit button
                    submit_patterns = [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button:contains('Login')",
                        "button:contains('Sign In')",
                        "button:contains('Log In')",
                        "input[value*='Login']",
                        "input[value*='Sign In']"
                    ]
                    
                    submit_button = None
                    for pattern in submit_patterns:
                        try:
                            button = self.driver.find_element(By.CSS_SELECTOR, pattern)
                            print(f"Found submit button: {pattern}")
                            submit_button = button
                            break
                        except NoSuchElementException:
                            continue
                    
                    if submit_button:
                        submit_button.click()
                        print("Submit button clicked")
                    else:
                        print("No submit button found, trying Enter key")
                        password_field.send_keys(Keys.RETURN)
                    
                    # Wait and check result
                    time.sleep(5)
                    print(f"After login attempt - URL: {self.driver.current_url}")
                    print(f"After login attempt - Title: {self.driver.title}")
                    
                    # Check if login was successful
                    page_source = self.driver.page_source.lower()
                    if "logout" in page_source or "welcome" in page_source:
                        print("[SUCCESS] Login appears successful!")
                        return True
                    elif "invalid" in page_source or "incorrect" in page_source:
                        print("[ERROR] Login failed - invalid credentials")
                        return False
                    else:
                        print("[WARNING] Login status unclear")
                        return False
                        
                except Exception as e:
                    print(f"Error during login attempt: {e}")
                    return False
            else:
                print("Cannot attempt login - missing username or password field")
                return False
                
        except Exception as e:
            print(f"Error during debugging: {e}")
            return False
        finally:
            if self.driver:
                print("Keeping browser open for 10 seconds to inspect...")
                time.sleep(10)
                self.driver.quit()

if __name__ == "__main__":
    debugger = QueensLoginDebugger()
    debugger.debug_login_page()
