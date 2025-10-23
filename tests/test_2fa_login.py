# Test Microsoft 2FA Login for Queen's Exam Bank
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

def test_microsoft_login():
    """Test Microsoft login with 2FA"""
    if not SELENIUM_AVAILABLE:
        print("Selenium not available")
        return False
    
    print("Testing Microsoft 2FA Login for Queen's Exam Bank")
    print("=" * 50)
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Navigating to QSpace login...")
        driver.get("https://qspace.library.queensu.ca/login")
        time.sleep(3)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Check if we're already on Microsoft login page
        if "microsoftonline.com" in driver.current_url:
            print("Already on Microsoft login page")
        else:
            print("Looking for Microsoft login button...")
            # Look for any link that might lead to Microsoft login
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute('href')
                if href and ('microsoft' in href.lower() or 'azure' in href.lower()):
                    print(f"Found Microsoft login link: {href}")
                    link.click()
                    time.sleep(3)
                    break
        
        print(f"After click - URL: {driver.current_url}")
        print(f"After click - Title: {driver.title}")
        
        # Now we should be on Microsoft login page
        if "microsoftonline.com" in driver.current_url:
            print("Successfully reached Microsoft login page!")
            
            # Find username field
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                print("Found username field")
                
                # Enter username
                username_field.clear()
                username_field.send_keys("22yyq@queensu.ca")
                print("Username entered")
                
                # Find Next button
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    next_button.click()
                    print("Next button clicked")
                    time.sleep(3)
                    
                    # Find password field
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                        print("Found password field")
                        
                        # Enter password
                        password_field.clear()
                        password_field.send_keys("7GearGlue&")
                        print("Password entered")
                        
                        # Find Sign In button
                        try:
                            signin_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                            signin_button.click()
                            print("Sign In button clicked")
                            
                            print("\n" + "="*60)
                            print("2FA AUTHENTICATION REQUIRED!")
                            print("Please complete 2FA in the browser window:")
                            print("- Check your phone for SMS code")
                            print("- Check your authenticator app")
                            print("- Check your email")
                            print("="*60)
                            
                            # Wait for 2FA completion
                            print("\nWaiting for 2FA completion...")
                            print("The browser will stay open for you to complete authentication.")
                            
                            # Wait up to 5 minutes
                            for i in range(300):  # 5 minutes
                                current_url = driver.current_url
                                if "qspace.library.queensu.ca" in current_url and "login" not in current_url:
                                    print(f"\n[SUCCESS] Login completed! Final URL: {current_url}")
                                    return True
                                time.sleep(1)
                            
                            print("\n[WARNING] Timeout waiting for 2FA completion")
                            return False
                            
                        except NoSuchElementException:
                            print("Sign In button not found")
                            return False
                            
                    except NoSuchElementException:
                        print("Password field not found")
                        return False
                        
                except NoSuchElementException:
                    print("Next button not found")
                    return False
                    
            except NoSuchElementException:
                print("Username field not found")
                return False
        else:
            print("Failed to reach Microsoft login page")
            return False
            
    except Exception as e:
        print(f"Error during login test: {e}")
        return False
    finally:
        print("Keeping browser open for inspection...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    test_microsoft_login()
