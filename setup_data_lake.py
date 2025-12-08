"""
Setup Data Lake Structure
Author: Raudatul Sholehah - 2310817220002
"""

import os
import shutil
from pathlib import Path

def setup_data_lake():
    """Create data lake folder structure and documentation"""
    
    # 1. Create folder structure
    print("Creating Data Lake folder structure...")
    folders = [
        'data/lake/raw',
        'data/lake/processed',
        'data/lake/curated'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {folder}")
    
    # 2. Copy raw files to lake
    print("\nCopying raw files to Data Lake Bronze layer...")
    raw_source = Path('data/raw')
    raw_dest = Path('data/lake/raw')
    
    if raw_source.exists():
        for csv_file in raw_source.glob('*.csv'):
            shutil.copy2(csv_file, raw_dest)
            print(f"✅ Copied: {csv_file.name}")
    
    # 3. Create documentation
    print("\nGenerating Data Lake documentation...")
    
    doc_content = """# Data Lake Implementation - Nourish Beauty

## Arsitektur Data Lake (Bronze-Silver-Gold)

### Bronze Layer (Raw Data)
- **Location**: `/data/lake/raw/`
- **Content**: Unprocessed CSV files dari sources
- **Format**: CSV original
- **Retention**: Permanent (backup)
- **Files**: 
  - SuperMarket-Analysis-penjualan.csv
  - HRDataset.csv
  - marketing_campaign.csv

### Silver Layer (Processed)
- **Location**: `/data/lake/processed/`
- **Content**: Cleaned & validated data dari staging
- **Format**: Parquet (compressed)
- **Purpose**: Intermediate storage untuk reprocessing

### Gold Layer (Curated)
- **Location**: `/data/lake/curated/`
- **Content**: Aggregated analytics-ready data
- **Format**: Parquet optimized
- **Purpose**: Fast query untuk ML/Advanced Analytics

## Integration dengan Data Warehouse

| Aspect | Data Lake | Data Warehouse |
|--------|-----------|----------------|
| **Schema** | Schema-on-read | Schema-on-write |
| **Data Type** | Raw, unstructured | Structured, cleaned |
| **Purpose** | Exploration, ML | BI, reporting |

### Integration Flow:
1. Raw data → Bronze layer (Lake)
2. ETL reads Bronze → Staging (DW)
3. Cleaned data → Silver layer (Lake)
4. Aggregated → Gold layer (Lake)
5. Dashboard queries DW

## Technology Stack

**Current**: Local filesystem, CSV format, Python pandas  
**Production**: AWS S3, Parquet, Apache Spark

## Use Cases

1. **Backup & Recovery**: Rebuild DW dari Bronze jika corruption
2. **Reprocessing**: Re-run ETL dengan business rules baru
3. **Advanced Analytics**: ML model training tanpa impact DW
4. **Compliance**: Raw data preservation untuk audit

---

**Author**: Raudatul Sholehah - 2310817220002  
**Date**: December 2025
"""
    
    doc_path = Path('docs/DATA_LAKE.md')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ Documentation created: {doc_path}")
    
    # 4. Summary
    print("\n" + "="*60)
    print("✅ DATA LAKE SETUP COMPLETED!")
    print("="*60)
    print(f"📁 Bronze layer: data/lake/raw/")
    print(f"📁 Silver layer: data/lake/processed/")
    print(f"📁 Gold layer: data/lake/curated/")
    print(f"📄 Documentation: docs/DATA_LAKE.md")
    print("="*60)

if __name__ == '__main__':
    setup_data_lake()
