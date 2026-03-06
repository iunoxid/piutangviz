"""
Command Line Interface untuk Piutang Visualizer
"""

import os
import sys
from typing import List, Optional

from .config import FUZZY
from .excel_reader import ExcelReader
from .fuzzy_matcher import FuzzyMatcher
from .image_generator import PiutangImageGenerator


class Colors:
    """ANSI Color codes untuk terminal"""
    # Reset
    RESET = "\033[0m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    
    @staticmethod
    def disable():
        """Disable colors (untuk terminal yang tidak support)"""
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')


class PiutangCLI:
    """CLI Handler untuk Piutang Visualizer"""
    
    def __init__(self):
        self.reader = ExcelReader()
        self.matcher = FuzzyMatcher()
        self.generator = PiutangImageGenerator()
        self.customer_data: List[dict] = []
    
    def _print_header(self):
        """Print header aplikasi dengan warna"""
        print(Colors.CYAN + "=" * 60 + Colors.RESET)
        print(Colors.BOLD + Colors.BRIGHT_CYAN + "   📊 VISUALISASI PIUTANG PELANGGAN" + Colors.RESET)
        print(Colors.CYAN + "=" * 60 + Colors.RESET)
    
    def _select_file(self) -> str:
        """Pilih file Excel"""
        files = ExcelReader.find_excel_files()
        
        if not files:
            print(Colors.BRIGHT_RED + "\n[!] Tidak ditemukan file .xlsx di direktori ini!" + Colors.RESET)
            return input(Colors.YELLOW + "Masukkan path file Excel: " + Colors.RESET).strip()
        
        if len(files) == 1:
            filepath = files[0]
            print(Colors.BRIGHT_GREEN + f"\n[FILE] File ditemukan: " + Colors.RESET + Colors.BOLD + filepath + Colors.RESET)
            confirm = input(Colors.YELLOW + "Gunakan file ini? (Y/n): " + Colors.RESET).strip().lower()
            if confirm == 'n':
                return input(Colors.YELLOW + "Masukkan path file Excel: " + Colors.RESET).strip()
            return filepath
        
        # Multiple files
        print(Colors.BRIGHT_BLUE + "\n[FILE] Beberapa file Excel ditemukan:" + Colors.RESET)
        for i, f in enumerate(files, 1):
            print(f"  {Colors.BRIGHT_CYAN}[{i}]{Colors.RESET} {f}")
        
        choice = input(Colors.YELLOW + "\nPilih nomor file (atau ketik 'manual'): " + Colors.RESET).strip()
        if choice.lower() == 'manual':
            return input(Colors.YELLOW + "Masukkan path file Excel: " + Colors.RESET).strip()
        
        try:
            return files[int(choice) - 1]
        except (ValueError, IndexError):
            print(Colors.BRIGHT_RED + "[!] Pilihan tidak valid, menggunakan file pertama." + Colors.RESET)
            return files[0]
    
    def _search_customer(self) -> Optional[str]:
        """Cari pelanggan dengan fuzzy matching"""
        query = input(Colors.YELLOW + "\n[SEARCH] " + Colors.RESET + "Cari nama pelanggan (atau '" + Colors.BRIGHT_RED + "exit" + Colors.RESET + "'): ").strip()
        
        if query.lower() == 'exit':
            return None
        
        if not query:
            return self._search_customer()
        
        # Fuzzy search
        customers = self.reader.get_unique_customers()
        self.matcher.set_choices(customers)
        results = self.matcher.search(query)
        
        if not results:
            print(Colors.BRIGHT_RED + "[WARNING] Tidak ditemukan hasil yang cocok." + Colors.RESET)
            return self._search_customer()
        
        # Display results
        print(Colors.BRIGHT_GREEN + f"\n[RESULT] Hasil pencarian untuk '{Colors.BOLD}{query}{Colors.RESET}{Colors.BRIGHT_GREEN}':" + Colors.RESET)
        print(Colors.DIM + "-" * 50 + Colors.RESET)
        for i, (name, score) in enumerate(results[:FUZZY.MAX_RESULTS], 1):
            if self.matcher.is_good_match(score):
                indicator = Colors.BRIGHT_GREEN + "[✓]" + Colors.RESET
                score_color = Colors.BRIGHT_GREEN
            else:
                indicator = Colors.DIM + "[ ]" + Colors.RESET
                score_color = Colors.YELLOW
            
            print(f"  {indicator} {Colors.BRIGHT_CYAN}{i}.{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET} ({score_color}cocok: {score}%{Colors.RESET})")
        
        # Select customer
        choice = input(Colors.YELLOW + "\nPilih nomor pelanggan: " + Colors.RESET).strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx][0]
        except ValueError:
            pass
        
        print(Colors.BRIGHT_RED + "[ERROR] Pilihan tidak valid!" + Colors.RESET)
        return self._search_customer()
    
    def _generate_report(self, customer_name: str):
        """Generate laporan untuk pelanggan"""
        data = self.reader.filter_by_customer(customer_name)
        
        if not data:
            print(Colors.BRIGHT_YELLOW + "[WARNING] Tidak ada data piutang untuk pelanggan ini!" + Colors.RESET)
            return
        
        print(Colors.BRIGHT_GREEN + f"\n[OK] Memilih: " + Colors.RESET + Colors.BOLD + customer_name + Colors.RESET)
        
        # Hitung total piutang
        total_piutang = sum(item['piutang'] for item in data)
        total_formatted = f"Rp {total_piutang:,.0f}".replace(',', '.')
        
        print(f"{Colors.CYAN}[INFO]{Colors.RESET} Ditemukan {Colors.BRIGHT_CYAN}{len(data)}{Colors.RESET} faktur | Total: {Colors.BRIGHT_GREEN}{total_formatted}{Colors.RESET}")
        
        # Show warning untuk yang kritis
        kritis_count = sum(1 for item in data if item['umur'] >= 75)
        if kritis_count > 0:
            print(f"{Colors.BRIGHT_RED}[ALERT]{Colors.RESET} Ada {Colors.BOLD}{kritis_count}{Colors.RESET} faktur {Colors.BRIGHT_RED}KRITIS (≥75 hari)!{Colors.RESET}")
        
        print(Colors.BRIGHT_MAGENTA + "\n[GENERATE] Membuat gambar..." + Colors.RESET)
        try:
            filename = self.generator.generate(data, customer_name)
            print(Colors.BRIGHT_GREEN + f"\n[OK] Gambar berhasil disimpan: " + Colors.RESET + Colors.BOLD + filename + Colors.RESET)
        except Exception as e:
            print(Colors.BRIGHT_RED + f"[ERROR] Gagal generate gambar: {e}" + Colors.RESET)
    
    def run(self):
        """Run CLI application"""
        self._print_header()
        
        # Select and load file
        filepath = self._select_file()
        
        print(Colors.BRIGHT_BLUE + f"\n[LOAD] Membaca data dari " + Colors.RESET + filepath)
        try:
            self.reader.load(filepath).process()
            stats = self.reader.get_stats()
            print(Colors.BRIGHT_GREEN + f"[OK] Berhasil memuat {Colors.BOLD}{stats['total_rows']}{Colors.RESET}{Colors.BRIGHT_GREEN} baris data!" + Colors.RESET)
            print(Colors.CYAN + f"[INFO] Ditemukan {Colors.BRIGHT_CYAN}{stats['unique_customers']}{Colors.RESET}{Colors.CYAN} pelanggan unik" + Colors.RESET)
        except Exception as e:
            print(Colors.BRIGHT_RED + f"[ERROR] Error membaca file: {e}" + Colors.RESET)
            return
        
        # Main loop
        while True:
            print(Colors.DIM + "\n" + "-" * 40 + Colors.RESET)
            customer_name = self._search_customer()
            
            if customer_name is None:
                print(Colors.BRIGHT_CYAN + "[BYE] Sampai jumpa! 👋" + Colors.RESET)
                break
            
            self._generate_report(customer_name)
            
            # Ask to continue
            again = input(Colors.YELLOW + "\nCari pelanggan lain? (Y/n): " + Colors.RESET).strip().lower()
            if again == 'n':
                print(Colors.BRIGHT_CYAN + "[BYE] Sampai jumpa! 👋" + Colors.RESET)
                break


def main():
    """Entry point"""
    try:
        cli = PiutangCLI()
        cli.run()
    except KeyboardInterrupt:
        print(Colors.BRIGHT_YELLOW + "\n\n[BYE] Program dihentikan." + Colors.RESET)
        sys.exit(0)


if __name__ == "__main__":
    main()
