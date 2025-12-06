# 📦 Data Staging Layer
## Nourish Beauty Data Warehouse

**Purpose:** Temporary storage for data during ETL process before loading into production Data Warehouse.

---

## 1. Staging Architecture

Source Systems → Staging Tables → Transformation → Data Warehouse


### 1.1 Staging Database Schema

**Database:** `dw_nourish_staging`  
**Schema:** `stg`

**Tables:**
- `stg.sales_raw`
- `stg.hr_raw`
- `stg.marketing_raw`
- `stg.user_activity_raw`
- `stg.usability_raw`

---

## 2. Staging Table Structure

### Example: `stg.sales_raw`

CREATE TABLE stg.sales_raw (
staging_id SERIAL PRIMARY KEY,
load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
source_file VARCHAR(255),
raw_data JSONB,
is_processed BOOLEAN DEFAULT FALSE,
error_message TEXT,
processed_date TIMESTAMP
);

**Purpose:**
- Store raw data as-is from source
- Track processing status
- Enable reprocessing if transformation fails

---

## 3. Staging Process Flow

### 3.1 Extract to Staging

etl/extract/to_staging.py
def extract_to_staging(source_file):
"""Load raw data to staging"""
df = pd.read_csv(source_file)

# Convert to JSON
raw_data = df.to_json(orient='records')

# Insert to staging
query = """
    INSERT INTO stg.sales_raw (source_file, raw_data)
    VALUES (%s, %s)
"""
execute_query(query, (source_file, raw_data))

### 3.2 Transform from Staging

etl/transform/from_staging.py
def transform_staging_data():
"""Apply 40 transformation rules"""

# Load unprocessed records
query = "SELECT * FROM stg.sales_raw WHERE is_processed = FALSE"
staging_data = fetch_data(query)

for record in staging_data:
    try:
        # Apply transformations
        transformed = apply_transformations(record['raw_data'])
        
        # Mark as processed
        update_query = """
            UPDATE stg.sales_raw 
            SET is_processed = TRUE, processed_date = NOW()
            WHERE staging_id = %s
        """
        execute_query(update_query, (record['staging_id'],))
        
    except Exception as e:
        # Log error
        error_query = """
            UPDATE stg.sales_raw 
            SET error_message = %s
            WHERE staging_id = %s
        """
        execute_query(error_query, (str(e), record['staging_id']))

## 4. Staging Data Retention

**Policy:**
- Successfully processed records: Retained for **7 days**
- Failed records: Retained for **30 days** for investigation
- Automatic cleanup job runs daily

-- Cleanup query (runs daily at 02:00)
DELETE FROM stg.sales_raw
WHERE is_processed = TRUE
AND processed_date < NOW() - INTERVAL '7 days';

DELETE FROM stg.sales_raw
WHERE error_message IS NOT NULL
AND load_date < NOW() - INTERVAL '30 days';


## 5. Staging Benefits

1. **Error Isolation**: Failed transformations don't affect source data
2. **Reprocessability**: Can reprocess data if business rules change
3. **Audit Trail**: Track data lineage from source to DW
4. **Performance**: Separate staging reduces load on production DW
5. **Testing**: Test transformations on staging before production

---

**End of Data Staging Documentation**