"""
Database models for RabbitRedux API.

This module defines SQLAlchemy models for tracking API usage,
classification results, and model metadata.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class APIRequest(Base):
    """Track API requests for monitoring and analytics."""
    
    __tablename__ = 'api_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    status_code = Column(Integer, index=True)
    response_time = Column(Float)  # in seconds
    
    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_endpoint_timestamp', 'endpoint', 'timestamp'),
        Index('idx_status_timestamp', 'status_code', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<APIRequest(id={self.id}, endpoint='{self.endpoint}', timestamp={self.timestamp})>"


class Classification(Base):
    """Store classification results for analysis and auditing."""
    
    __tablename__ = 'classifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code_snippet = Column(Text, nullable=False)
    code_hash = Column(String(64), index=True)  # SHA256 hash for deduplication
    result = Column(JSON, nullable=False)  # Store full classification result
    confidence_score = Column(Float, index=True)
    label = Column(String(255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processing_time = Column(Float)  # in seconds
    model_version = Column(String(50), index=True)
    
    # Composite index for analytics queries
    __table_args__ = (
        Index('idx_label_timestamp', 'label', 'timestamp'),
        Index('idx_confidence_timestamp', 'confidence_score', 'timestamp'),
        Index('idx_model_version_timestamp', 'model_version', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Classification(id={self.id}, label='{self.label}', confidence={self.confidence_score})>"


class ModelMetadata(Base):
    """Track model versions and metadata."""
    
    __tablename__ = 'model_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    loaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1, index=True)  # 1 for active, 0 for inactive
    config = Column(JSON)  # Store model configuration
    
    def __repr__(self):
        return f"<ModelMetadata(name='{self.model_name}', version='{self.version}')>"
