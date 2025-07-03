"""
Configuration module for Fiji Automator.

Handles configuration management, default parameters, and platform-specific settings.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Config:
    """
    Configuration management for Fiji Automator.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file (str, optional): Path to custom configuration file
        """
        self.platform = platform.system().lower()
        self.config_file = config_file
        self.config = self._load_default_config()
        
        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration settings.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            "fiji": {
                "urls": {
                    "windows": "https://downloads.imagej.net/fiji/latest/fiji-win64.zip",
                    "darwin": "https://downloads.imagej.net/fiji/latest/fiji-macosx.zip",
                    "linux": "https://downloads.imagej.net/fiji/latest/fiji-linux64.zip"
                },
                "install_paths": {
                    "windows": [
                        r"C:\Program Files\Fiji.app\ImageJ-win64.exe",
                        r"C:\Program Files (x86)\Fiji.app\ImageJ-win64.exe",
                        str(Path.home() / "Fiji.app" / "ImageJ-win64.exe"),
                        str(Path.home() / "Desktop" / "Fiji.app" / "ImageJ-win64.exe")
                    ],
                    "darwin": [
                        "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx",
                        "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx64",
                        str(Path.home() / "Applications" / "Fiji.app" / "Contents" / "MacOS" / "ImageJ-macosx")
                    ],
                    "linux": [
                        str(Path.home() / "Fiji.app" / "ImageJ-linux64"),
                        "/opt/Fiji.app/ImageJ-linux64"
                    ]
                },
                "default_install_dirs": {
                    "windows": os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                    "darwin": "/Applications",
                    "linux": str(Path.home())
                }
            },
            "thunderstorm": {
                "github_api_url": "https://api.github.com/repos/zitmen/thunderstorm/releases/latest",
                "default_parameters": {
                    "pixel_size": 100.0,
                    "gain": 100.0,
                    "offset": 100.0,
                    "processing_method": "Wavelet filter (B-Spline)",
                    "localization_method": "PSF: Integrated Gaussian",
                    "sigma": 1.6,
                    "fitting_radius": 3,
                    "threshold_offset": 500,
                    "create_reconstructed_image": True
                }
            },
            "analysis": {
                "timeout": 300,  # 5 minutes
                "output_files": [
                    "results.csv",
                    "reconstructed_image.tif",
                    "thunderstorm_macro.ijm"
                ]
            }
        }
    
    def _load_config_file(self, config_file: str):
        """
        Load configuration from JSON file.
        
        Args:
            config_file (str): Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                self._merge_config(custom_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _merge_config(self, custom_config: Dict[str, Any]):
        """
        Merge custom configuration with default configuration.
        
        Args:
            custom_config (Dict[str, Any]): Custom configuration to merge
        """
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, custom_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'fiji.urls.windows')
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'fiji.urls.windows')
            value (Any): Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_fiji_urls(self) -> Dict[str, str]:
        """Get Fiji download URLs for all platforms."""
        return self.get('fiji.urls', {})
    
    def get_fiji_install_paths(self, platform: Optional[str] = None) -> list:
        """Get Fiji installation paths for the specified platform."""
        platform = platform or self.platform
        return self.get(f'fiji.install_paths.{platform}', [])
    
    def get_fiji_default_install_dir(self, platform: Optional[str] = None) -> str:
        """Get default Fiji installation directory for the specified platform."""
        platform = platform or self.platform
        return self.get(f'fiji.default_install_dirs.{platform}', str(Path.home()))
    
    def get_thunderstorm_api_url(self) -> str:
        """Get ThunderSTORM GitHub API URL."""
        return self.get('thunderstorm.github_api_url', '')
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default ThunderSTORM analysis parameters."""
        return self.get('thunderstorm.default_parameters', {})
    
    def get_analysis_timeout(self) -> int:
        """Get analysis timeout in seconds."""
        return self.get('analysis.timeout', 300)
    
    def get_expected_output_files(self) -> list:
        """Get list of expected output files from analysis."""
        return self.get('analysis.output_files', [])
    
    def save_config(self, config_file: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            config_file (str, optional): Path to save configuration file
        """
        config_file = config_file or self.config_file or "config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def print_config(self):
        """Print current configuration."""
        print(json.dumps(self.config, indent=2))


# Global configuration instance
_config = None

def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_file (str, optional): Path to configuration file
        
    Returns:
        Config: Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config 