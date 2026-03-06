#!/usr/bin/env python3
"""
Piutang Visualizer - Main Entry Point

Script untuk visualisasi piutang pelanggan dari file Excel.
Warna otomatis: >=75 hari = Merah, >=60 hari = Kuning

Usage:
    python main.py                    # Jalankan CLI interaktif
    python main.py data.xlsx          # Auto-detect file

Features:
    - Auto-detect file Excel (.xlsx)
    - Fuzzy matching untuk pencarian pelanggan
    - Generate gambar tabel dengan warna status
    - Modular dan extensible
"""

import sys
from pathlib import Path

# Add current directory to path untuk import module
sys.path.insert(0, str(Path(__file__).parent))

from piutang_visualizer.cli import main

if __name__ == "__main__":
    main()
