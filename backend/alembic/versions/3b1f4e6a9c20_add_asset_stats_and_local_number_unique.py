"""add asset stats support and local number uniqueness

Revision ID: 3b1f4e6a9c20
Revises: 1c6ddf3a4d21
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3b1f4e6a9c20"
down_revision: Union[str, Sequence[str], None] = "1c6ddf3a4d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEX_NAME = "uq_assets_organization_id_local_number"


def upgrade() -> None:
    op.create_index(
        INDEX_NAME,
        "assets",
        ["organization_id", "local_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name="assets")
