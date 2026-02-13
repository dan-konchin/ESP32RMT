import subprocess
import sys
import os

MIN_PYTHON = (3, 14, 2)

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        print(f"Phiên bản Python hiện tại là {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"Vui lòng sử dụng Python phiên bản {MIN_PYTHON[0]}.{MIN_PYTHON[1]}.{MIN_PYTHON[2]} hoặc cao hơn.")
        sys.exit(1)

def install_packages_from_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} không tồn tại.")
        return

    with open(filename, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for package in packages:
        try:
            __import__(package)
            print(f"'{package}' đã được cài đặt.")
        except ImportError:
            print(f"Đang cài đặt '{package}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    check_python_version()
    requirements_file = 'requirements.txt'
    install_packages_from_file(requirements_file)
    print("Hoàn tất cài đặt các thư viện cần thiết.")