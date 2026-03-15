"""make_student_user_optional

Revision ID: f3a9b2d4c6e1
Revises: c685a10fea77
Create Date: 2026-03-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a9b2d4c6e1'
down_revision = 'c685a10fea77'
branch_labels = None
depends_on = None


def upgrade():
    # Safe schema change: only relaxes a NOT NULL constraint.
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(length=36),
            nullable=True,
        )


def downgrade():
    # Guard downgrade to avoid destructive behavior if profile-only rows exist.
    bind = op.get_bind()
    null_count = bind.execute(sa.text('SELECT COUNT(*) FROM students WHERE user_id IS NULL')).scalar()
    if null_count and int(null_count) > 0:
        raise RuntimeError(
            'Cannot downgrade: students.user_id has NULL values from profile-only records. '
            'Attach those profiles to user accounts first.'
        )

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(length=36),
            nullable=False,
        )
