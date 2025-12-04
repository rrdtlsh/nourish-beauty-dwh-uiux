"""
Extract HR Data from CSV
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


def extract_hr_data():
    """Extract HR data from CSV"""
    try:
        logger.info("Starting HR data extraction...")
        
        file_path = os.path.join(PATHS['raw'], CSV_FILES['hr'])
        logger.info(f"Reading file: {file_path}")
        
        # ✅ READ WITH SEMICOLON DELIMITER + ERROR HANDLING
        df = pd.read_csv(
            file_path, 
            delimiter=';',  # ✅ HR uses semicolon
            encoding='utf-8',
            on_bad_lines='skip',  # ✅ Skip malformed lines
            engine='python',  # ✅ More flexible
            skipinitialspace=True,  # ✅ Remove leading spaces
            quotechar='"'  # ✅ Handle quoted fields
        )
        
        logger.info(f"[OK] Loaded {len(df)} rows from {CSV_FILES['hr']}")
        logger.info(f"   Columns: {len(df.columns)}")
        
        # Clean column names (lowercase, remove spaces)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
        
        # ✅ CONVERT DATE COLUMNS (format: MM/DD/YY or MM/DD/YYYY)
        date_columns = ['dob', 'dateofhire', 'dateoftermination', 'lastperformancereview_date']
        for col in date_columns:
            if col in df.columns:
                logger.info(f"   Converting date column: {col}")
                # Try multiple date formats
                df[col] = pd.to_datetime(df[col], format='%m/%d/%Y', errors='coerce')
                if df[col].isna().all():
                    df[col] = pd.to_datetime(df[col], format='%m/%d/%y', errors='coerce')
        
        # ✅ CONVERT NUMERIC COLUMNS
        numeric_columns = ['empid', 'marriedid', 'maritalstatusid', 'genderid', 
                          'empstatusid', 'deptid', 'perfscoreid', 'fromdiversityjobfairid',
                          'salary', 'termd', 'positionid', 'zip', 'managerid',
                          'engagementsurvey', 'empsatisfaction', 'specialprojectscount',
                          'dayslatelast30', 'absences']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # ✅ REPLACE EMPTY STRINGS WITH None
        df = df.replace('', None)
        df = df.where(pd.notnull(df), None)
        
        # Add load timestamp
        df['load_timestamp'] = datetime.now()
        
        # Save to staging CSV
        staging_file = os.path.join(PATHS['staging'], 'staging_hr.csv')
        df.to_csv(staging_file, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to staging file: {staging_file}")
        logger.info(f"[OK] Extraction complete: {len(df)} records ready")
        
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error extracting HR data: {e}")
        raise


def load_to_staging_db(df):
    """Load HR data to staging_hr table - ROW BY ROW"""
    try:
        logger.info("Loading HR data to staging_hr table...")
        logger.info(f"   Records to load: {len(df)}")
        
        engine = get_engine()
        
        # Truncate staging table
        logger.info("   Truncating staging_hr table...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging_hr RESTART IDENTITY CASCADE"))
            conn.commit()
        
        # ✅ LOAD ROW BY ROW (SLOWEST BUT SAFEST)
        logger.info(f"   Loading rows individually...")
        
        for i, row in df.iterrows():
            row_df = pd.DataFrame([row])
            row_df.to_sql('staging_hr', engine, if_exists='append', index=False, method='multi')
            
            # Print progress every 50 rows
            if (i + 1) % 50 == 0 or (i + 1) == len(df):
                logger.info(f"   Progress: {i + 1}/{len(df)} rows loaded")
        
        logger.info(f"[OK] Successfully loaded {len(df)} rows")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging_hr"))
            row_count = result.scalar()
            logger.info(f"[OK] Verified row count: {row_count}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading HR data: {e}")
        raise

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("HR DATA EXTRACTION & LOADING TEST")
    logger.info("=" * 80)
    
    df = extract_hr_data()
    
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
