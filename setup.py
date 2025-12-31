"""
Air Canvas Pro - Complete Setup Script
Checks dependencies and downloads required model file
"""

import sys
import os
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("[FAIL] Python 3.7 or higher is required")
        return False

    print("[OK] Python version is compatible")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")

    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy'
    }

    missing_packages = []

    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            if module_name == 'cv2':
                import cv2
                print(f"[OK] {package_name:20s} (version {cv2.__version__})")
            elif module_name == 'mediapipe':
                import mediapipe
                print(f"[OK] {package_name:20s} (version {mediapipe.__version__})")
            elif module_name == 'numpy':
                import numpy
                print(f"[OK] {package_name:20s} (version {numpy.__version__})")
        except ImportError:
            print(f"[FAIL] {package_name:20s} (not installed)")
            missing_packages.append(package_name)

    return missing_packages


def install_dependencies(packages):
    """Install missing packages"""
    if not packages:
        return True

    print_header("Installing Missing Dependencies")
    print(f"Installing: {', '.join(packages)}\n")

    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages
        )
        print("\n[OK] All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FAIL] Installation failed: {e}")
        return False


def check_model_file():
    """Check if hand landmarker model exists"""
    print_header("Checking Model File")

    model_path = Path.cwd() / "hand_landmarker.task"

    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Model file found: {model_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"[FAIL] Model file not found: {model_path}")
        return False


def download_model():
    """Download the model file"""
    print_header("Downloading Model File")

    try:
        import urllib.request

        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        model_path = Path.cwd() / "hand_landmarker.task"

        print(f"Downloading from: {url}")
        print(f"Saving to: {model_path}")
        print("\nThis may take a minute...\n")

        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            bar_length = 40
            filled = int(bar_length * downloaded / total_size)
            bar = '#' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
            sys.stdout.flush()

        urllib.request.urlretrieve(url, model_path, reporthook=progress)
        print("\n\n[OK] Model downloaded successfully")
        return True

    except Exception as e:
        print(f"\n[FAIL] Download failed: {e}")
        print("\nManual Download Instructions:")
        print("1. Visit: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker")
        print("2. Download 'hand_landmarker.task'")
        print(f"3. Save it to: {Path.cwd()}")
        return False


def check_camera():
    """Check if camera is accessible"""
    print_header("Checking Camera")

    try:
        import cv2
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("[FAIL] Cannot access camera")
            print("   Possible issues:")
            print("   - Camera is being used by another application")
            print("   - Camera drivers not installed")
            print("   - No camera connected")
            return False

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("[FAIL] Camera opened but cannot read frames")
            return False

        print("[OK] Camera is accessible and working")
        return True

    except Exception as e:
        print(f"[FAIL] Error checking camera: {e}")
        return False


def create_requirements_txt():
    """Create requirements.txt file"""
    print_header("Creating requirements.txt")

    requirements = """opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
"""

    try:
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        print("[OK] requirements.txt created")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create requirements.txt: {e}")
        return False


def main():
    """Main setup function"""
    print("\n")
    print("*" * 60)
    print("     AIR CANVAS PRO - SETUP WIZARD")
    print("*" * 60)

    # Step 1: Check Python version
    if not check_python_version():
        print("\n[FAIL] Setup failed: Incompatible Python version")
        return False

    # Step 2: Check dependencies
    missing = check_dependencies()

    if missing:
        print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
        response = input("\nInstall missing packages? (y/n): ").strip().lower()

        if response == 'y':
            if not install_dependencies(missing):
                print("\n[FAIL] Setup failed: Could not install dependencies")
                return False
        else:
            print("\n[WARNING] Skipping installation. You can install manually with:")
            print(f"   pip install {' '.join(missing)}")

    # Step 3: Create requirements.txt
    create_requirements_txt()

    # Step 4: Check model file
    if not check_model_file():
        response = input("\nDownload model file now? (y/n): ").strip().lower()

        if response == 'y':
            if not download_model():
                print("\n[FAIL] Setup failed: Could not download model")
                return False
        else:
            print("\n[WARNING] Model file is required to run Air Canvas")
            print("   You can download it later by running: python download_model.py")

    # Step 5: Check camera (optional)
    response = input("\nTest camera access? (y/n): ").strip().lower()
    if response == 'y':
        check_camera()

    # Final summary
    print_header("Setup Summary")

    all_good = True

    # Check everything one more time
    print("\nFinal checks:")

    # Python
    print("[OK] Python version OK")

    # Dependencies
    try:
        import cv2, mediapipe, numpy
        print("[OK] All dependencies installed")
    except ImportError:
        print("[FAIL] Some dependencies missing")
        all_good = False

    # Model
    if Path("hand_landmarker.task").exists():
        print("[OK] Model file present")
    else:
        print("[FAIL] Model file missing")
        all_good = False

    if all_good:
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("\nYou can now run Air Canvas:")
        print("   python main.py")
        print("\nKeyboard shortcuts:")
        print("   ESC - Exit")
        print("   D   - Debug mode")
        print("   S   - Show statistics")
        print("   I   - Show instructions")
        print("   H   - Help")
        print("\nEnjoy drawing!")
        return True
    else:
        print("\n" + "=" * 60)
        print("SETUP INCOMPLETE")
        print("=" * 60)
        print("\nPlease resolve the issues above before running Air Canvas.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)