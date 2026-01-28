#!/bin/bash
#
# PostgreSQL Backup Validation Script
#
# This script validates database backups by restoring them to a test database
# and running integrity checks.
#
# Usage: ./validate_backup.sh <backup_file> [test_db_name]
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .env if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Parse DATABASE_URL if available
if [ -n "${DATABASE_URL:-}" ]; then
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*@.*/\1/p')
    DB_PASS=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
else
    DB_USER="${DB_USER:-postgres}"
    DB_PASS="${DB_PASS:-}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if backup file exists
if [ $# -lt 1 ]; then
    log_error "Usage: $0 <backup_file> [test_db_name]"
    exit 1
fi

BACKUP_FILE="$1"
TEST_DB_NAME="${2:-rabbitredux_test_$(date +%s)}"

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

export PGPASSWORD="$DB_PASS"

# Validation steps
validate_backup_file() {
    log_step "1. Validating backup file integrity"
    
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        log_info "Testing gzip integrity..."
        if gzip -t "$BACKUP_FILE" 2>/dev/null; then
            log_info "✓ Backup file is a valid gzip archive"
            return 0
        else
            log_error "✗ Backup file is corrupted or not a valid gzip archive"
            return 1
        fi
    else
        log_info "Backup file is not compressed"
    fi
    
    # Check if file is not empty
    if [ ! -s "$BACKUP_FILE" ]; then
        log_error "✗ Backup file is empty"
        return 1
    fi
    
    log_info "✓ Backup file exists and is not empty"
    return 0
}

create_test_database() {
    log_step "2. Creating test database: $TEST_DB_NAME"
    
    # Drop test database if it exists
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $TEST_DB_NAME" >/dev/null 2>&1 || true
    
    # Create test database
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "CREATE DATABASE $TEST_DB_NAME" >/dev/null 2>&1; then
        log_info "✓ Test database created successfully"
        return 0
    else
        log_error "✗ Failed to create test database"
        return 1
    fi
}

restore_backup() {
    log_step "3. Restoring backup to test database"
    
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        log_info "Decompressing and restoring backup..."
        if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
            -d "$TEST_DB_NAME" >/dev/null 2>&1; then
            log_info "✓ Backup restored successfully"
            return 0
        else
            log_error "✗ Failed to restore backup"
            return 1
        fi
    else
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
            < "$BACKUP_FILE" >/dev/null 2>&1; then
            log_info "✓ Backup restored successfully"
            return 0
        else
            log_error "✗ Failed to restore backup"
            return 1
        fi
    fi
}

validate_schema() {
    log_step "4. Validating database schema"
    
    # Check if expected tables exist
    local expected_tables=("api_requests" "classifications" "model_metadata")
    local all_tables_exist=true
    
    for table in "${expected_tables[@]}"; do
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
            -c "SELECT 1 FROM information_schema.tables WHERE table_name = '$table'" \
            | grep -q "1 row"; then
            log_info "✓ Table '$table' exists"
        else
            log_error "✗ Table '$table' not found"
            all_tables_exist=false
        fi
    done
    
    if [ "$all_tables_exist" = true ]; then
        log_info "✓ All expected tables found"
        return 0
    else
        log_error "✗ Schema validation failed"
        return 1
    fi
}

validate_indexes() {
    log_step "5. Validating indexes"
    
    local index_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
        -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'" | tr -d ' ')
    
    log_info "Found $index_count indexes"
    
    if [ "$index_count" -gt 0 ]; then
        log_info "✓ Indexes present in restored database"
        return 0
    else
        log_warn "⚠ No indexes found in restored database"
        return 0
    fi
}

check_record_counts() {
    log_step "6. Checking record counts"
    
    local tables=("api_requests" "classifications" "model_metadata")
    
    for table in "${tables[@]}"; do
        local count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
            -t -c "SELECT COUNT(*) FROM $table" 2>/dev/null | tr -d ' ' || echo "0")
        log_info "Table '$table': $count records"
    done
    
    log_info "✓ Record count check completed"
}

run_sample_queries() {
    log_step "7. Running sample queries"
    
    # Test basic SELECT
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
        -c "SELECT 1" >/dev/null 2>&1; then
        log_info "✓ Basic SELECT query works"
    else
        log_error "✗ Basic SELECT query failed"
        return 1
    fi
    
    # Test table queries
    local tables=("api_requests" "classifications" "model_metadata")
    for table in "${tables[@]}"; do
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" \
            -c "SELECT * FROM $table LIMIT 1" >/dev/null 2>&1; then
            log_info "✓ Query on '$table' works"
        else
            log_warn "⚠ Query on '$table' failed (table might be empty)"
        fi
    done
    
    log_info "✓ Sample queries completed"
}

cleanup_test_database() {
    log_step "8. Cleaning up test database"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $TEST_DB_NAME" >/dev/null 2>&1; then
        log_info "✓ Test database cleaned up"
        return 0
    else
        log_warn "⚠ Failed to clean up test database"
        return 0
    fi
}

generate_report() {
    local status=$1
    local backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
    
    echo ""
    echo "=========================================="
    echo "Backup Validation Report"
    echo "=========================================="
    echo "Backup File: $BACKUP_FILE"
    echo "Backup Size: $backup_size"
    echo "Test Database: $TEST_DB_NAME"
    echo "Timestamp: $(date)"
    echo ""
    
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}Status: PASSED ✓${NC}"
        echo ""
        echo "The backup is valid and can be restored successfully."
    else
        echo -e "${RED}Status: FAILED ✗${NC}"
        echo ""
        echo "The backup validation failed. Please check the errors above."
    fi
    echo "=========================================="
}

# Main execution
main() {
    local start_time=$(date +%s)
    local validation_failed=false
    
    log_info "=========================================="
    log_info "Starting Backup Validation"
    log_info "=========================================="
    log_info "Backup file: $BACKUP_FILE"
    log_info "Test database: $TEST_DB_NAME"
    echo ""
    
    # Run validation steps
    validate_backup_file || validation_failed=true
    
    if [ "$validation_failed" = false ]; then
        create_test_database || validation_failed=true
    fi
    
    if [ "$validation_failed" = false ]; then
        restore_backup || validation_failed=true
    fi
    
    if [ "$validation_failed" = false ]; then
        validate_schema || validation_failed=true
        validate_indexes
        check_record_counts
        run_sample_queries
    fi
    
    # Always try to cleanup
    cleanup_test_database
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_info "Validation completed in ${duration}s"
    
    if [ "$validation_failed" = true ]; then
        generate_report 1
        exit 1
    else
        generate_report 0
        exit 0
    fi
}

# Trap errors
trap 'log_error "Validation script encountered an error"; cleanup_test_database; exit 1' ERR

# Run main
main "$@"
