# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties
# of merchantability, fitness for a particular purpose and
# noninfringement. In no even shall the authors or copyright
# holders be liable for any claim, damages, or other liability,
# whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or
# other dealings in the software.

# Use this script to install all the necessary dependencies for you
# to run your node.

import os
import subprocess
import sys

def install_packages():
    required_packages = [
        'flask',
        'requests',
        'pycryptodome',
        'PyQt5',
        'pynacl',
        'waitress'
    ]

    for package in required_packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    install_packages()
    print("All dependencies installed successfully.")
