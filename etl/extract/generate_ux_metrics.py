import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Setup path (sama seperti file lain)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.database_config import get_engine

def generate_ux_metrics(num_days=60):
    """
    Generate data metrik UX: Usability Score (SUS), Error Rate, Load Time
    """
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    
    current_date = start_date
    while current_date <= end_date:
        # Simulasi: Semakin update sistem, error rate turun, usability naik
        progress_factor = (current_date - start_date).days / num_days
        
        daily_records = np.random.randint(50, 100) # Jumlah sesi per hari
        
        for _ in range(daily_records):
            # Usability Score (0-100) - cenderung naik seiring waktu
            base_score = 65 + (20 * progress_factor) 
            usability_score = min(100, max(0, np.random.normal(base_score, 5)))
            
            # Error Rate (persentase interaksi gagal) - cenderung turun
            base_error = 0.15 - (0.10 * progress_factor)
            error_rate = max(0, np.random.normal(base_error, 0.02))
            
            # Dwell Time (detik)
            dwell_time = np.random.exponential(120) # Rata-rata 2 menit
            
            data.append({
                'date_key': current_date.date(),
                'platform': np.random.choice(['Mobile App', 'Web Desktop', 'Mobile Web']),
                'page_visited': np.random.choice(['Home', 'Product Detail', 'Checkout', 'Profile'], p=[0.4, 0.3, 0.2, 0.1]),
                'usability_score': round(usability_score, 1),
                'error_rate': round(error_rate, 4),
                'load_time_ms': int(np.random.normal(1200 - (400 * progress_factor), 200)), # Load time makin cepat
                'bounce_rate': round(np.random.uniform(0.3, 0.7) - (0.1 * progress_factor), 2)
            })
            
        current_date += timedelta(days=1)
        
    return pd.DataFrame(data)

# Fungsi save_to_staging atau load_to_db perlu ditambahkan di sini