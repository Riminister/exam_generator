#!/usr/bin/env python3
"""Test the improved model with explicit error handling"""
import sys
import traceback

try:
    from models.build_improved_difficulty_model import main
    print("Import successful, running main...")
    main()
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

