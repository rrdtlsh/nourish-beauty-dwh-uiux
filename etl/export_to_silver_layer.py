"""
Export cleaned data to Silver Layer (Data Lake)
Author: Raudatul Sholehah - 2310817220002
"""

import pandas as pd
from pathlib import Path
from config.database_config import get_engine
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def export_to_silver():
    """Export cleaned staging data to Parquet in Silver layer"""
    
    engine = get_engine()
    silver_path = Path('data/lake/processed')
    silver_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Sales Data
        logger.info("  → cleaned_sales.parquet")
        with engine.connect() as conn:
            # ✅ FIX: Remove WHERE is_valid condition
            df = pd.read_sql(text("SELECT * FROM staging_sales"), conn)
        df.to_parquet(silver_path / 'cleaned_sales.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 2. HR Data
        logger.info("  → cleaned_hr.parquet")
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM staging_hr"), conn)
        df.to_parquet(silver_path / 'cleaned_hr.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 3. Marketing Data
        logger.info("  → cleaned_marketing.parquet")
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM staging_marketing"), conn)
        df.to_parquet(silver_path / 'cleaned_marketing.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        file_count = len(list(silver_path.glob('*.parquet')))
        logger.info(f"✅ Silver layer: {file_count} files created in {silver_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export Silver layer: {e}")
        raise
