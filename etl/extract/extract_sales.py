"""
Extract Sales Data from CSV
Author: Raudatul Sholehah - 2310817220002
"""

import pandas as pd
import logging
from datetime import datetime
import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database_config import get_engine
from config.etl_config import PATHS, CSV_FILES
from etl.transform.transform_sales import transform_sales_data

logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_sales_data():
    """Extract sales data from CSV and apply transformations"""
    try:
        logger.info("Starting sales data extraction...")
        
        file_path = os.path.join(PATHS['raw'], CSV_FILES['sales'])
        logger.info(f"Reading file: {file_path}")
        
        # ✅ Read CSV
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        logger.info(f"[OK] Loaded {len(df)} rows from {CSV_FILES['sales']}")
        
        # ✅ Apply transformations (HANYA 1 KALI!)
        logger.info("Applying transformations...")
        df_transformed = transform_sales_data(df)
        
        # ✅ Select ONLY staging columns
        staging_columns = [
            'id_invoice', 'cabang', 'kota', 'tipe_customer', 'jenis_kelamin',
            'kategori_produk', 'harga_satuan', 'jumlah', 'pajak_5_persen',
            'tanggal', 'waktu', 'metode_pembayaran', 'total_penjualan_sebelum_pajak',
            'persentase_gross_margin', 'pendapatan_kotor', 'rating'
        ]
        
        # ✅ Filter kolom yang ada
        available_columns = [col for col in staging_columns if col in df_transformed.columns]
        df_staging = df_transformed[available_columns].copy()
        
        # ✅ Add load timestamp
        df_staging['load_timestamp'] = datetime.now()
        
        # ✅ PENTING: Hapus duplikat kolom jika ada
        df_staging = df_staging.loc[:, ~df_staging.columns.duplicated()]
        
        # ✅ Save to staging CSV
        staging_file = os.path.join(PATHS['staging'], 'staging_sales.csv')
        df_staging.to_csv(staging_file, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to staging file: {staging_file}")
        logger.info(f"[OK] Extraction complete: {len(df_staging)} records ready")
        
        return df_staging
        
    except Exception as e:
        logger.error(f"[ERROR] Error extracting sales data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def load_to_staging_db(df):
    """
    Load extracted and transformed data to staging_sales table
    """
    try:
        logger.info("\nLoading sales data to staging_sales table...")
        logger.info(f"   Records to load: {len(df)}")
        
        # Get database engine
        engine = get_engine()
        
        # ✅ TRUNCATE staging table first
        logger.info("   Truncating staging_sales table...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging_sales RESTART IDENTITY CASCADE"))
            conn.commit()
        
        # ✅ PENTING: Hapus duplikat kolom SEBELUM load
        logger.info(f"   Original shape: {df.shape}")
        logger.info(f"   Original columns: {df.columns.tolist()}")
        
        df_clean = df.loc[:, ~df.columns.duplicated()].copy()
        logger.info(f"   Clean shape: {df_clean.shape}")
        logger.info(f"   Clean columns: {df_clean.columns.tolist()}")
        
        # ✅ Convert datetime columns to proper format
        if 'tanggal' in df_clean.columns:
            df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'], errors='coerce')
        
        if 'waktu' in df_clean.columns:
            df_clean['waktu'] = df_clean['waktu'].astype(str)
        
        # ✅ Verify expected columns
        expected_cols = [
            'id_invoice', 'cabang', 'kota', 'tipe_customer', 'jenis_kelamin',
            'kategori_produk', 'harga_satuan', 'jumlah', 'pajak_5_persen',
            'tanggal', 'waktu', 'metode_pembayaran', 'total_penjualan_sebelum_pajak',
            'persentase_gross_margin', 'pendapatan_kotor', 'rating', 'load_timestamp'
        ]
        
        missing_cols = [col for col in expected_cols if col not in df_clean.columns]
        if missing_cols:
            logger.warning(f"   Missing columns: {missing_cols}")
        
        # ✅ Load data in smaller chunks
        chunk_size = 100
        total_chunks = (len(df_clean) - 1) // chunk_size + 1
        
        logger.info(f"   Loading data in {total_chunks} chunks of {chunk_size} rows...")
        
        loaded_rows = 0
        for i in range(0, len(df_clean), chunk_size):
            chunk = df_clean.iloc[i:i+chunk_size].copy()
            chunk_num = (i // chunk_size) + 1
            
            try:
                # ✅ Verify chunk has no duplicate columns
                if chunk.columns.duplicated().any():
                    logger.error(f"   Chunk {chunk_num} has duplicate columns!")
                    logger.error(f"   Duplicates: {chunk.columns[chunk.columns.duplicated()].tolist()}")
                    chunk = chunk.loc[:, ~chunk.columns.duplicated()]
                
                chunk.to_sql(
                    'staging_sales', 
                    engine, 
                    if_exists='append', 
                    index=False, 
                    method='multi'
                )
                
                loaded_rows += len(chunk)
                logger.info(f"   ✓ Chunk {chunk_num}/{total_chunks} loaded ({len(chunk)} rows, total: {loaded_rows})")
                
            except Exception as chunk_error:
                logger.error(f"   ✗ Error loading chunk {chunk_num}:")
                logger.error(f"      Error: {chunk_error}")
                logger.error(f"      Chunk shape: {chunk.shape}")
                logger.error(f"      Chunk columns: {chunk.columns.tolist()}")
                logger.error(f"      Duplicate columns: {chunk.columns[chunk.columns.duplicated()].tolist()}")
                raise
        
        logger.info(f"[OK] Successfully loaded {loaded_rows} rows to staging_sales")
        
        # ✅ Verify row count in database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging_sales"))
            row_count = result.scalar()
            logger.info(f"[OK] Verified staging_sales row count: {row_count}")
            
            # ✅ Show sample data
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_rows,
                    AVG(total_penjualan_sebelum_pajak) as avg_sales,
                    MIN(total_penjualan_sebelum_pajak) as min_sales,
                    MAX(total_penjualan_sebelum_pajak) as max_sales
                FROM staging_sales
            """))
            stats = result.fetchone()
            logger.info(f"[OK] Stats: Rows={stats[0]}, Avg=Rp {stats[1]:,.0f}, Min=Rp {stats[2]:,.0f}, Max=Rp {stats[3]:,.0f}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading to staging: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("SALES DATA EXTRACTION & LOADING")
    logger.info("=" * 80)
    
    # ✅ Extract & Transform
    df = extract_sales_data()
    
    print(f"\n{'='*80}")
    print(f"PREVIEW (First 3 rows):")
    print(f"{'='*80}")
    print(df[['id_invoice', 'harga_satuan', 'jumlah', 'total_penjualan_sebelum_pajak']].head(3))
    
    print(f"\nShape: {df.shape}")
    print(f"Columns ({len(df.columns)}): {df.columns.tolist()}")
    
    # ✅ Check for duplicate columns
    duplicate_cols = df.columns[df.columns.duplicated()].tolist()
    if duplicate_cols:
        print(f"\n⚠️ WARNING: Duplicate columns detected: {duplicate_cols}")
        df = df.loc[:, ~df.columns.duplicated()]
        print(f"✓ Removed duplicates. New shape: {df.shape}")
    else:
        print(f"✓ No duplicate columns found")
    
    print(f"\n{'='*80}")
    print(f"LOADING TO DATABASE:")
    print(f"{'='*80}")
    
    # ✅ Load to database
    load_to_staging_db(df)
    
    print(f"\n{'='*80}")
    print(f"[OK] EXTRACTION & LOADING COMPLETED!")
    print(f"{'='*80}")
