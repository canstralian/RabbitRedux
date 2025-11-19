"""
Tests for the database layer.

These tests verify database connectivity, models, and operations.
"""
import pytest
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import models and database directly to avoid loading the whole app
import importlib.util

# Load models module
models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'models.py')
spec = importlib.util.spec_from_file_location("models", models_path)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
Base = models.Base
APIRequest = models.APIRequest
Classification = models.Classification
ModelMetadata = models.ModelMetadata

# Load database module
database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'database.py')
spec = importlib.util.spec_from_file_location("database", database_path)
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)
Database = database.Database
DatabaseConfig = database.DatabaseConfig


# Use SQLite for testing (no PostgreSQL required)
TEST_DATABASE_URL = "sqlite:///./test_rabbitredux.db"


@pytest.fixture
def test_db():
    """Create a test database instance."""
    # Set test database URL
    os.environ['DATABASE_URL'] = TEST_DATABASE_URL
    
    db = Database()
    db.initialize()
    
    # Create all tables
    db.create_tables()
    
    yield db
    
    # Cleanup
    db.drop_tables()
    db.close()
    
    # Remove test database file
    if os.path.exists("test_rabbitredux.db"):
        os.remove("test_rabbitredux.db")


@pytest.fixture
def session(test_db):
    """Create a test database session."""
    session = test_db.get_session()
    yield session
    session.close()


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DatabaseConfig()
        
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.environment in ['development', 'staging', 'production']
    
    def test_custom_pool_size(self):
        """Test custom pool size from environment."""
        os.environ['DB_POOL_SIZE'] = '20'
        config = DatabaseConfig()
        
        assert config.pool_size == 20
        
        # Cleanup
        del os.environ['DB_POOL_SIZE']
    
    def test_pgbouncer_mode(self):
        """Test PGBouncer configuration."""
        os.environ['USE_PGBOUNCER'] = 'true'
        config = DatabaseConfig()
        
        from sqlalchemy.pool import NullPool
        assert config.pool_class == NullPool
        
        # Cleanup
        del os.environ['USE_PGBOUNCER']


class TestDatabase:
    """Tests for Database class."""
    
    def test_initialization(self, test_db):
        """Test database initialization."""
        assert test_db._initialized is True
        assert test_db.engine is not None
        assert test_db.SessionLocal is not None
    
    def test_session_creation(self, test_db):
        """Test session creation."""
        session = test_db.get_session()
        assert session is not None
        session.close()
    
    def test_health_check(self, test_db):
        """Test database health check."""
        health = test_db.health_check()
        
        assert health['status'] == 'healthy'
        assert 'environment' in health


class TestAPIRequestModel:
    """Tests for APIRequest model."""
    
    def test_create_api_request(self, session):
        """Test creating an API request record."""
        request = APIRequest(
            endpoint='/classify',
            method='POST',
            timestamp=datetime.utcnow(),
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            status_code=200,
            response_time=0.5
        )
        
        session.add(request)
        session.commit()
        
        assert request.id is not None
        assert request.endpoint == '/classify'
    
    def test_query_api_requests(self, session):
        """Test querying API requests."""
        # Create multiple requests
        for i in range(5):
            request = APIRequest(
                endpoint=f'/endpoint{i}',
                method='GET',
                timestamp=datetime.utcnow(),
                status_code=200
            )
            session.add(request)
        
        session.commit()
        
        # Query all requests
        requests = session.query(APIRequest).all()
        assert len(requests) == 5
    
    def test_api_request_repr(self, session):
        """Test APIRequest string representation."""
        request = APIRequest(
            endpoint='/test',
            method='GET',
            timestamp=datetime.utcnow()
        )
        session.add(request)
        session.commit()
        
        repr_str = repr(request)
        assert 'APIRequest' in repr_str
        assert '/test' in repr_str


class TestClassificationModel:
    """Tests for Classification model."""
    
    def test_create_classification(self, session):
        """Test creating a classification record."""
        classification = Classification(
            code_snippet='def hello(): pass',
            code_hash='abc123',
            result={'label': 'Python Function', 'score': 0.95},
            confidence_score=0.95,
            label='Python Function',
            timestamp=datetime.utcnow(),
            processing_time=0.1,
            model_version='v1.0.0'
        )
        
        session.add(classification)
        session.commit()
        
        assert classification.id is not None
        assert classification.label == 'Python Function'
        assert classification.confidence_score == 0.95
    
    def test_query_by_label(self, session):
        """Test querying classifications by label."""
        # Create classifications with different labels
        for i in range(3):
            classification = Classification(
                code_snippet=f'code{i}',
                code_hash=f'hash{i}',
                result={'label': 'Python'},
                label='Python',
                timestamp=datetime.utcnow()
            )
            session.add(classification)
        
        for i in range(2):
            classification = Classification(
                code_snippet=f'code{i}',
                code_hash=f'hash{i}',
                result={'label': 'JavaScript'},
                label='JavaScript',
                timestamp=datetime.utcnow()
            )
            session.add(classification)
        
        session.commit()
        
        # Query Python classifications
        python_results = session.query(Classification).filter_by(label='Python').all()
        assert len(python_results) == 3
    
    def test_duplicate_code_detection(self, session):
        """Test finding duplicate code submissions."""
        code_hash = 'duplicate_hash'
        
        # Create multiple classifications with same hash
        for i in range(3):
            classification = Classification(
                code_snippet='duplicate code',
                code_hash=code_hash,
                result={'label': 'Test'},
                timestamp=datetime.utcnow()
            )
            session.add(classification)
        
        session.commit()
        
        # Query by hash
        duplicates = session.query(Classification).filter_by(code_hash=code_hash).all()
        assert len(duplicates) == 3


class TestModelMetadataModel:
    """Tests for ModelMetadata model."""
    
    def test_create_model_metadata(self, session):
        """Test creating model metadata."""
        metadata = ModelMetadata(
            model_name='canstralian/RabbitRedux',
            version='v1.0.0',
            description='Code classification model',
            loaded_at=datetime.utcnow(),
            is_active=1,
            config={'param1': 'value1'}
        )
        
        session.add(metadata)
        session.commit()
        
        assert metadata.id is not None
        assert metadata.model_name == 'canstralian/RabbitRedux'
        assert metadata.is_active == 1
    
    def test_unique_model_name(self, session):
        """Test model name uniqueness constraint."""
        metadata1 = ModelMetadata(
            model_name='test_model',
            version='v1.0.0',
            loaded_at=datetime.utcnow()
        )
        session.add(metadata1)
        session.commit()
        
        # Try to create another with same name
        metadata2 = ModelMetadata(
            model_name='test_model',
            version='v2.0.0',
            loaded_at=datetime.utcnow()
        )
        session.add(metadata2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            session.commit()
    
    def test_query_active_models(self, session):
        """Test querying active models."""
        # Create active and inactive models
        active_model = ModelMetadata(
            model_name='active_model',
            version='v1.0.0',
            loaded_at=datetime.utcnow(),
            is_active=1
        )
        inactive_model = ModelMetadata(
            model_name='inactive_model',
            version='v1.0.0',
            loaded_at=datetime.utcnow(),
            is_active=0
        )
        
        session.add(active_model)
        session.add(inactive_model)
        session.commit()
        
        # Query active models
        active_models = session.query(ModelMetadata).filter_by(is_active=1).all()
        assert len(active_models) == 1
        assert active_models[0].model_name == 'active_model'


class TestSessionScope:
    """Tests for session_scope context manager."""
    
    def test_successful_transaction(self, test_db):
        """Test successful transaction with session_scope."""
        with test_db.session_scope() as session:
            request = APIRequest(
                endpoint='/test',
                method='GET',
                timestamp=datetime.utcnow()
            )
            session.add(request)
        
        # Verify data was committed
        with test_db.session_scope() as session:
            requests = session.query(APIRequest).all()
            assert len(requests) == 1
    
    def test_failed_transaction_rollback(self, test_db):
        """Test transaction rollback on error."""
        try:
            with test_db.session_scope() as session:
                request = APIRequest(
                    endpoint='/test',
                    method='GET',
                    timestamp=datetime.utcnow()
                )
                session.add(request)
                # Force an error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify data was not committed
        with test_db.session_scope() as session:
            requests = session.query(APIRequest).all()
            assert len(requests) == 0


class TestIndexes:
    """Tests to verify indexes are created."""
    
    def test_api_requests_indexes(self, test_db, session):
        """Test that indexes exist on api_requests table."""
        # This is a basic test - in production, you'd query pg_indexes
        # For SQLite, we just verify the table was created with our schema
        request = APIRequest(
            endpoint='/test',
            method='GET',
            timestamp=datetime.utcnow()
        )
        session.add(request)
        session.commit()
        
        # Query should work (would be slow without indexes on large tables)
        result = session.query(APIRequest).filter_by(endpoint='/test').first()
        assert result is not None
    
    def test_classifications_indexes(self, test_db, session):
        """Test that indexes exist on classifications table."""
        classification = Classification(
            code_snippet='test',
            code_hash='hash',
            result={'test': 'data'},
            timestamp=datetime.utcnow()
        )
        session.add(classification)
        session.commit()
        
        # Query should work
        result = session.query(Classification).filter_by(code_hash='hash').first()
        assert result is not None
