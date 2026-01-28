# Database Layer Documentation

This directory contains comprehensive documentation and tools for the RabbitRedux database layer.

## Quick Links

- **[Database Setup Guide](docs/DATABASE_SETUP.md)** - Quick start guide for setting up the database
- **[Complete Documentation](docs/DATABASE.md)** - Comprehensive database documentation
- **[Usage Examples](examples/database_usage.py)** - Working code examples

## What's Included

### Database Models (`app/models.py`)
Three core models for tracking API usage, classification results, and model metadata:
- `APIRequest` - Monitor API calls
- `Classification` - Store classification results
- `ModelMetadata` - Track model versions

### Database Manager (`app/database.py`)
Production-ready database connection management:
- Connection pooling (SQLAlchemy + PGBouncer support)
- Health checks
- Transaction management
- Environment-specific configuration

### Migrations (`alembic/`)
Version-controlled schema changes using Alembic:
- Initial migration with all tables and indexes
- Auto-generation from model changes
- Rollback capabilities

### Backup Scripts (`scripts/`)
Automated backup and recovery tools:
- `backup_database.sh` - Daily backups with rotation
- `validate_backup.sh` - Backup integrity validation
- `setup_pitr.sh` - Point-in-Time Recovery setup

### Tests (`tests/test_database.py`)
Comprehensive test suite:
- 19 unit tests (all passing)
- Tests for models, connections, sessions, transactions
- Works with both SQLite and PostgreSQL

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Verify setup:**
   ```bash
   python examples/database_usage.py
   ```

## Documentation

- **DATABASE_SETUP.md** - Step-by-step setup guide for development, staging, and production
- **DATABASE.md** - Complete reference documentation covering all features

## Security

✅ No security vulnerabilities found (CodeQL scan)
✅ No hardcoded credentials
✅ SQL injection protection via SQLAlchemy ORM
✅ Connection pooling for resource management
✅ Environment-specific configurations

## Features

- ✅ PostgreSQL database schema
- ✅ SQLAlchemy ORM models
- ✅ Alembic migrations
- ✅ Connection pooling (SQLAlchemy + PGBouncer)
- ✅ Automated backups with rotation
- ✅ Point-in-Time Recovery (PITR)
- ✅ Query optimization with indexes
- ✅ Performance monitoring
- ✅ Health check endpoints
- ✅ Comprehensive documentation
- ✅ Working examples
- ✅ Full test coverage

## Support

For issues or questions, please refer to:
- [DATABASE.md](docs/DATABASE.md) - Complete documentation
- [DATABASE_SETUP.md](docs/DATABASE_SETUP.md) - Setup guide
- [Troubleshooting section](docs/DATABASE.md#troubleshooting) - Common issues

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
