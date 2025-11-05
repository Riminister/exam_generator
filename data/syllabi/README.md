# Syllabus Files

Place course syllabus PDF files in this folder.

## File Naming Convention

Name files with the course code:
- `ECON212.pdf` - For ECON212 syllabus
- `ECON222.pdf` - For ECON222 syllabus
- `ECON110A.pdf` - For ECON110A syllabus

## How to Extract Topics

Run the extraction script:
```bash
py scripts/extract_syllabus_topics.py
```

This will:
1. Process all PDF files in this folder
2. Extract topics using OCR
3. Save topics to `data/syllabus_topics.json`
4. Make topics available in the Streamlit app dropdown

## Supported Formats

- PDF files (scanned or text-based)
- OCR will be used automatically for scanned PDFs
- Text extraction for searchable PDFs

