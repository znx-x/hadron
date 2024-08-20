import os
import subprocess
import sys

def install_packages():
    required_packages = [
        'flask',
        'requests',
        'pycryptodome',
        'PyQt5'
    ]

    for package in required_packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
    print("All dependencies installed successfully.")
