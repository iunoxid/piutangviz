"""
API/Programmatic interface untuk Piutang Visualizer
Contoh penggunaan tanpa CLI
"""

from typing import List, Dict, Any, Optional
from .excel_reader import ExcelReader
from .fuzzy_matcher import FuzzyMatcher
from .image_generator import PiutangImageGenerator


class PiutangVisualizerAPI:
    """
    API untuk menggunakan Piutang Visualizer secara programmatic
    
    Contoh penggunaan:
        from piutang_visualizer import PiutangVisualizerAPI
        
        api = PiutangVisualizerAPI()
        api.load_file("data.xlsx")
        
        # Cari pelanggan
        customers = api.search_customers("Agung")
        
        # Generate gambar
        api.generate_report("Agung 2 Gresik", output_path="report.png")
    """
    
    def __init__(self):
        self.reader = ExcelReader()
        self.matcher = FuzzyMatcher()
        self.generator = PiutangImageGenerator()
        self._is_loaded = False
    
    def load_file(self, filepath: str) -> 'PiutangVisualizerAPI':
        """
        Load file Excel
        
        Args:
            filepath: Path ke file Excel
        
        Returns:
            Self untuk method chaining
        """
        self.reader.load(filepath).process()
        self.matcher.set_choices(self.reader.get_unique_customers())
        self._is_loaded = True
        return self
    
    def get_all_customers(self) -> List[str]:
        """Dapatkan semua nama pelanggan"""
        self._ensure_loaded()
        return self.reader.get_unique_customers()
    
    def search_customers(self, query: str, limit: int = 5) -> List[tuple]:
        """
        Cari pelanggan dengan fuzzy matching
        
        Args:
            query: Kata kunci pencarian
            limit: Jumlah hasil maksimal
        
        Returns:
            List of tuples (customer_name, score)
        """
        self._ensure_loaded()
        return self.matcher.search(query, limit=limit)
    
    def get_customer_data(self, customer_name: str) -> List[Dict[str, Any]]:
        """
        Dapatkan data piutang untuk pelanggan tertentu
        
        Args:
            customer_name: Nama pelanggan (harus exact match)
        
        Returns:
            List data piutang
        """
        self._ensure_loaded()
        return self.reader.filter_by_customer(customer_name)
    
    def generate_report(
        self, 
        customer_name: str, 
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate gambar laporan piutang
        
        Args:
            customer_name: Nama pelanggan
            output_path: Path output (optional)
        
        Returns:
            Path file gambar yang tersimpan
        """
        self._ensure_loaded()
        data = self.get_customer_data(customer_name)
        
        if not data:
            raise ValueError(f"Tidak ada data untuk pelanggan: {customer_name}")
        
        return self.generator.generate(data, customer_name, output_path)
    
    def get_summary(self, customer_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Dapatkan ringkasan data
        
        Args:
            customer_name: Nama pelanggan (optional, jika None = semua data)
        
        Returns:
            Dictionary summary
        """
        self._ensure_loaded()
        
        if customer_name:
            data = self.get_customer_data(customer_name)
        else:
            data = self.reader.processed_data
        
        if not data:
            return {}
        
        total_piutang = sum(item['piutang'] for item in data)
        
        # Hitung per kategori umur
        kritis = sum(1 for item in data if item['umur'] >= 75)
        peringatan = sum(1 for item in data if 60 <= item['umur'] < 75)
        aman = sum(1 for item in data if item['umur'] < 60)
        
        return {
            'customer': customer_name or 'ALL',
            'total_faktur': len(data),
            'total_piutang': total_piutang,
            'piutang_formatted': f"Rp {total_piutang:,.0f}".replace(',', '.'),
            'kategori': {
                'kritis': kritis,
                'peringatan': peringatan,
                'aman': aman
            }
        }
    
    def _ensure_loaded(self):
        """Pastikan file sudah di-load"""
        if not self._is_loaded:
            raise RuntimeError("File belum di-load. Panggil load_file() terlebih dahulu.")


# Convenience function untuk quick usage
def quick_generate(
    excel_path: str, 
    customer_query: str, 
    output_path: Optional[str] = None
) -> str:
    """
    Quick generate gambar tanpa setup
    
    Args:
        excel_path: Path file Excel
        customer_query: Nama/kata kunci pelanggan
        output_path: Path output (optional)
    
    Returns:
        Path file gambar
    
    Example:
        from piutang_visualizer import quick_generate
        quick_generate("data.xlsx", "Agung 2", "output.png")
    """
    api = PiutangVisualizerAPI()
    api.load_file(excel_path)
    
    # Search customer
    results = api.search_customers(customer_query, limit=1)
    if not results:
        raise ValueError(f"Pelanggan tidak ditemukan: {customer_query}")
    
    customer_name = results[0][0]
    return api.generate_report(customer_name, output_path)
