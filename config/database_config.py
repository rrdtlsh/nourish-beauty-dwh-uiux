"""
Database Configuration for Nourish Beauty DWH
Author: Raudatul Sholehah - 2310817220002
UAS Business Intelligence 2025
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import psycopg2

# ✅ MATIKAN SQLALCHEMY LOGGING
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'dw_nourish',
    'user': 'postgres',
    'password': 'rute'  # GANTI dengan password PostgreSQL Anda!
}

# SQLAlchemy Connection String
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


def get_engine():
    """Get SQLAlchemy engine WITHOUT any logging"""
    # ✅ Force disable engine logging
    engine_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
    engine_logger.handlers = [logging.NullHandler()]
    engine_logger.propagate = False
    engine_logger.setLevel(logging.CRITICAL)
    
    return create_engine(
        DATABASE_URL,
        echo=False,  # ✅ MUST BE False
        logging_name=None,  # ✅ Disable logging name
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10
    )


def get_connection():
    """Create raw psycopg2 connection"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        raise


def test_connection():
    """Test database connection"""
    try:
        engine = get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[OK] Database connected successfully!")
            print(f"   PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
