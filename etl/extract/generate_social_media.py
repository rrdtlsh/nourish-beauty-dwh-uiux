"""
Generate Social Media Engagement Data
Simulates Instagram/Facebook engagement metrics
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

def generate_social_media(num_records=365):
    """Generate daily social media engagement data"""
    
    np.random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = []
    
    for i in range(num_records):
        post_date = start_date + timedelta(days=i)
        
        # Base engagement (increases over time)
        base_engagement = 100 + (i * 2)
        
        record = {
            'post_date': post_date.date(),
            'platform': np.random.choice(['Instagram', 'Facebook', 'Twitter', 'TikTok'], p=[0.4, 0.3, 0.2, 0.1]),
            'post_type': np.random.choice(['Photo', 'Video', 'Story', 'Reel', 'Carousel'], p=[0.3, 0.25, 0.2, 0.15, 0.1]),
            'impressions': int(np.random.normal(base_engagement * 50, base_engagement * 10)),
            'reach': int(np.random.normal(base_engagement * 40, base_engagement * 8)),
            'likes': int(np.random.normal(base_engagement * 2, base_engagement * 0.5)),
            'comments': int(np.random.normal(base_engagement * 0.3, base_engagement * 0.1)),
            'shares': int(np.random.normal(base_engagement * 0.5, base_engagement * 0.15)),
            'saves': int(np.random.normal(base_engagement * 0.8, base_engagement * 0.2)),
            'clicks': int(np.random.normal(base_engagement * 1.5, base_engagement * 0.4)),
            'followers_gained': np.random.randint(0, 50),
            'followers_lost': np.random.randint(0, 10),
            'engagement_rate': round(np.random.uniform(2.5, 8.5), 2),
            'post_content': np.random.choice([
                'Product Launch', 'Customer Testimonial', 'Behind the Scenes',
                'Tutorial', 'Promotion', 'Company Culture'
            ]),
            'created_date': datetime.now()
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def save_to_database(df):
    """Save data to fact_social_media_engagement table"""
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fact_social_media_engagement RESTART IDENTITY CASCADE"))
        conn.commit()
        
        df.to_sql('fact_social_media_engagement', conn, if_exists='append', index=False, method='multi')
        conn.commit()
        
        print(f"✅ Loaded {len(df)} records to fact_social_media_engagement")

if __name__ == "__main__":
    print("🔄 Generating social media engagement data...")
    df = generate_social_media(365)
    
    print(f"✅ Generated {len(df)} records (1 year of data)")
    
    print("💾 Saving to database...")
    save_to_database(df)
    
    print("✅ Social media data complete!\n")

