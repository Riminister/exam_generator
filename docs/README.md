# Queen's University Exam Bank Downloader

A Python script to download exams from the Queen's University QSpace exam bank collection.

## Features

- **Secure Login**: Handles Queen's NetID authentication
- **Course Filtering**: Filter exams by course code (e.g., ELEC371)
- **Interactive Interface**: User-friendly command-line interface
- **Batch Download**: Download multiple exams at once
- **Error Handling**: Robust error handling and validation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python parse.py
```

## Usage

### Interactive Mode (Recommended)
```bash
python parse.py
```

The script will:
1. Prompt for your Queen's NetID and password
2. Ask for a course code filter (optional)
3. Display available exams
4. Let you select which exam to download
5. Download the selected exam to the `downloads/` folder

### Programmatic Usage
```python
from parse import QueensExamBankDownloader

# Create downloader instance
downloader = QueensExamBankDownloader()

# Login
downloader.login("your_netid", "your_password")

# Get exams for a specific course
exams = downloader.get_exam_list("ELEC371")

# Download the first exam
if exams:
    downloader.download_exam(exams[0]['url'])
```

## Example Usage

See `example_usage.py` for more detailed examples of how to use the downloader programmatically.

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- lxml

## Notes

- Downloads are saved to the `downloads/` directory
- The script handles various file formats (PDF, DOC, etc.)
- Course codes are automatically extracted from exam titles
- Supports both spaced (ELEC 371) and non-spaced (ELEC371) course codes

## Troubleshooting

- **Login Issues**: Make sure you're using your correct Queen's NetID and password
- **No Exams Found**: Check if the course code is correct or try without a filter
- **Download Errors**: Ensure you have write permissions in the current directory

## Legal Notice

This tool is for educational purposes only. Please respect Queen's University's terms of service and copyright policies when downloading exam materials.
