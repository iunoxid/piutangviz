"""
Piutang Visualizer - Modul untuk visualisasi data piutang pelanggan

Usage:
    # CLI Mode
    from piutang_visualizer.cli import main
    main()
    
    # API Mode
    from piutang_visualizer import PiutangVisualizerAPI, quick_generate
    
    api = PiutangVisualizerAPI()
    api.load_file("data.xlsx")
    api.generate_report("Nama Pelanggan")
    
    # Atau quick generate
    quick_generate("data.xlsx", "Nama Pelanggan", "output.png")
"""

__version__ = "1.0.0"
__author__ = "Piutang Visualizer"

# Export main classes untuk convenient import
from .api import PiutangVisualizerAPI, quick_generate
from .excel_reader import ExcelReader
from .fuzzy_matcher import FuzzyMatcher
from .image_generator import PiutangImageGenerator

__all__ = [
    'PiutangVisualizerAPI',
    'quick_generate',
    'ExcelReader',
    'FuzzyMatcher',
    'PiutangImageGenerator',
]
