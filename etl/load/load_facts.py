"""
Load Fact Tables from Staging
Author: Raudatul Sholehah - 2310817220002

This script loads data to fact tables:
- fact_sales (from staging_sales)
- fact_marketing_response (from staging_marketing)
- fact_employee_performance (from staging_hr)
"""

import pandas as pd
import logging
from datetime import datetime
import traceback
import sys
import os
from sqlalchemy import text  # ✅ ADD THIS

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database_config import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_fact_sales():
    """
    Load fact_sales from staging_sales
    Joins with dimension tables to get surrogate keys
    """
    try:
        logger.info("Loading fact_sales...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ TRUNCATE before insert
            conn.execute(text("TRUNCATE TABLE fact_sales CASCADE"))
            conn.commit()
            logger.info("   Truncated fact_sales table")
            
            # ✅ CHECK: Sample staging data
            sample_query = text("""
            SELECT tanggal, kategori_produk, cabang, metode_pembayaran
            FROM staging_sales 
            LIMIT 3
            """)
            sample = conn.execute(sample_query).fetchall()
            logger.info(f"   Debug - Sample data: {sample}")
            
            # ✅ INSERT dengan EXACT columns dari schema fact_sales
            query = text("""
            INSERT INTO fact_sales (
                tanggal_key, produk_key, cabang_key, payment_key,
                id_invoice, tipe_customer, jenis_kelamin,
                harga_satuan, jumlah, total_penjualan_sebelum_pajak,
                pajak_5_persen, pendapatan_kotor, persentase_gross_margin,
                rating, waktu_transaksi, created_date, updated_date
            )
            SELECT 
                dt.tanggal_key,
                dp.produk_key,
                dc.cabang_key,
                dpm.payment_key,
                ss.id_invoice,
                ss.tipe_customer,
                ss.jenis_kelamin,
                ss.harga_satuan,
                ss.jumlah,
                ss.total_penjualan_sebelum_pajak,
                ss.pajak_5_persen,
                ss.pendapatan_kotor,
                ss.persentase_gross_margin,
                ss.rating,
                ss.waktu::TIME as waktu_transaksi,
                NOW() as created_date,
                NOW() as updated_date
            FROM staging_sales ss
            INNER JOIN dim_tanggal dt 
                ON ss.tanggal::DATE = dt.tanggal
            INNER JOIN dim_produk dp 
                ON LOWER(TRIM(ss.kategori_produk)) = LOWER(TRIM(dp.kategori_produk))
            INNER JOIN dim_cabang dc 
                ON LOWER(TRIM(ss.cabang)) = LOWER(TRIM(dc.kode_cabang))
            INNER JOIN dim_payment dpm 
                ON LOWER(TRIM(ss.metode_pembayaran)) = LOWER(TRIM(dpm.metode_pembayaran))
            WHERE ss.tanggal IS NOT NULL
            AND ss.kategori_produk IS NOT NULL
            AND ss.cabang IS NOT NULL
            AND ss.metode_pembayaran IS NOT NULL
            """)
            
            result = conn.execute(query)
            conn.commit()
            
            # ✅ Get actual count
            count_result = conn.execute(text("SELECT COUNT(*) FROM fact_sales"))
            row_count = count_result.scalar()
            
            logger.info(f"[OK] Loaded {row_count} rows to fact_sales")
            
            # ✅ DEBUG jika masih 0
            if row_count == 0:
                logger.warning("⚠️ fact_sales is still 0 - checking JOIN mismatches...")
                
                # Check individual JOINs
                debug_queries = {
                    "staging_total": "SELECT COUNT(*) FROM staging_sales WHERE tanggal IS NOT NULL",
                    "tanggal_join": """
                        SELECT COUNT(*) FROM staging_sales ss
                        INNER JOIN dim_tanggal dt ON ss.tanggal::DATE = dt.tanggal
                    """,
                    "produk_join": """
                        SELECT COUNT(*) FROM staging_sales ss
                        INNER JOIN dim_produk dp 
                            ON LOWER(TRIM(ss.kategori_produk)) = LOWER(TRIM(dp.kategori_produk))
                    """,
                    "cabang_join": """
                        SELECT COUNT(*) FROM staging_sales ss
                        INNER JOIN dim_cabang dc 
                            ON LOWER(TRIM(ss.cabang)) = LOWER(TRIM(dc.kode_cabang))
                    """,
                    "payment_join": """
                        SELECT COUNT(*) FROM staging_sales ss
                        INNER JOIN dim_payment dpm 
                            ON LOWER(TRIM(ss.metode_pembayaran)) = LOWER(TRIM(dpm.metode_pembayaran))
                    """
                }
                
                for name, query_str in debug_queries.items():
                    count = conn.execute(text(query_str)).scalar()
                    logger.info(f"   {name}: {count} rows")
        
    except Exception as e:
        logger.error(f"[ERROR] Error loading fact_sales: {e}")
        logger.error(traceback.format_exc())
        raise


def load_fact_marketing_response():
    """Load marketing response fact table"""
    try:
        logger.info("Loading fact_marketing_response...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ FIX: Debug query yang benar
            debug_query1 = text("""
            SELECT 
                COUNT(*) as total_marketing,
                MIN(dt_customer::DATE) as min_date,
                MAX(dt_customer::DATE) as max_date
            FROM staging_marketing
            WHERE dt_customer IS NOT NULL
            """)
            
            debug_query2 = text("""
            SELECT 
                COUNT(*) as total_dates,
                MIN(tanggal) as min_date,
                MAX(tanggal) as max_date
            FROM dim_tanggal
            """)
            
            debug_query3 = text("""
            SELECT COUNT(*) as matching_rows
            FROM staging_marketing m
            INNER JOIN dim_tanggal dt ON m.dt_customer::DATE = dt.tanggal
            WHERE m.dt_customer IS NOT NULL
            """)
            
            result1 = conn.execute(debug_query1).fetchone()
            result2 = conn.execute(debug_query2).fetchone()
            result3 = conn.execute(debug_query3).fetchone()
            
            logger.info(f"   Debug - Marketing: {result1[0]} rows, dates: {result1[1]} to {result1[2]}")
            logger.info(f"   Debug - dim_tanggal: {result2[0]} dates, range: {result2[1]} to {result2[2]}")
            logger.info(f"   Debug - Matching rows after JOIN: {result3[0]}")
            
            # ✅ Main INSERT query
            query = text("""
            INSERT INTO fact_marketing_response (
                tanggal_key, customer_key, kampanye_key,
                recency, mnt_wines, mnt_fruits, mnt_meat_products,
                mnt_fish_products, mnt_sweet_products, mnt_gold_prods,
                total_spending, num_deals_purchases, num_web_purchases,
                num_catalog_purchases, num_store_purchases, num_web_visits_month,
                accepted_cmp1, accepted_cmp2, accepted_cmp3, accepted_cmp4, accepted_cmp5,
                response, complain, created_date
            )
            SELECT
                dt.tanggal_key,
                c.customer_key,
                NULL as kampanye_key,
                m.recency,
                COALESCE(m.mntwines, 0),
                COALESCE(m.mntfruits, 0),
                COALESCE(m.mntmeatproducts, 0),
                COALESCE(m.mntfishproducts, 0),
                COALESCE(m.mntsweetproducts, 0),
                COALESCE(m.mntgoldprods, 0),
                (COALESCE(m.mntwines, 0) + COALESCE(m.mntfruits, 0) +
                 COALESCE(m.mntmeatproducts, 0) + COALESCE(m.mntfishproducts, 0) +
                 COALESCE(m.mntsweetproducts, 0) + COALESCE(m.mntgoldprods, 0)) as total_spending,
                m.numdealspurchases,
                m.numwebpurchases,
                m.numcatalogpurchases,
                m.numstorepurchases,
                m.numwebvisitsmonth,
                m.acceptedcmp1,
                m.acceptedcmp2,
                m.acceptedcmp3,
                m.acceptedcmp4,
                m.acceptedcmp5,
                m.response,
                m.complain,
                NOW()
            FROM staging_marketing m
            INNER JOIN dim_customer c ON m.id = c.customer_id
            INNER JOIN dim_tanggal dt ON m.dt_customer::DATE = dt.tanggal
            WHERE m.id IS NOT NULL
            AND m.dt_customer IS NOT NULL
            ON CONFLICT DO NOTHING;
            """)
            
            result = conn.execute(query)
            conn.commit()
            row_count = result.rowcount
            logger.info(f"[OK] Loaded {row_count} rows to fact_marketing_response")
            
    except Exception as e:
        logger.error(f"[ERROR] Error loading fact_marketing_response: {e}")
        logger.error(traceback.format_exc())
        raise

def load_fact_employee_performance():
    """Load employee performance fact table"""
    try:
        logger.info("Loading fact_employee_performance...")
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # ✅ FIX: Ganti h.emp_id dengan h.empid (dan kolom lainnya tanpa underscore)
            query = text("""
            INSERT INTO fact_employee_performance (
                tanggal_key, employee_key,
                performance_score_id, performance_score,
                engagement_survey, emp_satisfaction,
                special_projects_count, days_late_last_30,
                absences, salary, recruitment_source,
                review_date, created_date
            )
            SELECT
                dt.tanggal_key,
                e.employee_key,
                h.perfscoreid,
                h.performancescore,
                h.engagementsurvey,
                h.empsatisfaction,
                h.specialprojectscount,
                h.dayslatelast30,
                h.absences,
                h.salary,
                h.recruitmentsource,
                h.lastperformancereview_date,
                NOW()
            FROM staging_hr h
            INNER JOIN dim_employee e ON h.empid = e.emp_id
            INNER JOIN dim_tanggal dt ON h.lastperformancereview_date = dt.tanggal
            WHERE h.empid IS NOT NULL
            AND h.lastperformancereview_date IS NOT NULL
            ON CONFLICT DO NOTHING;
            """)
            
            result = conn.execute(query)
            conn.commit()
            row_count = result.rowcount
            logger.info(f"[OK] Loaded {row_count} rows to fact_employee_performance")
            
    except Exception as e:
        logger.error(f"[ERROR] Error loading fact_employee_performance: {e}")
        logger.error(traceback.format_exc())
        raise


def verify_facts():
    """
    Verify fact tables after load
    """
    try:
        logger.info("Verifying fact tables...")
        
        engine = get_engine()
        
        # ✅ Verification query dengan text() wrapper
        verification_query = text("""
        SELECT 'fact_sales' as table_name, COUNT(*) as row_count FROM fact_sales
        UNION ALL
        SELECT 'fact_marketing_response', COUNT(*) FROM fact_marketing_response
        UNION ALL
        SELECT 'fact_employee_performance', COUNT(*) FROM fact_employee_performance
        UNION ALL
        SELECT 'fact_dashboard_usage', COUNT(*) FROM fact_dashboard_usage
        UNION ALL
        SELECT 'fact_usability_score', COUNT(*) FROM fact_usability_score
        UNION ALL
        SELECT 'fact_user_funnel', COUNT(*) FROM fact_user_funnel
        UNION ALL
        SELECT 'fact_social_media_engagement', COUNT(*) FROM fact_social_media_engagement
        ORDER BY table_name;
        """)
        
        with engine.connect() as conn:
            df = pd.read_sql(verification_query, conn)
        
        print("\n" + "=" * 50)
        print("FACT TABLES ROW COUNTS:")
        print("=" * 50)
        print(df.to_string(index=False))
        print("=" * 50)
        
        return df
        
    except Exception as e:
        logger.error(f"[ERROR] Error verifying facts: {e}")
        raise


def load_all_facts():
    """
    Load all fact tables in correct order
    """
    logger.info("=" * 70)
    logger.info("STARTING FACT TABLES LOAD PROCESS")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    try:
        # Load fact tables
        load_fact_sales()
        load_fact_marketing_response()
        load_fact_employee_performance()
        
        # Verify results
        verify_facts()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("[OK] ALL FACT TABLES LOADED SUCCESSFULLY!")
        logger.info(f"Total time: {duration:.2f} seconds")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"[ERROR] FACT LOAD FAILED: {e}")
        logger.error("=" * 70)
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = load_all_facts()
    sys.exit(0 if success else 1)
