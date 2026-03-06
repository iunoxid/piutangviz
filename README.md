# Piutang Visualizer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Piutang Visualizer** adalah tool Python untuk memvisualisasikan data piutang pelanggan dari file Excel. Tool ini secara otomatis generate gambar tabel dengan kode warna berdasarkan umur piutang.

## 🎯 Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📁 **Auto-detect Excel** | Mendeteksi otomatis file `.xlsx` di direktori |
| 🔍 **Fuzzy Search** | Pencarian pelanggan dengan fuzzy matching (toleran typo) |
| 🎨 **Warna Status** | Visualisasi warna berdasarkan umur piutang |
| 🖼️ **HD Output** | Gambar HD dengan scaling 2x untuk kualitas tinggi |
| 💻 **Dual Mode** | Bisa digunakan via CLI atau API programmatic |

### Kode Warna Status

| Warna | Umur Piutang | Status |
|-------|--------------|--------|
| 🔴 **Merah** | ≥ 75 hari | KRITIS |
| 🟡 **Kuning** | ≥ 60 hari | PAST DUE |
| 🟢 **Hijau** | < 60 hari | CURRENT |

## 📋 Prasyarat

- Python 3.8 atau lebih baru
- Windows/Linux/MacOS

## 🚀 Instalasi

1. **Clone atau download repository:**
```bash
git clone <repo-url>
cd piutang_visualizer
```

2. **Buat virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 📖 Cara Penggunaan

### Mode CLI (Interactive)

```bash
# Jalankan CLI interaktif
python main.py

# Atau dengan file spesifik
python main.py data.xlsx
```

**Alur CLI:**
1. Pilih file Excel (auto-detect atau manual input)
2. Cari nama pelanggan (fuzzy search)
3. Pilih pelanggan dari hasil pencarian
4. Gambar tabel otomatis tersimpan sebagai PNG

### Mode API (Programmatic)

```python
from piutang_visualizer import PiutangVisualizerAPI, quick_generate

# Method 1: Menggunakan API Class
api = PiutangVisualizerAPI()
api.load_file("data.xlsx")

# Cari pelanggan
results = api.search_customers("Agung", limit=5)
print(results)  # [('Agung 2 Gresik', 95), ...]

# Generate gambar
api.generate_report("Agung 2 Gresik", "output.png")

# Get summary
summary = api.get_summary("Agung 2 Gresik")
print(summary)

# Method 2: Quick generate (one-liner)
from piutang_visualizer import quick_generate
quick_generate("data.xlsx", "Agung", "report.png")
```

## 📁 Format File Excel

Tool ini mendukung auto-deteksi kolom dengan berbagai nama header:

| Kolom | Variasi Nama yang Didukung |
|-------|---------------------------|
| Nama Pelanggan | `nama pelanggan`, `pelanggan`, `customer name`, `customer` |
| No. Faktur | `no. faktur`, `no faktur`, `nomor faktur`, `invoice` |
| Tgl. Faktur | `tgl. faktur`, `tgl faktur`, `tanggal faktur`, `invoice date` |
| Piutang | `piutang`, `total`, `amount`, `jumlah`, `nilai` |
| Umur | `umur`, `umur (hr)`, `age`, `days`, `hari` |

### Contoh Struktur Excel:

| Nama Pelanggan | No. Faktur | Tgl. Faktur | Piutang | Umur (hr) |
|----------------|------------|-------------|---------|-----------|
| PT ABC | INV001 | 2024-01-15 | 5000000 | 45 |
| PT XYZ | INV002 | 2024-01-01 | 7500000 | 85 |

## 📂 Struktur Project

```
piutang_visualizer/
├── main.py                      # Entry point CLI
├── requirements.txt             # Dependencies
├── README.md                    # Dokumentasi
├── .gitignore                   # Git ignore rules
├── piutang_visualizer/          # Main package
│   ├── __init__.py              # Package exports
│   ├── api.py                   # API/Programmatic interface
│   ├── cli.py                   # Command Line Interface
│   ├── config.py                # Konfigurasi & konstanta
│   ├── excel_reader.py          # Excel file reader
│   ├── fuzzy_matcher.py         # Fuzzy string matching
│   └── image_generator.py       # Image generation (PIL)
└── venv/                        # Virtual environment
```

## ⚙️ Konfigurasi

Konfigurasi dapat dimodifikasi di `piutang_visualizer/config.py`:

```python
# Threshold umur piutang (hari)
OVERDUE = 75       # >= 75 = Merah
PAST_DUE = 60      # >= 60 = Kuning

# Fuzzy matching
SCORE_THRESHOLD = 30    # Minimum score match
MAX_RESULTS = 5         # Jumlah hasil pencarian

# HD Scale (2x = HD, 3x = 4K)
HD_SCALE = 2.0
```

## 📦 Dependencies

| Package | Versi | Kegunaan |
|---------|-------|----------|
| `openpyxl` | >=3.0.0 | Membaca file Excel |
| `Pillow` | >=9.0.0 | Generate gambar |
| `thefuzz` | >=0.19.0 | Fuzzy string matching |
| `python-Levenshtein` | >=0.12.0 | Optimasi fuzzy matching |

## 📝 Contoh Output

Gambar yang dihasilkan memiliki format:
- **Filename:** `{Nama_Pelanggan}_{timestamp}.png`
- **Resolusi:** HD (2x scale)
- **Konten:**
  - Header nama pelanggan (bold)
  - Info total piutang & jumlah faktur
  - Tabel dengan kolom: No, No. Faktur, Tgl. Faktur, Piutang, Umur
  - Legend warna status
  - Timestamp generate

## 🤝 Contributing

1. Fork repository
2. Buat branch fitur (`git checkout -b feature/amazing-feature`)
3. Commit perubahan (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` untuk informasi lebih lanjut.

---

<p align="center">Made with ❤️ for easier debt visualization</p>
