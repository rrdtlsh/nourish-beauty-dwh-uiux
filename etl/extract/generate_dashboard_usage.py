"""
Generate Dashboard Usage Data
Simulates dashboard interaction and usage patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine
from sqlalchemy import text

def generate_dashboard_usage(num_records=2000):
    """Generate dashboard usage data"""
    
    np.random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    data = []
    
    dashboard_pages = [
        'Dashboard Home', 'Sales Analysis', 'HR Performance',
        'Marketing Campaign', 'Product Catalog', 'Customer Profile',
        'Reports', 'Settings'
    ]
    
    for i in range(num_records):
        usage_date = start_date + timedelta(days=np.random.randint(0, 90))
        
        record = {
            'usage_date': usage_date.date(),
            'user_id': f"USER_{np.random.randint(1, 500):04d}",
            'dashboard_page': np.random.choice(dashboard_pages),
            'visit_count': np.random.randint(1, 10),
            'time_spent_seconds': np.random.randint(30, 600),
            'interaction_count': np.random.randint(5, 50),
            'filter_used': np.random.choice([True, False], p=[0.7, 0.3]),
            'export_count': np.random.randint(0, 5),
            'refresh_count': np.random.randint(1, 10),
            'error_encountered': np.random.choice([True, False], p=[0.1, 0.9]),
            'session_id': f"SESSION_{i:06d}",
            'device_type': np.random.choice(['Desktop', 'Tablet', 'Mobile'], p=[0.7, 0.2, 0.1]),
            'browser': np.random.choice(['Chrome', 'Firefox', 'Edge', 'Safari'], p=[0.6, 0.2, 0.15, 0.05]),
            'created_date': datetime.now()
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def save_to_database(df):
    """Save data to fact_dashboard_usage table"""
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fact_dashboard_usage RESTART IDENTITY CASCADE"))
        conn.commit()
        
        df.to_sql('fact_dashboard_usage', conn, if_exists='append', index=False, method='multi')
        conn.commit()
        
        print(f"✅ Loaded {len(df)} records to fact_dashboard_usage")

if __name__ == "__main__":
    print("🔄 Generating dashboard usage data...")
    df = generate_dashboard_usage(2000)
    
    print(f"✅ Generated {len(df)} records")
    
    print("💾 Saving to database...")
    save_to_database(df)
    
    print("✅ Dashboard usage data complete!\n")

