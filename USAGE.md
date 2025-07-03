# Fiji and ThunderSTORM Automation - Usage Guide

This guide provides step-by-step instructions for setting up and using the automated Fiji and ThunderSTORM analysis system.

## Quick Start

### For Windows Users

1. **Simple Setup** (Recommended):
   ```cmd
   # Double-click setup.bat or run in Command Prompt
   setup.bat
   ```

2. **PowerShell Setup**:
   ```powershell
   # Run in PowerShell as Administrator
   .\setup.ps1
   ```

3. **Manual Setup**:
   ```cmd
   python setup_fiji.py
   ```

### For macOS/Linux Users

1. **Simple Setup** (Recommended):
   ```bash
   # Run in Terminal
   ./setup.sh
   ```

2. **Manual Setup**:
   ```bash
   python3 setup_fiji.py
   ```

## Detailed Setup Process

### 1. Prerequisites

- **Python 3.7+** must be installed
- **Internet connection** for downloading Fiji and ThunderSTORM
- **Administrator/sudo privileges** for system-wide installation (optional)

### 2. Installation Options

#### Option A: Automatic Installation (Recommended)

The setup script will automatically:
- Download the latest Fiji for your platform
- Download the latest ThunderSTORM plugin
- Install both in the appropriate directories
- Verify the installation

#### Option B: Custom Installation Directory

```bash
# Install to a custom directory
python3 setup_fiji.py /path/to/your/custom/directory
```

#### Option C: Manual Installation

1. Install Fiji manually from https://fiji.sc/
2. Install ThunderSTORM plugin via Fiji's update sites
3. Use the automation script directly

### 3. Testing Your Installation

#### Quick Test
```bash
# Test basic functionality
python3 test_setup.py setup
```

#### Comprehensive Test
```bash
# Test all components
python3 test_setup.py

# Or test specific components
python3 test_setup.py automation
python3 test_setup.py integration
```

## Using the ThunderSTORM Automation

### Basic Usage

1. **Prepare your data**: Place your TIFF stack in a known location
2. **Update the script**: Edit the file paths in `thunderstorm_automation.py`
3. **Run the analysis**:
   ```bash
   python3 thunderstorm_automation.py
   ```

### Advanced Usage

```python
from thunderstorm_automation import ThunderSTORMAutomator

# Initialize with custom Fiji path
automator = ThunderSTORMAutomator(fiji_path="/path/to/fiji")

# Test installation
if automator.test_fiji_installation():
    print("Fiji is ready!")

# Run analysis with custom parameters
automator.run_thunderstorm_analysis(
    input_path="data/sample.tif",
    output_dir="results/",
    pixel_size=107.0,         # nm
    gain=200.0,               # EM gain
    offset=100.0,             # Camera offset
    sigma=1.2,                # Expected PSF sigma
    fitting_radius=4,         # Fitting radius
    create_reconstructed_image=True
)
```

## Understanding the Output

### Files Generated

1. **`results.csv`**: Localization data with columns:
   - `x`, `y`: Molecule coordinates (pixels)
   - `intensity`: Photon count
   - `sigma`: PSF width
   - `offset`: Local background
   - `bkgstd`: Background standard deviation
   - `uncertainty`: Localization uncertainty

2. **`reconstructed_image.tif`**: Super-resolved image

3. **`thunderstorm_macro.ijm`**: Generated ImageJ macro (for debugging)

### Quality Control

- Check the number of localizations in the CSV file
- Verify the super-resolved image looks reasonable
- Review the macro file for any error messages

## Troubleshooting

### Common Issues

1. **"Fiji executable not found"**
   - Solution: Run the setup script or specify custom path
   - Check: Ensure Fiji is in a standard location

2. **"ThunderSTORM plugin not found"**
   - Solution: Reinstall using the setup script
   - Check: Verify .jar file is in Fiji.app/plugins/

3. **"Permission denied"**
   - Solution: Run as Administrator (Windows) or with sudo (macOS/Linux)
   - Alternative: Use a custom installation directory

4. **"Process timed out"**
   - Solution: Check input file validity and size
   - Try: Use smaller test images first

5. **"No localizations found"**
   - Solution: Adjust detection parameters (sigma, threshold)
   - Check: Verify input is a suitable STORM dataset

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your analysis
automator.run_thunderstorm_analysis(...)
```

### Getting Help

1. **Check the generated macro file** (`thunderstorm_macro.ijm`) for errors
2. **Run the test suite** to verify installation
3. **Try with a smaller test image** first
4. **Check ThunderSTORM documentation** for parameter guidance

## Advanced Configuration

### Custom Parameters

```python
# For high-density samples
automator.run_thunderstorm_analysis(
    input_path="high_density.tif",
    output_dir="results/",
    sigma=0.8,                # Smaller PSF
    fitting_radius=2,         # Smaller fitting radius
    processing_method="Difference of Gaussians"
)

# For low-SNR samples
automator.run_thunderstorm_analysis(
    input_path="low_snr.tif",
    output_dir="results/",
    sigma=2.0,                # Larger PSF
    fitting_radius=5,         # Larger fitting radius
    processing_method="Wavelet filter (B-Spline)"
)
```

### Batch Processing

```python
import os
from pathlib import Path

# Process multiple files
input_dir = Path("data")
output_dir = Path("results")

for tif_file in input_dir.glob("*.tif"):
    print(f"Processing {tif_file.name}...")
    
    file_output_dir = output_dir / tif_file.stem
    automator.run_thunderstorm_analysis(
        input_path=str(tif_file),
        output_dir=str(file_output_dir)
    )
```

## Performance Tips

1. **Use appropriate pixel size**: Correct camera pixel size improves accuracy
2. **Optimize sigma parameter**: Should match your PSF size
3. **Adjust fitting radius**: Larger for sparse data, smaller for dense data
4. **Use headless mode**: Automatic with the script (no GUI overhead)
5. **Monitor memory usage**: Large datasets may require more RAM

## Integration with Other Tools

### Export to Other Software

```python
# After analysis, load the results
import pandas as pd
results = pd.read_csv("results/results.csv")

# Convert to other formats
results.to_csv("results/results_for_matlab.csv", index=False)
results.to_pickle("results/results.pkl")  # For Python analysis
```

### Custom Post-Processing

```python
# Filter localizations
filtered_results = results[
    (results['uncertainty'] < 50) &  # High precision
    (results['intensity'] > 1000)    # Bright spots
]

# Save filtered results
filtered_results.to_csv("results/filtered_results.csv", index=False)
```

## Support and Resources

- **ThunderSTORM Documentation**: https://github.com/zitmen/thunderstorm
- **Fiji Documentation**: https://fiji.sc/
- **ImageJ Macro Language**: https://imagej.nih.gov/ij/developer/macro/macros.html

## Version History

- **v1.0**: Initial release with basic automation
- **v1.1**: Added automatic setup and testing
- **v1.2**: Enhanced cross-platform support and error handling 