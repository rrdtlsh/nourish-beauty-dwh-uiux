"""
Generate synthetic user activity data for dashboard demo
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
import os

# Suppress pandas output
pd.set_option('display.max_rows', 5)
pd.set_option('display.max_columns', 10)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def generate_user_activity(num_records=5000):
    """Generate synthetic user activity logs"""
    
    np.random.seed(42)
    random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, periods=num_records)
    
    user_ids = [f"USER_{str(i).zfill(4)}" for i in range(1, 501)]
    pages = ['home', 'product_catalog', 'product_detail', 'cart', 'checkout', 'payment', 'confirmation', 'profile', 'search', 'category']
    actions = ['page_view', 'click', 'scroll', 'form_submit', 'error', 'exit']
    devices = ['desktop', 'mobile', 'tablet']
    
    data = []
    for i in range(num_records):
        record = {
            'session_id': f"SESSION_{str(i // 10).zfill(5)}",
            'user_id': random.choice(user_ids),
            'timestamp': dates[i],
            'page': random.choice(pages),
            'action': random.choice(actions),
            'device': random.choice(devices),
            'dwell_time_seconds': np.random.exponential(45) if random.random() > 0.1 else np.random.exponential(10),
            'clicks_count': np.random.poisson(3),
            'scroll_depth_percent': np.random.uniform(10, 100),
            'is_error': 1 if random.random() < 0.05 else 0,
            'is_bounce': 1 if random.random() < 0.35 else 0,
            'conversion': 1 if random.random() < 0.08 else 0
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    df['session_duration'] = df.groupby('session_id')['dwell_time_seconds'].transform('sum')
    df['session_page_count'] = df.groupby('session_id')['page'].transform('count')
    
    return df

def save_to_database(df, table_name='user_activity_log'):
    """Save to PostgreSQL"""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()
        
        create_table_sql = f"""
        CREATE TABLE {table_name} (
            log_id SERIAL PRIMARY KEY,
            session_id VARCHAR(50),
            user_id VARCHAR(50),
            timestamp TIMESTAMP,
            page VARCHAR(100),
            action VARCHAR(50),
            device VARCHAR(20),
            dwell_time_seconds FLOAT,
            clicks_count INTEGER,
            scroll_depth_percent FLOAT,
            is_error INTEGER,
            is_bounce INTEGER,
            conversion INTEGER,
            session_duration FLOAT,
            session_page_count INTEGER
        );
        """
        conn.execute(text(create_table_sql))
        conn.commit()
        
        df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        conn.commit()
    
    print(f"✅ Loaded {len(df)} records to {table_name}")

if __name__ == "__main__":
    print("🔄 Generating user activity data...")
    df = generate_user_activity(5000)
    print(f"✅ Generated {len(df)} records | Columns: {len(df.columns)}")
    
    print("💾 Saving to database...")
    save_to_database(df)
    print("✅ Complete!\n")
