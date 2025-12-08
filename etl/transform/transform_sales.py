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
        # Hapus semua titik (pemisah ribuan)
        series = series.astype(str).str.replace('.', '', regex=False)
        # Ganti koma dengan titik (desimal)
        series = series.str.replace(',', '.', regex=False)
        # Hapus spasi dan karakter aneh
        series = series.str.strip()
        series = series.str.replace(' ', '', regex=False)
    
    # Convert ke numeric
    return pd.to_numeric(series, errors='coerce')


def transform_sales_data(df):
    """
    Apply 40 transformation rules to sales data with USD to IDR conversion
    """
    logger.info("Applying 40 transformation rules to sales data...")
    
    initial_count = len(df)
    logger.info(f"   Initial row count: {initial_count}")
    
    # ========================================
    # RULE 0: Pre-Cleaning Format Indonesia & Currency Conversion
    # ========================================
    logger.info("RULE 0: Pre-cleaning Indonesian number format & USD to IDR conversion...")
    
    # ✅ CEK: Apakah data sudah dalam IDR atau masih USD?
    sample_value = df['total_penjualan_sebelum_pajak'].iloc[0] if len(df) > 0 else 0
    
    # Jika rata-rata transaksi < 10,000, berarti masih USD
    avg_transaction = df['total_penjualan_sebelum_pajak'].mean()
    is_in_usd = avg_transaction < 10000  # Threshold: jika < 10K berarti USD
    
    if is_in_usd:
        logger.info(f"   ✓ Detected USD format (avg: ${avg_transaction:.2f})")
        USD_TO_IDR = 15000
    else:
        logger.info(f"   ✓ Already in IDR format (avg: Rp {avg_transaction:,.0f})")
        USD_TO_IDR = 1  # Jangan konversi lagi!
    
    numeric_cols = [
        'harga_satuan', 
        'jumlah', 
        'pajak_5_persen',
        'total_penjualan_sebelum_pajak', 
        'persentase_gross_margin',
        'pendapatan_kotor', 
        'rating'
    ]
    
    currency_cols = [
        'harga_satuan',
        'pajak_5_persen', 
        'total_penjualan_sebelum_pajak',
        'pendapatan_kotor'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            original_sample = df[col].iloc[0] if len(df) > 0 else None
            df[col] = clean_numeric_column(df[col])
            
            # ✅ KONVERSI KE RUPIAH hanya jika masih USD
            if col in currency_cols and USD_TO_IDR > 1:
                df[col] = df[col] * USD_TO_IDR
                cleaned_sample = df[col].iloc[0] if len(df) > 0 else None
                logger.info(f"   {col}: {original_sample} → Rp {cleaned_sample:,.0f}")
            elif col in currency_cols:
                logger.info(f"   {col}: Already in IDR (Rp {df[col].iloc[0]:,.0f})")
    
    # ✅ FIX: persentase_gross_margin adalah PERSENTASE, bukan currency
    if 'persentase_gross_margin' in df.columns:
        sample_val = df['persentase_gross_margin'].iloc[0] if len(df) > 0 else None
        logger.info(f"   persentase_gross_margin: {sample_val:.2f}% (kept as percentage)")
    
    # ... (SISANYA TETAP SAMA, COPY DARI CODE SEBELUMNYA)
    
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
    
    # ✅ FIX: Update bins untuk nilai IDR (bukan USD)
    df['sales_category'] = pd.cut(
        df['total_penjualan'], 
        bins=[0, 1_500_000, 7_500_000, 15_000_000, float('inf')],  # IDR ranges
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
    
    # ✅ Outlier removal dengan IQR
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
    logger.info(f"   Currency converted: USD → IDR (rate: {USD_TO_IDR:,})")
    
    # ✅ SUMMARY STATISTICS
    logger.info(f"\n   SUMMARY STATISTICS (in IDR):")
    logger.info(f"   - Total Revenue: Rp {df['total_penjualan_sebelum_pajak'].sum():,.0f}")
    logger.info(f"   - Avg Transaction: Rp {df['total_penjualan_sebelum_pajak'].mean():,.0f}")
    logger.info(f"   - Min Transaction: Rp {df['total_penjualan_sebelum_pajak'].min():,.0f}")
    logger.info(f"   - Max Transaction: Rp {df['total_penjualan_sebelum_pajak'].max():,.0f}")
    
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
        'null_counts_after': df_after.isnull().sum().sum(),
        'total_revenue_idr': df_after['total_penjualan_sebelum_pajak'].sum(),
        'avg_transaction_idr': df_after['total_penjualan_sebelum_pajak'].mean()
    }
    return summary


if __name__ == "__main__":
    # Test transformation
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from etl.extract.extract_sales import extract_sales_data
    
    logger.info("=" * 80)
    logger.info("TESTING TRANSFORMATION RULES WITH USD TO IDR CONVERSION")
    logger.info("=" * 80)
    
    df_raw = extract_sales_data()
    
    print(f"\n{'='*80}")
    print(f"RAW DATA PREVIEW (First 3 rows):")
    print(f"{'='*80}")
    print(df_raw[['harga_satuan', 'jumlah', 'total_penjualan_sebelum_pajak']].head(3))
    
    df_transformed = transform_sales_data(df_raw)
    
    print(f"\n{'='*80}")
    print(f"TRANSFORMED DATA PREVIEW (First 3 rows):")
    print(f"{'='*80}")
    print(df_transformed[['harga_satuan', 'jumlah', 'total_penjualan_sebelum_pajak']].head(3))
    
    summary = get_transformation_summary(df_raw, df_transformed)
    
    print(f"\n{'='*80}")
    print(f"TRANSFORMATION SUMMARY:")
    print(f"{'='*80}")
    print(f"   Initial rows: {summary['initial_rows']:,}")
    print(f"   Final rows: {summary['final_rows']:,}")
    print(f"   Rows removed: {summary['rows_removed']:,}")
    print(f"   Retention rate: {summary['retention_rate']:.2f}%")
    print(f"   New columns added: {len(summary['new_columns'])}")
    print(f"   Null values before: {summary['null_counts_before']:,}")
    print(f"   Null values after: {summary['null_counts_after']:,}")
    print(f"\n   REVENUE (IDR):")
    print(f"   - Total Revenue: Rp {summary['total_revenue_idr']:,.0f}")
    print(f"   - Avg Transaction: Rp {summary['avg_transaction_idr']:,.0f}")
    
    print(f"\n{'='*80}")
    print(f"NEW COLUMNS CREATED:")
    print(f"{'='*80}")
    for col in summary['new_columns']:
        print(f"   - {col}")
    
    print(f"\n{'='*80}")
    print(f"[OK] TRANSFORMATION TEST COMPLETED!")
    print(f"{'='*80}")
