"""
Example usage of the RabbitRedux database layer.

This script demonstrates how to:
1. Initialize the database
2. Create records
3. Query data
4. Use transactions
"""
import os
import sys
from datetime import datetime
import hashlib

# Set test database URL BEFORE importing database module
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///./example.db'
    print("Using SQLite database for examples: example.db")
    print("Set DATABASE_URL environment variable to use PostgreSQL\n")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import database and models directly to avoid loading the whole app
import importlib.util

parent_dir = os.path.dirname(os.path.dirname(__file__))

# Load database module
database_path = os.path.join(parent_dir, 'app', 'database.py')
spec = importlib.util.spec_from_file_location("database", database_path)
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)
db = database.db

# Load models module
models_path = os.path.join(parent_dir, 'app', 'models.py')
spec = importlib.util.spec_from_file_location("models", models_path)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
APIRequest = models.APIRequest
Classification = models.Classification
ModelMetadata = models.ModelMetadata


def initialize_database():
    """Initialize database connection."""
    print("Initializing database...")
    db.initialize()
    
    # Create tables for the example (normally done via migrations)
    db.create_tables()
    
    print(f"✓ Database initialized and tables created")


def check_database_health():
    """Check database connectivity."""
    print("\nChecking database health...")
    health = db.health_check()
    print(f"Status: {health['status']}")
    if 'environment' in health:
        print(f"Environment: {health['environment']}")
    if 'pool_stats' in health:
        print(f"Pool stats: {health['pool_stats']}")
    if 'error' in health:
        print(f"Error: {health['error']}")


def create_api_request_example():
    """Example: Create API request record."""
    print("\n--- Creating API Request ---")
    
    with db.session_scope() as session:
        request = APIRequest(
            endpoint='/classify',
            method='POST',
            timestamp=datetime.utcnow(),
            ip_address='192.168.1.100',
            user_agent='Python/3.12',
            status_code=200,
            response_time=0.234
        )
        session.add(request)
    
    print(f"✓ API request created")


def create_classification_example():
    """Example: Create classification record."""
    print("\n--- Creating Classification ---")
    
    code_snippet = "def hello_world():\n    print('Hello, World!')"
    code_hash = hashlib.sha256(code_snippet.encode()).hexdigest()
    
    with db.session_scope() as session:
        classification = Classification(
            code_snippet=code_snippet,
            code_hash=code_hash,
            result={
                'label': 'Python Function',
                'score': 0.95,
                'details': 'Simple Python function definition'
            },
            confidence_score=0.95,
            label='Python Function',
            timestamp=datetime.utcnow(),
            processing_time=0.156,
            model_version='v1.0.0'
        )
        session.add(classification)
    
    print(f"✓ Classification created")
    print(f"  Code hash: {code_hash[:16]}...")
    print(f"  Label: Python Function")
    print(f"  Confidence: 0.95")


def create_model_metadata_example():
    """Example: Create model metadata record."""
    print("\n--- Creating Model Metadata ---")
    
    with db.session_scope() as session:
        # Check if model already exists
        existing = session.query(ModelMetadata).filter_by(
            model_name='canstralian/RabbitRedux'
        ).first()
        
        if existing:
            print("Model metadata already exists, updating...")
            existing.version = 'v1.0.1'
            existing.updated_at = datetime.utcnow()
            existing.is_active = 1
        else:
            metadata = ModelMetadata(
                model_name='canstralian/RabbitRedux',
                version='v1.0.0',
                description='WhiteRabbitNeo Code Classification Model',
                loaded_at=datetime.utcnow(),
                is_active=1,
                config={
                    'max_length': 512,
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            )
            session.add(metadata)
    
    print(f"✓ Model metadata created/updated")


def query_api_requests_example():
    """Example: Query API requests."""
    print("\n--- Querying API Requests ---")
    
    with db.session_scope() as session:
        # Get last 5 requests
        requests = session.query(APIRequest)\
            .order_by(APIRequest.timestamp.desc())\
            .limit(5)\
            .all()
        
        print(f"Found {len(requests)} recent requests:")
        for req in requests:
            print(f"  {req.timestamp} - {req.method} {req.endpoint} - {req.status_code}")


def query_classifications_by_label_example():
    """Example: Query classifications by label."""
    print("\n--- Querying Classifications by Label ---")
    
    with db.session_scope() as session:
        # Count classifications by label
        from sqlalchemy import func
        
        results = session.query(
            Classification.label,
            func.count(Classification.id).label('count'),
            func.avg(Classification.confidence_score).label('avg_confidence')
        ).group_by(Classification.label).all()
        
        if results:
            print("Classification statistics:")
            for label, count, avg_conf in results:
                print(f"  {label}: {count} classifications, avg confidence: {avg_conf:.3f}")
        else:
            print("No classifications found")


def query_duplicate_code_example():
    """Example: Find duplicate code submissions."""
    print("\n--- Finding Duplicate Code Submissions ---")
    
    with db.session_scope() as session:
        from sqlalchemy import func
        
        duplicates = session.query(
            Classification.code_hash,
            func.count(Classification.id).label('occurrences')
        ).group_by(Classification.code_hash)\
         .having(func.count(Classification.id) > 1)\
         .all()
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate code submissions:")
            for code_hash, occurrences in duplicates:
                print(f"  Hash {code_hash[:16]}...: {occurrences} occurrences")
        else:
            print("No duplicate code submissions found")


def query_model_metadata_example():
    """Example: Query active models."""
    print("\n--- Querying Active Models ---")
    
    with db.session_scope() as session:
        active_models = session.query(ModelMetadata)\
            .filter_by(is_active=1)\
            .all()
        
        print(f"Found {len(active_models)} active models:")
        for model in active_models:
            print(f"  {model.model_name} v{model.version}")
            print(f"    Loaded: {model.loaded_at}")
            print(f"    Config: {model.config}")


def transaction_rollback_example():
    """Example: Transaction rollback on error."""
    print("\n--- Transaction Rollback Example ---")
    
    try:
        with db.session_scope() as session:
            request = APIRequest(
                endpoint='/test',
                method='GET',
                timestamp=datetime.utcnow()
            )
            session.add(request)
            
            # Simulate an error
            print("Simulating error during transaction...")
            raise ValueError("Simulated error")
    except ValueError:
        print("✓ Transaction rolled back successfully")
    
    # Verify data was not saved
    with db.session_scope() as session:
        count = session.query(APIRequest).filter_by(endpoint='/test').count()
        print(f"Records with endpoint='/test': {count} (should be 0)")


def performance_example():
    """Example: Batch operations for performance."""
    print("\n--- Batch Insert Performance Example ---")
    
    import time
    
    batch_size = 100
    print(f"Inserting {batch_size} records...")
    
    start_time = time.time()
    
    with db.session_scope() as session:
        for i in range(batch_size):
            request = APIRequest(
                endpoint=f'/endpoint{i % 10}',
                method='GET' if i % 2 == 0 else 'POST',
                timestamp=datetime.utcnow(),
                status_code=200
            )
            session.add(request)
    
    elapsed = time.time() - start_time
    print(f"✓ Inserted {batch_size} records in {elapsed:.3f}s")
    print(f"  Rate: {batch_size/elapsed:.0f} records/second")


def main():
    """Run all examples."""
    print("=" * 60)
    print("RabbitRedux Database Usage Examples")
    print("=" * 60)
    
    # Initialize
    initialize_database()
    check_database_health()
    
    # Create examples
    create_api_request_example()
    create_classification_example()
    create_model_metadata_example()
    
    # Query examples
    query_api_requests_example()
    query_classifications_by_label_example()
    query_duplicate_code_example()
    query_model_metadata_example()
    
    # Advanced examples
    transaction_rollback_example()
    performance_example()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    
    # Cleanup
    db.close()


if __name__ == '__main__':
    main()
