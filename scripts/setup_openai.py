#!/usr/bin/env python3
"""
Setup OpenAI API Key
Interactive script to help you configure your OpenAI API key
"""

import os
from pathlib import Path


def setup_api_key():
    """Interactive setup for OpenAI API key"""
    print("=" * 70)
    print("OpenAI API Key Setup")
    print("=" * 70)
    print()
    print("This script will help you set up your OpenAI API key securely.")
    print("Your API key will be stored in a .env file (not committed to git).")
    print()
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to update your API key? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing configuration.")
            return
    
    # Get API key from user
    print("\nTo get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (you'll only see it once!)")
    print()
    
    api_key = input("Enter your OpenAI API key (starts with 'sk-'): ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API keys typically start with 'sk-'. Are you sure this is correct?")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Read existing .env or create new
    env_content = []
    key_found = False
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    env_content.append(f'OPENAI_API_KEY={api_key}\n')
                    key_found = True
                else:
                    env_content.append(line)
    
    if not key_found:
        env_content.append(f'OPENAI_API_KEY={api_key}\n')
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    # Set file permissions (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        os.chmod(env_file, 0o600)  # Read/write for owner only
    
    print("\n✅ API key saved to .env file")
    print("   The .env file is in .gitignore and won't be committed to git.")
    print()
    
    # Test the key
    print("Testing API key...")
    try:
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
        except ImportError:
            print("⚠️  openai package not installed")
            print("   Install it with: pip install openai python-dotenv")
            print("   The API key has been saved, but you need to install packages to test it.")
            return
        
        load_dotenv()
        client = OpenAI()
        
        # Simple test call
        response = client.models.list()
        print("✅ API key is valid and working!")
        print(f"   You have access to {len(response.data)} models")
        
    except Exception as e:
        print(f"⚠️  Could not verify API key: {e}")
        print("   Make sure you have:")
        print("   1. Installed: pip install openai python-dotenv")
        print("   2. Added credits to your OpenAI account")
        print("   3. Entered the correct API key")
    
    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print("\nYou can now use OpenAI to generate questions:")
    print("  python generate_questions_with_openai.py")


if __name__ == "__main__":
    setup_api_key()

