# ThunderSTORM Automation

This project provides a Python wrapper for automating ThunderSTORM analysis in Fiji/ImageJ without manual GUI interaction. It allows for automated processing of super-resolution microscopy data across different operating systems (Windows, macOS, Linux).

## Features

- **Cross-platform support**: Automatically detects Fiji installation on Windows, macOS, and Linux
- **Automated ThunderSTORM analysis**: Runs complete analysis pipeline including localization and super-resolution reconstruction
- **Installation testing**: Built-in Fiji installation verification
- **Flexible parameters**: Customizable camera settings, processing methods, and analysis parameters
- **Comprehensive output**: Generates CSV localization data, super-resolved images, and analysis protocols

## Prerequisites

1. **Fiji Installation**
   - Download and install Fiji from [https://fiji.sc/](https://fiji.sc/)
   - Supported installation locations:
     - **Windows**: `C:\Program Files\Fiji.app\`, `C:\Program Files (x86)\Fiji.app\`, or user directory
     - **macOS**: `/Applications/Fiji.app/` or user Applications folder
     - **Linux**: `~/Fiji.app/` or `/opt/Fiji.app/`

2. **ThunderSTORM Plugin Installation**
   
   **Method 1 (Recommended):**
   - Open Fiji
   - Go to `Help > Update...`
   - Click "Manage Update Sites"
   - Find and enable "ThunderSTORM" in the list
   - Click "Apply changes"
   - Restart Fiji

   **Method 2:**
   - Download the ThunderSTORM .jar file from [GitHub](https://github.com/zitmen/thunderstorm)
   - Place it in `Fiji.app/plugins/` directory
   - Restart Fiji

3. **Python Environment**
   - Python 3.7 or higher is required

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd fiji_automator
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from thunderstorm_automation import ThunderSTORMAutomator

# Initialize the automator (auto-detects Fiji installation)
automator = ThunderSTORMAutomator()

# Test Fiji installation
if automator.test_fiji_installation():
    print("Fiji is working correctly!")
else:
    print("Fiji installation issues detected")

# Run analysis
automator.run_thunderstorm_analysis(
    input_path="path/to/your/image_stack.tif",
    output_dir="path/to/output",
    pixel_size=100.0,  # Camera pixel size in nm
    gain=300.0,        # EM gain
    offset=100.0,      # Camera offset
    create_reconstructed_image=True  # Generate super-resolved image
)
```

### Advanced Usage

```python
# Custom Fiji location
automator = ThunderSTORMAutomator(
    fiji_path="/custom/path/to/Fiji.app/ImageJ-executable"
)

# Advanced analysis with custom parameters
automator.run_thunderstorm_analysis(
    input_path="data/sample.tif",
    output_dir="results/",
    pixel_size=107.0,  # Camera pixel size in nm
    gain=200.0,        # EM gain
    offset=100.0,      # Camera offset
    processing_method="Wavelet filter (B-Spline)",
    localization_method="PSF: Integrated Gaussian",
    sigma=1.2,         # Expected PSF sigma in pixels
    fitting_radius=4,  # Fitting radius in pixels
    create_reconstructed_image=True
)
```

### Command Line Usage

Update the paths in the script and run:
```bash
python thunderstorm_automation.py
```

## Parameters

### Camera Settings
- `pixel_size`: Camera pixel size in nm (default: 100.0)
- `gain`: Camera EM gain (default: 100.0)
- `offset`: Camera base-level offset in A/D counts (default: 100.0)

### Processing Settings
- `processing_method`: Pre-processing filter method (default: "Wavelet filter (B-Spline)")
- `localization_method`: Localization method (default: "PSF: Integrated Gaussian")
- `sigma`: Expected PSF standard deviation in pixels (default: 1.6)
- `fitting_radius`: Fitting radius in pixels (default: 3)

### Output Settings
- `create_reconstructed_image`: Whether to generate super-resolved image (default: True)

## Output Files

The script generates several files in the output directory:

1. **`results.csv`**: Localization data with columns:
   - x, y coordinates
   - Intensity values
   - Localization uncertainty
   - Background statistics

2. **`reconstructed_image.tif`**: Super-resolved image reconstructed from localizations

3. **`thunderstorm_macro.ijm`**: Generated ImageJ macro (kept for debugging)

## Troubleshooting

### Common Issues

1. **Fiji not found:**
   ```
   FileNotFoundError: Fiji executable not found
   ```
   - Ensure Fiji is installed in a standard location
   - Use custom path: `ThunderSTORMAutomator(fiji_path="/your/path")`

2. **ThunderSTORM plugin not available:**
   ```
   Error: ThunderSTORM commands not recognized
   ```
   - Verify ThunderSTORM is installed via Help > Update... > Manage update sites
   - Or manually download and place .jar file in plugins folder

3. **Permission errors:**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - Ensure write permissions for output directory
   - Run with appropriate user privileges

4. **Timeout errors:**
   ```
   Fiji process timed out (5 minutes)
   ```
   - Large datasets may take longer to process
   - Check input file validity

### Testing Installation

Use the built-in test function:
```python
automator = ThunderSTORMAutomator()
if automator.test_fiji_installation():
    print("✓ Fiji installation is working")
else:
    print("✗ Fiji installation has issues")
```

## OS-Specific Notes

### Windows
- **Executable locations checked:**
  - `C:\Program Files\Fiji.app\ImageJ-win64.exe`
  - `C:\Program Files (x86)\Fiji.app\ImageJ-win64.exe`
  - User directory and Desktop installations
- **Path format**: Use forward slashes or raw strings

### macOS
- **Executable locations checked:**
  - `/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx`
  - User Applications folder
- **Permissions**: Ensure Fiji has proper execution permissions

### Linux
- **Executable locations checked:**
  - `~/Fiji.app/ImageJ-linux64`
  - `/opt/Fiji.app/ImageJ-linux64`
- **Permissions**: Ensure Fiji is executable (`chmod +x`)

## Example Workflow

1. **Install Fiji and ThunderSTORM**
2. **Prepare your data**: Ensure TIFF stack is properly formatted
3. **Test installation**: Run the built-in test
4. **Configure parameters**: Adjust camera settings and analysis parameters
5. **Run analysis**: Execute the automated pipeline
6. **Review results**: Check output files and quality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues related to:
- **ThunderSTORM**: Visit the [ThunderSTORM GitHub repository](https://github.com/zitmen/thunderstorm)
- **Fiji**: Visit the [Fiji documentation](https://fiji.sc/)
- **This wrapper**: Open an issue in this repository
