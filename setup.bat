@echo off
REM Windows batch script for setting up Fiji and ThunderSTORM
REM Run this script as Administrator for system-wide installation

echo ==========================================
echo Fiji and ThunderSTORM Setup for Windows
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python is available. Starting setup...

REM Run the Python setup script
python setup_fiji.py

if %errorlevel% neq 0 (
    echo ERROR: Setup failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo You can now run the ThunderSTORM automation:
echo   python thunderstorm_automation.py
echo.
echo Or run tests:
echo   python test_setup.py
echo.
pause 