"""
Konfigurasi dan konstanta untuk Piutang Visualizer
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Colors:
    """Konfigurasi warna"""
    # Warna status umur
    MERAH: Tuple[int, int, int] = (255, 150, 150)      # >= 75 hari
    KUNING: Tuple[int, int, int] = (255, 255, 200)     # >= 60 hari
    HIJAU: Tuple[int, int, int] = (200, 255, 200)      # < 60 hari
    
    # Warna UI
    BG: Tuple[int, int, int] = (255, 255, 255)
    HEADER_BG: Tuple[int, int, int] = (50, 50, 50)
    HEADER_TEXT: Tuple[int, int, int] = (255, 255, 255)
    TEXT: Tuple[int, int, int] = (0, 0, 0)
    BORDER: Tuple[int, int, int] = (100, 100, 100)
    TITLE: Tuple[int, int, int] = (0, 0, 100)
    INFO: Tuple[int, int, int] = (80, 80, 80)
    FOOTER: Tuple[int, int, int] = (150, 150, 150)
    
    # Warna status text
    STATUS_KRITIS: Tuple[int, int, int] = (200, 0, 0)
    STATUS_PERINGATAN: Tuple[int, int, int] = (200, 150, 0)
    STATUS_AMAN: Tuple[int, int, int] = (0, 150, 0)


@dataclass
class TableConfig:
    """Konfigurasi tabel"""
    PADDING: int = 20
    ROW_HEIGHT: int = 40
    HEADER_HEIGHT: int = 50
    COL_WIDTHS: Tuple[int, ...] = (50, 180, 150, 120, 100)  # Tambah kolom No.
    
    # HD Scale - faktor pengali untuk resolusi lebih tinggi
    HD_SCALE: float = 2.0  # 2x = 2x lebih besar (HD), 3x = 4K-ish
    
    @property
    def TABLE_WIDTH(self) -> int:
        return int((sum(self.COL_WIDTHS) + self.PADDING * 2) * self.HD_SCALE)
    
    def calculate_height(self, row_count: int) -> int:
        """Hitung tinggi tabel berdasarkan jumlah baris"""
        base_height = self.HEADER_HEIGHT + (row_count + 1) * self.ROW_HEIGHT + self.PADDING * 3
        return int(base_height * self.HD_SCALE)


@dataclass
class FontConfig:
    """Konfigurasi font - akan dikalikan HD_SCALE"""
    BASE_TITLE_SIZE: int = 18
    BASE_HEADER_SIZE: int = 14
    BASE_DATA_SIZE: int = 12
    BASE_BOLD_SIZE: int = 14
    
    TITLE_FONT: str = "arial.ttf"
    HEADER_FONT: str = "arial.ttf"
    DATA_FONT: str = "arial.ttf"
    BOLD_FONT: str = "arialbd.ttf"
    
    @property
    def TITLE_SIZE(self) -> int:
        return int(self.BASE_TITLE_SIZE * TABLE.HD_SCALE)
    
    @property
    def HEADER_SIZE(self) -> int:
        return int(self.BASE_HEADER_SIZE * TABLE.HD_SCALE)
    
    @property
    def DATA_SIZE(self) -> int:
        return int(self.BASE_DATA_SIZE * TABLE.HD_SCALE)
    
    @property
    def BOLD_SIZE(self) -> int:
        return int(self.BASE_BOLD_SIZE * TABLE.HD_SCALE)


@dataclass
class AgeThresholds:
    """Threshold umur piutang"""
    OVERDUE: int = 75       # >= 75 hari = Merah
    PAST_DUE: int = 60      # >= 60 hari = Kuning


@dataclass
class FuzzyConfig:
    """Konfigurasi fuzzy matching"""
    SCORE_THRESHOLD: int = 30
    MAX_RESULTS: int = 5
    SCORER = None  # Akan di-set di runtime


# Instance global
COLORS = Colors()
TABLE = TableConfig()
FONTS = FontConfig()
THRESHOLDS = AgeThresholds()
FUZZY = FuzzyConfig()

# Mapping kolom Excel
COLUMN_MAPPING = {
    'nama_pelanggan': ['nama pelanggan', 'pelanggan', 'customer name', 'customer'],
    'no_faktur': ['no. faktur', 'no faktur', 'nomor faktur', 'invoice', 'invoice no'],
    'tgl_faktur': ['tgl. faktur', 'tgl faktur', 'tanggal faktur', 'invoice date', 'date'],
    'piutang': ['piutang', 'total', 'amount', 'jumlah', 'nilai'],
    'umur': ['umur', 'umur (hr)', 'age', 'days', 'hari']
}

# Header tabel output
OUTPUT_HEADERS = ["No.", "No. Faktur", "Tgl. Faktur", "Piutang", "Umur (hr)"]
