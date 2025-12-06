# 📋 Data Governance Policy
## Nourish Beauty Data Warehouse

**Version:** 1.0  
**Effective Date:** December 5, 2025  
**Owner:** Raudatul Sholehah (2310817220002)

---

## 1. Overview

This document defines the data governance framework for the Nourish Beauty Data Warehouse, ensuring data quality, security, privacy, and compliance.

---

## 2. Data Governance Principles

### 2.1 Data Quality Standards

| **Dimension** | **Target** | **Measurement** |
|--------------|-----------|-----------------|
| **Accuracy** | 99%+ | Data validation checks |
| **Completeness** | 95%+ | Null value monitoring |
| **Consistency** | 100% | Referential integrity |
| **Timeliness** | < 1 hour | ETL latency tracking |
| **Uniqueness** | 100% | Duplicate detection |

### 2.2 Data Quality Rules (40 Transformation Rules)

#### **Category 1: Data Type & Format (10 rules)**
1. Convert `tanggal` to DATE type
2. Convert numeric strings to INTEGER/FLOAT
3. Standardize date format to ISO 8601
4. Convert boolean values to TRUE/FALSE
5. Trim whitespace from all text fields
6. Convert text to lowercase for consistency
7. Standardize currency format (Rupiah)
8. Parse timestamp to UTC timezone
9. Convert empty strings to NULL
10. Validate email format

#### **Category 2: Missing Value Handling (8 rules)**
11. Impute missing `rating` with median
12. Fill missing `gender` with "Unknown"
13. Replace NULL `customer_id` with generated ID
14. Forward-fill missing dates
15. Impute missing `salary` with department average
16. Default missing `device_type` to "Desktop"
17. Replace missing `browser` with "Other"
18. Fill missing `city` with "Unknown Location"

#### **Category 3: Business Rule Validation (10 rules)**
19. Validate `total_harga` = `harga_satuan` × `jumlah`
20. Check `rating` range (1-5)
21. Ensure `tanggal` not in future
22. Validate `email` contains "@" symbol
23. Check `age` range (18-100)
24. Ensure `salary` > 0
25. Validate `phone` format (10-15 digits)
26. Check `product_id` exists in `dim_produk`
27. Ensure `payment_type` in allowed list
28. Validate `discount` percentage (0-100)

#### **Category 4: Outlier Detection & Handling (6 rules)**
31. Cap `dwell_time` at 3 standard deviations
32. Flag `total_harga` > 10M for review
33. Detect anomalous `click_count` (>100)
34. Cap `salary` at 99th percentile
35. Flag unusually high `order_quantity` (>50)
36. Detect impossible `conversion_time` (<10s)

#### **Category 5: Data Standardization (6 rules)**
37. Standardize product categories to 6 fixed values
38. Normalize city names (uppercase first letter)
39. Standardize payment methods (3 types)
40. Normalize department names
41. Standardize device types (Desktop/Mobile/Tablet)
42. Normalize gender values (M/F/Other)

---

## 3. Data Access Control

### 3.1 Role-Based Access (RBAC)

| **Role** | **Access Level** | **Permissions** |
|---------|-----------------|-----------------|
| **Admin** | Full | Read, Write, Delete, Schema Change |
| **Analyst** | Read-Only | Query, Export (anonymized) |
| **ETL Service** | Write | Insert, Update (fact/dim tables) |
| **Dashboard** | Read-Only | Query (aggregated data) |

### 3.2 Data Masking Rules

**Sensitive Fields (PII):**
- `customer_email`: Masked as `****@domain.com`
- `phone_number`: Show last 4 digits only
- `employee_salary`: Show salary range, not exact value
- `user_id`: Hashed with SHA-256

---

## 4. Data Retention Policy

### 4.1 Retention Periods

| **Data Type** | **Hot Storage** | **Cold Storage** | **Archive** | **Deletion** |
|--------------|----------------|------------------|-------------|--------------|
| **Transactional (Sales)** | 1 year | 2-3 years | 4-7 years | Never |
| **User Activity Logs** | 90 days | 91-365 days | 1-2 years | After 2 years |
| **Dashboard Usage** | 180 days | 181-365 days | 1 year | After 1 year |
| **Usability Evaluations** | Permanent | - | - | Never |
| **Error Logs** | 30 days | 31-90 days | 90-180 days | After 180 days |

### 4.2 Data Archival Process

1. **Automated Monthly Archive Job**
   - Runs on 1st of each month at 02:00 UTC
   - Moves data older than hot storage period to cold storage (AWS S3 Glacier)
   - Compresses data with gzip (70% reduction)

2. **Archive Retrieval**
   - Standard retrieval: 3-5 hours
   - Expedited retrieval: 1-5 minutes (additional cost)

---

## 5. Data Privacy & Compliance

### 5.1 Compliance Standards

- **GDPR** (General Data Protection Regulation): User consent for data collection
- **PDPA** (Personal Data Protection Act - Indonesia): Data minimization
- **ISO 27001**: Information security management

### 5.2 User Rights

1. **Right to Access**: Users can request their data
2. **Right to Rectification**: Correct inaccurate data
3. **Right to Erasure**: Delete personal data upon request
4. **Right to Data Portability**: Export data in CSV/JSON

---

## 6. Metadata Management

### 6.1 Data Dictionary

Maintained in: `docs/DATA_DICTIONARY.md`

**Mandatory Metadata:**
- Column name
- Data type
- Description
- Business definition
- Source system
- Transformation rules applied
- Owner
- Last updated

### 6.2 Lineage Tracking

**Tools:** dbt (data build tool) for lineage visualization

**Tracked Information:**
- Data origin (source → staging → DW)
- Transformations applied
- Dependencies between tables
- Data refresh schedule

---

## 7. Data Quality Monitoring

### 7.1 Automated Quality Checks

**Frequency:** After each ETL run

**Checks Performed:**
1. Row count validation (expected vs. actual)
2. NULL value percentage per column
3. Duplicate detection
4. Referential integrity checks
5. Data type validation
6. Range checks for numeric fields

### 7.2 Quality Metrics Dashboard

**KPIs Tracked:**
- Data completeness rate: **99.1%** ✅
- Data accuracy rate: **99.5%** ✅
- ETL success rate: **100%** ✅
- Average data latency: **45 minutes** ✅

---

## 8. Change Management

### 8.1 Schema Change Process

1. **Proposal**: Document change request with impact analysis
2. **Review**: Data governance committee approval
3. **Testing**: Validate in staging environment
4. **Migration**: Execute with rollback plan
5. **Documentation**: Update data dictionary

### 8.2 Versioning

- Schema version tracked in `dw_metadata.schema_version` table
- All changes logged with timestamp, user, and description

---

## 9. Audit & Monitoring

### 9.1 Audit Logging

**Logged Events:**
- Data access (SELECT queries)
- Data modifications (INSERT/UPDATE/DELETE)
- Schema changes (DDL statements)
- User login/logout
- Failed authentication attempts

**Retention:** 1 year (hot), 2-3 years (archive)

### 9.2 Alerting

**Alert Triggers:**
- ETL failure
- Data quality threshold breached (<95% completeness)
- Unauthorized access attempt
- Disk space >80% full
- Query performance degradation (>10s)

**Notification Channels:**
- Email
- Slack integration
- SMS (critical alerts only)

---

## 10. Roles & Responsibilities

| **Role** | **Responsibility** |
|---------|-------------------|
| **Data Owner** | Business unit responsible for data accuracy |
| **Data Steward** | Enforce data quality standards |
| **Data Custodian** | Manage physical database (DBA) |
| **Data Analyst** | Consume data for insights |
| **ETL Developer** | Maintain data pipelines |

---

## 11. Contact & Escalation

**Data Governance Lead:** Raudatul Sholehah  
**Email:** [your-email]  
**Escalation Path:** Lead → Manager → CTO

---

**Document History:**

| **Version** | **Date** | **Changes** | **Author** |
|------------|---------|------------|-----------|
| 1.0 | 2025-12-05 | Initial version | Raudatul Sholehah |

