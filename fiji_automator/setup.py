"""
Setup module for Fiji Automator.

Handles downloading and installing Fiji and ThunderSTORM plugin.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
import urllib.request
import json

from .config import get_config
from .utils import FileUtils, ProcessUtils


class FijiSetup:
    """
    A class to automatically download and install Fiji and ThunderSTORM plugin.
    """
    
    def __init__(self, install_dir: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the setup class.
        
        Args:
            install_dir (str, optional): Custom installation directory
            config_file (str, optional): Path to configuration file
        """
        self.config = get_config(config_file)
        self.platform = self.config.platform
        
        # Set installation directory
        if install_dir:
            self.install_dir = Path(install_dir)
        else:
            self.install_dir = Path(self.config.get_fiji_default_install_dir())
        
        self.fiji_dir = self.install_dir / "Fiji.app"
        self.plugins_dir = self.fiji_dir / "plugins"
    
    def check_permissions(self) -> bool:
        """
        Check if we have write permissions to the installation directory.
        
        Returns:
            bool: True if we have write permissions, False otherwise
        """
        return FileUtils.check_permissions(self.install_dir)
    
    def download_fiji(self) -> bool:
        """
        Download and install Fiji for the current platform.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"Setting up Fiji for {self.platform}...")
        
        # Check if Fiji is already installed
        if self.fiji_dir.exists():
            print(f"Fiji already exists at {self.fiji_dir}")
            response = input("Do you want to reinstall? (y/N): ").lower()
            if response != 'y':
                return True
            else:
                print("Removing existing Fiji installation...")
                import shutil
                shutil.rmtree(self.fiji_dir)
        
        # Get download URL for current platform
        fiji_urls = self.config.get_fiji_urls()
        download_url = fiji_urls.get(self.platform)
        
        if not download_url:
            print(f"✗ Unsupported platform: {self.platform}")
            return False
        
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_name = f"fiji-{self.platform}.zip"
            archive_path = temp_path / archive_name
            
            # Download Fiji
            if not FileUtils.download_file(download_url, archive_path, "Fiji"):
                return False
            
            # Extract Fiji
            if not FileUtils.extract_archive(archive_path, self.install_dir, "Fiji"):
                return False
        
        # Verify installation
        if self.fiji_dir.exists():
            print(f"✓ Fiji installed successfully at {self.fiji_dir}")
            
            # Make executable on Unix systems
            if self.platform in ["darwin", "linux"]:
                self._make_fiji_executable()
            
            return True
        else:
            print("✗ Fiji installation failed - directory not found")
            return False
    
    def _make_fiji_executable(self):
        """
        Make Fiji executable on Unix systems.
        """
        try:
            fiji_executable = self.get_fiji_executable()
            if fiji_executable and fiji_executable.exists():
                os.chmod(fiji_executable, 0o755)
                print(f"✓ Made {fiji_executable} executable")
        except Exception as e:
            print(f"⚠ Warning: Could not make Fiji executable: {e}")
    
    def get_thunderstorm_download_url(self) -> tuple:
        """
        Get the download URL for the latest ThunderSTORM release.
        
        Returns:
            tuple: (download_url, jar_filename) or (None, None) if failed
        """
        api_url = self.config.get_thunderstorm_api_url()
        
        try:
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                
                # Look for the .jar file in assets
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".jar") and "thunderstorm" in asset["name"].lower():
                        return asset["browser_download_url"], asset["name"]
                
                print("✗ ThunderSTORM .jar file not found in latest release")
                return None, None
                
        except Exception as e:
            print(f"✗ Failed to get ThunderSTORM release info: {e}")
            return None, None
    
    def install_thunderstorm(self) -> bool:
        """
        Download and install ThunderSTORM plugin.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("Installing ThunderSTORM plugin...")
        
        # Ensure plugins directory exists
        FileUtils.ensure_directory(self.plugins_dir)
        
        # Get download URL
        download_url, jar_name = self.get_thunderstorm_download_url()
        if not download_url:
            print("✗ Could not find ThunderSTORM download URL")
            return False
        
        # Check if already installed
        existing_jars = FileUtils.find_files(self.plugins_dir, "*thunderstorm*.jar")
        if existing_jars:
            print(f"ThunderSTORM plugin already exists: {existing_jars[0]}")
            response = input("Do you want to reinstall? (y/N): ").lower()
            if response != 'y':
                return True
            else:
                for jar in existing_jars:
                    FileUtils.remove_file(jar)
        
        # Download ThunderSTORM
        jar_path = self.plugins_dir / jar_name
        if FileUtils.download_file(download_url, jar_path, "ThunderSTORM plugin"):
            print(f"✓ ThunderSTORM plugin installed at {jar_path}")
            return True
        else:
            return False
    
    def verify_installation(self) -> bool:
        """
        Verify that Fiji and ThunderSTORM are properly installed.
        
        Returns:
            bool: True if installation is valid, False otherwise
        """
        print("\nVerifying installation...")
        
        # Check Fiji directory
        if not self.fiji_dir.exists():
            print("✗ Fiji directory not found")
            return False
        
        # Check Fiji executable
        fiji_executable = self.get_fiji_executable()
        if not fiji_executable or not fiji_executable.exists():
            print("✗ Fiji executable not found")
            return False
        
        print(f"✓ Fiji executable found at {fiji_executable}")
        
        # Check ThunderSTORM plugin
        thunderstorm_jars = FileUtils.find_files(self.plugins_dir, "*thunderstorm*.jar")
        if not thunderstorm_jars:
            print("✗ ThunderSTORM plugin not found")
            return False
        
        print(f"✓ ThunderSTORM plugin found: {thunderstorm_jars[0]}")
        
        # Test Fiji execution
        return self.test_fiji_execution()
    
    def get_fiji_executable(self) -> Optional[Path]:
        """
        Get the path to the Fiji executable for the current platform.
        
        Returns:
            Optional[Path]: Path to Fiji executable, or None if not found
        """
        if self.platform == "windows":
            return self.fiji_dir / "ImageJ-win64.exe"
        elif self.platform == "darwin":
            return self.fiji_dir / "Contents" / "MacOS" / "ImageJ-macosx"
        elif self.platform == "linux":
            return self.fiji_dir / "ImageJ-linux64"
        else:
            return None
    
    def test_fiji_execution(self) -> bool:
        """
        Test that Fiji can be executed.
        
        Returns:
            bool: True if Fiji can run, False otherwise
        """
        print("Testing Fiji execution...")
        
        fiji_executable = self.get_fiji_executable()
        if not fiji_executable or not fiji_executable.exists():
            print("✗ Fiji executable not found")
            return False
        
        # Create a simple test macro
        test_macro = '''
        print("Fiji test successful!");
        print("ImageJ version: " + getVersion());
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ijm', delete=False) as f:
            f.write(test_macro)
            macro_path = f.name
        
        try:
            # Run Fiji with the test macro
            cmd = [str(fiji_executable), '--headless', '--console', '--run', macro_path]
            returncode, stdout, stderr = ProcessUtils.run_command(cmd, timeout=30)
            
            if returncode == 0:
                print("✓ Fiji execution test passed")
                if stdout:
                    print(f"  Output: {stdout.strip()}")
                return True
            else:
                print("✗ Fiji execution test failed")
                if stderr:
                    print(f"  Error: {stderr.strip()}")
                return False
                
        except Exception as e:
            print(f"✗ Fiji execution test failed: {e}")
            return False
        finally:
            # Clean up test macro
            try:
                FileUtils.remove_file(macro_path)
            except Exception as e:
                print(f"Warning: Could not clean up test macro file: {e}")
    
    def setup_all(self) -> bool:
        """
        Complete setup process: download Fiji and ThunderSTORM.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        print("=== Fiji and ThunderSTORM Setup ===")
        print(f"Platform: {self.platform}")
        print(f"Installation directory: {self.install_dir}")
        
        # Check permissions
        if not self.check_permissions():
            print(f"✗ No write permissions to {self.install_dir}")
            print("Please run as administrator/sudo or choose a different directory")
            return False
        
        # Create installation directory
        FileUtils.ensure_directory(self.install_dir)
        
        # Download and install Fiji
        if not self.download_fiji():
            print("✗ Fiji installation failed")
            return False
        
        # Install ThunderSTORM plugin
        if not self.install_thunderstorm():
            print("✗ ThunderSTORM installation failed")
            return False
        
        # Verify installation
        if not self.verify_installation():
            print("✗ Installation verification failed")
            return False
        
        print("\n" + "="*50)
        print("✓ Setup completed successfully!")
        print("="*50)
        print(f"Fiji installed at: {self.fiji_dir}")
        print(f"ThunderSTORM plugin installed in: {self.plugins_dir}")
        print("\nYou can now use the thunderstorm_automation.py script")
        
        return True


def main():
    """
    Main function to run the setup process.
    """
    print("Fiji and ThunderSTORM Automatic Setup")
    print("====================================")
    
    # Allow custom installation directory
    install_dir = None
    if len(sys.argv) > 1:
        install_dir = sys.argv[1]
        print(f"Using custom installation directory: {install_dir}")
    
    # Create setup instance and run
    setup = FijiSetup(install_dir)
    success = setup.setup_all()
    
    if success:
        print("\nSetup completed successfully!")
        print("You can now run the ThunderSTORM automation script.")
    else:
        print("\nSetup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 