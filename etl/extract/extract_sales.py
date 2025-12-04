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
from etl.transform.transform_sales import transform_sales_data  # ✅ IMPORT TRANSFORM

logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_sales_data():
    """Extract sales data from CSV and apply transformations"""
    try:
        logger.info("Starting sales data extraction...")
        
        file_path = os.path.join(PATHS['raw'], CSV_FILES['sales'])
        logger.info(f"Reading file: {file_path}")
        
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        logger.info(f"[OK] Loaded {len(df)} rows from {CSV_FILES['sales']}")
        
        # Apply transformations
        logger.info("Applying transformations...")
        df_transformed = transform_sales_data(df)
        
        # Select staging columns
        staging_columns = [
            'id_invoice', 'cabang', 'kota', 'tipe_customer', 'jenis_kelamin',
            'kategori_produk', 'harga_satuan', 'jumlah', 'pajak_5_persen',
            'tanggal', 'waktu', 'metode_pembayaran', 'total_penjualan_sebelum_pajak',
            'persentase_gross_margin', 'pendapatan_kotor', 'rating', 'transform_date'
        ]
        
        available_columns = [col for col in staging_columns if col in df_transformed.columns]
        df_staging = df_transformed[available_columns].copy()
        
        if 'transform_date' in df_staging.columns:
            df_staging = df_staging.rename(columns={'transform_date': 'load_timestamp'})
        else:
            df_staging['load_timestamp'] = datetime.now()
        
        # Save to staging CSV
        staging_file = os.path.join(PATHS['staging'], 'staging_sales.csv')
        df_staging.to_csv(staging_file, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to staging file: {staging_file}")
        logger.info(f"[OK] Extraction complete: {len(df_staging)} records ready")
        
        return df_staging
        
    except Exception as e:
        logger.error(f"[ERROR] Error extracting sales data: {e}")
        raise


def load_to_staging_db(df):
    """Load extracted data to staging_sales table"""
    try:
        logger.info("Loading sales data to staging_sales table...")
        logger.info(f"   Records to load: {len(df)}")
        
        engine = get_engine()
        
        # Truncate staging table
        logger.info("   Truncating staging_sales table...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging_sales RESTART IDENTITY CASCADE"))
            conn.commit()
        
        # Convert datetime columns
        if 'tanggal' in df.columns:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        
        if 'waktu' in df.columns:
            df['waktu'] = df['waktu'].astype(str)
        
        # Load data in chunks
        chunk_size = 500
        total_chunks = (len(df) - 1) // chunk_size + 1
        
        logger.info(f"   Loading {total_chunks} chunks...")
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            chunk_num = (i // chunk_size) + 1
            
            chunk.to_sql('staging_sales', engine, if_exists='append', index=False, method='multi')
            logger.info(f"   Chunk {chunk_num}/{total_chunks} loaded")
        
        logger.info(f"[OK] Successfully loaded {len(df)} rows")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging_sales"))
            row_count = result.scalar()
            logger.info(f"[OK] Verified row count: {row_count}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading to staging: {e}")
        raise


def load_to_staging_db(df):
    """
    Load extracted and transformed data to staging_sales table
    """
    try:
        logger.info("Loading sales data to staging_sales table...")
        logger.info(f"   Records to load: {len(df)}")
        
        # Get database engine
        engine = get_engine()
        
        # ✅ TRUNCATE staging table first
        logger.info("   Truncating staging_sales table...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging_sales RESTART IDENTITY CASCADE"))
            conn.commit()
        
        # ✅ Convert datetime columns to proper format
        if 'tanggal' in df.columns:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        
        if 'waktu' in df.columns and df['waktu'].dtype == 'object':
            # Convert time object to string format HH:MM:SS
            df['waktu'] = df['waktu'].astype(str)
        
        # ✅ Load data in smaller chunks to avoid memory issues
        chunk_size = 500
        total_chunks = (len(df) - 1) // chunk_size + 1
        
        logger.info(f"   Loading data in {total_chunks} chunks of {chunk_size} rows...")
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            chunk_num = (i // chunk_size) + 1
            
            chunk.to_sql(
                'staging_sales', 
                engine, 
                if_exists='append', 
                index=False, 
                method='multi'
            )
            
            logger.info(f"   Chunk {chunk_num}/{total_chunks} loaded ({len(chunk)} rows)")
        
        logger.info(f"[OK] Successfully loaded {len(df)} rows to staging_sales")
        
        # ✅ Verify row count
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging_sales"))
            row_count = result.scalar()
            logger.info(f"[OK] Verified staging_sales row count: {row_count}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading to staging: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("SALES DATA EXTRACTION & LOADING TEST")
    logger.info("=" * 80)
    
    df = extract_sales_data()
    
    print(f"\n{'='*80}")
    print(f"PREVIEW (First 5 rows):")
    print(f"{'='*80}")
    print(df.head())
    
    print(f"\nShape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    
    print(f"\n{'='*80}")
    print(f"LOADING TO DATABASE:")
    print(f"{'='*80}")
    load_to_staging_db(df)
    
    print(f"\n[OK] TEST COMPLETED!")