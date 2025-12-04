"""
Extract Marketing Data from CSV
Author: Raudatul Sholehah - 2310817220002
"""

import pandas as pd
import logging
from datetime import datetime
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database_config import get_engine
from config.etl_config import PATHS, CSV_FILES

# ✅ MATIKAN SQLALCHEMY LOGGING
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_marketing_data():
    """Extract marketing data from CSV"""
    try:
        logger.info("Starting marketing data extraction...")
        
        file_path = os.path.join(PATHS['raw'], CSV_FILES['marketing'])
        logger.info(f"Reading file: {file_path}")
        
        # ✅ TRY MULTIPLE DELIMITERS
        delimiters = ['\t', ';', ',', '|']
        df = None
        
        for delimiter in delimiters:
            try:
                logger.info(f"   Trying delimiter: '{delimiter}'")
                df = pd.read_csv(
                    file_path, 
                    delimiter=delimiter,
                    encoding='utf-8',
                    on_bad_lines='skip',
                    engine='python',
                    skipinitialspace=True
                )
                
                # Validate: should have multiple columns
                if len(df.columns) > 5:
                    logger.info(f"   [OK] Successfully read with delimiter '{delimiter}'")
                    logger.info(f"   Columns detected: {len(df.columns)}")
                    break
                else:
                    logger.warning(f"   Failed: only {len(df.columns)} columns detected")
                    df = None
                    
            except Exception as e:
                logger.warning(f"   Failed with delimiter '{delimiter}': {str(e)[:100]}")
                continue
        
        if df is None or len(df) == 0:
            raise ValueError("Could not read CSV with any known delimiter")
        
        logger.info(f"[OK] Loaded {len(df)} rows from {CSV_FILES['marketing']}")
        logger.info(f"   Columns: {list(df.columns)[:5]}... ({len(df.columns)} total)")
        
        # Clean column names
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
        
        # ✅ CONVERT DATE COLUMNS (format: DD-MM-YYYY)
        date_columns = ['dt_customer']
        for col in date_columns:
            if col in df.columns:
                logger.info(f"   Converting date column: {col}")
                df[col] = pd.to_datetime(df[col], format='%d-%m-%Y', errors='coerce')
        
        # ✅ CONVERT NUMERIC COLUMNS
        numeric_columns = ['id', 'year_birth', 'income', 'kidhome', 'teenhome', 'recency',
                          'mntwines', 'mntfruits', 'mntmeatproducts', 'mntfishproducts',
                          'mntsweetproducts', 'mntgoldprods', 'numdealspurchases',
                          'numwebpurchases', 'numcatalogpurchases', 'numstorepurchases',
                          'numwebvisitsmonth', 'acceptedcmp3', 'acceptedcmp4', 'acceptedcmp5',
                          'acceptedcmp1', 'acceptedcmp2', 'complain', 'z_costcontact',
                          'z_revenue', 'response']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # ✅ REPLACE EMPTY STRINGS WITH None
        df = df.replace('', None)
        df = df.where(pd.notnull(df), None)
        
        # Add load timestamp
        df['load_timestamp'] = datetime.now()
        
        # Save to staging CSV
        staging_file = os.path.join(PATHS['staging'], 'staging_marketing.csv')
        df.to_csv(staging_file, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to staging file: {staging_file}")
        logger.info(f"[OK] Extraction complete: {len(df)} records ready")
        
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error extracting marketing data: {e}")
        raise


def load_to_staging_db(df):
    """Load marketing data to staging_marketing table"""
    try:
        logger.info("Loading marketing data to staging_marketing table...")
        logger.info(f"   Records to load: {len(df)}")
        
        engine = get_engine()
        
        # ✅ DROP AND RECREATE TABLE
        logger.info("   Dropping and recreating staging_marketing table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS staging_marketing CASCADE"))
            conn.commit()
        
        # ✅ LOAD DATA WITH AUTO-SCHEMA
        logger.info(f"   Loading data with auto-schema detection...")
        df.to_sql('staging_marketing', engine, if_exists='replace', index=False, method='multi', chunksize=100)
        
        logger.info(f"[OK] Successfully loaded {len(df)} rows")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging_marketing"))
            row_count = result.scalar()
            logger.info(f"[OK] Verified row count: {row_count}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading marketing data: {e}")
        raise


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("MARKETING DATA EXTRACTION & LOADING TEST")
    logger.info("=" * 80)
    
    df = extract_marketing_data()
    
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
