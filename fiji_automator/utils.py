"""
Utility functions for Fiji Automator.

Contains helper functions for file operations, image processing, and other common tasks.
"""

import os
import shutil
import tempfile
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import List, Optional, Tuple, Union
import json
import platform
import subprocess


class FileUtils:
    """
    Utility class for file operations.
    """
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path (Union[str, Path]): Directory path
            
        Returns:
            Path: Path object for the directory
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def download_file(url: str, dest_path: Union[str, Path], 
                     description: str = "file", 
                     show_progress: bool = True) -> bool:
        """
        Download a file with optional progress indication.
        
        Args:
            url (str): URL to download from
            dest_path (Union[str, Path]): Destination path for the file
            description (str): Description of what's being downloaded
            show_progress (bool): Whether to show progress
            
        Returns:
            bool: True if successful, False otherwise
        """
        dest_path = Path(dest_path)
        
        if show_progress:
            print(f"Downloading {description} from {url}")
        
        def progress_hook(block_num, block_size, total_size):
            if show_progress and total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\rProgress: {percent}%", end="", flush=True)
        
        try:
            urllib.request.urlretrieve(url, dest_path, 
                                     reporthook=progress_hook if show_progress else None)
            if show_progress:
                print(f"\n✓ Downloaded {description} successfully")
            return True
        except Exception as e:
            if show_progress:
                print(f"\n✗ Failed to download {description}: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path: Union[str, Path], 
                       extract_to: Union[str, Path], 
                       description: str = "archive") -> bool:
        """
        Extract zip or tar archive.
        
        Args:
            archive_path (Union[str, Path]): Path to the archive file
            extract_to (Union[str, Path]): Directory to extract to
            description (str): Description of what's being extracted
            
        Returns:
            bool: True if successful, False otherwise
        """
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)
        
        print(f"Extracting {description}...")
        
        try:
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix.lower() in ['.tar', '.tgz', '.tar.gz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
            
            print(f"✓ Extracted {description} successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to extract {description}: {e}")
            return False
    
    @staticmethod
    def check_permissions(path: Union[str, Path]) -> bool:
        """
        Check if we have write permissions to a directory.
        
        Args:
            path (Union[str, Path]): Directory path to check
            
        Returns:
            bool: True if we have write permissions, False otherwise
        """
        path = Path(path)
        try:
            # Try to create a test file
            test_file = path / "test_write_permission.tmp"
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False
    
    @staticmethod
    def sanitize_path(path: Union[str, Path]) -> str:
        """
        Sanitize a path for use in ImageJ macros (use forward slashes).
        
        Args:
            path (Union[str, Path]): Path to sanitize
            
        Returns:
            str: Sanitized path string
        """
        return str(Path(path)).replace('\\', '/')
    
    @staticmethod
    def find_files(directory: Union[str, Path], pattern: str) -> List[Path]:
        """
        Find files matching a pattern in a directory.
        
        Args:
            directory (Union[str, Path]): Directory to search in
            pattern (str): Glob pattern to match
            
        Returns:
            List[Path]: List of matching file paths
        """
        directory = Path(directory)
        if not directory.exists():
            return []
        
        return list(directory.glob(pattern))
    
    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            src (Union[str, Path]): Source file path
            dst (Union[str, Path]): Destination file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    @staticmethod
    def remove_file(path: Union[str, Path]) -> bool:
        """
        Remove a file.
        
        Args:
            path (Union[str, Path]): File path to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            Path(path).unlink()
            return True
        except Exception as e:
            print(f"Error removing file: {e}")
            return False


class ImageUtils:
    """
    Utility class for image operations.
    """
    
    @staticmethod
    def validate_tiff_file(path: Union[str, Path]) -> bool:
        """
        Validate that a file is a valid TIFF file.
        
        Args:
            path (Union[str, Path]): Path to the TIFF file
            
        Returns:
            bool: True if valid TIFF, False otherwise
        """
        path = Path(path)
        
        # Check file exists and has correct extension
        if not path.exists():
            return False
        
        if path.suffix.lower() not in ['.tif', '.tiff']:
            return False
        
        # Try to read the file header
        try:
            with open(path, 'rb') as f:
                # Read first 4 bytes to check TIFF magic number
                magic = f.read(4)
                # TIFF files start with either 'II*\x00' (little-endian) or 'MM\x00*' (big-endian)
                if magic[:2] in [b'II', b'MM'] and magic[2:4] in [b'*\x00', b'\x00*']:
                    return True
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def get_image_info(path: Union[str, Path]) -> dict:
        """
        Get basic information about an image file.
        
        Args:
            path (Union[str, Path]): Path to the image file
            
        Returns:
            dict: Dictionary with image information
        """
        path = Path(path)
        info = {
            'path': str(path),
            'exists': path.exists(),
            'size_bytes': path.stat().st_size if path.exists() else 0,
            'valid_tiff': False
        }
        
        if path.exists():
            info['valid_tiff'] = ImageUtils.validate_tiff_file(path)
            
            # Try to get more detailed info using PIL if available
            try:
                from PIL import Image
                with Image.open(path) as img:
                    info.update({
                        'width': img.width,
                        'height': img.height,
                        'mode': img.mode,
                        'format': img.format,
                        'n_frames': getattr(img, 'n_frames', 1)
                    })
            except ImportError:
                info['pil_unavailable'] = True
                print("Warning: PIL/Pillow not available for detailed image info")
            except Exception as e:
                info['error'] = str(e)
                print(f"Warning: Could not get detailed image info: {e}")
        
        return info
    
    @staticmethod
    def create_test_image(width: int = 100, height: int = 100, 
                         n_frames: int = 1) -> Optional[Path]:
        """
        Create a test TIFF image for testing purposes.
        
        Args:
            width (int): Image width in pixels
            height (int): Image height in pixels
            n_frames (int): Number of frames
            
        Returns:
            Optional[Path]: Path to created test image, or None if failed
        """
        try:
            import numpy as np
            from PIL import Image
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            if n_frames == 1:
                # Single frame image
                test_image = np.random.randint(0, 255, (height, width), dtype=np.uint8)
                Image.fromarray(test_image).save(temp_path)
            else:
                # Multi-frame image
                images = []
                for i in range(n_frames):
                    frame = np.random.randint(0, 255, (height, width), dtype=np.uint8)
                    images.append(Image.fromarray(frame))
                
                # Save as multi-page TIFF
                images[0].save(temp_path, save_all=True, append_images=images[1:])
            
            return temp_path
            
        except ImportError:
            print("PIL/Pillow and numpy required for test image creation")
            return None
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None


class ProcessUtils:
    """
    Utility class for process operations.
    """
    
    @staticmethod
    def run_command(cmd: List[str], 
                   timeout: int = 300, 
                   capture_output: bool = True,
                   cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run a command and return the result.
        
        Args:
            cmd (List[str]): Command to run
            timeout (int): Timeout in seconds
            capture_output (bool): Whether to capture output
            cwd (Optional[str]): Working directory
            
        Returns:
            Tuple[int, str, str]: Return code, stdout, stderr
        """
        try:
            result = subprocess.run(
                cmd, 
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                cwd=cwd
            )
            return result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.TimeoutExpired:
            return -1, "", "Process timed out"
        except Exception as e:
            return -1, "", str(e)
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Check if a process is running.
        
        Args:
            process_name (str): Name of the process to check
            
        Returns:
            bool: True if process is running, False otherwise
        """
        try:
            system = platform.system().lower()
            if system == "windows":
                cmd = ["tasklist", "/FI", f"IMAGENAME eq {process_name}"]
            else:
                cmd = ["pgrep", "-f", process_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and process_name in result.stdout
        except Exception:
            return False


class ConfigUtils:
    """
    Utility class for configuration operations.
    """
    
    @staticmethod
    def load_json(path: Union[str, Path]) -> dict:
        """
        Load JSON configuration from file.
        
        Args:
            path (Union[str, Path]): Path to JSON file
            
        Returns:
            dict: Loaded configuration
        """
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {path}: {e}")
            return {}
    
    @staticmethod
    def save_json(data: dict, path: Union[str, Path]) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data (dict): Data to save
            path (Union[str, Path]): Path to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON to {path}: {e}")
            return False 