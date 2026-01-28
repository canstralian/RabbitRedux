"""Initial migration - create api_requests, classifications, model_metadata tables

Revision ID: 7cb424717edc
Revises: 
Create Date: 2025-11-19 15:42:24.896195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cb424717edc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create api_requests table
    op.create_table(
        'api_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_requests_endpoint', 'api_requests', ['endpoint'])
    op.create_index('ix_api_requests_timestamp', 'api_requests', ['timestamp'])
    op.create_index('ix_api_requests_status_code', 'api_requests', ['status_code'])
    op.create_index('idx_endpoint_timestamp', 'api_requests', ['endpoint', 'timestamp'])
    op.create_index('idx_status_timestamp', 'api_requests', ['status_code', 'timestamp'])
    
    # Create classifications table
    op.create_table(
        'classifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code_snippet', sa.Text(), nullable=False),
        sa.Column('code_hash', sa.String(length=64), nullable=True),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_classifications_code_hash', 'classifications', ['code_hash'])
    op.create_index('ix_classifications_confidence_score', 'classifications', ['confidence_score'])
    op.create_index('ix_classifications_label', 'classifications', ['label'])
    op.create_index('ix_classifications_timestamp', 'classifications', ['timestamp'])
    op.create_index('ix_classifications_model_version', 'classifications', ['model_version'])
    op.create_index('idx_label_timestamp', 'classifications', ['label', 'timestamp'])
    op.create_index('idx_confidence_timestamp', 'classifications', ['confidence_score', 'timestamp'])
    op.create_index('idx_model_version_timestamp', 'classifications', ['model_version', 'timestamp'])
    
    # Create model_metadata table
    op.create_table(
        'model_metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('loaded_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name')
    )
    op.create_index('ix_model_metadata_is_active', 'model_metadata', ['is_active'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('model_metadata')
    op.drop_table('classifications')
    op.drop_table('api_requests')
