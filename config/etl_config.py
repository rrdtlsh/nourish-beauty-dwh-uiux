"""
ETL Configuration
"""

import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

PATHS = {
    'raw': os.path.join(DATA_DIR, 'raw'),
    'staging': os.path.join(DATA_DIR, 'staging'),
    'external': os.path.join(DATA_DIR, 'external'),
    'processed': os.path.join(DATA_DIR, 'processed'),
    'logs': os.path.join(BASE_DIR, 'logs')
}

# CSV Files (yang Anda upload)
CSV_FILES = {
    'sales': 'SuperMarket-Analysis-penjualan.csv',
    'hr': 'HRDataset.csv',
    'marketing': 'marketing_campaign.csv'
}

# ETL Settings
ETL_CONFIG = {
    'batch_size': 1000,
    'error_threshold': 0.05,  # 5% max error rate
    'date_format': '%Y-%m-%d',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
    'encoding': 'utf-8'
}

# Instagram API Config (untuk data eksternal)
INSTAGRAM_CONFIG = {
    'access_token': 'YOUR_INSTAGRAM_ACCESS_TOKEN',  # ⚠️ Isi dengan token Anda
    'base_url': 'https://graph.instagram.com/v21.0/',
    'rate_limit': 200,
    'fields': 'id,caption,media_type,media_url,timestamp,like_count,comments_count'
}

# Logging
LOG_CONFIG = {
    'log_file': os.path.join(PATHS['logs'], f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Create directories if not exist
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)
