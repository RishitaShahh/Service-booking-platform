"""Initial schema creation for users, services, time_slots, and bookings.

Revision ID: 0001_initial_migration
Revises: 
Create Date: 2026-09-22 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='customer'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # 2. Create services table
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)
    op.create_index(op.f('ix_services_provider_id'), 'services', ['provider_id'], unique=False)

    # 3. Create time_slots table
    op.create_table(
        'time_slots',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='available'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_time_slots_id'), 'time_slots', ['id'], unique=False)
    op.create_index(op.f('ix_time_slots_provider_id'), 'time_slots', ['provider_id'], unique=False)
    op.create_index(op.f('ix_time_slots_service_id'), 'time_slots', ['service_id'], unique=False)
    op.create_index(op.f('ix_time_slots_start_time'), 'time_slots', ['start_time'], unique=False)
    op.create_index(op.f('ix_time_slots_status'), 'time_slots', ['status'], unique=False)

    # 4. Create bookings table with unique constraint on slot_id
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('slot_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='confirmed'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('booking_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['slot_id'], ['time_slots.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_bookings_customer_id'), 'bookings', ['customer_id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_provider_id'), 'bookings', ['provider_id'], unique=False)
    op.create_index(op.f('ix_bookings_service_id'), 'bookings', ['service_id'], unique=False)
    op.create_index(op.f('ix_bookings_slot_id'), 'bookings', ['slot_id'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)



def downgrade() -> None:
    op.drop_table('bookings')
    op.drop_table('time_slots')
    op.drop_table('services')
    op.drop_table('users')
