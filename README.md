# 🏪 Nourish Beauty - Data Warehouse & UI/UX Dashboard

**Mata Kuliah:** Business Intelligence  
**Dosen:** [Nama Dosen]  
**Nama:** Raudatul Sholehah  
**NIM:** 2310817220002  
**Tanggal:** 4 Desember 2025

---

## 📋 Project Overview

Data Warehouse implementation untuk mengintegrasikan data dari multiple sources (Sales, HR, Marketing, Social Media, User Behavior) dengan dashboard UI/UX analytics untuk mendukung business decision making.

### Business Problem
- Data terisolasi di multiple systems
- Sulit melakukan cross-functional analysis
- Tidak ada visibility terhadap user behavior & engagement
- Manual reporting memakan waktu

### Solution
Centralized Data Warehouse dengan:
- Star Schema Design
- ETL Pipeline automation
- UI/UX Analytics Dashboard
- Business Intelligence Reports

---

## 🏗️ Architecture

### Data Warehouse Schema
**Star Schema** dengan:
- **7 Dimension Tables**: dim_customer, dim_employee, dim_produk, dim_tanggal, dim_cabang, dim_gender, dim_kampanye
- **8 Fact Tables**: 
  - fact_sales (664 records)
  - fact_marketing_response (1,000 records)
  - fact_employee_performance (306 records)
  - fact_usability_score (100 records)
  - fact_dashboard_usage (2,000 records)
  - fact_social_media_engagement (365 records)
  - fact_user_funnel (1,000 records)
  - user_activity_log (5,000 records)

**Total Records**: 10,435 records

---

## 🔄 ETL Pipeline

### Extract
- CSV files: SuperMarket-Analysis-penjualan.csv, HRDataset.csv, marketing_campaign.csv
- Synthetic data generation: User activity, Social media, Dashboard usage

### Transform
**40 Transformation Rules** implemented:
- Data type conversion
- Missing value handling
- Data standardization
- Outlier detection
- Business rule validation
- Data quality checks

### Load
- Incremental loading strategy
- Referential integrity maintenance
- Error handling & logging
- Data validation post-load

---

## 📊 Data Quality Metrics

- **Data Retention Rate**: 99.1%
- **Referential Integrity**: 100%
- **Null Values Handled**: 2,850 records
- **Duplicates Removed**: 127 records
- **ETL Success Rate**: 100%

---

## 🛠️ Technology Stack

- **Database**: PostgreSQL 18.1
- **Programming**: Python 3.11
- **Libraries**: pandas, numpy, SQLAlchemy, psycopg2
- **Dashboard**: Streamlit, Plotly
- **ETL**: Custom Python scripts

---

## 📁 Project Structure
nourish-beauty-dwh-uiux/
├── data/ # Raw & processed data
├── etl/ # ETL scripts
│ ├── extract/
│ ├── transform/
│ └── load/
├── database/ # DB connection & schema
├── dashboard/ # Streamlit dashboard
├── queries/ # SQL analysis queries
├── docs/ # Documentation
└── logs/ # ETL logs

## 🚀 How to Run

### 1. Setup Database
psql -U postgres -d dw_nourish -f database/schema/create_ui_ux_tables.sql

### 2. Run ETL Pipeline
python run_etl.py

### 3. Generate UI/UX Data
python -m etl.extract.generate_user_activity
python -m etl.extract.generate_usability_score
python -m etl.extract.generate_dashboard_usage
python -m etl.extract.generate_social_media
python -m etl.extract.generate_user_funnel

### 4. Launch Dashboard
streamlit run dashboard/app.py

---

## 📈 Key Features

### Business Intelligence
- Sales trend analysis
- Customer segmentation
- Campaign effectiveness tracking
- Employee performance monitoring

### UI/UX Analytics
- User behavior tracking
- Conversion funnel analysis
- Usability scoring (Nielsen's Heuristics)
- Dashboard usage patterns
- Social media engagement metrics

---

## 📊 Sample Insights

1. **Top Revenue Product**: Health and Beauty (Rp 19.7M)
2. **Best Performing Branch**: Branch A (45% revenue)
3. **Campaign Success Rate**: 15.3% acceptance
4. **Average Usability Score**: 4.2/5 (SUS: 78.5)
5. **Funnel Conversion Rate**: 14.7% (landing to purchase)

---

## 📚 Documentation

- [ETL Documentation](docs/ETL_Documentation.md)
- [40 Transformation Rules](docs/TRANSFORMATION_RULES.md)
- [DW Architecture](docs/DW_Architecture.md)
- [User Guide](docs/User_Guide.md)

---

## 👨‍💻 Author

**Raudatul Sholehah**  
NIM: 2310817220002  
Email: [Your Email]  
GitHub: [Your GitHub]

---

## 📄 License

This project is for academic purposes - Business Intelligence Course, University.
