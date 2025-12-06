# 🆘 Disaster Recovery Plan (DRP)
## Nourish Beauty Data Warehouse

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Owner:** Raudatul Sholehah (2310817220002)

---

## 1. Executive Summary

This Disaster Recovery Plan (DRP) outlines procedures to restore the Nourish Beauty Data Warehouse in the event of:
- Hardware failure
- Data corruption
- Natural disaster
- Cyber attack
- Human error

**Recovery Objectives:**
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 1 hour

---

## 2. Backup Strategy

### 2.1 Backup Types

| **Backup Type** | **Frequency** | **Retention** | **Storage Location** |
|----------------|--------------|--------------|---------------------|
| **Full Backup** | Daily (00:00 UTC) | 30 days | On-premise + AWS S3 |
| **Incremental Backup** | Every 6 hours | 7 days | On-premise |
| **Transaction Log Backup** | Every 1 hour | 24 hours | On-premise |
| **Monthly Archive** | 1st of month | 1 year | AWS S3 Glacier |

### 2.2 Backup Commands

**PostgreSQL Full Backup:**
Daily full backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgresql"
DB_NAME="dw_nourish"

Create backup
pg_dump -U postgres -F c -b -v -f "$BACKUP_DIR/dw_nourish_$DATE.backup" $DB_NAME

Compress
gzip "$BACKUP_DIR/dw_nourish_$DATE.backup"

Upload to S3
aws s3 cp "$BACKUP_DIR/dw_nourish_$DATE.backup.gz" s3://nourish-dw-backup/daily/

Remove local backups older than 7 days
find $BACKUP_DIR -name "*.backup.gz" -mtime +7 -delete

echo "Backup completed: dw_nourish_$DATE.backup.gz"

text

**Incremental Backup (WAL Archiving):**
-- Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/postgresql/wal/%f'


### 2.3 Backup Verification

**Monthly Test Restore:**
- Schedule: 1st Sunday of each month
- Restore to staging environment
- Validate data integrity
- Document results

---

## 3. Disaster Scenarios & Recovery Procedures

### 3.1 Scenario 1: Database Corruption

**Symptoms:**
- Query errors (corrupt index)
- Inconsistent data
- PostgreSQL crash

**Recovery Steps:**

1. **Assess Damage**
-- Check database integrity
SELECT * FROM pg_stat_database WHERE datname = 'dw_nourish';

-- Identify corrupt tables
REINDEX DATABASE dw_nourish;


2. **Restore from Backup**
Stop PostgreSQL
sudo systemctl stop postgresql

Drop corrupted database
psql -U postgres -c "DROP DATABASE dw_nourish;"

Create new database
psql -U postgres -c "CREATE DATABASE dw_nourish;"

Restore latest backup
pg_restore -U postgres -d dw_nourish /backup/postgresql/dw_nourish_latest.backup

Start PostgreSQL
sudo systemctl start postgresql


3. **Verify Restoration**
-- Check row counts
SELECT COUNT() FROM fact_sales;
SELECT COUNT() FROM user_activity_log;

-- Validate referential integrity
SELECT * FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY';


4. **Resume ETL**
python run_etl.py --resume --from-checkpoint


**Estimated Recovery Time:** 2-3 hours

---

### 3.2 Scenario 2: Complete Server Failure

**Symptoms:**
- Server unresponsive
- Hardware failure (disk crash)
- Data center outage

**Recovery Steps:**

1. **Activate Standby Server**
Promote standby replica to primary
/usr/pgsql-14/bin/pg_ctl promote -D /var/lib/pgsql/14/data

2. **Update DNS/Connection Strings**
Update database.connection.py
DB_HOST = "standby.nourishbeauty.com" # New primary


3. **Restore from S3 Backup (if no standby)**
Download latest backup from S3
aws s3 cp s3://nourish-dw-backup/daily/dw_nourish_latest.backup.gz /tmp/

Decompress
gunzip /tmp/dw_nourish_latest.backup.gz

Restore
pg_restore -U postgres -d dw_nourish /tmp/dw_nourish_latest.backup


4. **Restore Transaction Logs (minimize data loss)**
Apply WAL archives
pg_resetwal -D /var/lib/pgsql/14/data


5. **Validate & Resume Operations**

**Estimated Recovery Time:** 4-6 hours

---

### 3.3 Scenario 3: Ransomware Attack

**Symptoms:**
- Encrypted files
- Ransom note
- Unauthorized access

**Recovery Steps:**

1. **Isolate Infected Systems**
Disconnect from network
sudo ifconfig eth0 down

Kill all connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'dw_nourish';"


2. **Assess Damage**
- Identify encrypted files
- Check backup integrity
- Review audit logs for entry point

3. **Restore from Clean Backup**
Use backup from BEFORE attack date
aws s3 cp s3://nourish-dw-backup/daily/dw_nourish_20251201.backup.gz /tmp/

Restore
pg_restore -U postgres -d dw_nourish /tmp/dw_nourish_20251201.backup


4. **Security Hardening**
- Change all passwords
- Update firewall rules
- Patch vulnerabilities
- Enable 2FA

5. **Resume Operations with Monitoring**

**Estimated Recovery Time:** 8-12 hours

---

### 3.4 Scenario 4: Accidental Data Deletion

**Symptoms:**
- User reports missing data
- Unexpected DROP TABLE/TRUNCATE

**Recovery Steps:**

1. **Identify Deletion Scope**
-- Check audit logs
SELECT * FROM audit_log
WHERE action IN ('DELETE', 'TRUNCATE', 'DROP')
ORDER BY timestamp DESC
LIMIT 100;


2. **Point-in-Time Recovery (PITR)**
Restore to specific timestamp (before deletion)
pg_restore -U postgres -d dw_nourish_recovery
--target-time='2025-12-05 10:30:00'
/backup/postgresql/dw_nourish_latest.backup


3. **Extract Deleted Data**
-- Copy missing data to production
INSERT INTO dw_nourish.fact_sales
SELECT * FROM dw_nourish_recovery.fact_sales
WHERE sales_key NOT IN (SELECT sales_key FROM dw_nourish.fact_sales);


4. **Validate Data Integrity**

**Estimated Recovery Time:** 1-2 hours

---

## 4. Recovery Procedures by Data Loss Severity

| **Data Loss** | **RPO** | **RTO** | **Recovery Method** |
|--------------|--------|--------|---------------------|
| **< 1 hour** | 1 hour | 30 min | Transaction log replay |
| **1-6 hours** | 6 hours | 2 hours | Incremental backup restore |
| **6-24 hours** | 24 hours | 4 hours | Daily backup restore + log replay |
| **> 24 hours** | 1 day | 8 hours | Full backup restore |

---

## 5. Backup Restoration Testing Schedule

| **Test Type** | **Frequency** | **Scope** | **Responsible** |
|--------------|--------------|-----------|----------------|
| **Single Table Restore** | Weekly | Random table | ETL Team |
| **Full Database Restore** | Monthly | Complete DW | DBA |
| **Disaster Simulation** | Quarterly | Full DR drill | IT Team |
| **Point-in-Time Recovery** | Bi-annually | Specific timestamp | DBA |

---

## 6. Communication Plan

### 6.1 Incident Response Team

| **Role** | **Name** | **Contact** | **Responsibility** |
|---------|---------|------------|-------------------|
| **Incident Commander** | Raudatul Sholehah | [phone/email] | Overall coordination |
| **DBA Lead** | [Name] | [phone/email] | Database recovery |
| **Infrastructure Lead** | [Name] | [phone/email] | Server/network |
| **Communication Lead** | [Name] | [phone/email] | Stakeholder updates |

### 6.2 Notification Hierarchy

**Severity Levels:**

| **Severity** | **Definition** | **Notify** | **Timeframe** |
|-------------|---------------|-----------|---------------|
| **Critical** | Complete DW down | All stakeholders | Immediate |
| **High** | Major data loss/corruption | Management + IT | Within 15 min |
| **Medium** | Degraded performance | IT Team | Within 1 hour |
| **Low** | Minor issues | DBA only | Within 4 hours |

### 6.3 Status Update Template
Subject: [SEVERITY] Nourish Beauty DW - Incident Update

Incident ID: DR-2025-001
Severity: HIGH
Status: IN PROGRESS

Impact:

[Describe impact]

Root Cause:

[If known]

Actions Taken:

[Action 1]

[Action 2]

Next Steps:

[Next action]

Estimated Resolution: [Time]

Next Update: [Time]

Contact: [RaudatulSholehah] ([raudtlsholhh27@gmail.com])


---

## 7. Post-Recovery Actions

### 7.1 Validation Checklist

- [ ] Verify row counts for all fact tables
- [ ] Check referential integrity
- [ ] Validate recent transactions
- [ ] Test ETL pipeline
- [ ] Verify dashboard functionality
- [ ] Run sample queries
- [ ] Check backup schedule resumed
- [ ] Review audit logs for anomalies

### 7.2 Post-Incident Review (PIR)

**Conducted Within:** 48 hours after resolution

**Agenda:**
1. Timeline of events
2. Root cause analysis
3. What worked well
4. What needs improvement
5. Action items to prevent recurrence

**Document Template:** `docs/PIR_YYYYMMDD.md`

---

## 8. Preventive Measures

### 8.1 Monitoring & Alerting

**Proactive Monitoring:**
- Disk space alerts (>80% threshold)
- Backup job failure alerts
- Database performance degradation
- Unusual query patterns
- Failed login attempts

**Tools:**
- Prometheus + Grafana
- PgBadger (PostgreSQL log analyzer)
- AWS CloudWatch

### 8.2 Regular Maintenance

**Weekly:**
- VACUUM ANALYZE (reclaim space)
- Index maintenance
- Log rotation

**Monthly:**
- Review slow queries
- Optimize table partitions
- Update statistics

**Quarterly:**
- Disaster recovery drill
- Security audit
- Capacity planning review

---

## 9. Backup Storage Locations

### 9.1 Primary Backup (On-Premise)

**Location:** `/backup/postgresql/`
**Storage:** 2TB SSD RAID 10
**Retention:** 7 days (incremental), 30 days (full)

### 9.2 Secondary Backup (Cloud)

**Provider:** AWS S3
**Bucket:** `s3://nourish-dw-backup/`
**Region:** `ap-southeast-1` (Singapore)
**Replication:** Multi-region (ap-southeast-2 Sydney)
**Retention:**
- Daily backups: 30 days
- Monthly archives: 1 year (S3 Glacier)

### 9.3 Offline Backup

**Medium:** External HDD (4TB)
**Frequency:** Monthly
**Storage Location:** Secure offsite facility
**Retention:** 6 months

---

## 10. Contact Information

**Emergency Hotline:** [Phone Number]  
**Email:** disaster-recovery@nourishbeauty.com  
**Slack Channel:** #dw-incidents

**Vendor Contacts:**
- AWS Support: [account-specific]
- PostgreSQL Expert: [consultant contact]
- Hardware Vendor: [support number]

---

## 11. Document Maintenance

**Review Frequency:** Quarterly  
**Next Review Date:** March 5, 2026  
**Approval:** [Manager Name]

**Version History:**

| **Version** | **Date** | **Changes** | **Author** |
|------------|---------|------------|-----------|
| 1.0 | 2025-12-05 | Initial DRP | Raudatul Sholehah |

---

**END OF DISASTER RECOVERY PLAN**
