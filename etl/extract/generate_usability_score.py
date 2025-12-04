"""
Generate Usability Score Data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Suppress pandas output
pd.set_option('display.max_rows', 5)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from database.connection import get_engine
from sqlalchemy import text

def generate_usability_scores(num_records=100):
    """Generate usability score evaluation data"""
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    data = []
    
    for i in range(num_records):
        evaluation_date = start_date + timedelta(days=np.random.randint(0, 180))
        
        visibility_score = np.random.randint(3, 6)
        match_system_score = np.random.randint(3, 6)
        user_control_score = np.random.randint(3, 6)
        consistency_score = np.random.randint(4, 6)
        error_prevention_score = np.random.randint(3, 6)
        recognition_score = np.random.randint(4, 6)
        flexibility_score = np.random.randint(3, 6)
        aesthetic_score = np.random.randint(4, 6)
        help_users_score = np.random.randint(3, 6)
        documentation_score = np.random.randint(3, 6)
        
        overall_score = np.mean([
            visibility_score, match_system_score, user_control_score,
            consistency_score, error_prevention_score, recognition_score,
            flexibility_score, aesthetic_score, help_users_score,
            documentation_score
        ])
        
        sus_score = np.random.uniform(65, 95)
        
        record = {
            'evaluation_date': evaluation_date.date(),
            'evaluator_id': f"EVAL_{i % 10:03d}",
            'page_evaluated': np.random.choice(['Dashboard Home', 'Sales Analysis', 'HR Performance', 'Marketing Campaign', 'Product Catalog', 'Customer Profile']),
            'visibility_score': visibility_score,
            'match_system_score': match_system_score,
            'user_control_score': user_control_score,
            'consistency_score': consistency_score,
            'error_prevention_score': error_prevention_score,
            'recognition_score': recognition_score,
            'flexibility_score': flexibility_score,
            'aesthetic_score': aesthetic_score,
            'help_users_score': help_users_score,
            'documentation_score': documentation_score,
            'overall_score': round(overall_score, 2),
            'sus_score': round(sus_score, 2),
            'satisfaction_rating': np.random.randint(3, 6),
            'comments': np.random.choice(['Good overall experience', 'Intuitive navigation', 'Need better loading speed', 'Excellent data visualization', 'Some features hard to find', None]),
            'created_date': datetime.now()
        }
        data.append(record)
    
    return pd.DataFrame(data)

def save_to_database(df):
    """Save data to fact_usability_score table"""
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fact_usability_score RESTART IDENTITY CASCADE"))
        conn.commit()
        df.to_sql('fact_usability_score', conn, if_exists='append', index=False, method='multi')
        conn.commit()
        print(f"✅ Loaded {len(df)} records to fact_usability_score")

if __name__ == "__main__":
    print("🔄 Generating usability score data...")
    df = generate_usability_scores(100)
    print(f"✅ Generated {len(df)} records")
    
    print("💾 Saving to database...")
    save_to_database(df)
    print("✅ Complete!\n")
