"""
Module untuk generate gambar tabel piutang
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from .config import (
    COLORS, TABLE, FONTS, OUTPUT_HEADERS
)


class FontManager:
    """Manager untuk loading font"""
    
    def __init__(self):
        self._fonts = {}
        self._load_fonts()
    
    def _load_fonts(self):
        """Load semua font yang dibutuhkan"""
        font_configs = [
            ('title', FONTS.TITLE_FONT, FONTS.TITLE_SIZE),
            ('header', FONTS.HEADER_FONT, FONTS.HEADER_SIZE),
            ('data', FONTS.DATA_FONT, FONTS.DATA_SIZE),
            ('bold', FONTS.BOLD_FONT, FONTS.BOLD_SIZE),
        ]
        
        for name, font_file, size in font_configs:
            try:
                self._fonts[name] = ImageFont.truetype(font_file, size)
            except OSError:
                # Fallback ke default font
                self._fonts[name] = ImageFont.load_default()
    
    def get(self, name: str) -> ImageFont:
        """Get font by name"""
        return self._fonts.get(name, self._fonts.get('data'))


class PiutangImageGenerator:
    """Generator untuk gambar tabel piutang"""
    
    def __init__(self):
        self.fonts = FontManager()
    
    def _s(self, value: int) -> int:
        """Scale value berdasarkan HD_SCALE"""
        return int(value * TABLE.HD_SCALE)
    
    def _get_row_color(self, umur: int) -> Tuple[int, int, int]:
        """Dapatkan warna baris berdasarkan umur"""
        if umur >= 75:
            return COLORS.MERAH
        elif umur >= 60:
            return COLORS.KUNING
        return COLORS.BG  # Putih/tanpa warna untuk yang < 60 hari
    
    def _get_status(self, umur: int) -> Tuple[str, Tuple[int, int, int]]:
        """Dapatkan status dan warna text berdasarkan umur"""
        if umur >= THRESHOLDS.OVERDUE:
            return "OVERDUE", COLORS.STATUS_KRITIS
        elif umur >= THRESHOLDS.PAST_DUE:
            return "PAST DUE", COLORS.STATUS_PERINGATAN
        return "CURRENT", COLORS.STATUS_AMAN
    
    def _calculate_text_position(
        self, 
        draw: ImageDraw, 
        text: str, 
        font: ImageFont,
        x: int, 
        width: int, 
        align: str = 'center'
    ) -> int:
        """Hitung posisi x text berdasarkan alignment"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        if align == 'right':
            return x + width - text_width - 10
        elif align == 'center':
            return x + (width - text_width) // 2
        return x + 10
    
    def _draw_header(self, draw: ImageDraw, y_start: int, x_start: int):
        """Draw header tabel"""
        x = x_start
        font = self.fonts.get('header')
        
        for header, width in zip(OUTPUT_HEADERS, TABLE.COL_WIDTHS):
            width_scaled = self._s(width)
            # Background
            draw.rectangle(
                [x, y_start, x + width_scaled, y_start + self._s(TABLE.HEADER_HEIGHT)],
                fill=COLORS.HEADER_BG
            )
            # Border
            draw.rectangle(
                [x, y_start, x + width_scaled, y_start + self._s(TABLE.HEADER_HEIGHT)],
                outline=COLORS.BORDER
            )
            # Text
            text_x = self._calculate_text_position(draw, header, font, x, width_scaled)
            draw.text(
                (text_x, y_start + self._s(15)), 
                header, 
                fill=COLORS.HEADER_TEXT, 
                font=font
            )
            x += width_scaled
    
    def _draw_row(
        self, 
        draw: ImageDraw, 
        item: Dict[str, Any], 
        row_num: int,
        y: int, 
        x_start: int
    ):
        """Draw satu baris data"""
        umur = item['umur']
        row_color = self._get_row_color(umur)
        
        values = [
            (str(row_num), 'center'),  # Nomor urut
            (item['no_faktur'], 'center'),
            (item['tgl_faktur_fmt'], 'center'),
            (item['piutang_fmt'], 'right'),
            (str(item['umur']), 'center')
        ]
        
        x = x_start
        for i, (value, align) in enumerate(values):
            width = self._s(TABLE.COL_WIDTHS[i])
            
            # Background
            draw.rectangle(
                [x, y, x + width, y + self._s(TABLE.ROW_HEIGHT)],
                fill=row_color
            )
            # Border
            draw.rectangle(
                [x, y, x + width, y + self._s(TABLE.ROW_HEIGHT)],
                outline=COLORS.BORDER
            )
            
            # Text
            font = self.fonts.get('data')
            text_x = self._calculate_text_position(draw, value, font, x, width, align)
            draw.text((text_x, y + self._s(12)), value, fill=COLORS.TEXT, font=font)
            
            x += width
    
    def _draw_legend(self, draw: ImageDraw, y: int, x_start: int):
        """Draw legend warna"""
        font = self.fonts.get('data')
        legend_items = [
            (COLORS.HIJAU, "< 60 hari"),
            (COLORS.KUNING, ">= 60 hari"),
            (COLORS.MERAH, ">= 75 hari")
        ]
        
        x = x_start
        box_size = self._s(20)
        for color, text in legend_items:
            # Box warna
            draw.rectangle(
                [x, y, x + box_size, y + self._s(15)],
                fill=color,
                outline=COLORS.BORDER
            )
            # Text
            draw.text((x + box_size + self._s(5), y), text, fill=COLORS.TEXT, font=font)
            
            # Hitung posisi x berikutnya
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x += box_size + self._s(25) + text_width
    
    def generate(
        self, 
        customer_data: List[Dict[str, Any]], 
        customer_name: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate gambar tabel piutang
        
        Args:
            customer_data: List data piutang
            customer_name: Nama pelanggan
            output_path: Path untuk menyimpan gambar (optional)
        
        Returns:
            Path file gambar yang tersimpan
        """
        if not customer_data:
            raise ValueError("Tidak ada data untuk ditampilkan!")
        
        # Sort by umur descending
        customer_data = sorted(customer_data, key=lambda x: x['umur'], reverse=True)
        
        # Calculate dimensions
        table_height = TABLE.calculate_height(len(customer_data))
        
        # Create image
        img = Image.new('RGB', (TABLE.TABLE_WIDTH, table_height), COLORS.BG)
        draw = ImageDraw.Draw(img)
        
        # Draw title (nama pelanggan saja, bold dan besar)
        title = customer_name.upper()
        draw.text(
            (self._s(TABLE.PADDING), self._s(TABLE.PADDING)), 
            title, 
            fill=COLORS.TITLE, 
            font=self.fonts.get('title')
        )
        
        # Draw info
        total_piutang = sum(item['piutang'] for item in customer_data)
        info_text = (
            f"Total Piutang: Rp {total_piutang:,.0f}  |  "
            f"Jumlah Faktur: {len(customer_data)}"
        ).replace(',', '.')
        draw.text(
            (self._s(TABLE.PADDING), self._s(TABLE.PADDING + 25)), 
            info_text, 
            fill=COLORS.INFO, 
            font=self.fonts.get('data')
        )
        
        # Draw table
        y_start = self._s(TABLE.PADDING + 60)
        x_start = self._s(TABLE.PADDING)
        
        # Header
        self._draw_header(draw, y_start, x_start)
        
        # Data rows
        y = y_start + self._s(TABLE.HEADER_HEIGHT)
        for row_num, item in enumerate(customer_data, 1):
            self._draw_row(draw, item, row_num, y, x_start)
            y += self._s(TABLE.ROW_HEIGHT)
        
        # Legend
        self._draw_legend(draw, y + self._s(15), x_start)
        
        # Footer
        footer_text = f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        draw.text(
            (x_start, table_height - self._s(20)), 
            footer_text, 
            fill=COLORS.FOOTER, 
            font=self.fonts.get('data')
        )
        
        # Save
        if output_path is None:
            safe_name = customer_name.replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{safe_name}_{timestamp}.png"
            output_path = filename
        
        img.save(output_path)
        return output_path


# Helper function untuk backward compatibility
def generate_image(
    customer_data: List[Dict[str, Any]], 
    customer_name: str,
    output_path: Optional[str] = None
) -> str:
    """Generate image helper function"""
    generator = PiutangImageGenerator()
    return generator.generate(customer_data, customer_name, output_path)
