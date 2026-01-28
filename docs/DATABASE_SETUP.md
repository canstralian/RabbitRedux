# Database Setup Guide

This guide will help you set up the PostgreSQL database for RabbitRedux in different environments.

## Quick Start

### 1. Install PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Docker
```bash
docker run --name rabbitredux-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=rabbitredux \
  -p 5432:5432 \
  -d postgres:14
```

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE rabbitredux;
CREATE USER rabbitredux_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rabbitredux TO rabbitredux_user;

# Exit psql
\q
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your database URL:
```bash
DATABASE_URL=postgresql://rabbitredux_user:your_secure_password@localhost:5432/rabbitredux
ENVIRONMENT=development
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
# Apply all migrations
alembic upgrade head
```

### 6. Verify Setup

```python
from app.database import db

# Initialize database
db.initialize()

# Check health
health = db.health_check()
print(health)
# Should output: {"status": "healthy", ...}
```

## Environment-Specific Setup

### Development Environment

1. Create development database:
```bash
createdb rabbitredux_dev
```

2. Configure `.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rabbitredux_dev
ENVIRONMENT=development
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

3. Run migrations:
```bash
alembic upgrade head
```

### Staging Environment

1. Use separate database:
```bash
createdb rabbitredux_staging
```

2. Configure environment:
```bash
DATABASE_URL=postgresql://rabbitredux_user:password@staging-host:5432/rabbitredux_staging
ENVIRONMENT=staging
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

3. Run migrations:
```bash
alembic upgrade head
```

### Production Environment

#### Option 1: Direct PostgreSQL Connection

1. Configure production database with strong password
2. Set environment variables:
```bash
DATABASE_URL=postgresql://rabbitredux_user:strong_password@prod-host:5432/rabbitredux
ENVIRONMENT=production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600
```

3. Run migrations:
```bash
alembic upgrade head
```

#### Option 2: With PGBouncer (Recommended)

1. Install PGBouncer:
```bash
sudo apt install pgbouncer
```

2. Configure `/etc/pgbouncer/pgbouncer.ini`:
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
```

3. Create `/etc/pgbouncer/userlist.txt`:
```bash
# Generate MD5 hash
echo -n "passwordrabbitredux_user" | md5sum
# Output: abc123...

# Add to userlist.txt
"rabbitredux_user" "md5abc123..."
```

4. Start PGBouncer:
```bash
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer
```

5. Configure application:
```bash
DATABASE_URL=postgresql://rabbitredux_user:password@localhost:6432/rabbitredux
ENVIRONMENT=production
USE_PGBOUNCER=true
```

6. Run migrations (note: use PostgreSQL port, not PGBouncer):
```bash
# Temporarily set DATABASE_URL to PostgreSQL port
export DATABASE_URL=postgresql://rabbitredux_user:password@localhost:5432/rabbitredux
alembic upgrade head

# Then switch back to PGBouncer port for application
export DATABASE_URL=postgresql://rabbitredux_user:password@localhost:6432/rabbitredux
```

## Database Backups

### Setup Automated Backups

1. Configure backup directory:
```bash
sudo mkdir -p /var/backups/rabbitredux
sudo chown $USER:$USER /var/backups/rabbitredux
```

2. Test backup script:
```bash
./scripts/backup_database.sh
```

3. Schedule with cron:
```bash
crontab -e

# Add line for daily backup at 2 AM
0 2 * * * /path/to/RabbitRedux/scripts/backup_database.sh
```

4. Optional: Configure S3 backup:
```bash
# Install AWS CLI
pip install awscli
aws configure

# Set S3 bucket in .env
S3_BUCKET=your-backup-bucket
```

### Restore from Backup

```bash
# List available backups
ls -lh /var/backups/rabbitredux/

# Restore from backup
gunzip -c /var/backups/rabbitredux/rabbitredux_20251119_020000.sql.gz | \
  psql -U rabbitredux_user -d rabbitredux
```

### Setup Point-in-Time Recovery (PITR)

1. Run PITR setup script:
```bash
sudo ./scripts/setup_pitr.sh
```

2. Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

3. Create initial base backup:
```bash
sudo /usr/local/bin/create_base_backup.sh
```

4. Monitor WAL archiving:
```bash
# Check archive directory
ls -lh /var/lib/postgresql/archive/

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## Monitoring and Maintenance

### Check Database Size

```sql
SELECT 
    pg_size_pretty(pg_database_size('rabbitredux')) as database_size;
```

### Monitor Table Sizes

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Connection Pool Status

```python
from app.database import db

db.initialize()
health = db.health_check()
print(health['pool_stats'])
```

### Monitor Query Performance

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    calls,
    total_exec_time,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Regular Maintenance Tasks

```sql
-- Analyze tables (update statistics)
ANALYZE;

-- Vacuum tables (reclaim space)
VACUUM;

-- Full maintenance
VACUUM ANALYZE;

-- Reindex (if needed)
REINDEX DATABASE rabbitredux;
```

## Troubleshooting

### Cannot Connect to Database

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if database exists
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='rabbitredux'"

# Check connection
psql -h localhost -U rabbitredux_user -d rabbitredux -c "SELECT 1"
```

### Migration Errors

```bash
# Check current migration version
alembic current

# Show migration history
alembic history

# Force set version (use with caution!)
alembic stamp head
```

### Connection Pool Issues

```bash
# Check active connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE datname='rabbitredux'"

# Kill idle connections (if needed)
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='rabbitredux' AND state='idle'"
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Check PostgreSQL data directory
du -sh /var/lib/postgresql/14/main/

# Clean up old backups
find /var/backups/rabbitredux -name "*.sql.gz" -mtime +30 -delete

# Clean up old WAL files (if using PITR)
# Be careful! Only delete archived WAL files that are backed up
find /var/lib/postgresql/archive -name "*.wal" -mtime +7 -delete
```

## Security Best Practices

### 1. Use Strong Passwords

```bash
# Generate strong password
openssl rand -base64 32
```

### 2. Restrict Network Access

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```conf
# Local connections only
host    rabbitredux    rabbitredux_user    127.0.0.1/32    md5
host    rabbitredux    rabbitredux_user    ::1/128         md5
```

### 3. Enable SSL

In `postgresql.conf`:
```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

### 4. Regular Updates

```bash
# Update PostgreSQL
sudo apt update
sudo apt upgrade postgresql

# Update Python dependencies
pip install --upgrade -r requirements.txt
```

### 5. Monitor Logs

```bash
# Configure log rotation
sudo logrotate /etc/logrotate.d/postgresql-common

# Check logs regularly
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## Performance Tuning

### PostgreSQL Configuration

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Memory settings (adjust based on available RAM)
shared_buffers = 256MB              # 25% of RAM
effective_cache_size = 1GB          # 50-75% of RAM
work_mem = 16MB                     # For complex queries
maintenance_work_mem = 128MB        # For VACUUM, CREATE INDEX

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Query planner
random_page_cost = 1.1             # For SSD
effective_io_concurrency = 200     # For SSD

# Connection settings
max_connections = 200
```

Restart PostgreSQL after changes:
```bash
sudo systemctl restart postgresql
```

## Additional Resources

- [DATABASE.md](./DATABASE.md) - Complete database documentation
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PGBouncer Documentation](https://www.pgbouncer.org/)
