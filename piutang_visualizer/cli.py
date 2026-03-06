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


class PiutangCLI:
    """CLI Handler untuk Piutang Visualizer"""
    
    def __init__(self):
        self.reader = ExcelReader()
        self.matcher = FuzzyMatcher()
        self.generator = PiutangImageGenerator()
        self.customer_data: List[dict] = []
    
    def _print_header(self):
        """Print header aplikasi"""
        print("=" * 60)
        print("   VISUALISASI PIUTANG PELANGGAN")
        print("=" * 60)
    
    def _select_file(self) -> str:
        """Pilih file Excel"""
        files = ExcelReader.find_excel_files()
        
        if not files:
            print("\n[!] Tidak ditemukan file .xlsx di direktori ini!")
            return input("Masukkan path file Excel: ").strip()
        
        if len(files) == 1:
            filepath = files[0]
            print(f"\n[FILE] File ditemukan: {filepath}")
            confirm = input("Gunakan file ini? (Y/n): ").strip().lower()
            if confirm == 'n':
                return input("Masukkan path file Excel: ").strip()
            return filepath
        
        # Multiple files
        print("\n[FILE] Beberapa file Excel ditemukan:")
        for i, f in enumerate(files, 1):
            print(f"  [{i}] {f}")
        
        choice = input("\nPilih nomor file (atau ketik 'manual'): ").strip()
        if choice.lower() == 'manual':
            return input("Masukkan path file Excel: ").strip()
        
        try:
            return files[int(choice) - 1]
        except (ValueError, IndexError):
            print("[!] Pilihan tidak valid, menggunakan file pertama.")
            return files[0]
    
    def _search_customer(self) -> Optional[str]:
        """Cari pelanggan dengan fuzzy matching"""
        query = input("\n[SEARCH] Cari nama pelanggan (atau 'exit'): ").strip()
        
        if query.lower() == 'exit':
            return None
        
        if not query:
            return self._search_customer()
        
        # Fuzzy search
        customers = self.reader.get_unique_customers()
        self.matcher.set_choices(customers)
        results = self.matcher.search(query)
        
        if not results:
            print("[WARNING] Tidak ditemukan hasil yang cocok.")
            return self._search_customer()
        
        # Display results
        print(f"\n[RESULT] Hasil pencarian untuk '{query}':")
        print("-" * 50)
        for i, (name, score) in enumerate(results[:FUZZY.MAX_RESULTS], 1):
            indicator = "[*]" if self.matcher.is_good_match(score) else "[ ]"
            # Bold nama pelanggan pakai ANSI escape code
            print(f"  {indicator} {i}. \033[1m{name}\033[0m (cocok: {score}%)")
        
        # Select customer
        choice = input("\nPilih nomor pelanggan: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx][0]
        except ValueError:
            pass
        
        print("[ERROR] Pilihan tidak valid!")
        return self._search_customer()
    
    def _generate_report(self, customer_name: str):
        """Generate laporan untuk pelanggan"""
        data = self.reader.filter_by_customer(customer_name)
        
        if not data:
            print("[WARNING] Tidak ada data piutang untuk pelanggan ini!")
            return
        
        print(f"\n[OK] Memilih: {customer_name}")
        print(f"[INFO] Ditemukan {len(data)} faktur")
        
        print("\n[GENERATE] Membuat gambar...")
        try:
            filename = self.generator.generate(data, customer_name)
            print(f"\n[OK] Gambar berhasil disimpan: {filename}")
        except Exception as e:
            print(f"[ERROR] Gagal generate gambar: {e}")
    
    def run(self):
        """Run CLI application"""
        self._print_header()
        
        # Select and load file
        filepath = self._select_file()
        
        print(f"\n[LOAD] Membaca data dari {filepath}...")
        try:
            self.reader.load(filepath).process()
            stats = self.reader.get_stats()
            print(f"[OK] Berhasil memuat {stats['total_rows']} baris data!")
            print(f"[INFO] Ditemukan {stats['unique_customers']} pelanggan unik")
        except Exception as e:
            print(f"[ERROR] Error membaca file: {e}")
            return
        
        # Main loop
        while True:
            print("\n" + "-" * 40)
            customer_name = self._search_customer()
            
            if customer_name is None:
                print("[BYE] Sampai jumpa!")
                break
            
            self._generate_report(customer_name)
            
            # Ask to continue
            again = input("\nCari pelanggan lain? (Y/n): ").strip().lower()
            if again == 'n':
                print("[BYE] Sampai jumpa!")
                break


def main():
    """Entry point"""
    try:
        cli = PiutangCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n[BYE] Program dihentikan.")
        sys.exit(0)


if __name__ == "__main__":
    main()
