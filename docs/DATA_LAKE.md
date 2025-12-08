# Data Lake Implementation - Nourish Beauty

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
