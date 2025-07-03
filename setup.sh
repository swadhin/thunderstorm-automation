#!/bin/bash
# Shell script for setting up Fiji and ThunderSTORM on macOS and Linux
# Run with sudo for system-wide installation

echo "=========================================="
echo "Fiji and ThunderSTORM Setup for macOS/Linux"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

echo "Python 3 is available. Starting setup..."

# Run the Python setup script
python3 setup_fiji.py

if [ $? -ne 0 ]; then
    echo "ERROR: Setup failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "You can now run the ThunderSTORM automation:"
echo "  python3 thunderstorm_automation.py"
echo ""
echo "Or run tests:"
echo "  python3 test_setup.py"
echo ""

# Make the script executable
chmod +x setup_fiji.py
chmod +x thunderstorm_automation.py
chmod +x test_setup.py

echo "Scripts have been made executable." 