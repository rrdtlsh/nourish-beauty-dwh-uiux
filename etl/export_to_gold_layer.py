"""
Create aggregated analytics in Gold Layer (Data Lake)
Author: Raudatul Sholehah - 2310817220002
"""

import pandas as pd
from pathlib import Path
from config.database_config import get_engine
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def export_to_gold():
    """Create pre-aggregated analytics for Gold layer"""
    
    engine = get_engine()
    gold_path = Path('data/lake/curated')
    gold_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Sales Metrics Daily ✅ (Already working - 177 rows)
        logger.info("  → sales_metrics_daily.parquet")
        query = text("""
            SELECT 
                dt.tanggal as full_date,
                dt.tahun as year,
                dt.bulan as month,
                dt.nama_bulan as month_name,
                dc.nama_cabang as branch_name,
                dc.kota as city,
                COUNT(DISTINCT fs.id_invoice) as transaction_count,
                SUM(fs.jumlah) as total_quantity,
                SUM(fs.total_penjualan_sebelum_pajak) as total_revenue_before_tax,
                SUM(fs.pajak_5_persen) as total_tax,
                SUM(fs.pendapatan_kotor) as total_gross_income,
                AVG(fs.rating) as avg_rating,
                AVG(fs.persentase_gross_margin) as avg_gross_margin_pct
            FROM fact_sales fs
            JOIN dim_tanggal dt ON fs.tanggal_key = dt.tanggal_key
            JOIN dim_cabang dc ON fs.cabang_key = dc.cabang_key
            GROUP BY dt.tanggal, dt.tahun, dt.bulan, dt.nama_bulan, 
                     dc.nama_cabang, dc.kota
            ORDER BY dt.tanggal DESC
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'sales_metrics_daily.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 2. Product Performance (FIXED: product_line → kategori_produk, category → sub_kategori)
        logger.info("  → product_performance.parquet")
        query = text("""
            SELECT 
                dp.kategori_produk as product_category,
                dp.sub_kategori as product_subcategory,
                dp.nama_produk as product_name,
                COUNT(DISTINCT fs.id_invoice) as transaction_count,
                SUM(fs.jumlah) as total_quantity_sold,
                SUM(fs.total_penjualan_sebelum_pajak) as total_revenue,
                SUM(fs.pendapatan_kotor) as total_profit,
                AVG(fs.harga_satuan) as avg_unit_price,
                AVG(fs.rating) as avg_rating,
                AVG(fs.persentase_gross_margin) as avg_margin_pct
            FROM fact_sales fs
            JOIN dim_produk dp ON fs.produk_key = dp.produk_key
            GROUP BY dp.kategori_produk, dp.sub_kategori, dp.nama_produk
            ORDER BY total_revenue DESC
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'product_performance.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 3. Branch Performance
        logger.info("  → branch_performance.parquet")
        query = text("""
            SELECT 
                dc.nama_cabang as branch_name,
                dc.kota as city,
                dc.kode_cabang as branch_code,
                COUNT(DISTINCT fs.id_invoice) as transaction_count,
                SUM(fs.total_penjualan_sebelum_pajak) as total_revenue,
                SUM(fs.pendapatan_kotor) as total_profit,
                AVG(fs.rating) as avg_rating,
                AVG(fs.total_penjualan_sebelum_pajak) as avg_transaction_value,
                AVG(fs.persentase_gross_margin) as avg_margin_pct
            FROM fact_sales fs
            JOIN dim_cabang dc ON fs.cabang_key = dc.cabang_key
            GROUP BY dc.nama_cabang, dc.kota, dc.kode_cabang
            ORDER BY total_revenue DESC
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'branch_performance.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 4. Payment Method Analysis (FIXED: payment_method → metode_pembayaran)
        logger.info("  → payment_analysis.parquet")
        query = text("""
            SELECT 
                pm.metode_pembayaran as payment_method,
                pm.kategori_payment as payment_category,
                COUNT(DISTINCT fs.id_invoice) as transaction_count,
                SUM(fs.total_penjualan_sebelum_pajak) as total_revenue,
                AVG(fs.total_penjualan_sebelum_pajak) as avg_transaction_value,
                AVG(fs.rating) as avg_rating
            FROM fact_sales fs
            JOIN dim_payment pm ON fs.payment_key = pm.payment_key
            GROUP BY pm.metode_pembayaran, pm.kategori_payment
            ORDER BY transaction_count DESC
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'payment_analysis.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 5. Customer Demographics Analysis
        logger.info("  → customer_demographics.parquet")
        query = text("""
            SELECT 
                tipe_customer,
                jenis_kelamin,
                COUNT(DISTINCT id_invoice) as transaction_count,
                SUM(total_penjualan_sebelum_pajak) as total_revenue,
                AVG(total_penjualan_sebelum_pajak) as avg_transaction_value,
                AVG(rating) as avg_rating,
                AVG(jumlah) as avg_quantity_per_transaction
            FROM fact_sales
            GROUP BY tipe_customer, jenis_kelamin
            ORDER BY total_revenue DESC
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'customer_demographics.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        # 6. Time-based Analysis (Hourly patterns)
        logger.info("  → sales_time_patterns.parquet")
        query = text("""
            SELECT 
                EXTRACT(HOUR FROM waktu_transaksi) as transaction_hour,
                COUNT(*) as transaction_count,
                SUM(total_penjualan_sebelum_pajak) as total_revenue,
                AVG(total_penjualan_sebelum_pajak) as avg_transaction_value,
                AVG(rating) as avg_rating
            FROM fact_sales
            WHERE waktu_transaksi IS NOT NULL
            GROUP BY EXTRACT(HOUR FROM waktu_transaksi)
            ORDER BY transaction_hour
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        df.to_parquet(gold_path / 'sales_time_patterns.parquet', 
                      compression='snappy', index=False)
        logger.info(f"     Exported {len(df)} rows")
        
        file_count = len(list(gold_path.glob('*.parquet')))
        logger.info(f"✅ Gold layer: {file_count} files created in {gold_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export Gold layer: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
