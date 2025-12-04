"""
Generate User Funnel Data
Simulates conversion funnel stages
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
# Suppress pandas output
pd.set_option('display.max_rows', 5)

from database.connection import get_engine
from sqlalchemy import text

def generate_user_funnel(num_records=1000):
    """Generate user funnel conversion data"""
    
    np.random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    data = []
    
    for i in range(num_records):
        funnel_date = start_date + timedelta(days=np.random.randint(0, 60))
        
        # Funnel stages with decreasing conversion
        reached_landing = True
        viewed_product = np.random.choice([True, False], p=[0.7, 0.3])
        added_to_cart = viewed_product and np.random.choice([True, False], p=[0.5, 0.5])
        initiated_checkout = added_to_cart and np.random.choice([True, False], p=[0.6, 0.4])
        completed_purchase = initiated_checkout and np.random.choice([True, False], p=[0.7, 0.3])
        
        record = {
            'funnel_date': funnel_date.date(),
            'user_id': f"USER_{i:04d}",
            'session_id': f"SESSION_{i:06d}",
            'reached_landing': reached_landing,
            'viewed_product': viewed_product,
            'added_to_cart': added_to_cart,
            'initiated_checkout': initiated_checkout,
            'completed_purchase': completed_purchase,
            'time_to_purchase_minutes': np.random.randint(5, 120) if completed_purchase else None,
            'product_category': np.random.choice([
                'Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Tools'
            ]),
            'traffic_source': np.random.choice([
                'Organic Search', 'Paid Ads', 'Social Media', 'Direct', 'Email'
            ], p=[0.3, 0.25, 0.25, 0.15, 0.05]),
            'device_type': np.random.choice(['Desktop', 'Mobile', 'Tablet'], p=[0.5, 0.4, 0.1]),
            'exit_stage': 'Purchase Complete' if completed_purchase else (
                'Checkout' if initiated_checkout else (
                    'Cart' if added_to_cart else (
                        'Product Page' if viewed_product else 'Landing Page'
                    )
                )
            ),
            'created_date': datetime.now()
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def save_to_database(df):
    """Save data to fact_user_funnel table"""
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fact_user_funnel RESTART IDENTITY CASCADE"))
        conn.commit()
        
        df.to_sql('fact_user_funnel', conn, if_exists='append', index=False, method='multi')
        conn.commit()
        
        print(f"✅ Loaded {len(df)} records to fact_user_funnel")

if __name__ == "__main__":
    print("🔄 Generating user funnel data...")
    df = generate_user_funnel(1000)
    
    print(f"✅ Generated {len(df)} records")
    
    print("💾 Saving to database...")
    save_to_database(df)
    
    print("✅ User funnel data complete!\n")

