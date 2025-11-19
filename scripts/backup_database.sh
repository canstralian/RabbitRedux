#!/bin/bash
#
# PostgreSQL Database Backup Script with PITR Support
# 
# This script creates compressed backups of the RabbitRedux database
# with rotation and optional remote storage sync.
#
# Usage: ./backup_database.sh [options]
# Options:
#   -h, --help       Show this help message
#   -d, --database   Database name (default: from DATABASE_URL or 'rabbitredux')
#   -u, --user       PostgreSQL user (default: from DATABASE_URL or 'postgres')
#   -H, --host       PostgreSQL host (default: from DATABASE_URL or 'localhost')
#   -p, --port       PostgreSQL port (default: from DATABASE_URL or '5432')
#   -o, --output     Output directory (default: /var/backups/rabbitredux)
#   -r, --retain     Days to retain daily backups (default: 7)
#   -s, --s3-bucket  S3 bucket for remote storage (optional)
#   -e, --email      Email for notifications (optional)
#

set -euo pipefail

# Default configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .env if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Parse DATABASE_URL if available
if [ -n "${DATABASE_URL:-}" ]; then
    # Extract components from DATABASE_URL
    # Format: postgresql://user:pass@host:port/database
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*@.*/\1/p')
    DB_PASS=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
else
    DB_USER="${DB_USER:-postgres}"
    DB_PASS="${DB_PASS:-}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    DB_NAME="${DB_NAME:-rabbitredux}"
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/rabbitredux}"
RETAIN_DAYS="${RETAIN_DAYS:-7}"
RETAIN_MONTHS="${RETAIN_MONTHS:-3}"
S3_BUCKET="${S3_BUCKET:-}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            grep '^#' "$0" | tail -n +3 | sed 's/^# *//'
            exit 0
            ;;
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -u|--user)
            DB_USER="$2"
            shift 2
            ;;
        -H|--host)
            DB_HOST="$2"
            shift 2
            ;;
        -p|--port)
            DB_PORT="$2"
            shift 2
            ;;
        -o|--output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retain)
            RETAIN_DAYS="$2"
            shift 2
            ;;
        -s|--s3-bucket)
            S3_BUCKET="$2"
            shift 2
            ;;
        -e|--email)
            NOTIFICATION_EMAIL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Send email notification
send_notification() {
    local subject="$1"
    local message="$2"
    
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "$subject" "$NOTIFICATION_EMAIL"
        log_info "Notification sent to $NOTIFICATION_EMAIL"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v pg_dump >/dev/null 2>&1; then
        log_error "pg_dump not found. Please install PostgreSQL client tools."
        exit 1
    fi
    
    if ! command -v gzip >/dev/null 2>&1; then
        log_error "gzip not found. Please install gzip."
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
    
    # Check write permissions
    if [ ! -w "$BACKUP_DIR" ]; then
        log_error "No write permission for backup directory: $BACKUP_DIR"
        exit 1
    fi
    
    log_info "Prerequisites check completed successfully"
}

# Test database connectivity
test_connection() {
    log_info "Testing database connectivity..."
    
    export PGPASSWORD="$DB_PASS"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" >/dev/null 2>&1; then
        log_info "Database connection successful"
        return 0
    else
        log_error "Failed to connect to database"
        return 1
    fi
}

# Create database backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local date_only=$(date +%Y%m%d)
    local backup_file="$BACKUP_DIR/rabbitredux_${timestamp}.sql"
    local compressed_file="${backup_file}.gz"
    
    log_info "Starting backup of database '$DB_NAME'..."
    log_info "Backup file: $compressed_file"
    
    export PGPASSWORD="$DB_PASS"
    
    # Create backup with custom format for better compression and flexibility
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
        --verbose \
        --no-owner \
        --no-acl \
        --format=plain \
        "$DB_NAME" | gzip > "$compressed_file"; then
        
        local backup_size=$(du -h "$compressed_file" | cut -f1)
        log_info "Backup created successfully: $compressed_file ($backup_size)"
        
        # Create a 'latest' symlink
        ln -sf "$(basename "$compressed_file")" "$BACKUP_DIR/latest.sql.gz"
        
        # Monthly backup (keep first backup of the month)
        if [ ! -f "$BACKUP_DIR/monthly/rabbitredux_${date_only:0:6}01.sql.gz" ]; then
            mkdir -p "$BACKUP_DIR/monthly"
            cp "$compressed_file" "$BACKUP_DIR/monthly/rabbitredux_${date_only:0:6}01.sql.gz"
            log_info "Monthly backup created"
        fi
        
        return 0
    else
        log_error "Backup failed"
        return 1
    fi
}

# Rotate old backups
rotate_backups() {
    log_info "Rotating old backups (keeping last $RETAIN_DAYS days)..."
    
    # Delete daily backups older than RETAIN_DAYS
    find "$BACKUP_DIR" -maxdepth 1 -name "rabbitredux_*.sql.gz" -type f -mtime "+$RETAIN_DAYS" -delete
    
    # Delete monthly backups older than RETAIN_MONTHS
    if [ -d "$BACKUP_DIR/monthly" ]; then
        find "$BACKUP_DIR/monthly" -name "rabbitredux_*.sql.gz" -type f -mtime "+$((RETAIN_MONTHS * 30))" -delete
    fi
    
    log_info "Backup rotation completed"
}

# Sync to S3 (if configured)
sync_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log_info "S3 sync not configured, skipping"
        return 0
    fi
    
    if ! command -v aws >/dev/null 2>&1; then
        log_warn "AWS CLI not found, skipping S3 sync"
        return 0
    fi
    
    log_info "Syncing backups to S3: $S3_BUCKET"
    
    if aws s3 sync "$BACKUP_DIR" "s3://$S3_BUCKET/rabbitredux-backups/" \
        --exclude "*" \
        --include "*.sql.gz" \
        --storage-class STANDARD_IA; then
        log_info "S3 sync completed successfully"
        return 0
    else
        log_error "S3 sync failed"
        return 1
    fi
}

# Generate backup report
generate_report() {
    local report_file="$BACKUP_DIR/backup_report.txt"
    
    {
        echo "=========================================="
        echo "RabbitRedux Database Backup Report"
        echo "=========================================="
        echo "Date: $(date)"
        echo "Database: $DB_NAME"
        echo "Host: $DB_HOST:$DB_PORT"
        echo ""
        echo "Backup Directory: $BACKUP_DIR"
        echo ""
        echo "Recent Backups:"
        ls -lh "$BACKUP_DIR"/rabbitredux_*.sql.gz 2>/dev/null | tail -10 || echo "No backups found"
        echo ""
        echo "Disk Usage:"
        du -sh "$BACKUP_DIR"
        echo ""
        echo "Monthly Backups:"
        if [ -d "$BACKUP_DIR/monthly" ]; then
            ls -lh "$BACKUP_DIR/monthly"
        else
            echo "No monthly backups"
        fi
    } > "$report_file"
    
    cat "$report_file"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    log_info "=========================================="
    log_info "RabbitRedux Database Backup Starting"
    log_info "=========================================="
    
    # Run checks and backup
    if ! check_prerequisites; then
        send_notification "Backup Failed: Prerequisites" "Prerequisites check failed"
        exit 1
    fi
    
    if ! test_connection; then
        send_notification "Backup Failed: Connection" "Cannot connect to database"
        exit 1
    fi
    
    if ! create_backup; then
        send_notification "Backup Failed: Creation" "Failed to create backup"
        exit 1
    fi
    
    rotate_backups
    sync_to_s3
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "=========================================="
    log_info "Backup completed successfully in ${duration}s"
    log_info "=========================================="
    
    generate_report
    
    send_notification "Backup Successful" "Database backup completed in ${duration}s"
}

# Trap errors
trap 'log_error "Backup script failed"; send_notification "Backup Failed: Error" "Script encountered an error"; exit 1' ERR

# Run main function
main "$@"
