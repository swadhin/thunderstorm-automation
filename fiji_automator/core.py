#!/usr/bin/env python3
"""
Core module for Fiji Automator.

Contains the main ThunderSTORM automation logic.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from .config import get_config
from .utils import FileUtils, ProcessUtils, ImageUtils


class ThunderSTORMAutomator:
    """
    A class to automate ThunderSTORM analysis using a local Fiji installation.
    
    Prerequisites:
    1. Fiji must be installed on your system
    2. ThunderSTORM plugin must be installed in Fiji:
       - Via Help > Update... > Manage update sites, or
       - Download the .jar file from GitHub and place it in Fiji.app/plugins/
    """
    
    def __init__(self, fiji_path: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initializes the automator and finds the Fiji executable.
        
        Args:
            fiji_path (str, optional): Custom path to Fiji executable
            config_file (str, optional): Path to configuration file
        """
        self.config = get_config(config_file)
        
        # Try to find Fiji executable if no path is provided
        if fiji_path is None:
            fiji_path = self._find_fiji_executable()

        if not fiji_path or not Path(fiji_path).exists():
            raise FileNotFoundError(
                f"Fiji executable not found at: {fiji_path}\n"
                f"Please ensure Fiji is installed and specify the correct path.\n"
                f"Common installation locations:\n"
                f"  macOS: /Applications/Fiji.app/Contents/MacOS/ImageJ-macosx\n"
                f"  Windows: C:\\Program Files\\Fiji.app\\ImageJ-win64.exe"
            )
        
        self.fiji_path = fiji_path
        print(f"Fiji executable found at: {self.fiji_path}")
        
        # Verify ThunderSTORM plugin availability
        self._verify_thunderstorm_plugin()

    def _find_fiji_executable(self) -> Optional[str]:
        """
        Attempts to find the Fiji executable based on the operating system.
        
        Returns:
            Optional[str]: Path to Fiji executable or None if not found
        """
        possible_paths = self.config.get_fiji_install_paths()
        
        # Check each possible path
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None

    def _verify_thunderstorm_plugin(self):
        """
        Attempts to verify that ThunderSTORM plugin is available.
        This is a basic check - the actual verification happens when running the analysis.
        """
        print("Note: Please ensure ThunderSTORM plugin is installed in Fiji:")
        print("  Method 1: Help > Update... > Manage update sites")
        print("  Method 2: Download .jar from GitHub and place in Fiji.app/plugins/")

    def run_thunderstorm_analysis(self, input_path: str, output_dir: str,
                                **kwargs) -> bool:
        """
        Runs ThunderSTORM analysis on an input image using a generated ImageJ macro.

        Args:
            input_path (str): Path to the input TIFF stack.
            output_dir (str): Directory to save the analysis results.
            **kwargs: Additional parameters (see config for defaults)
            
        Returns:
            bool: True if analysis completed successfully, False otherwise
        """
        # Get default parameters and update with kwargs
        params = self.config.get_default_parameters().copy()
        params.update(kwargs)
        
        # Validate input file
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Validate TIFF file
        if not ImageUtils.validate_tiff_file(input_path):
            print(f"Warning: {input_path} may not be a valid TIFF file")
        
        # Create output directory if it doesn't exist
        FileUtils.ensure_directory(output_dir)

        # Sanitize paths for the ImageJ macro (must use forward slashes)
        sanitized_input_path = FileUtils.sanitize_path(input_path)
        sanitized_output_dir = FileUtils.sanitize_path(output_dir)

        # Generate the ImageJ macro script
        macro_script = self._generate_macro(sanitized_input_path, sanitized_output_dir, params)

        # Save the generated macro to a file
        macro_path = Path(output_dir) / "thunderstorm_macro.ijm"
        try:
            with open(macro_path, 'w') as f:
                f.write(macro_script)
            print(f"Generated macro saved to: {macro_path}")
        except Exception as e:
            print(f"Error saving macro file: {e}")
            raise

        # Construct and run the command-line call to Fiji
        cmd = [
            str(self.fiji_path),
            '--headless',  # Run Fiji without the graphical user interface
            '--console',   # Enable console output
            '--run', str(macro_path)
        ]

        print("Running ThunderSTORM analysis via Fiji...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the analysis
        timeout = self.config.get_analysis_timeout()
        returncode, stdout, stderr = ProcessUtils.run_command(cmd, timeout=timeout)
        
        # Process results
        success = self._process_analysis_results(returncode, stdout, stderr, output_dir, params)
        
        return success
    
    def _generate_macro(self, input_path: str, output_dir: str, params: Dict[str, Any]) -> str:
        """
        Generate the ImageJ macro script for ThunderSTORM analysis.
        
        Args:
            input_path (str): Sanitized input file path
            output_dir (str): Sanitized output directory path
            params (Dict[str, Any]): Analysis parameters
            
        Returns:
            str: Generated macro script
        """
        # Prepare the ImageJ macro script
        macro_script = f"""
        // ThunderSTORM Analysis Macro
        print("Starting ThunderSTORM analysis...");
        
        // Open the input image
        open("{input_path}");
        print("Opened input file: {input_path}");
        
        // Ensure the image is selected
        if (nImages == 0) {{
            print("Error: No images are open!");
            exit();
        }}
        
        // Run ThunderSTORM analysis
        // The plugin should be accessible via the Plugins menu
        run("Run analysis",
            "filter='{params['processing_method']}' " +
            "detector='[Local maximum]' " +
            "estimator='{params['localization_method']}' " +
            "sigma={params['sigma']} " +
            "fitradius={params['fitting_radius']} " +
            "method='[Weighted Least squares]' " +
            "camera.gain={params['gain']} " +
            "camera.offset={params['offset']} " +
            "camera.pixelsize={params['pixel_size']}");
        
        print("ThunderSTORM analysis completed.");
        
        // Export the localization results to a CSV file
        run("Export results", 
            "filepath='{output_dir}/results.csv' " +
            "fileformat=[CSV (comma separated)] " +
            "x=true y=true sigma=true intensity=true offset=true " +
            "bkgstd=true uncertainty=true saveprotocol=true");
        
        print("Results exported to: {output_dir}/results.csv");
        """

        # Add super-resolution image creation if requested
        if params.get('create_reconstructed_image', True):
            macro_script += f"""
        
        // Create and save super-resolved image
        run("Visualization",
            "imleft=0.0 imtop=0.0 imwidth=512.0 imheight=512.0 " +
            "renderer='[Averaged shifted histograms]' " +
            "magnification=5.0 " +
            "colorizez=false " +
            "threed=false " +
            "shifts=2 " +
            "repaint=50");
        
        if (nImages > 1) {{
            // Find and save the reconstructed image
            for (i = 1; i <= nImages; i++) {{
                selectImage(i);
                title = getTitle();
                if (indexOf(title, "Reconstructed") >= 0 || indexOf(title, "Visualization") >= 0) {{
                    saveAs("Tiff", "{output_dir}/reconstructed_image.tif");
                    print("Super-resolved image saved: {output_dir}/reconstructed_image.tif");
                    break;
                }}
            }}
        }}
        """

        macro_script += """
        
        // Close all windows to allow Fiji to exit cleanly
        run("Close All");
        print("Analysis complete. All windows closed.");
        """
        
        return macro_script
    
    def _process_analysis_results(self, returncode: int, stdout: str, stderr: str, 
                                output_dir: str, params: Dict[str, Any]) -> bool:
        """
        Process the results of the ThunderSTORM analysis.
        
        Args:
            returncode (int): Return code from Fiji process
            stdout (str): Standard output from Fiji
            stderr (str): Standard error from Fiji
            output_dir (str): Output directory path
            params (Dict[str, Any]): Analysis parameters
            
        Returns:
            bool: True if analysis was successful, False otherwise
        """
        if returncode == 0:
            if stdout:
                print("Fiji stdout:")
                print(stdout)
            
            if stderr:
                print("Fiji stderr:")
                print(stderr)
            
            print(f"Analysis complete! Results saved in: {output_dir}")
            
            # Check if expected output files were created
            self._verify_output_files(output_dir, params)
            return True
            
        elif returncode == -1:
            print("Error: Fiji process timed out or failed to run")
            return False
        else:
            print(f"Error running ThunderSTORM analysis:")
            print(f"Return Code: {returncode}")
            if stdout:
                print(f"Stdout: {stdout}")
            if stderr:
                print(f"Stderr: {stderr}")
            print("\nTroubleshooting tips:")
            print("1. Ensure ThunderSTORM plugin is properly installed")
            print("2. Check that the input file is a valid TIFF stack")
            print("3. Verify Fiji can run in headless mode")
            return False
    
    def _verify_output_files(self, output_dir: str, params: Dict[str, Any]):
        """
        Verify that expected output files were created.
        
        Args:
            output_dir (str): Output directory path
            params (Dict[str, Any]): Analysis parameters
        """
        try:
            output_path = Path(output_dir)
            
            # Check for results CSV
            results_file = output_path / "results.csv"
            if results_file.exists():
                print(f"✓ Localization results: {results_file}")
                
                # Try to get some basic stats about the results
                try:
                    with open(results_file, 'r') as f:
                        lines = f.readlines()
                        if len(lines) > 1:  # Header + at least one data row
                            print(f"  Found {len(lines) - 1} localizations")
                        else:
                            print("  Warning: No localizations found in results")
                except Exception as e:
                    print(f"  Could not read results file: {e}")
            else:
                print("⚠ Warning: Expected results.csv file not found")
            
            # Check for reconstructed image if requested
            if params.get('create_reconstructed_image', True):
                reconstructed_file = output_path / "reconstructed_image.tif"
                if reconstructed_file.exists():
                    print(f"✓ Super-resolved image: {reconstructed_file}")
                    
                    # Get image info with error handling
                    try:
                        img_info = ImageUtils.get_image_info(reconstructed_file)
                        if 'width' in img_info and 'height' in img_info:
                            print(f"  Image size: {img_info['width']}x{img_info['height']} pixels")
                    except Exception as e:
                        print(f"  Could not get image info: {e}")
                else:
                    print("⚠ Warning: Expected reconstructed_image.tif file not found")
            
            # Check for macro file
            macro_file = output_path / "thunderstorm_macro.ijm"
            if macro_file.exists():
                print(f"✓ Macro file: {macro_file}")
            
            print(f"Macro file retained for debugging: {macro_file}")
        except Exception as e:
            print(f"Error during output file verification: {e}")
            print("Some output files may not have been created correctly")

    def test_fiji_installation(self) -> bool:
        """
        Tests if Fiji can be launched and runs a simple command.
        
        Returns:
            bool: True if Fiji is working, False otherwise
        """
        print("Testing Fiji installation...")
        
        # Simple test macro
        test_macro = """
        print("Fiji is working!");
        print("ImageJ version: " + getVersion());
        """
        
        # Create a temporary macro file
        temp_dir = Path.cwd() / "temp_test"
        FileUtils.ensure_directory(temp_dir)
        macro_path = temp_dir / "test_macro.ijm"
        
        try:
            with open(macro_path, 'w') as f:
                f.write(test_macro)
            
            cmd = [str(self.fiji_path), '--headless', '--console', '--run', str(macro_path)]
            
            returncode, stdout, stderr = ProcessUtils.run_command(cmd, timeout=30)
            
            if returncode == 0:
                print("✓ Fiji installation test passed")
                if stdout:
                    print("Fiji output:", stdout)
                return True
            else:
                print("✗ Fiji installation test failed")
                if stderr:
                    print("Error output:", stderr)
                return False
                
        except Exception as e:
            print(f"✗ Fiji installation test failed: {e}")
            return False
        finally:
            # Clean up
            try:
                FileUtils.remove_file(macro_path)
                if temp_dir.exists():
                    temp_dir.rmdir()
            except Exception as e:
                print(f"Warning: Could not clean up temporary files: {e}")

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get information about an image file.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict[str, Any]: Dictionary with image information
        """
        return ImageUtils.get_image_info(image_path)
    
    def validate_input_file(self, image_path: str) -> bool:
        """
        Validate that an input file is suitable for ThunderSTORM analysis.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not Path(image_path).exists():
            print(f"✗ Input file does not exist: {image_path}")
            return False
        
        if not ImageUtils.validate_tiff_file(image_path):
            print(f"✗ Input file is not a valid TIFF: {image_path}")
            return False
        
        img_info = ImageUtils.get_image_info(image_path)
        
        if img_info.get('size_bytes', 0) == 0:
            print(f"✗ Input file is empty: {image_path}")
            return False
        
        if 'width' in img_info and 'height' in img_info:
            if img_info['width'] < 10 or img_info['height'] < 10:
                print(f"✗ Input image is too small: {img_info['width']}x{img_info['height']}")
                return False
        
        print(f"✓ Input file validation passed: {image_path}")
        if 'width' in img_info:
            print(f"  Image size: {img_info['width']}x{img_info['height']} pixels")
        if 'n_frames' in img_info:
            print(f"  Number of frames: {img_info['n_frames']}")
        
        return True


def main():
    """
    Main function for running ThunderSTORM analysis from command line.
    """
    # Example usage - replace with actual file paths
    input_file = "/path/to/your/input.tif"
    output_folder = "/path/to/your/output"

    try:
        # Create an instance of the automator
        automator = ThunderSTORMAutomator()

        # Test Fiji installation first
        if not automator.test_fiji_installation():
            print("Fiji installation test failed. Please check your Fiji installation.")
            sys.exit(1)

        # Validate input file
        if not automator.validate_input_file(input_file):
            print("Input file validation failed.")
            sys.exit(1)

        # Run the analysis with enhanced parameters
        success = automator.run_thunderstorm_analysis(
            input_path=input_file,
            output_dir=output_folder,
            pixel_size=100.0,          # Camera pixel size in nm
            gain=300.0,                # EM gain
            offset=100.0,              # Camera offset
            processing_method="Wavelet filter (B-Spline)",
            localization_method="PSF: Integrated Gaussian",
            sigma=1.6,                 # Expected PSF sigma in pixels
            fitting_radius=3,          # Fitting radius in pixels
            create_reconstructed_image=True  # Create super-resolved image
        )
        
        if success:
            print("\n" + "="*60)
            print("ThunderSTORM Analysis Complete!")
            print("="*60)
            print(f"Check the output directory: {output_folder}")
            print("Expected files:")
            print("  - results.csv: Localization data")
            print("  - reconstructed_image.tif: Super-resolved image")
            print("  - thunderstorm_macro.ijm: Generated macro (for debugging)")
        else:
            print("Analysis failed. Check the error messages above.")
            sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Fiji is installed in a standard location")
        print("2. Check that the input file exists and is a valid TIFF")
        print("3. Verify you have write permissions for the output directory")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 