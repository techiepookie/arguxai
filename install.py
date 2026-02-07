"""
Install dependencies for ArguxAI
Run this first: python install.py
"""

import subprocess
import sys

print("\n" + "="*60)
print("           Installing ArguxAI Dependencies")
print("="*60 + "\n")

print("📦 Installing packages from requirements.txt...")
print("   This may take a few minutes...\n")

try:
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "pip", 
        "install", 
        "-r", 
        "requirements.txt"
    ])
    
    print("\n" + "="*60)
    print("✅ Installation complete!")
    print("="*60)
    print("\nNext step: Run the application")
    print("  python app.py")
    print()
    
except Exception as e:
    print(f"\n❌ Installation failed: {e}")
    print("\nPlease try manually:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
