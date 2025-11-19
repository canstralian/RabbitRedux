#!/bin/bash
#
# PostgreSQL Point-in-Time Recovery (PITR) Setup Script
#
# This script configures PostgreSQL for continuous archiving and PITR support.
#
# Usage: ./setup_pitr.sh [archive_directory]
#

set -euo pipefail

# Configuration
ARCHIVE_DIR="${1:-/var/lib/postgresql/archive}"
PG_VERSION="${PG_VERSION:-14}"
PG_DATA_DIR="/var/lib/postgresql/$PG_VERSION/main"
PG_CONF="$PG_DATA_DIR/postgresql.conf"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as postgres user or root
if [ "$(id -u)" != "0" ] && [ "$(whoami)" != "postgres" ]; then
    log_error "This script must be run as root or postgres user"
    exit 1
fi

log_info "=========================================="
log_info "PostgreSQL PITR Setup"
log_info "=========================================="

# Create archive directory
log_info "Creating archive directory: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR"
chown postgres:postgres "$ARCHIVE_DIR"
chmod 700 "$ARCHIVE_DIR"

# Backup current postgresql.conf
log_info "Backing up postgresql.conf"
cp "$PG_CONF" "$PG_CONF.backup.$(date +%Y%m%d_%H%M%S)"

# Configure WAL archiving
log_info "Configuring WAL archiving in postgresql.conf"

# Check if settings already exist
if grep -q "^wal_level" "$PG_CONF"; then
    log_warn "WAL settings already exist in postgresql.conf"
    log_warn "Please manually review and update if needed"
else
    cat >> "$PG_CONF" << EOF

# ==========================================
# Point-in-Time Recovery (PITR) Configuration
# Added by setup_pitr.sh on $(date)
# ==========================================

# Enable WAL archiving
wal_level = replica
archive_mode = on
archive_command = 'test ! -f $ARCHIVE_DIR/%f && cp %p $ARCHIVE_DIR/%f'
archive_timeout = 300  # Force archival every 5 minutes

# WAL configuration for better performance
max_wal_size = 2GB
min_wal_size = 80MB

# Keep extra WAL segments for replication/recovery
wal_keep_size = 1GB

# Enable checksums for data integrity (requires initdb with --data-checksums)
# data_checksums = on  # Uncomment if cluster was initialized with checksums

EOF
    log_info "✓ WAL archiving configured"
fi

# Create archive script for better reliability
ARCHIVE_SCRIPT="/usr/local/bin/archive_wal.sh"
log_info "Creating WAL archive script: $ARCHIVE_SCRIPT"

cat > "$ARCHIVE_SCRIPT" << 'EOF'
#!/bin/bash
# PostgreSQL WAL Archive Script
# This script is called by PostgreSQL for each WAL segment

WAL_PATH="$1"
WAL_FILE="$2"
ARCHIVE_DIR="/var/lib/postgresql/archive"
LOG_FILE="/var/log/postgresql/archive.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log archive attempt
echo "$(date '+%Y-%m-%d %H:%M:%S') - Archiving $WAL_FILE" >> "$LOG_FILE"

# Archive the WAL file
if [ -f "$ARCHIVE_DIR/$WAL_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $WAL_FILE already exists in archive" >> "$LOG_FILE"
    exit 0
fi

if cp "$WAL_PATH" "$ARCHIVE_DIR/$WAL_FILE"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $WAL_FILE archived" >> "$LOG_FILE"
    exit 0
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Failed to archive $WAL_FILE" >> "$LOG_FILE"
    exit 1
fi
EOF

chmod +x "$ARCHIVE_SCRIPT"
chown postgres:postgres "$ARCHIVE_SCRIPT"

log_info "✓ Archive script created"

# Create base backup script
BASE_BACKUP_SCRIPT="/usr/local/bin/create_base_backup.sh"
log_info "Creating base backup script: $BASE_BACKUP_SCRIPT"

cat > "$BASE_BACKUP_SCRIPT" << EOF
#!/bin/bash
# Create PostgreSQL base backup for PITR

BACKUP_DIR="/var/lib/postgresql/basebackup"
BACKUP_NAME="base_\$(date +%Y%m%d_%H%M%S)"

echo "Creating base backup: \$BACKUP_NAME"

# Create backup directory
mkdir -p "\$BACKUP_DIR"

# Create base backup
pg_basebackup -D "\$BACKUP_DIR/\$BACKUP_NAME" \\
    -Ft -z -Xs -P \\
    -U postgres

echo "Base backup created: \$BACKUP_DIR/\$BACKUP_NAME"
echo "Archive directory: $ARCHIVE_DIR"
echo ""
echo "To restore to a point in time, use:"
echo "  1. Stop PostgreSQL"
echo "  2. Clear data directory"
echo "  3. Extract base backup"
echo "  4. Create recovery.signal with restore_command"
echo "  5. Start PostgreSQL"
EOF

chmod +x "$BASE_BACKUP_SCRIPT"
chown postgres:postgres "$BASE_BACKUP_SCRIPT"

log_info "✓ Base backup script created at $BASE_BACKUP_SCRIPT"

# Create restore example script
RESTORE_SCRIPT="/usr/local/bin/restore_pitr_example.sh"
log_info "Creating PITR restore example: $RESTORE_SCRIPT"

cat > "$RESTORE_SCRIPT" << EOF
#!/bin/bash
# Example PostgreSQL PITR Restore Script
# 
# WARNING: This is an example script. Modify before using!
# This script will DESTROY the current database!

# Configuration
BASE_BACKUP="/var/lib/postgresql/basebackup/base_YYYYMMDD_HHMMSS"
ARCHIVE_DIR="$ARCHIVE_DIR"
PG_DATA_DIR="$PG_DATA_DIR"
TARGET_TIME="YYYY-MM-DD HH:MM:SS"  # e.g., "2025-11-19 10:30:00"

echo "WARNING: This will destroy the current database!"
echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
sleep 10

# Stop PostgreSQL
sudo systemctl stop postgresql

# Clear data directory (DANGEROUS!)
sudo rm -rf "\$PG_DATA_DIR"/*

# Extract base backup
sudo tar -xzf "\$BASE_BACKUP/base.tar.gz" -C "\$PG_DATA_DIR"
sudo tar -xzf "\$BASE_BACKUP/pg_wal.tar.gz" -C "\$PG_DATA_DIR/pg_wal"

# Create recovery configuration
cat > "\$PG_DATA_DIR/recovery.signal" << RECOVERY
restore_command = 'cp \$ARCHIVE_DIR/%f %p'
recovery_target_time = '\$TARGET_TIME'
recovery_target_action = 'promote'
RECOVERY

# Set permissions
sudo chown -R postgres:postgres "\$PG_DATA_DIR"

# Start PostgreSQL (will perform recovery)
sudo systemctl start postgresql

echo "PITR restore initiated. Check PostgreSQL logs for progress."
EOF

chmod +x "$RESTORE_SCRIPT"
chown postgres:postgres "$RESTORE_SCRIPT"

log_info "✓ PITR restore example created at $RESTORE_SCRIPT"

# Print summary
echo ""
log_info "=========================================="
log_info "PITR Setup Complete!"
log_info "=========================================="
echo ""
log_info "Next steps:"
echo "  1. Restart PostgreSQL: sudo systemctl restart postgresql"
echo "  2. Create initial base backup: $BASE_BACKUP_SCRIPT"
echo "  3. WAL files will be archived to: $ARCHIVE_DIR"
echo ""
log_info "Important files:"
echo "  - PostgreSQL config: $PG_CONF"
echo "  - Archive directory: $ARCHIVE_DIR"
echo "  - Archive script: $ARCHIVE_SCRIPT"
echo "  - Base backup script: $BASE_BACKUP_SCRIPT"
echo "  - Restore example: $RESTORE_SCRIPT"
echo ""
log_warn "Remember to:"
echo "  - Test your backup and restore procedures regularly"
echo "  - Monitor archive directory disk space"
echo "  - Set up archive cleanup (old WAL files)"
echo "  - Configure off-site backup for archive files"
echo ""
log_info "Restart PostgreSQL now? (y/n)"
read -r response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    sudo systemctl restart postgresql
    log_info "PostgreSQL restarted"
else
    log_warn "Please restart PostgreSQL manually: sudo systemctl restart postgresql"
fi
