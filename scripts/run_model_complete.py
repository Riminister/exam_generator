#!/usr/bin/env python3
"""Complete script to install packages and run model building"""
import sys
import subprocess
import os

def install_package(package_name):
    """Install a package using pip"""
    print(f"\n📦 Installing {package_name}...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"⚠️  {package_name} installation had issues:")
            if result.stderr:
                print(result.stderr[:500])  # First 500 chars
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {package_name} installation timed out (takes several minutes)")
        return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 70)
    print("🚀 COMPLETE MODEL BUILDING SETUP & EXECUTION")
    print("=" * 70)
    
    # Step 1: Check current packages
    print("\n📋 Step 1: Checking installed packages...")
    packages_needed = [
        ('scikit-learn', 'sklearn'),
        ('scipy', 'scipy'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy')
    ]
    
    missing_packages = []
    for package_name, import_name in packages_needed:
        if check_package(package_name, import_name):
            print(f"✅ {package_name} is installed")
        else:
            print(f"❌ {package_name} is NOT installed")
            missing_packages.append(package_name)
    
    # Step 2: Install missing packages
    if missing_packages:
        print(f"\n📦 Step 2: Installing {len(missing_packages)} missing packages...")
        print("   (This may take 5-10 minutes for scikit-learn and scipy)")
        print("   Please be patient...\n")
        
        for package in missing_packages:
            install_package(package)
    else:
        print("\n✅ All packages are already installed!")
    
    # Step 3: Verify installation
    print("\n🔍 Step 3: Verifying installation...")
    all_installed = True
    for package_name, import_name in packages_needed:
        if check_package(package_name, import_name):
            print(f"✅ {package_name} verified")
        else:
            print(f"❌ {package_name} still not available")
            all_installed = False
    
    if not all_installed:
        print("\n❌ Some packages failed to install.")
        print("   Please install manually:")
        print(f"   {sys.executable} -m pip install {' '.join(missing_packages)}")
        return
    
    # Step 4: Run the model building script
    print("\n" + "=" * 70)
    print("🤖 Step 4: Running Model Building Script")
    print("=" * 70)
    
    # Import and run the main function
    try:
        sys.path.insert(0, '.')
        from models.build_first_model import main as build_model
        build_model()
    except Exception as e:
        print(f"\n❌ Error running model script: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Tip: Try running manually:")
        print("   python models/build_first_model.py")

if __name__ == "__main__":
    main()

