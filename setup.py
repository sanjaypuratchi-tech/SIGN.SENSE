"""
Setup script for ISL Translator
Helps create necessary directories and check dependencies
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    dirs = ['sign_media', 'downloads']
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created: {directory}/")
        else:
            print(f"   ℹ️  Already exists: {directory}/")

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'PIL': 'Pillow',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    return missing

def install_dependencies(packages):
    """Install missing dependencies"""
    if not packages:
        return
    
    print(f"\n🔧 Installing {len(packages)} missing package(s)...")
    
    for package in packages:
        print(f"\n   Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")

def check_excel_file():
    """Check if signs.xlsx exists"""
    print("\n📊 Checking for signs.xlsx...")
    
    if os.path.exists('signs.xlsx'):
        print("   ✅ signs.xlsx found")
        return True
    else:
        print("   ❌ signs.xlsx NOT FOUND")
        print("   ⚠️  Please place signs.xlsx in the same directory as this script")
        return False

def create_sample_media_info():
    """Create a README in sign_media folder"""
    readme_path = os.path.join('sign_media', 'README.txt')
    
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""
=========================================
SIGN MEDIA FOLDER - INSTRUCTIONS
=========================================

This folder should contain images or videos for each sign.

NAMING CONVENTION:
------------------
- Use the exact word from signs.xlsx
- Replace spaces with underscores
- Use uppercase (recommended)
- Include file extension

EXAMPLES:
---------
✅ HELLO.png
✅ THANK_YOU.mp4
✅ EAT_FOOD.jpg
✅ WATER.gif

❌ hello.png (lowercase might not match)
❌ THANK YOU.mp4 (space instead of underscore)
❌ thankyou.png (doesn't match Excel entry)

SUPPORTED FORMATS:
------------------
Images: .png, .jpg, .jpeg, .gif
Videos: .mp4, .avi, .mov

TIPS:
-----
- Use high-quality, clear images
- Videos should be 2-5 seconds
- Show hand position clearly
- Good lighting is essential
- Plain background works best

Place your media files here and the program
will automatically load them when converting
text to signs!

=========================================
""")
        print(f"\n📄 Created instructions in sign_media/README.txt")

def main():
    """Run setup"""
    print("=" * 60)
    print("🤟 ISL TRANSLATOR - SETUP SCRIPT")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        response = input(f"\n❓ Install {len(missing)} missing package(s)? (y/n): ")
        if response.lower() == 'y':
            install_dependencies(missing)
        else:
            print("\n⚠️  Some packages are missing. Install them manually:")
            print(f"   pip install {' '.join(missing)}")
    else:
        print("\n✅ All dependencies are installed!")
    
    # Check Excel file
    excel_exists = check_excel_file()
    
    # Create media folder instructions
    create_sample_media_info()
    
    # Final summary
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    
    if not missing and excel_exists:
        print("✅ Setup complete! You're ready to run the program.")
        print("\n🚀 To start the application, run:")
        print("   python isl_translator.py")
    else:
        print("⚠️  Setup incomplete. Please:")
        if missing:
            print("   - Install missing packages")
        if not excel_exists:
            print("   - Add signs.xlsx to this directory")
    
    print("\n💡 Don't forget to add sign images/videos to sign_media/ folder")
    print("=" * 60)

if __name__ == "__main__":
    main()
