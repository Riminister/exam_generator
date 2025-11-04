#!/usr/bin/env python3
"""
Run All Tests and Organize Project
Master script to test everything and clean up the project
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Run all tests and organization"""
    print("=" * 70)
    print("PROJECT CLEANUP AND TESTING")
    print("=" * 70)
    print()
    
    # Step 1: Create directories
    print("Step 1: Creating directories...")
    directories = [
        'scripts',
        'tests',
        'outputs',
        'docs/guides',
        'generated_graphs',
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    print()
    
    # Step 2: Run tests
    print("Step 2: Running comprehensive tests...")
    print()
    
    try:
        from tests.test_comprehensive import TestSuite
        suite = TestSuite()
        success = suite.run_all_tests()
        
        if not success:
            print("\n⚠️  Some tests failed. Review errors above.")
            return 1
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review project structure in PROJECT_STRUCTURE.md")
    print("2. Run: python scripts/organize_project.py --dry-run")
    print("3. Review proposed changes")
    print("4. Run: python scripts/organize_project.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

