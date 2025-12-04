-- database/schema/create_staging.sql
CREATE TABLE staging_sales (...);
CREATE TABLE staging_hr (...);
CREATE TABLE staging_marketing (...);

-- database/schema/create_dimensions.sql
CREATE TABLE dim_customer (...);
CREATE TABLE dim_employee (...);
CREATE TABLE dim_tanggal (...);

-- database/schema/create_facts.sql
CREATE TABLE fact_sales (...);
CREATE TABLE fact_marketing_response (...);
CREATE TABLE fact_employee_performance (...);
