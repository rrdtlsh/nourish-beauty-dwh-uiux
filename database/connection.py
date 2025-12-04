"""
Database Connection Module
Handles PostgreSQL connection using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_engine() -> Engine:
    """
    Create and return SQLAlchemy engine for PostgreSQL connection
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    # Get database credentials from environment variables
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'dw_nourish')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Create connection string
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,         # Connection pool size
        max_overflow=20,      # Max overflow connections
        echo=False            # Don't log SQL statements
    )
    
    return engine


def test_connection():
    """
    Test database connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("[OK] Database connected successfully!")
            print(f"   PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connection when run directly
    test_connection()
