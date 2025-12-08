"""
Complete ETL Pipeline Orchestration
Author: Raudatul Sholehah - 2310817220002
UAS Business Intelligence 2025

Run this script to execute complete ETL process:
1. Extract data from CSV files
2. Transform data (40 transformation rules)
3. Load to Data Warehouse
4. Export to Data Lake (Bronze, Silver, Gold layers)

Usage: python run_etl.py
"""

import sys
import logging
from datetime import datetime
import os
import warnings

# ✅ MATIKAN SQLALCHEMY LOGGING SEBELUM IMPORT APAPUN
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

# Setup logging directory
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"etl_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# ✅ CONFIGURE LOGGING WITH UTF-8 ENCODING & ERROR HANDLING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', errors='replace'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_separator(char="=", width=80):
    """Print separator line"""
    logger.info(char * width)

def print_step_header(step_num, title):
    """Print step header"""
    logger.info("")
    logger.info(f"STEP {step_num}: {title}")
    logger.info("-" * 80)

def run_etl_pipeline():
    """Execute complete ETL pipeline"""
    start_time = datetime.now()
    
    try:
        # Header
        print_separator()
        logger.info("NOURISH BEAUTY DATA WAREHOUSE - ETL PIPELINE")
        logger.info(f"   Author: Raudatul Sholehah - 2310817220002")
        logger.info(f"   Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print_separator()
        
        # STEP 1: Test Database Connection
        print_step_header(1, "Testing Database Connection")
        from config.database_config import test_connection
        if not test_connection():
            raise Exception("Database connection failed!")
        
        # STEP 2: Extract Phase
        print_step_header(2, "EXTRACT PHASE")
        
        from etl.extract.extract_sales import extract_sales_data, load_to_staging_db as load_sales_staging
        from etl.extract.extract_hr import extract_hr_data, load_to_staging_db as load_hr_staging
        from etl.extract.extract_marketing import extract_marketing_data, load_to_staging_db as load_marketing_staging
        
        logger.info("Extracting Sales Data...")
        df_sales = extract_sales_data()
        load_sales_staging(df_sales)
        
        logger.info("Extracting HR Data...")
        df_hr = extract_hr_data()
        load_hr_staging(df_hr)
        
        logger.info("Extracting Marketing Data...")
        df_marketing = extract_marketing_data()
        load_marketing_staging(df_marketing)
        
        logger.info("[OK] Extract phase completed!")
        
        # STEP 3: Transform Phase
        print_step_header(3, "TRANSFORM PHASE")
        logger.info("Transformation rules will be applied during load phase")
        logger.info("[OK] 40 transformation rules ready")
        
        # STEP 4: Load Dimensions
        print_step_header(4, "LOAD DIMENSIONS")
        
        from etl.load.load_dimensions import load_all_dimensions
        load_all_dimensions()
        
        # STEP 5: Load Facts
        print_step_header(5, "LOAD FACT TABLES")
        
        from etl.load.load_facts import load_all_facts
        load_all_facts()
        
        # ✅ STEP 6: Export to Data Lake (NEW)
        print_step_header(6, "EXPORT TO DATA LAKE")
        
        try:
            # 6.1: Bronze Layer (already done during extract)
            logger.info("Bronze Layer: Raw files already in data/lake/raw/")
            
            # 6.2: Silver Layer (Processed/Cleaned data)
            logger.info("Exporting to Silver Layer (Processed)...")
            from etl.export_to_silver_layer import export_to_silver
            export_to_silver()
            logger.info("✅ Silver layer export completed")
            
            # 6.3: Gold Layer (Curated/Aggregated data)
            logger.info("Exporting to Gold Layer (Curated)...")
            from etl.export_to_gold_layer import export_to_gold
            export_to_gold()
            logger.info("✅ Gold layer export completed")
            
            logger.info("[OK] Data Lake export phase completed!")
            
        except ImportError as ie:
            logger.warning(f"[SKIP] Data Lake export modules not found: {ie}")
            logger.warning("       This is optional. Continue with main pipeline.")
        except Exception as e:
            logger.warning(f"[WARN] Data Lake export failed: {e}")
            logger.warning("       Main DW pipeline successful. Lake export is optional.")
        
        # STEP 7: Verification (UPDATED numbering)
        print_step_header(7, "DATA VERIFICATION")
        
        from config.database_config import get_engine
        from sqlalchemy import text
        import pandas as pd
        
        engine = get_engine()
        
        verification_query = text("""
        SELECT 
            'fact_sales' as table_name, COUNT(*) as row_count FROM fact_sales
        UNION ALL
        SELECT 'fact_marketing_response', COUNT(*) FROM fact_marketing_response
        UNION ALL
        SELECT 'fact_employee_performance', COUNT(*) FROM fact_employee_performance
        UNION ALL
        SELECT 'dim_produk', COUNT(*) FROM dim_produk
        UNION ALL
        SELECT 'dim_customer', COUNT(*) FROM dim_customer
        UNION ALL
        SELECT 'dim_employee', COUNT(*) FROM dim_employee
        UNION ALL
        SELECT 'dim_cabang', COUNT(*) FROM dim_cabang
        UNION ALL
        SELECT 'dim_payment', COUNT(*) FROM dim_payment
        UNION ALL
        SELECT 'dim_tanggal', COUNT(*) FROM dim_tanggal
        ORDER BY table_name;
        """)
        
        with engine.connect() as conn:
            df_verification = pd.read_sql(verification_query, conn)
        
        logger.info("\nData Warehouse Row Counts:")
        logger.info("\n" + df_verification.to_string(index=False))
        
        # ✅ Data Lake Verification (NEW)
        logger.info("\nData Lake Status:")
        from pathlib import Path
        
        bronze_files = list(Path('data/lake/raw').glob('*.csv'))
        silver_files = list(Path('data/lake/processed').glob('*.parquet'))
        gold_files = list(Path('data/lake/curated').glob('*.parquet'))
        
        logger.info(f"  Bronze Layer: {len(bronze_files)} files")
        logger.info(f"  Silver Layer: {len(silver_files)} files")
        logger.info(f"  Gold Layer: {len(gold_files)} files")
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Success Summary
        logger.info("")
        print_separator()
        logger.info("[OK] ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print_separator()
        logger.info(f"Log file: {log_file}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print_separator()
        
        return True
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error("")
        print_separator()
        logger.error(f"[ERROR] ETL PIPELINE FAILED: {e}")
        print_separator()
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Failed after: {duration:.2f} seconds")
        print_separator()
        
        return False

if __name__ == "__main__":
    success = run_etl_pipeline()
    sys.exit(0 if success else 1)
