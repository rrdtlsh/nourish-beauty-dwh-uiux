"""
Transform Sales Data - 40 Transformation Rules
Author: Raudatul Sholehah - 2310817220002

TRANSFORMATION RULES APPLIED:
1-5:   Data Type Conversion
6-10:  Handle Missing Values
11-15: Data Cleaning
16-20: Standardization
21-25: Calculate Derived Fields
26-30: Validation & Quality Checks
31-35: Business Logic & Categorization
36-40: Final Cleaning & Outlier Removal
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def clean_numeric_column(series):
    """
    Bersihkan kolom numerik dari format Indonesia (titik pemisah ribuan)
    Contoh: '4.761.904.762' → 4761904762.0
    """
    if series.dtype == 'object':  # Jika masih string
        # Hapus semua titik (pemisah ribuan)
        series = series.astype(str).str.replace('.', '', regex=False)
        # Ganti koma dengan titik (desimal)
        series = series.str.replace(',', '.', regex=False)
    # Convert ke numeric
    return pd.to_numeric(series, errors='coerce')


"""
Transform Sales Data - 40 Transformation Rules
Author: Raudatul Sholehah - 2310817220002
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# ✅ MATIKAN LOGGING VERBOSE
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def clean_numeric_column(series):
    """
    Bersihkan kolom numerik dari format Indonesia (titik pemisah ribuan)
    Contoh: '4.761.904.762' → 4761904762.0
    """
    if series.dtype == 'object':
        series = series.astype(str).str.replace('.', '', regex=False)
        series = series.str.replace(',', '.', regex=False)
    return pd.to_numeric(series, errors='coerce')


def transform_sales_data(df):
    """
    Apply 40 transformation rules to sales data
    """
    logger.info("Applying 40 transformation rules to sales data...")
    
    initial_count = len(df)
    logger.info(f"   Initial row count: {initial_count}")
    
    # ========================================
    # RULE 0: Pre-Cleaning Format Indonesia
    # ========================================
    logger.info("RULE 0: Pre-cleaning Indonesian number format...")
    
    numeric_cols = [
        'harga_satuan', 
        'jumlah', 
        'pajak_5_persen',
        'total_penjualan_sebelum_pajak', 
        'persentase_gross_margin',
        'pendapatan_kotor', 
        'rating'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric_column(df[col])
    
    # ✅ FIX: persentase_gross_margin terlalu besar, bagi dengan 1 miliar
    if 'persentase_gross_margin' in df.columns:
        df['persentase_gross_margin'] = df['persentase_gross_margin'] / 1_000_000_000
        logger.info(f"   Fixed persentase_gross_margin scale")
    
    # ========================================
    # RULE 1-5: Data Type Conversion
    # ========================================
    logger.info("RULE 1-5: Data Type Conversion")
    
    df['tanggal'] = pd.to_datetime(df['tanggal'], format='%m/%d/%Y', errors='coerce')
    df['harga_satuan'] = pd.to_numeric(df['harga_satuan'], errors='coerce')
    df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce').astype('Int64')
    df['pajak_5_persen'] = pd.to_numeric(df['pajak_5_persen'], errors='coerce')
    df['total_penjualan_sebelum_pajak'] = pd.to_numeric(df['total_penjualan_sebelum_pajak'], errors='coerce')
    
    # ========================================
    # RULE 6-10: Handle Missing Values
    # ========================================
    logger.info("RULE 6-10: Handle Missing Values")
    
    df['rating'] = df['rating'].fillna(df['rating'].median())
    df['jenis_kelamin'] = df['jenis_kelamin'].fillna('Unknown')
    df['tipe_customer'] = df['tipe_customer'].fillna('Normal')
    df = df.dropna(subset=['id_invoice', 'tanggal'])
    df['kategori_produk'] = df['kategori_produk'].fillna('Uncategorized')
    
    # ========================================
    # RULE 11-15: Data Cleaning
    # ========================================
    logger.info("RULE 11-15: Data Cleaning")
    
    df['id_invoice'] = df['id_invoice'].astype(str).str.strip()
    df['cabang'] = df['cabang'].astype(str).str.strip().str.title()
    df['kota'] = df['kota'].astype(str).str.strip().str.title()
    df['metode_pembayaran'] = df['metode_pembayaran'].astype(str).str.strip().str.title()
    df['kategori_produk'] = df['kategori_produk'].astype(str).str.strip()
    
    # ========================================
    # RULE 16-20: Standardization
    # ========================================
    logger.info("RULE 16-20: Standardization")
    
    gender_mapping = {
        'Male': 'Male', 'Female': 'Female', 
        'M': 'Male', 'F': 'Female',
        'L': 'Male', 'P': 'Female'
    }
    df['jenis_kelamin'] = df['jenis_kelamin'].map(gender_mapping).fillna('Unknown')
    
    customer_type_mapping = {
        'Member': 'Member', 'Normal': 'Normal', 
        'VIP': 'VIP', 'Regular': 'Normal'
    }
    df['tipe_customer'] = df['tipe_customer'].map(customer_type_mapping).fillna('Normal')
    
    payment_mapping = {
        'Cash': 'Cash', 'Credit Card': 'Credit card',
        'Ewallet': 'Ewallet', 'E-Wallet': 'Ewallet',
        'E-wallet': 'Ewallet', 'Debit Card': 'Debit card'
    }
    df['metode_pembayaran'] = df['metode_pembayaran'].replace(payment_mapping)
    
    branch_code_mapping = {
        'Alex': 'ALEX', 'Giza': 'GIZA',
        'Cairo': 'CAIRO', 'Mandalay': 'MANDALAY'
    }
    df['cabang'] = df['cabang'].replace(branch_code_mapping)
    df['kota'] = df['kota'].str.title()
    
    # ========================================
    # RULE 21-25: Calculate Derived Fields
    # ========================================
    logger.info("RULE 21-25: Calculate Derived Fields")
    
    df['total_penjualan'] = df['total_penjualan_sebelum_pajak'] + df['pajak_5_persen']
    df['margin'] = df['persentase_gross_margin'] / 100 * df['total_penjualan_sebelum_pajak']
    df['tahun'] = df['tanggal'].dt.year
    df['bulan'] = df['tanggal'].dt.month
    df['quarter'] = df['tanggal'].dt.quarter
    
    # ========================================
    # RULE 26-30: Validation & Quality Checks
    # ========================================
    logger.info("RULE 26-30: Validation & Quality Checks")
    
    df = df[df['harga_satuan'] > 0]
    df = df[df['jumlah'] > 0]
    df = df[df['total_penjualan_sebelum_pajak'] > 0]
    df = df[df['rating'] >= 0]
    df = df[df['rating'] <= 10]
    
    # ========================================
    # RULE 31-35: Business Logic
    # ========================================
    logger.info("RULE 31-35: Business Logic & Categorization")
    
    df['sales_category'] = pd.cut(
        df['total_penjualan'], 
        bins=[0, 100, 500, 1000, float('inf')],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    df['customer_satisfaction'] = pd.cut(
        df['rating'],
        bins=[0, 5, 7, 9, 10],
        labels=['Poor', 'Fair', 'Good', 'Excellent'],
        include_lowest=True
    )
    
    df['waktu'] = pd.to_datetime(df['waktu'], format='%H:%M:%S', errors='coerce').dt.time
    df['revenue_per_unit'] = df['total_penjualan'] / df['jumlah']
    df['tax_percentage'] = (df['pajak_5_persen'] / df['total_penjualan_sebelum_pajak'] * 100).round(2)
    
    # ========================================
    # RULE 36-40: Final Cleaning
    # ========================================
    logger.info("RULE 36-40: Final Cleaning & Outlier Removal")
    
    df = df.drop_duplicates(subset=['id_invoice'], keep='first')
    df = df.reset_index(drop=True)
    
    Q1 = df['total_penjualan'].quantile(0.25)
    Q3 = df['total_penjualan'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df['total_penjualan'] >= Q1 - 1.5 * IQR) & (df['total_penjualan'] <= Q3 + 1.5 * IQR)]
    
    df['transform_date'] = datetime.now()
    df['data_quality_score'] = 100.0
    
    final_count = len(df)
    removed_count = initial_count - final_count
    retention_rate = (final_count / initial_count * 100) if initial_count > 0 else 0
    
    logger.info(f"[OK] Transformation complete!")
    logger.info(f"   Initial rows: {initial_count}")
    logger.info(f"   Final rows: {final_count}")
    logger.info(f"   Removed: {removed_count} ({100-retention_rate:.1f}%)")
    logger.info(f"   Retention rate: {retention_rate:.1f}%")
    
    return df


def get_transformation_summary(df_before, df_after):
    """Generate transformation summary report"""
    summary = {
        'initial_rows': len(df_before),
        'final_rows': len(df_after),
        'rows_removed': len(df_before) - len(df_after),
        'retention_rate': (len(df_after) / len(df_before) * 100) if len(df_before) > 0 else 0,
        'new_columns': [col for col in df_after.columns if col not in df_before.columns],
        'null_counts_before': df_before.isnull().sum().sum(),
        'null_counts_after': df_after.isnull().sum().sum()
    }
    return summary

if __name__ == "__main__":
    # Test transformation
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from etl.extract.extract_sales import extract_sales_data
    
    logger.info("=" * 70)
    logger.info("TESTING TRANSFORMATION RULES")
    logger.info("=" * 70)
    
    df_raw = extract_sales_data()
    df_transformed = transform_sales_data(df_raw)
    
    summary = get_transformation_summary(df_raw, df_transformed)
    
    print(f"\nTransformation Summary:")
    print(f"   Initial rows: {summary['initial_rows']}")
    print(f"   Final rows: {summary['final_rows']}")
    print(f"   Rows removed: {summary['rows_removed']}")
    print(f"   Retention rate: {summary['retention_rate']:.2f}%")
    print(f"   New columns added: {len(summary['new_columns'])}")
    print(f"   Null values before: {summary['null_counts_before']}")
    print(f"   Null values after: {summary['null_counts_after']}")
    
    print(f"\nNew Columns:")
    for col in summary['new_columns']:
        print(f"   - {col}")
    
    print(f"\nTransformed Data Preview:")
    print(df_transformed.head())
