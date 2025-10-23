# Debug QSpace Login Page
import time
from parse import QueensExamBankDownloader

def debug_login_page():
    """Debug what's actually on the login page"""
    print("Debugging QSpace Login Page")
    print("=" * 40)
    
    downloader = QueensExamBankDownloader()
    
    try:
        if not downloader.setup_selenium(headless=False):
            return
        
        print("Navigating to QSpace login...")
        downloader.driver.get("https://qspace.library.queensu.ca/login")
        time.sleep(5)
        
        print(f"Page title: {downloader.driver.title}")
        print(f"Current URL: {downloader.driver.current_url}")
        
        # Save page source
        page_source = downloader.driver.page_source
        with open('login_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Login page saved to 'login_debug.html'")
        
        # Look for all links
        links = downloader.driver.find_elements("tag name", "a")
        print(f"\nFound {len(links)} links on the page:")
        
        for i, link in enumerate(links[:10]):  # Show first 10
            try:
                text = link.text.strip()
                href = link.get_attribute('href')
                if text:
                    print(f"  {i+1}. '{text}' -> {href}")
            except:
                continue
        
        # Look for buttons
        buttons = downloader.driver.find_elements("tag name", "button")
        print(f"\nFound {len(buttons)} buttons on the page:")
        
        for i, button in enumerate(buttons[:10]):  # Show first 10
            try:
                text = button.text.strip()
                if text:
                    print(f"  {i+1}. '{text}'")
            except:
                continue
        
        # Look for input fields
        inputs = downloader.driver.find_elements("tag name", "input")
        print(f"\nFound {len(inputs)} input fields on the page:")
        
        for i, input_field in enumerate(inputs):
            try:
                field_type = input_field.get_attribute('type') or 'text'
                field_name = input_field.get_attribute('name') or 'no-name'
                field_placeholder = input_field.get_attribute('placeholder') or 'no-placeholder'
                print(f"  {i+1}. Type: {field_type}, Name: {field_name}, Placeholder: {field_placeholder}")
            except:
                continue
        
        print("\nKeeping browser open for 10 seconds to inspect...")
        time.sleep(10)
        
    finally:
        downloader.close()

if __name__ == "__main__":
    debug_login_page()
