"""Add grade release control fields

Revision ID: a1b2c3d4e5f6
Revises: f3a9b2d4c6e1
Create Date: 2026-03-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f3a9b2d4c6e1'
branch_labels = None
depends_on = None


def upgrade():
    # Add grade release control fields
    op.add_column('grades', sa.Column('is_released', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('grades', sa.Column('released_at', sa.DateTime(), nullable=True))
    op.add_column('grades', sa.Column('released_by_id', sa.String(length=36), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_grades_released_by_id',
        'grades', 'users',
        ['released_by_id'], ['id']
    )

    # Update existing grades to be released by default (for backwards compatibility)
    op.execute("UPDATE grades SET is_released = true WHERE grade_value IS NOT NULL")

    # Make is_released NOT NULL after setting defaults
    op.alter_column('grades', 'is_released', nullable=False)


def downgrade():
    op.drop_constraint('fk_grades_released_by_id', 'grades', type_='foreignkey')
    op.drop_column('grades', 'released_by_id')
    op.drop_column('grades', 'released_at')
    op.drop_column('grades', 'is_released')
