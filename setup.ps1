# PowerShell script for setting up Fiji and ThunderSTORM on Windows
# Run as Administrator for system-wide installation

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Fiji and ThunderSTORM Setup for Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Python is available: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting setup..." -ForegroundColor Yellow

# Run the Python setup script
try {
    python setup_fiji.py
    if ($LASTEXITCODE -ne 0) {
        throw "Setup script failed"
    }
}
catch {
    Write-Host "ERROR: Setup failed - $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the ThunderSTORM automation:" -ForegroundColor Cyan
Write-Host "  python thunderstorm_automation.py" -ForegroundColor White
Write-Host ""
Write-Host "Or run tests:" -ForegroundColor Cyan
Write-Host "  python test_setup.py" -ForegroundColor White
Write-Host ""
Write-Host "To run a quick test:" -ForegroundColor Cyan
Write-Host "  python test_setup.py setup" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit" 