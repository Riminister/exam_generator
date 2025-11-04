#!/usr/bin/env python3
"""
Clean Up Project - Remove unnecessary files and organize structure
"""

import shutil
from pathlib import Path
import json


def cleanup():
    """Clean up project"""
    print("=" * 70)
    print("PROJECT CLEANUP")
    print("=" * 70)
    print()
    
    # Create necessary directories
    directories = [
        'scripts',
        'tests',
        'outputs',
        'docs/guides',
        'generated_graphs',
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    print()
    print("✅ Cleanup complete!")
    print()
    print("Next steps:")
    print("1. Run: python scripts/organize_project.py --dry-run")
    print("2. Review changes")
    print("3. Run: python scripts/organize_project.py")


if __name__ == "__main__":
    cleanup()

