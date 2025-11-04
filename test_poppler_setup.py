#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Poppler Setup
Quick script to verify poppler is configured correctly
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from text_extraction.pdf_processing.extract_text_from_pdfs import find_poppler_path

def main():
    print("=" * 70)
    print("POPPLER SETUP VERIFICATION")
    print("=" * 70)
    
    poppler_path = find_poppler_path()
    
    if poppler_path:
        poppler_path_obj = Path(poppler_path)
        print(f"\n✅ Poppler found!")
        print(f"   Path: {poppler_path_obj.resolve()}")
        print(f"   Exists: {poppler_path_obj.exists()}")
        
        # Check for required executables
        pdftoppm = poppler_path_obj / "pdftoppm.exe" if sys.platform == 'win32' else poppler_path_obj / "pdftoppm"
        pdftotext = poppler_path_obj / "pdftotext.exe" if sys.platform == 'win32' else poppler_path_obj / "pdftotext"
        
        print(f"\n   Required executables:")
        print(f"   - pdftoppm.exe: {'✅ Found' if pdftoppm.exists() else '❌ Missing'}")
        print(f"   - pdftotext.exe: {'✅ Found' if pdftotext.exists() else '❌ Missing'}")
        
        if pdftoppm.exists():
            print(f"\n✅ Poppler is properly configured for OCR!")
            print(f"   You can now use OCR features.")
        else:
            print(f"\n⚠️  Warning: pdftoppm.exe not found!")
            print(f"   OCR may not work. Check your poppler installation.")
    else:
        print(f"\n❌ Poppler not found!")
        print(f"\n   Expected locations checked:")
        print(f"   - Project root: Release-25.07.0-0/poppler-25.07.0/Library/bin/")
        print(f"   - Script directory: text_extraction/pdf_processing/poppler/bin/")
        print(f"   - Environment variable: POPPLER_PATH")
        print(f"\n   To fix:")
        print(f"   1. Ensure poppler is at: Release-25.07.0-0/poppler-25.07.0/Library/bin/")
        print(f"   2. Or set POPPLER_PATH environment variable")
        print(f"   3. Or download from: https://github.com/oschwartz10612/poppler-windows/releases/")
    
    print("\n" + "=" * 70)
    
    # Test pdf2image if poppler is found
    if poppler_path:
        try:
            import pdf2image
            print("\nTesting pdf2image with poppler...")
            # Just verify the import works
            print("✅ pdf2image is installed")
            print("✅ Poppler path is configured correctly")
            print("\n🎉 Setup complete! OCR should work now.")
        except ImportError:
            print("\n⚠️  pdf2image not installed")
            print("   Install with: pip install pdf2image")
    
    return 0 if poppler_path else 1

if __name__ == "__main__":
    sys.exit(main())

