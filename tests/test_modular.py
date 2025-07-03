#!/usr/bin/env python3
"""
Test suite for the modular Fiji Automator package.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import our package
sys.path.insert(0, str(Path(__file__).parent.parent))

from fiji_automator import ThunderSTORMAutomator, FijiSetup, Config, ImageUtils, FileUtils


class TestConfig(unittest.TestCase):
    """Test cases for the Config module."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = Config()
    
    def test_initialization(self):
        """Test config initialization."""
        self.assertIsNotNone(self.config.platform)
        self.assertIn(self.config.platform, ['windows', 'darwin', 'linux'])
    
    def test_get_set_values(self):
        """Test getting and setting configuration values."""
        # Test setting a new value
        self.config.set('test.key', 'test_value')
        self.assertEqual(self.config.get('test.key'), 'test_value')
        
        # Test default value
        self.assertEqual(self.config.get('nonexistent.key', 'default'), 'default')
    
    def test_fiji_configuration(self):
        """Test Fiji-specific configuration."""
        fiji_urls = self.config.get_fiji_urls()
        self.assertIsInstance(fiji_urls, dict)
        self.assertIn(self.config.platform, fiji_urls)
        
        install_paths = self.config.get_fiji_install_paths()
        self.assertIsInstance(install_paths, list)
        self.assertGreater(len(install_paths), 0)
        
        default_dir = self.config.get_fiji_default_install_dir()
        self.assertIsInstance(default_dir, str)
        self.assertGreater(len(default_dir), 0)
    
    def test_thunderstorm_configuration(self):
        """Test ThunderSTORM-specific configuration."""
        api_url = self.config.get_thunderstorm_api_url()
        self.assertTrue(api_url.startswith('https://'))
        
        default_params = self.config.get_default_parameters()
        self.assertIsInstance(default_params, dict)
        self.assertIn('pixel_size', default_params)
        self.assertIn('gain', default_params)


class TestFileUtils(unittest.TestCase):
    """Test cases for the FileUtils module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_ensure_directory(self):
        """Test directory creation."""
        new_dir = self.test_dir / "new_directory"
        self.assertFalse(new_dir.exists())
        
        result = FileUtils.ensure_directory(new_dir)
        self.assertTrue(new_dir.exists())
        self.assertEqual(result, new_dir)
    
    def test_check_permissions(self):
        """Test permission checking."""
        # Should have permissions to our test directory
        self.assertTrue(FileUtils.check_permissions(self.test_dir))
        
        # Test with non-existent directory path - should fail
        fake_dir = self.test_dir / "nonexistent"
        self.assertFalse(FileUtils.check_permissions(fake_dir))  # Should fail for non-existent dir
    
    def test_sanitize_path(self):
        """Test path sanitization."""
        windows_path = r"C:\Users\test\file.txt"
        sanitized = FileUtils.sanitize_path(windows_path)
        self.assertEqual(sanitized, "C:/Users/test/file.txt")
    
    def test_find_files(self):
        """Test file finding."""
        # Create test files
        (self.test_dir / "test1.txt").touch()
        (self.test_dir / "test2.txt").touch()
        (self.test_dir / "other.log").touch()
        
        # Find .txt files
        txt_files = FileUtils.find_files(self.test_dir, "*.txt")
        self.assertEqual(len(txt_files), 2)
        
        # Find all files
        all_files = FileUtils.find_files(self.test_dir, "*")
        self.assertEqual(len(all_files), 3)
    
    def test_copy_and_remove_file(self):
        """Test file copying and removal."""
        # Create a test file
        source_file = self.test_dir / "source.txt"
        source_file.write_text("test content")
        
        # Copy file
        dest_file = self.test_dir / "dest.txt"
        self.assertTrue(FileUtils.copy_file(source_file, dest_file))
        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.read_text(), "test content")
        
        # Remove file
        self.assertTrue(FileUtils.remove_file(dest_file))
        self.assertFalse(dest_file.exists())


class TestImageUtils(unittest.TestCase):
    """Test cases for the ImageUtils module."""
    
    def test_validate_tiff_file(self):
        """Test TIFF file validation."""
        # Test with non-existent file
        self.assertFalse(ImageUtils.validate_tiff_file("/nonexistent/file.tif"))
        
        # Test with wrong extension
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.close()
        try:
            self.assertFalse(ImageUtils.validate_tiff_file(temp_file.name))
        finally:
            os.unlink(temp_file.name)
    
    def test_get_image_info(self):
        """Test getting image information."""
        # Test with non-existent file
        info = ImageUtils.get_image_info("/nonexistent/file.tif")
        self.assertFalse(info['exists'])
        self.assertEqual(info['size_bytes'], 0)
    
    def test_create_test_image(self):
        """Test test image creation."""
        try:
            test_image_path = ImageUtils.create_test_image(50, 50, 1)
            if test_image_path:
                self.assertTrue(test_image_path.exists())
                self.assertTrue(ImageUtils.validate_tiff_file(test_image_path))
                
                # Clean up
                test_image_path.unlink()
        except ImportError:
            self.skipTest("PIL/numpy not available for image creation")


class TestFijiSetup(unittest.TestCase):
    """Test cases for the FijiSetup module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.setup = FijiSetup(install_dir=str(self.test_dir))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test FijiSetup initialization."""
        self.assertEqual(self.setup.install_dir, self.test_dir)
        self.assertEqual(self.setup.fiji_dir, self.test_dir / "Fiji.app")
        self.assertEqual(self.setup.plugins_dir, self.test_dir / "Fiji.app" / "plugins")
    
    def test_check_permissions(self):
        """Test permission checking."""
        # Should have permissions to our test directory
        self.assertTrue(self.setup.check_permissions())
    
    def test_get_fiji_executable(self):
        """Test getting Fiji executable path."""
        exe_path = self.setup.get_fiji_executable()
        self.assertIsInstance(exe_path, (Path, type(None)))
        
        # Path should be platform-specific
        if exe_path:
            path_str = str(exe_path)
            if self.setup.platform == "windows":
                self.assertTrue(path_str.endswith(".exe"))
            elif self.setup.platform == "darwin":
                self.assertTrue("MacOS" in path_str)
    
    def test_get_thunderstorm_download_url(self):
        """Test getting ThunderSTORM download URL."""
        # This test requires internet connection
        try:
            url, filename = self.setup.get_thunderstorm_download_url()
            if url and filename:
                self.assertTrue(url.startswith("https://"))
                self.assertTrue(filename.endswith(".jar"))
        except Exception:
            self.skipTest("No internet connection or GitHub API unavailable")


class TestThunderSTORMAutomator(unittest.TestCase):
    """Test cases for the ThunderSTORMAutomator module."""
    
    def setUp(self):
        """Set up test environment."""
        # Try to create automator with existing Fiji installation
        try:
            self.automator = ThunderSTORMAutomator()
            self.fiji_available = True
        except FileNotFoundError:
            self.fiji_available = False
    
    def test_initialization_with_existing_fiji(self):
        """Test automator initialization with existing Fiji."""
        if not self.fiji_available:
            self.skipTest("Fiji not available")
        
        self.assertIsNotNone(self.automator.fiji_path)
        self.assertTrue(Path(self.automator.fiji_path).exists())
    
    def test_initialization_with_invalid_path(self):
        """Test automator initialization with invalid path."""
        with self.assertRaises(FileNotFoundError):
            ThunderSTORMAutomator(fiji_path="/nonexistent/path")
    
    def test_validate_input_file(self):
        """Test input file validation."""
        if not self.fiji_available:
            self.skipTest("Fiji not available")
        
        # Test with non-existent file
        self.assertFalse(self.automator.validate_input_file("/nonexistent/file.tif"))
    
    def test_get_image_info(self):
        """Test getting image information."""
        if not self.fiji_available:
            self.skipTest("Fiji not available")
        
        # Test with non-existent file
        info = self.automator.get_image_info("/nonexistent/file.tif")
        self.assertFalse(info['exists'])


class TestIntegrationWithTestFile(unittest.TestCase):
    """Integration tests using the test TIFF file."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_cases_dir = Path(__file__).parent.parent / "test_cases"
        self.output_dir = Path(tempfile.mkdtemp())
        
        # Find test TIFF files
        self.test_files = list(self.test_cases_dir.glob("*.tif*"))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
    
    def test_with_real_test_file(self):
        """Test with actual test TIFF file if available."""
        if not self.test_files:
            self.skipTest("No test TIFF files available")
        
        test_file = self.test_files[0]
        
        # Test image validation
        self.assertTrue(ImageUtils.validate_tiff_file(test_file))
        
        # Get image info
        img_info = ImageUtils.get_image_info(test_file)
        self.assertTrue(img_info['exists'])
        self.assertGreater(img_info['size_bytes'], 0)
        
        print(f"Test file: {test_file}")
        print(f"File size: {img_info['size_bytes'] / (1024*1024):.1f} MB")
        
        if 'width' in img_info and 'height' in img_info:
            print(f"Dimensions: {img_info['width']} x {img_info['height']} pixels")


def run_modular_tests():
    """Run all modular package tests."""
    print("Running Modular Fiji Automator Tests...")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConfig,
        TestFileUtils,
        TestImageUtils,
        TestFijiSetup,
        TestThunderSTORMAutomator,
        TestIntegrationWithTestFile
    ]
    
    for test_class in test_classes:
        suite.addTest(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_modular_tests()
    
    print("\n" + "=" * 50)
    print(f"Modular Tests: {'PASSED' if success else 'FAILED'}")
    print("=" * 50)
    
    sys.exit(0 if success else 1) 