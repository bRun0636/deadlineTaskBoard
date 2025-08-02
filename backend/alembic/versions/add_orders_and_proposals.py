"""add orders and proposals tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем enum для ролей пользователей
    op.execute("CREATE TYPE userrole AS ENUM ('customer', 'executor', 'admin')")
    
    # Добавляем поле role в таблицу users
    op.add_column('users', sa.Column('role', sa.Enum('customer', 'executor', 'admin', name='userrole'), nullable=False, server_default='executor'))
    
    # Создаем enum для статусов заказов
    op.execute("CREATE TYPE orderstatus AS ENUM ('open', 'in_progress', 'completed', 'cancelled')")
    
    # Создаем enum для приоритетов заказов
    op.execute("CREATE TYPE orderpriority AS ENUM ('low', 'medium', 'high', 'urgent')")
    
    # Создаем таблицу orders
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('budget', sa.Float(), nullable=False),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='orderpriority'), nullable=False, server_default='medium'),
        sa.Column('status', sa.Enum('open', 'in_progress', 'completed', 'cancelled', name='orderstatus'), nullable=False, server_default='open'),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('assigned_executor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_executor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    
    # Создаем enum для статусов предложений
    op.execute("CREATE TYPE proposalstatus AS ENUM ('pending', 'accepted', 'rejected', 'withdrawn')")
    
    # Создаем таблицу proposals
    op.create_table('proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', 'withdrawn', name='proposalstatus'), nullable=False, server_default='pending'),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('executor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['executor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposals_id'), 'proposals', ['id'], unique=False)


def downgrade():
    # Удаляем таблицы
    op.drop_index(op.f('ix_proposals_id'), table_name='proposals')
    op.drop_table('proposals')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    
    # Удаляем enum типы
    op.execute("DROP TYPE proposalstatus")
    op.execute("DROP TYPE orderpriority")
    op.execute("DROP TYPE orderstatus")
    
    # Удаляем поле role из таблицы users
    op.drop_column('users', 'role')
    
    # Удаляем enum для ролей пользователей
    op.execute("DROP TYPE userrole") 