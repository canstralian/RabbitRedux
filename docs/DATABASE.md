# RabbitRedux Database Layer Documentation

## Overview

This document describes the database infrastructure for the RabbitRedux application, including schema design, migration management, connection pooling, backup strategies, and query optimization.

## Table of Contents

1. [Database Schema](#database-schema)
2. [Migration Management with Alembic](#migration-management-with-alembic)
3. [Connection Pooling](#connection-pooling)
4. [Backup and Recovery](#backup-and-recovery)
5. [Query Optimization](#query-optimization)
6. [Environment Configuration](#environment-configuration)

---

## Database Schema

The RabbitRedux database tracks API usage, classification results, and model metadata for analytics and auditing purposes.

### Tables

#### 1. `api_requests`

Tracks all API requests for monitoring and analytics.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| endpoint | String(255) | API endpoint called |
| method | String(10) | HTTP method (GET, POST, etc.) |
| timestamp | DateTime | Request timestamp (UTC) |
| ip_address | String(45) | Client IP address (supports IPv6) |
| user_agent | String(500) | Client user agent string |
| status_code | Integer | HTTP response status code |
| response_time | Float | Response time in seconds |

**Indexes:**
- `ix_api_requests_endpoint`: Single-column index on endpoint
- `ix_api_requests_timestamp`: Single-column index on timestamp
- `ix_api_requests_status_code`: Single-column index on status_code
- `idx_endpoint_timestamp`: Composite index for endpoint + timestamp queries
- `idx_status_timestamp`: Composite index for status_code + timestamp queries

#### 2. `classifications`

Stores classification results for analysis and auditing.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| code_snippet | Text | Code that was classified |
| code_hash | String(64) | SHA256 hash for deduplication |
| result | JSON | Full classification result |
| confidence_score | Float | Confidence score of classification |
| label | String(255) | Classification label |
| timestamp | DateTime | Classification timestamp (UTC) |
| processing_time | Float | Processing time in seconds |
| model_version | String(50) | Model version used |

**Indexes:**
- `ix_classifications_code_hash`: For finding duplicate code
- `ix_classifications_confidence_score`: For confidence-based queries
- `ix_classifications_label`: For label-based filtering
- `ix_classifications_timestamp`: For time-based queries
- `ix_classifications_model_version`: For version-specific queries
- `idx_label_timestamp`: Composite index for analytics
- `idx_confidence_timestamp`: Composite index for confidence trends
- `idx_model_version_timestamp`: Composite index for version comparisons

#### 3. `model_metadata`

Tracks model versions and their metadata.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| model_name | String(255) | Model name (unique) |
| version | String(50) | Model version |
| description | Text | Model description |
| loaded_at | DateTime | When model was loaded |
| updated_at | DateTime | Last update timestamp |
| is_active | Integer | 1 if active, 0 if inactive |
| config | JSON | Model configuration |

**Indexes:**
- `ix_model_metadata_is_active`: For finding active models

---

## Migration Management with Alembic

### Overview

We use [Alembic](https://alembic.sqlalchemy.org/) for database schema versioning and migrations. This provides:
- Version control for database schemas
- Easy rollback capabilities
- Team collaboration on schema changes
- Production-safe deployments

### Directory Structure

```
RabbitRedux/
├── alembic/
│   ├── versions/          # Migration scripts
│   ├── env.py            # Alembic environment configuration
│   ├── README            # Alembic documentation
│   └── script.py.mako    # Migration template
├── alembic.ini           # Alembic configuration
└── app/
    ├── models.py         # SQLAlchemy models
    └── database.py       # Database connection management
```

### Common Migration Commands

#### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create a blank migration (for manual changes)
alembic revision -m "Description of changes"
```

#### Apply Migrations

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade to a specific version
alembic upgrade <revision_id>

# Upgrade one step forward
alembic upgrade +1
```

#### Rollback Migrations

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to a specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

#### View Migration History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show SQL that would be executed (without running it)
alembic upgrade head --sql
```

### Creating a Migration

1. **Modify models** in `app/models.py`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Add new column to table"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Test the migration** on development database:
   ```bash
   alembic upgrade head
   ```
5. **Verify the rollback** works:
   ```bash
   alembic downgrade -1
   alembic upgrade head
   ```

### Best Practices

1. **Always review auto-generated migrations** - Alembic may not detect all changes
2. **Test rollbacks** before deploying to production
3. **Use descriptive migration messages**
4. **Never modify existing migrations** that have been deployed
5. **Keep migrations small and focused** on one logical change

### Deployment Workflow

```bash
# Production deployment
export DATABASE_URL="postgresql://user:pass@prod-host:5432/rabbitredux"
alembic upgrade head
```

---

## Connection Pooling

### Overview

Connection pooling improves performance by reusing database connections instead of creating new ones for each request.

### Configuration Options

The database layer supports two connection pooling strategies:

#### 1. SQLAlchemy Connection Pool (Default)

Best for: Development, staging, and small to medium production deployments

Configuration via environment variables:

```bash
# Pool settings
DB_POOL_SIZE=10              # Number of connections to maintain
DB_MAX_OVERFLOW=20           # Additional connections when pool is full
DB_POOL_TIMEOUT=30           # Seconds to wait for available connection
DB_POOL_RECYCLE=3600         # Recycle connections after 1 hour
```

**Features:**
- Automatic connection health checks (`pool_pre_ping=True`)
- Connection recycling to prevent stale connections
- Overflow connections for traffic spikes

#### 2. PGBouncer (Production Recommended)

Best for: High-traffic production environments

To use PGBouncer, set:

```bash
USE_PGBOUNCER=true
```

This switches to `NullPool`, which doesn't maintain connections (PGBouncer handles pooling).

### PGBouncer Setup

#### Installation

```bash
# Ubuntu/Debian
sudo apt-get install pgbouncer

# RHEL/CentOS
sudo yum install pgbouncer
```

#### Configuration

Create `/etc/pgbouncer/pgbouncer.ini`:

```ini
[databases]
rabbitredux = host=localhost port=5432 dbname=rabbitredux

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
max_db_connections = 100
reserve_pool_size = 5
reserve_pool_timeout = 3
```

#### Pool Modes

- **session**: One server connection per client connection (most compatible)
- **transaction**: Server connection returned after each transaction (recommended)
- **statement**: Most aggressive, connection returned after each statement

#### User Authentication

Create `/etc/pgbouncer/userlist.txt`:

```
"postgres" "md5<password_hash>"
```

Generate password hash:

```bash
echo -n "passwordpostgres" | md5sum
```

#### Start PGBouncer

```bash
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer
```

#### Connect via PGBouncer

```bash
# Update DATABASE_URL to use PGBouncer port
export DATABASE_URL="postgresql://postgres:password@localhost:6432/rabbitredux"
export USE_PGBOUNCER=true
```

### Environment-Specific Configuration

#### Development

```bash
export ENVIRONMENT=development
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rabbitredux_dev"
export DB_POOL_SIZE=5
export DB_MAX_OVERFLOW=10
```

#### Production

```bash
export ENVIRONMENT=production
export DATABASE_URL="postgresql://postgres:secure_password@db-host:6432/rabbitredux"
export USE_PGBOUNCER=true
```

### Monitoring Connection Pool

The database health check endpoint provides pool statistics:

```python
from app.database import db

health = db.health_check()
print(health)
# Output:
# {
#     "status": "healthy",
#     "environment": "production",
#     "pool_stats": {
#         "pool_size": 10,
#         "checked_in": 8,
#         "checked_out": 2,
#         "overflow": 0
#     }
# }
```

---

## Backup and Recovery

### Overview

A comprehensive backup strategy ensures data protection and business continuity. We support:
- Automated daily backups
- Point-in-Time Recovery (PITR)
- On-demand backup creation
- Backup validation

### Backup Scripts

#### 1. Automated Backup Script

Location: `scripts/backup_database.sh`

Features:
- Creates compressed PostgreSQL dumps
- Implements backup rotation (keeps last 7 days + monthly)
- Supports remote storage (S3, etc.)
- Email notifications on failure

Usage:

```bash
# Run manual backup
./scripts/backup_database.sh

# Schedule with cron (daily at 2 AM)
0 2 * * * /path/to/RabbitRedux/scripts/backup_database.sh
```

#### 2. Point-in-Time Recovery (PITR)

PostgreSQL WAL-based continuous archiving for PITR support.

**Setup:**

1. Enable WAL archiving in `postgresql.conf`:

```conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /mnt/postgres/archive/%f && cp %p /mnt/postgres/archive/%f'
archive_timeout = 300  # Force archival every 5 minutes
```

2. Create base backup:

```bash
pg_basebackup -h localhost -U postgres -D /mnt/postgres/basebackup \
    -Ft -z -Xs -P
```

3. Configure archiving location in backup script

**Restore to Point in Time:**

```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Clear data directory
rm -rf /var/lib/postgresql/14/main/*

# Extract base backup
tar -xzf /mnt/postgres/basebackup/base.tar.gz -C /var/lib/postgresql/14/main/

# Create recovery.conf
cat > /var/lib/postgresql/14/main/recovery.signal << EOF
restore_command = 'cp /mnt/postgres/archive/%f %p'
recovery_target_time = '2025-11-19 10:30:00'
EOF

# Start PostgreSQL (will perform recovery)
sudo systemctl start postgresql
```

#### 3. Backup Validation Script

Location: `scripts/validate_backup.sh`

Tests backup integrity by:
- Restoring to a test database
- Running validation queries
- Checking record counts

Usage:

```bash
./scripts/validate_backup.sh /path/to/backup.sql.gz
```

### Backup Storage

#### Local Storage

```bash
# Default location
BACKUP_DIR=/var/backups/rabbitredux
```

#### Remote Storage (S3)

Configure in backup script:

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Update backup script to sync to S3
aws s3 sync $BACKUP_DIR s3://your-bucket/rabbitredux-backups/
```

### Restore Procedures

#### Full Database Restore

```bash
# From compressed backup
gunzip -c backup_2025-11-19.sql.gz | psql -U postgres -d rabbitredux

# From uncompressed backup
psql -U postgres -d rabbitredux < backup_2025-11-19.sql
```

#### Selective Table Restore

```bash
# Restore only specific table
pg_restore -U postgres -d rabbitredux -t api_requests backup.dump
```

### Backup Testing Schedule

Regular backup testing is critical:

- **Weekly**: Validate latest backup integrity
- **Monthly**: Full restore to test environment
- **Quarterly**: Disaster recovery drill

---

## Query Optimization

### Indexing Strategy

#### Current Indexes

All indexes are defined in `app/models.py` and created via migrations:

1. **Single-column indexes**: Fast lookups on frequently queried columns
2. **Composite indexes**: Optimized for multi-column WHERE clauses and JOINs
3. **Partial indexes**: (Future) For conditional queries

#### Index Maintenance

```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Rebuild indexes (after bulk operations)
REINDEX TABLE api_requests;

-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';
```

### Query Analysis Tools

#### 1. EXPLAIN ANALYZE

Always use EXPLAIN ANALYZE for query performance analysis:

```sql
-- Basic analysis
EXPLAIN ANALYZE
SELECT * FROM classifications 
WHERE label = 'Python Function' 
AND timestamp > NOW() - INTERVAL '7 days';

-- Detailed analysis
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT 
    c.label,
    COUNT(*) as count,
    AVG(c.confidence_score) as avg_confidence
FROM classifications c
WHERE c.timestamp > NOW() - INTERVAL '30 days'
GROUP BY c.label;
```

**What to look for:**
- Seq Scan vs Index Scan (prefer Index Scan)
- Execution time
- Buffer reads (shared vs temp)
- Join methods (Hash Join vs Nested Loop)

#### 2. Query Monitoring Extensions

Install `pg_stat_statements` for ongoing monitoring:

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

#### 3. Auto-Explain

Configure PostgreSQL to automatically log slow queries:

```conf
# In postgresql.conf
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 1000  # Log queries > 1 second
auto_explain.log_analyze = true
auto_explain.log_buffers = true
auto_explain.log_timing = true
auto_explain.log_nested_statements = true
```

### Common Query Patterns

#### 1. Time-Series Queries

Optimized with timestamp indexes:

```sql
-- API requests in last 24 hours
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as requests,
    AVG(response_time) as avg_response_time
FROM api_requests
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

#### 2. Classification Analytics

Optimized with composite indexes:

```sql
-- Model performance by version
SELECT 
    model_version,
    COUNT(*) as total_classifications,
    AVG(confidence_score) as avg_confidence,
    AVG(processing_time) as avg_processing_time
FROM classifications
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY model_version;
```

#### 3. Duplicate Detection

Optimized with hash index:

```sql
-- Find duplicate code submissions
SELECT 
    code_hash,
    COUNT(*) as occurrences,
    MAX(timestamp) as last_seen
FROM classifications
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY code_hash
HAVING COUNT(*) > 1;
```

### Performance Guidelines

1. **Use LIMIT** for large result sets
2. **Add indexes** for columns in WHERE, JOIN, and ORDER BY clauses
3. **Avoid SELECT \***: Specify needed columns
4. **Use EXISTS** instead of COUNT for existence checks
5. **Batch inserts** instead of individual INSERTs
6. **Use connection pooling** to reduce connection overhead
7. **Regular VACUUM**: Run VACUUM ANALYZE weekly

### Query Optimization Checklist

Before deploying a new query:

- [ ] Run EXPLAIN ANALYZE
- [ ] Check execution time < 100ms
- [ ] Verify index usage (no Seq Scan on large tables)
- [ ] Test with production-size dataset
- [ ] Add appropriate indexes if needed
- [ ] Document expected performance characteristics

---

## Environment Configuration

### Required Environment Variables

```bash
# Database connection
DATABASE_URL=postgresql://user:password@host:port/database

# Environment (affects logging and pooling)
ENVIRONMENT=development|staging|production

# Connection pooling (optional, uses defaults if not set)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# PGBouncer (optional)
USE_PGBOUNCER=false
```

### Configuration Files

#### .env.development

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rabbitredux_dev
ENVIRONMENT=development
DB_POOL_SIZE=5
```

#### .env.production

```bash
DATABASE_URL=postgresql://postgres:secure_pass@db.prod.com:6432/rabbitredux
ENVIRONMENT=production
USE_PGBOUNCER=true
```

### Loading Environment Variables

```python
from dotenv import load_dotenv
load_dotenv()  # Load from .env file
```

---

## Troubleshooting

### Connection Issues

```bash
# Test database connectivity
psql -h localhost -U postgres -d rabbitredux -c "SELECT 1"

# Check if database exists
psql -h localhost -U postgres -c "SELECT datname FROM pg_database"

# Check connection pool status
python -c "from app.database import db; db.initialize(); print(db.health_check())"
```

### Migration Issues

```bash
# Check current migration version
alembic current

# Show pending migrations
alembic history

# Force set version (use with caution!)
alembic stamp head
```

### Performance Issues

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PGBouncer Documentation](https://www.pgbouncer.org/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
