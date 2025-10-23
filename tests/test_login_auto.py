# Test Microsoft 2FA Login for Queen's Exam Bank
# This script automatically tests the login with your credentials

import re
from parse import QueensExamBankDownloader

def test_login_automatically():
    """Test Microsoft 2FA login automatically"""
    print("Testing Microsoft 2FA Login for Queen's Exam Bank")
    print("=" * 60)
    print("Your credentials: 22yyq@queensu.ca / 7GearGlue&")
    print("The browser will open for you to complete 2FA.")
    print("=" * 60)
    
    downloader = QueensExamBankDownloader()
    
    try:
        # Use your specific credentials
        success = downloader.login("22yyq", "7GearGlue&")
        
        if success:
            print("\n[SUCCESS] Microsoft 2FA login test passed!")
            print("Now testing access to exam collection after login...")
            
            # Test accessing exam collection after login
            try:
                response = downloader.session.get(downloader.exam_collection_url)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
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
    test_login_automatically()
