"""
Fiji Automator Package

A Python package for automated ThunderSTORM analysis using Fiji/ImageJ.
"""

from .core import ThunderSTORMAutomator
from .setup import FijiSetup
from .config import Config
from .utils import ImageUtils, FileUtils

__version__ = "1.2.0"
__author__ = "Fiji Automator Team"
__email__ = "support@fiji-automator.com"

__all__ = [
    'ThunderSTORMAutomator',
    'FijiSetup', 
    'Config',
    'ImageUtils',
    'FileUtils'
] 