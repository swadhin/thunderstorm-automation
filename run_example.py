#!/usr/bin/env python3
"""
Example script demonstrating ThunderSTORM automation with the modular package.

This script uses the test TIFF file in the test_cases directory to demonstrate
the complete workflow.
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our package
sys.path.insert(0, str(Path(__file__).parent))

from fiji_automator import ThunderSTORMAutomator, FijiSetup, Config, ImageUtils


def check_test_file():
    """
    Check if the test TIFF file exists and get information about it.
    
    Returns:
        Path: Path to the test file if found, None otherwise
    """
    test_cases_dir = Path(__file__).parent / "test_cases"
    
    # Look for TIFF files in test_cases directory
    tiff_files = list(test_cases_dir.glob("*.tif*"))
    
    if not tiff_files:
        print("No TIFF files found in test_cases directory")
        return None
    
    # Use the first TIFF file found
    test_file = tiff_files[0]
    print(f"Found test file: {test_file}")
    
    # Get image information
    img_info = ImageUtils.get_image_info(test_file)
    print(f"File size: {img_info['size_bytes'] / (1024*1024):.1f} MB")
    
    if 'width' in img_info and 'height' in img_info:
        print(f"Image dimensions: {img_info['width']} x {img_info['height']} pixels")
    
    if 'n_frames' in img_info:
        print(f"Number of frames: {img_info['n_frames']}")
    
    return test_file


def run_fiji_setup():
    """
    Run the Fiji setup if Fiji is not available.
    
    Returns:
        bool: True if setup successful or Fiji already available
    """
    try:
        # Try to create automator - if this fails, Fiji is not installed
        automator = ThunderSTORMAutomator()
        print("✓ Fiji installation found")
        return True
    except FileNotFoundError:
        print("Fiji not found. Running automatic setup...")
        
        # Run Fiji setup
        setup = FijiSetup()
        
        # Check if we can install to default location
        if not setup.check_permissions():
            print("No permissions to install to default location.")
            print("Try running as administrator/sudo or specify a custom directory.")
            
            # Try installing to user directory
            user_install_dir = Path.home() / "fiji_automator_install"
            print(f"Attempting installation to: {user_install_dir}")
            setup = FijiSetup(install_dir=str(user_install_dir))
        
        success = setup.setup_all()
        
        if success:
            print("✓ Fiji setup completed successfully")
            return True
        else:
            print("✗ Fiji setup failed")
            return False


def run_example_analysis():
    """
    Run the example ThunderSTORM analysis.
    
    Returns:
        bool: True if analysis successful
    """
    # Check for test file
    test_file = check_test_file()
    if not test_file:
        print("No test file found. Please add a TIFF file to the test_cases directory.")
        return False
    
    # Ensure Fiji is available
    if not run_fiji_setup():
        print("Cannot proceed without Fiji installation")
        return False
    
    try:
        # Create automator instance
        automator = ThunderSTORMAutomator()
        
        # Test Fiji installation
        print("\nTesting Fiji installation...")
        if not automator.test_fiji_installation():
            print("Fiji installation test failed")
            return False
        
        # Validate input file
        print("\nValidating input file...")
        if not automator.validate_input_file(str(test_file)):
            print("Input file validation failed")
            return False
        
        # Set up output directory
        output_dir = Path(__file__).parent / "example_output"
        output_dir.mkdir(exist_ok=True)
        print(f"\nOutput directory: {output_dir}")
        
        # Run ThunderSTORM analysis
        print("\nRunning ThunderSTORM analysis...")
        success = automator.run_thunderstorm_analysis(
            input_path=str(test_file),
            output_dir=str(output_dir),
            # Custom parameters for the example
            pixel_size=100.0,                    # Camera pixel size in nm
            gain=100.0,                          # EM gain (lower for test)
            offset=100.0,                        # Camera offset
            processing_method="Wavelet filter (B-Spline)",
            localization_method="PSF: Integrated Gaussian",
            sigma=1.6,                           # Expected PSF sigma in pixels
            fitting_radius=3,                    # Fitting radius in pixels
            create_reconstructed_image=True      # Create super-resolved image
        )
        
        if success:
            print("\n" + "="*60)
            print("🎉 Example Analysis Complete!")
            print("="*60)
            print(f"Results saved in: {output_dir}")
            print("\nGenerated files:")
            
            # List output files
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"  📄 {file_path.name} ({size_mb:.2f} MB)")
            
            print("\nNext steps:")
            print("1. Open results.csv to view localization data")
            print("2. View reconstructed_image.tif for super-resolved image")
            print("3. Check thunderstorm_macro.ijm for the generated macro")
            
            return True
        else:
            print("Analysis failed")
            return False
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_configuration():
    """
    Display current configuration settings.
    """
    print("\n" + "="*50)
    print("Configuration Settings")
    print("="*50)
    
    config = Config()
    
    print(f"Platform: {config.platform}")
    print(f"Fiji URLs: {config.get_fiji_urls()}")
    print(f"Default install directory: {config.get_fiji_default_install_dir()}")
    print(f"Analysis timeout: {config.get_analysis_timeout()} seconds")
    
    default_params = config.get_default_parameters()
    print("\nDefault analysis parameters:")
    for key, value in default_params.items():
        print(f"  {key}: {value}")


def main():
    """
    Main function to run the example.
    """
    print("🔬 Fiji Automator - Example Analysis")
    print("="*50)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config":
            show_configuration()
            return
        elif sys.argv[1] == "--setup-only":
            success = run_fiji_setup()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_example.py              # Run full example")
            print("  python run_example.py --config     # Show configuration")
            print("  python run_example.py --setup-only # Setup Fiji only")
            print("  python run_example.py --help       # Show this help")
            return
    
    # Run the example analysis
    success = run_example_analysis()
    
    if success:
        print("\n✅ Example completed successfully!")
        print("You can now use the fiji_automator package for your own analyses.")
    else:
        print("\n❌ Example failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 