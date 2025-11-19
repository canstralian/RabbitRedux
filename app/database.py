"""
Database connection and session management for RabbitRedux.

This module provides database connectivity with connection pooling,
session management, and health checks.
"""
import os
import logging
import importlib.util
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

# Import Base from models without loading entire app package
_models_path = os.path.join(os.path.dirname(__file__), 'models.py')
_spec = importlib.util.spec_from_file_location("_models", _models_path)
_models = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_models)
Base = _models.Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration with environment-specific settings."""
    
    def __init__(self):
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://user:password@localhost:5432/rabbitredux'
        )
        
        # Environment detection
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Connection pool settings
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        
        # Connection pool type
        self.pool_class = pool.QueuePool
        
        # For production with PGBouncer, use NullPool
        if os.getenv('USE_PGBOUNCER', 'false').lower() == 'true':
            self.pool_class = pool.NullPool
            logger.info("Using NullPool for PGBouncer compatibility")
    
    def get_engine_kwargs(self):
        """Get engine configuration based on environment."""
        kwargs = {
            'poolclass': self.pool_class,
            'echo': self.environment == 'development',
            'pool_pre_ping': True,  # Enable connection health checks
        }
        
        # Only add pool settings if not using PGBouncer
        if self.pool_class != pool.NullPool:
            kwargs.update({
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
                'pool_timeout': self.pool_timeout,
                'pool_recycle': self.pool_recycle,
            })
        
        return kwargs


class Database:
    """Database manager with connection pooling and session handling."""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database engine and session factory."""
        if self._initialized:
            logger.warning("Database already initialized")
            return
        
        try:
            # Create engine with configured pool settings
            self.engine = create_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs()
            )
            
            # Add connection pool event listeners
            self._setup_event_listeners()
            
            # Create session factory
            session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            self.SessionLocal = scoped_session(session_factory)
            
            self._initialized = True
            logger.info(f"Database initialized successfully ({self.config.environment} mode)")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners for monitoring."""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug("Connection returned to pool")
    
    def create_tables(self):
        """Create all tables defined in models."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def get_session(self):
        """Get a new database session."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self):
        """Check database connectivity and return status."""
        if not self._initialized:
            return {"status": "error", "message": "Database not initialized"}
        
        try:
            from sqlalchemy import text
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            
            # Get pool statistics if available
            pool_stats = {}
            if hasattr(self.engine.pool, 'size'):
                pool_stats = {
                    'pool_size': self.engine.pool.size(),
                    'checked_in': self.engine.pool.checkedin(),
                    'checked_out': self.engine.pool.checkedout(),
                    'overflow': self.engine.pool.overflow(),
                }
            
            return {
                "status": "healthy",
                "environment": self.config.environment,
                "pool_stats": pool_stats
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def close(self):
        """Close all database connections."""
        if self._initialized and self.SessionLocal:
            self.SessionLocal.remove()
            self.engine.dispose()
            logger.info("Database connections closed")
            self._initialized = False


# Global database instance
db = Database()


def init_db():
    """Initialize the database (convenience function)."""
    db.initialize()


def get_db():
    """Get database session (for dependency injection)."""
    return db.get_session()
