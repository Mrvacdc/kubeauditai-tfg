"""change cis control remediation reference to text

Revision ID: 0c89249f9d9e
Revises: 749ad5a46e4b
Create Date: 2026-06-22 01:26:51.280497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c89249f9d9e'
down_revision: Union[str, None] = '749ad5a46e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "cis_controls",
        "remediation_reference",
        existing_type=sa.VARCHAR(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "cis_controls",
        "remediation_reference",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )

