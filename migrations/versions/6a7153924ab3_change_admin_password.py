"""change_admin_password

Revision ID: 6a7153924ab3
Revises: b386fe06d6b1
Create Date: 2026-03-17 06:27:32.366040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a7153924ab3'
down_revision = 'b386fe06d6b1'
branch_labels = None
depends_on = None


def upgrade():
    from app.services.auth_service import _get_admin_client
    import os
    
    # admin@isufst.edu.ph
    user_id = "dfc230b6-4ca6-4a46-9be0-6fbf74dcd87b"
    new_password = "cictadmin2026"
    
    admin_client = _get_admin_client()
    try:
        response = admin_client.auth.admin.update_user_by_id(
            user_id,
            attributes={'password': new_password}
        )
        print(f"Sucessfully updated password for user {user_id}")
    except Exception as e:
        print(f"Failed to update password for user {user_id}: {e}")
        # We don't necessarily want to fail the migration if this is already done or fails due to network,
        # but for a password change migration, failing is probably safer to avoid false sense of security.
        raise e


def downgrade():
    """Downgrade is not implemented as we don't know the previous password."""
    pass
