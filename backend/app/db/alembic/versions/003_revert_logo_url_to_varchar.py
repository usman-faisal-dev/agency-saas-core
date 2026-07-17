"""revert_logo_url_to_varchar

Logo storage migrated from base64 data URIs (Text column) to file storage
URLs (VARCHAR(2048) is sufficient). See: Cloudflare R2 storage integration.

Revision ID: 003
Revises: 6295287caf8f
Create Date: 2026-07-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '6295287caf8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Truncate any existing base64 data before shrinking the column.
    # Existing base64 blobs will no longer render after the storage migration;
    # the agency user can re-upload their logo via the new file upload flow.
    op.execute("UPDATE organizations SET logo_url = NULL WHERE logo_url LIKE 'data:%'")
    op.execute("UPDATE clients SET logo_url = NULL WHERE logo_url LIKE 'data:%'")

    op.alter_column(
        'organizations', 'logo_url',
        existing_type=sa.Text(),
        type_=sa.String(2048),
        existing_nullable=True,
    )
    op.alter_column(
        'clients', 'logo_url',
        existing_type=sa.Text(),
        type_=sa.String(2048),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'clients', 'logo_url',
        existing_type=sa.String(2048),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        'organizations', 'logo_url',
        existing_type=sa.String(2048),
        type_=sa.Text(),
        existing_nullable=True,
    )
