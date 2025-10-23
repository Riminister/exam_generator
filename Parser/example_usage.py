#!/usr/bin/env python3
"""
Example usage of the Queen's Exam Bank Downloader
"""

from parse import QueensExamBankDownloader

def download_specific_course_exam():
    """Example: Download a specific course exam"""
    downloader = QueensExamBankDownloader()
    
    # Login with credentials
    if not downloader.login("your_netid", "your_password"):
        print("Login failed!")
        return
    
    # Get exams for a specific course
    exams = downloader.get_exam_list("ELEC371")
    
    if exams:
        # Download the first exam found
        exam = exams[0]
        print(f"Downloading: {exam['title']}")
        downloaded_files = downloader.download_exam(exam['url'])
        
        if downloaded_files:
            print(f"Downloaded {len(downloaded_files)} files successfully!")
        else:
            print("Download failed!")
    else:
        print("No exams found for ELEC371")

def download_all_exams():
    """Example: Download all available exams"""
    downloader = QueensExamBankDownloader()
    
    if not downloader.login():
        return
    
    exams = downloader.get_exam_list()  # No course filter
    
    print(f"Found {len(exams)} exams")
    for exam in exams[:5]:  # Download first 5 as example
        print(f"Downloading: {exam['title']}")
        downloader.download_exam(exam['url'])

if __name__ == "__main__":
    # Run interactive mode
    downloader = QueensExamBankDownloader()
    downloader.interactive_download()
