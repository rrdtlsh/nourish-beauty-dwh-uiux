"""
Load Dimension Tables from Staging
Author: Raudatul Sholehah - 2310817220002

This script loads data from staging tables to dimension tables:
- dim_produk (from staging_sales)
- dim_customer (from staging_marketing)
- dim_employee (from staging_hr)
"""

import pandas as pd
import logging
from datetime import datetime
import sys
import os
from sqlalchemy import text  # ✅ ADD THIS
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database_config import get_engine, get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dim_produk():
    """
    Load unique products to dim_produk
    Extract distinct products from staging_sales
    """
    try:
        logger.info("Loading dim_produk...")
        
        engine = get_engine()
        
        # ✅ Get unique products from staging dengan text() wrapper
        query = text("""
        SELECT DISTINCT 
            kategori_produk,
            NOW() as created_date,
            NOW() as updated_date
        FROM staging_sales
        WHERE kategori_produk IS NOT NULL
        AND kategori_produk != ''
        """)
        
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        if len(df) == 0:
            logger.warning("No products found in staging_sales")
            return
        
        # Use helper function to insert products
        conn = get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute(
                    "SELECT get_or_create_produk_key(%s)",
                    (row['kategori_produk'],)
                )
                inserted_count += 1
            except Exception as e:
                logger.warning(f"Error inserting product '{row['kategori_produk']}': {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"[OK] Loaded {inserted_count} products to dim_produk")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading dim_produk: {e}")
        raise


def load_dim_customer():
    """Load customer dimension from staging_marketing"""
    try:
        logger.info("Loading dim_customer...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ TRUNCATE TABLE BEFORE LOAD (Clear old data)
            conn.execute(text("TRUNCATE TABLE dim_customer RESTART IDENTITY CASCADE"))
            conn.commit()
            logger.info("   Truncated dim_customer table")
            
            query = text("""
            SELECT DISTINCT
                id as customer_id,
                year_birth,
                EXTRACT(YEAR FROM CURRENT_DATE) - year_birth as age,
                education,
                marital_status,
                income,
                kidhome,
                teenhome,
                dt_customer,
                CASE
                    WHEN income > 75000 THEN 'VIP'
                    WHEN income > 50000 THEN 'Premium'
                    ELSE 'Regular'
                END as customer_segment,
                (COALESCE(mntwines, 0) + COALESCE(mntfruits, 0) +
                 COALESCE(mntmeatproducts, 0) + COALESCE(mntfishproducts, 0) +
                 COALESCE(mntsweetproducts, 0) + COALESCE(mntgoldprods, 0)) as total_spending,
                TRUE as is_active,
                NOW() as created_date,
                NOW() as updated_date
            FROM staging_marketing
            WHERE id IS NOT NULL
            """)
            
            df = pd.read_sql(query, conn)
            
            if len(df) > 0:
                # ✅ Load in chunks (50 rows per chunk)
                chunk_size = 50
                total_loaded = 0
                
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i+chunk_size]
                    chunk.to_sql('dim_customer', conn, if_exists='append', index=False, method='multi')
                    total_loaded += len(chunk)
                    logger.info(f"   Loaded chunk {i//chunk_size + 1}: {len(chunk)} rows (Total: {total_loaded}/{len(df)})")
                
                conn.commit()
                logger.info(f"[OK] Successfully loaded {len(df)} customers to dim_customer")
            else:
                logger.warning("No customer data to load")
                
    except Exception as e:
        logger.error(f"[ERROR] Error loading dim_customer: {e}")
        logger.error(traceback.format_exc())
        raise

def load_dim_employee():
    """Load employee dimension from staging_hr"""
    try:
        logger.info("Loading dim_employee...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ TRUNCATE TABLE SEBELUM LOAD (Clear old data)
            conn.execute(text("TRUNCATE TABLE dim_employee RESTART IDENTITY CASCADE"))
            conn.commit()
            logger.info("   Truncated dim_employee table")
            
            query = text("""
            SELECT DISTINCT
                empid as emp_id,
                employee_name,
                position,
                department,
                managername as manager_name,
                managerid as manager_id,
                sex,
                maritaldesc as marital_desc,
                dob,
                EXTRACT(YEAR FROM age(COALESCE(dob, CURRENT_DATE))) as age,
                dateofhire as date_of_hire,
                employmentstatus as employment_status,
                salary,
                CASE WHEN employmentstatus = 'Active' THEN TRUE ELSE FALSE END as is_active,
                NOW() as created_date,
                NOW() as updated_date
            FROM staging_hr
            WHERE empid IS NOT NULL
            """)
            
            df = pd.read_sql(query, conn)
            
            if len(df) > 0:
                # ✅ Load dengan chunking untuk avoid parameter limit
                chunk_size = 50
                total_loaded = 0
                
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i+chunk_size]
                    chunk.to_sql('dim_employee', conn, if_exists='append', index=False, method='multi')
                    total_loaded += len(chunk)
                    logger.info(f"   Loaded chunk {i//chunk_size + 1}: {len(chunk)} rows (Total: {total_loaded}/{len(df)})")
                
                conn.commit()
                logger.info(f"[OK] Successfully loaded {len(df)} employees to dim_employee")
            else:
                logger.warning("No employee data to load")
                
    except Exception as e:
        logger.error(f"[ERROR] Error loading dim_employee: {e}")
        logger.error(traceback.format_exc())
        raise

def verify_dimensions():
    """
    Verify dimension tables after load
    """
    try:
        logger.info("Verifying dimension tables...")
        
        engine = get_engine()
        
        # ✅ Verification query dengan text() wrapper
        verification_query = text("""
        SELECT 'dim_produk' as table_name, COUNT(*) as row_count FROM dim_produk
        UNION ALL
        SELECT 'dim_customer', COUNT(*) FROM dim_customer
        UNION ALL
        SELECT 'dim_employee', COUNT(*) FROM dim_employee
        UNION ALL
        SELECT 'dim_cabang', COUNT(*) FROM dim_cabang
        UNION ALL
        SELECT 'dim_payment', COUNT(*) FROM dim_payment
        UNION ALL
        SELECT 'dim_kampanye', COUNT(*) FROM dim_kampanye
        UNION ALL
        SELECT 'dim_tanggal', COUNT(*) FROM dim_tanggal
        ORDER BY table_name;
        """)
        
        with engine.connect() as conn:
            df = pd.read_sql(verification_query, conn)
        
        print("\n" + "=" * 50)
        print("DIMENSION TABLES ROW COUNTS:")
        print("=" * 50)
        print(df.to_string(index=False))
        print("=" * 50)
        
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error verifying dimensions: {e}")
        raise


def load_all_dimensions():
    """
    Load all dimension tables in correct order
    """
    logger.info("=" * 70)
    logger.info("STARTING DIMENSION LOAD PROCESS")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    try:
        # Load dimensions
        load_dim_produk()
        load_dim_customer()
        load_dim_employee()
        
        # Verify results
        verify_dimensions()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("[OK] ALL DIMENSIONS LOADED SUCCESSFULLY!")
        logger.info(f"Total time: {duration:.2f} seconds")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"[ERROR] DIMENSION LOAD FAILED: {e}")
        logger.error("=" * 70)
        import traceback
        logger.error(traceback.format_exc())
        return False

def load_dim_tanggal():
    """Load date dimension covering all required date ranges"""
    try:
        logger.info("Loading dim_tanggal...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ Get min/max dates from ALL staging tables
            query_dates = text("""
            WITH all_dates AS (
                SELECT dt_customer::DATE as tanggal FROM staging_marketing WHERE dt_customer IS NOT NULL
                UNION
                SELECT tanggal_transaksi::DATE FROM staging_sales WHERE tanggal_transaksi IS NOT NULL
                UNION
                SELECT dateofhire::DATE FROM staging_hr WHERE dateofhire IS NOT NULL
                UNION
                SELECT lastperformancereview_date::DATE FROM staging_hr WHERE lastperformancereview_date IS NOT NULL
            )
            SELECT 
                MIN(tanggal) as min_date,
                MAX(tanggal) as max_date
            FROM all_dates
            """)
            
            result = conn.execute(query_dates).fetchone()
            min_date = result[0]
            max_date = result[1]
            
            logger.info(f"   Date range: {min_date} to {max_date}")
            
            # ✅ TRUNCATE and regenerate dim_tanggal
            conn.execute(text("TRUNCATE TABLE dim_tanggal RESTART IDENTITY CASCADE"))
            conn.commit()
            logger.info("   Truncated dim_tanggal table")
            
            # Generate dates dari min_date - 1 year sampai max_date + 1 year
            query_generate = text("""
            INSERT INTO dim_tanggal (tanggal, hari, bulan, tahun, kuartal, nama_hari, nama_bulan)
            SELECT 
                d::DATE as tanggal,
                EXTRACT(DAY FROM d) as hari,
                EXTRACT(MONTH FROM d) as bulan,
                EXTRACT(YEAR FROM d) as tahun,
                EXTRACT(QUARTER FROM d) as kuartal,
                TO_CHAR(d, 'Day') as nama_hari,
                TO_CHAR(d, 'Month') as nama_bulan
            FROM generate_series(
                :min_date::DATE - INTERVAL '1 year',
                :max_date::DATE + INTERVAL '1 year',
                '1 day'::INTERVAL
            ) d
            ON CONFLICT (tanggal) DO NOTHING;
            """)
            
            result = conn.execute(query_generate, {
                'min_date': min_date,
                'max_date': max_date
            })
            conn.commit()
            
            # Verify count
            verify_query = text("SELECT COUNT(*) FROM dim_tanggal")
            row_count = conn.execute(verify_query).scalar()
            
            logger.info(f"[OK] Loaded {row_count} dates to dim_tanggal")
            
    except Exception as e:
        logger.error(f"[ERROR] Error loading dim_tanggal: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    success = load_all_dimensions()
    sys.exit(0 if success else 1)
