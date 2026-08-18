"""add report fields to assets

Revision ID: 1c6ddf3a4d21
Revises: ba8d0871b0c8
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1c6ddf3a4d21"
down_revision: Union[str, Sequence[str], None] = "ba8d0871b0c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assets",
        sa.Column("report_category", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "assets",
        sa.Column(
            "is_used_for_education",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "assets",
        sa.Column(
            "is_available_for_students",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "assets",
        sa.Column("has_lan", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "assets",
        sa.Column(
            "has_internet", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "assets",
        sa.Column(
            "has_intranet", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "assets",
        sa.Column(
            "received_in_current_year",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "assets",
        sa.Column("ownership_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "assets",
        sa.Column(
            "include_in_reports",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_index(
        op.f("ix_assets_report_category"),
        "assets",
        ["report_category"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_assets_report_category"), table_name="assets")
    op.drop_column("assets", "include_in_reports")
    op.drop_column("assets", "ownership_type")
    op.drop_column("assets", "received_in_current_year")
    op.drop_column("assets", "has_intranet")
    op.drop_column("assets", "has_internet")
    op.drop_column("assets", "has_lan")
    op.drop_column("assets", "is_available_for_students")
    op.drop_column("assets", "is_used_for_education")
    op.drop_column("assets", "report_category")
